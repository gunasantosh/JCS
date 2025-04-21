from fastapi import APIRouter, Form, UploadFile, File, Request
from typing import List, Optional
from datetime import datetime
from app.models.schemas import WelcomeResponse
from app.utils.guardrails import validate_user_input
from dotenv import load_dotenv
from app.services.summarization import summarize_document
import tempfile
import shutil
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from PIL import Image
import pytesseract
import fitz  # PyMuPDF

load_dotenv()

router = APIRouter()
openai_client = OpenAI()


def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        text = page.get_text()
        if text.strip():
            full_text += text
        else:
            # If page has no text, fallback to OCR on image
            pix = page.get_pixmap(dpi=300)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(image)
            full_text += ocr_text
    doc.close()
    return full_text


def extract_text_via_ocr(file_path: str) -> Optional[str]:
    if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        return extract_text_from_image(file_path)
    elif file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    return None


@router.get("/")
def read_root():
    return WelcomeResponse(
        message="Welcome to the JCS Bot!",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@router.post("/chat")
async def chat(
    request: Request,
    prompt: str = Form(...),
    task: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    # Get task info
    print(f"Files: {[file.filename for file in files] if files else 'No files'}")
    task_info = validate_user_input(prompt, task, files)

    if task_info.task == "general conversation" and not files:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are JCS Bot, an enterprise assistant. Be concise and informative."},
                {"role": "user", "content": prompt}
            ],
        )
        return {"response": response.choices[0].message.content}

    elif task_info.task in ["summarization", "file Q&A"]:
        temp_dir = tempfile.mkdtemp()
        try:
            documents = []

            # Save each file and handle based on type
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    f.write(file.file.read())

                if file.filename.lower().endswith((".txt", ".md", ".docx")):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append(Document(text=content, metadata={"filename": file.filename}))
                else:
                    ocr_text = extract_text_via_ocr(file_path)
                    if ocr_text:
                        documents.append(Document(text=ocr_text, metadata={"filename": file.filename}))

            if not documents:
                return {"message": "No readable or extractable content found in uploaded files."}

            openai_embeddings = OpenAIEmbedding(model="text-embedding-3-small")
            llm_querying = OpenAI(model="gpt-3.5-turbo")

            index = VectorStoreIndex.from_documents(documents, embed_model=openai_embeddings)
            query_engine = index.as_query_engine(llm=llm_querying)
            response = query_engine.query(prompt)
            return str(response)

        finally:
            shutil.rmtree(temp_dir)

    return {"message": "Task not recognized or unsupported."}

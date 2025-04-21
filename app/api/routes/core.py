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
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


load_dotenv()

router = APIRouter()
openai_client = OpenAI()


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

    elif task_info.task == "summarization" and files or task_info.task == "file Q&A":
        temp_dir = tempfile.mkdtemp()
        try:
            # Save each file to the temp directory
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    f.write(file.file.read())

            # Use the files (example: llama-index SimpleDirectoryReader)
            documents = SimpleDirectoryReader(temp_dir).load_data()
            openai_embeddings=OpenAIEmbedding(model="text-embedding-3-small")
            llm_querying=OpenAI(model="gpt-3.5-turbo")

            # Create vector index
            index = VectorStoreIndex.from_documents(documents, embed_model=openai_embeddings)

            query_engine = index.as_query_engine(llm=llm_querying)
            response = query_engine.query(prompt)
            return str(response)


        finally:
            # Always clean up the temp directory
            shutil.rmtree(temp_dir)

    return {"message": "Task not recognized or unsupported."}

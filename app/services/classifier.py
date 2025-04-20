import logging
from fastapi import HTTPException
from openai import OpenAI
from models.schemas import UserInput, TaskCategoryResponseFormat

logger = logging.getLogger(__name__)
openai_client = OpenAI()


def classify_user_prompt(data: UserInput):
    logger.info("Starting Task extraction analysis")
    logger.debug(f"Input text: {data}")

    completion = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that classifies user prompts into task categories.\n"
                    "Categories: general conversation, summarization, comparison, data analysis and forecast, file Q&A.\n"
                    "Use optional context (task, files) to improve classification.\n"
                    "If the task is unclear, respond with 'unknown'."
                )
            },
            {"role": "user", "content": f"{data.prompt}, files: {data.files}, task: {data.task}"},
        ],
        response_format=TaskCategoryResponseFormat,
    )

    result = completion.choices[0].message.parsed
    logger.info(f"Task: {result.task}, Confidence: {result.confidence_score:.2f}")

    if result.task == "unknown":
        raise HTTPException(status_code=400, detail="Please provide a valid prompt. Insufficient context.")

    if result.task == "general conversation":
        response = openai_client.responses.create(
            model="gpt-3.5-turbo",
            instructions=(
                "You are an enterprise assistant that helps users with their queries. "
                "Maintain a balance between being informative and concise."
            ),
            input=data.prompt,
        )
        return {"response": response.output_text}

    elif result.task == "summarization":
        # You can implement summarization logic here
        pass

    return result

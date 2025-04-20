from fastapi import APIRouter

router = APIRouter(tags=["Tasks"])


@router.get("/summarization")
def get_summarization():
    """
    Endpoint to get the summarization task.
    """
    

    return 
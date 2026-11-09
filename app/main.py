import logging

from anthropic import APIError
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.generator import GenerationError, MissingApiKeyError, generate_ad_copy
from app.models import AdCopyResponse, ProductRequest

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Ad Copy Microservice", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ad-copy", response_model=AdCopyResponse)
async def create_ad_copy(body: ProductRequest) -> AdCopyResponse:
    try:
        return await generate_ad_copy(body)
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (GenerationError, APIError) as exc:
        raise HTTPException(status_code=502, detail="Ad copy generation failed") from exc

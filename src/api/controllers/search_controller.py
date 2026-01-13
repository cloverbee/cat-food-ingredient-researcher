from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from slowapi.util import get_remote_address

from src.core.config import settings
from src.core.rate_limit import limiter
from src.infrastructure.ai.search_service import SearchService

router = APIRouter()


class SearchQuery(BaseModel):
    query: str


class SearchResponse(BaseModel):
    result: str


def get_search_service():
    return SearchService()


@router.post("/", response_model=SearchResponse)
@limiter.limit(f"{settings.RATE_LIMIT_SEARCH_PER_MINUTE}/minute", key_func=get_remote_address)
async def search(
    request: Request,
    search_query: SearchQuery,
    service: SearchService = Depends(get_search_service),
):
    try:
        result = await service.search(search_query.query)
        return SearchResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

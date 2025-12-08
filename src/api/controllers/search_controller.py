from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.infrastructure.ai.search_service import SearchService

router = APIRouter()


class SearchQuery(BaseModel):
    query: str


class SearchResponse(BaseModel):
    result: str


def get_search_service():
    return SearchService()


@router.post("/", response_model=SearchResponse)
async def search(search_query: SearchQuery, service: SearchService = Depends(get_search_service)):
    try:
        result = await service.search(search_query.query)
        return SearchResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

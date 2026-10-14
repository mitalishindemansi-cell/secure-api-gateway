import httpx

from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import get_settings


router = APIRouter(prefix="/gateway", tags=["gateway"])
settings = get_settings()


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def gateway(request: Request, path: str):
    target_url = f"{settings.BACKEND_URL.rstrip('/')}/{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            backend_response = await client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                content=await request.body(),
            )

        return Response(
            content=backend_response.content,
            status_code=backend_response.status_code,
            media_type=backend_response.headers.get(
                "content-type",
                "application/json",
            ),
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Backend service unavailable",
        )
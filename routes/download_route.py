from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

from services.request_handlers import get_user_os

router = APIRouter()


@router.get("/")
async def download(request: Request, os: str = Query(default=None)):
    if os is None:
        os = get_user_os(request)
        if os is None:
            raise HTTPException(400, "Unknown OS. Please enter query parameters to download specific OS")
    os = os.lower()
    if os == "win" or os == "windows":
        return FileResponse("/home/ahmedh/test.txt", media_type="text/plain", filename="test.txt")
    if os == "ubuntu" or os == "debian":
        return FileResponse("/home/ahmedh/test.txt", media_type="text/plain", filename="test.txt")
    return RedirectResponse(url="/download", headers=request.headers)


@router.get("/test")
async def download_test():
    return FileResponse("/home/ahmedh/test.txt", media_type="text/plain", filename="test.txt")

import logging
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import kerberos

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('auth_server')


class KerberosMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get('Authorization')
        print(auth_header)
        if not auth_header or not auth_header.startswith('Negotiate '):
            logger.info("No Authorization header or not starting with Negotiate")
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        token = auth_header[len('Negotiate '):]
        try:
            result, context = kerberos.authGSSServerInit('HTTP')
            if result != kerberos.AUTH_GSS_COMPLETE:
                raise HTTPException(status_code=401, detail="Unauthorized")

            kerberos.authGSSServerStep(context, token)
            if kerberos.authGSSServerResponse(context) != 'complete':
                raise HTTPException(status_code=401, detail="Unauthorized")

            username = kerberos.authGSSServerUserName(context)
            request.state.user = username
            kerberos.authGSSServerClean(context)
            logger.info(f"Authenticated user: {username}")
        except kerberos.GSSError as e:
            logger.error(f"Kerberos authentication failed: {e}")
            raise HTTPException(status_code=401, detail="Kerberos authentication failed")

        response = await call_next(request)
        return response


app.add_middleware(KerberosMiddleware)


@app.get("/secure-data")
async def get_secure_data(request: Request):
    return {"message": f"Hello, {request.state.user}. You have accessed secure data!"}


@app.get("/")
async def read_root():
    return {"message": "This is a public endpoint."}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

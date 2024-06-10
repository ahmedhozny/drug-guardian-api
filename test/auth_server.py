from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from requests_kerberos import HTTPKerberosAuth, REQUIRED

app = FastAPI()

# Middleware to handle Kerberos authentication
class SPNEGOMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            response = JSONResponse(
                status_code=401, content={"detail": "Unauthorized"})
            response.headers['WWW-Authenticate'] = 'Negotiate'
            return response

        try:
            # Here we would validate the SPNEGO token (not shown)
            # For illustration purposes, we're bypassing validation
            # You should validate the token against Kerberos KDC
            response = await call_next(request)
        except Exception as e:
            response = JSONResponse(
                status_code=401, content={"detail": "Unauthorized"})
            response.headers['WWW-Authenticate'] = 'Negotiate'

        return response

# Add the SPNEGO middleware to the application
app.add_middleware(SPNEGOMiddleware)

@app.get("/protected-resource")
async def protected_resource():
    return {"message": "This is a protected resource"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

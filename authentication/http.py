from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


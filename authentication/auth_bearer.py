from typing import List

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import status

import schemas
from models import AccountDetails, AccountBearer, AccountSecurity, EmailAddresses
from storage import get_storage, StorageSession, Storage


class AuthBearer:
    __security = HTTPBearer()
    __pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    __secret = 'SECRET'
    __algorithm = 'HS256'
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    async def __call__(self, token: str = Depends(oauth2_scheme)):
        print("token:: " + token)
        if not self.verify_token(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token

    def verify_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, self.__secret, algorithms=[self.__algorithm])
            # Check if the token has expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return False

            # Additional checks can be added here (e.g., issuer, audience)
            # For example:
            # iss = payload.get("iss")
            # if iss != "expected_issuer":
            #     return False

            # Check if the subject (sub) is present in the payload
            sub = payload.get("sub")
            if not sub:
                return False

            return True
        except jwt.ExpiredSignatureError:

            return False
        except jwt.InvalidTokenError:
            return False

    @staticmethod
    def get_password_hash(password):
        return AuthBearer.__pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return AuthBearer.__pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, credentials: schemas.LoginBase) -> schemas.TokenBase:
        exception = HTTPException(401, "Incorrect username or password", {"WWW-Authenticate": "Bearer"})
        users: List[AccountSecurity] = await Storage.find(AccountSecurity, {AccountSecurity.account_id: credentials.account_id})

        if users is None or len(users) < 1:
            raise exception

        user = users[0] if users else None

        if not user or not AuthBearer.verify_password(credentials.password, user.password_hashed):
            raise exception

        access_token = self.create_access_token(data={"sub": credentials.email, "iat": datetime.utcnow()})
        token_data = {"access_token": access_token, "token_type": "Bearer"}

        Storage.new_object(AccountBearer(
            account_id=user.id,
            access_token=access_token
        ))
        return schemas.TokenBase(access_token=token_data["access_token"], token_type="Bearer")

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
            to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__secret, self.__algorithm)
        return encoded_jwt

    def verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, self.__secret, algorithms=[self.__algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
                )
            # Here, you would typically mark the email as verified in your database
            return {"email": email}
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
            )

    @staticmethod
    def revoke_token(db: Storage = Depends(get_storage), token: schemas.TokenBase = Depends()):
        tokens = Storage.find(AccountBearer, {AccountBearer.access_token: token.access_token})
        if tokens is None or len(tokens) == 0:
            raise HTTPException(400, detail="Invalid session token")
        token = tokens[0]
        Storage.remove_object(token)

    @staticmethod
    async def get_current_user(db: Session = Depends(get_storage), token: schemas.TokenBase = Depends()):
        token = token.access_token
        try:
            payload = jwt.decode(token, AuthBearer.__secret, algorithms=["HS256"])
        except ExpiredSignatureError as e:
            raise HTTPException(403, "Session expired.", {"WWW-Authenticate": "Bearer"})
        except Exception:
            raise HTTPException(403, "An error occurred while fetching you details.", {"WWW-Authenticate": "Bearer"})

        emp_email: str = payload.get("sub")
        emails: List[EmailAddresses] = Storage.find(EmailAddresses, {EmailAddresses.email: emp_email})
        if len(emails) < 1:
            raise HTTPException(401, "Could not validate credentials.", {"WWW-Authenticate": "Bearer"})
        email = emails[0]
        exp: int = payload.get("exp")
        if exp < datetime.utcnow().timestamp():
            raise HTTPException(403, "Session expired.", {"WWW-Authenticate": "Bearer"})
        users = Storage.find(AccountDetails, {AccountDetails.organization_uuid: email.organization_uuid})
        user = users[0]
        if user is None:
            raise HTTPException(401, "Could not validate credentials.", {"WWW-Authenticate": "Bearer"})
        return user

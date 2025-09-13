from pydantic import BaseModel


class User(BaseModel):
    nickname: str
    name: str
    picture: str
    email: str
    email_verified: bool
    sub: str

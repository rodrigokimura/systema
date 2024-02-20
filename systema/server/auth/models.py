from sqlmodel import Field, SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class UserBase(SQLModel):
    username: str = Field(..., primary_key=True)
    active: bool = True
    superuser: bool = False


class User(UserBase, table=True):
    hashed_password: str

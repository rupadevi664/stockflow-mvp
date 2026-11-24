from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    organization_name: str = Field(
        min_length=2,
        max_length=150
    )


class SignupResponse(BaseModel):
    message: str
    user_id: int
    organization_id: int
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    organization_id: int

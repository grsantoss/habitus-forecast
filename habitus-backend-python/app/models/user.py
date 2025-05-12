from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    company: str = Field(...)
    role: str = Field(default="user")
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)
    verification_token: Optional[str] = Field(default=None)
    reset_password_token: Optional[str] = Field(default=None)
    reset_password_expires: Optional[datetime] = Field(default=None)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "hashedpassword",
                "company": "Acme Inc.",
                "role": "user",
                "active": True,
            }
        }


class UserInDB(UserModel):
    """User model stored in database with password hash"""
    pass


class UserOut(BaseModel):
    """Model for user information returned to clients (no password)"""
    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    company: str
    role: str
    active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        } 
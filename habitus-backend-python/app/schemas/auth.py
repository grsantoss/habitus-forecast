from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr


class Token(BaseModel):
    """Token schema returned after successful login"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: Optional[str] = None


class UserBase(BaseModel):
    """Base model for user data"""
    email: EmailStr
    name: str
    company: str


class UserLogin(BaseModel):
    """Schema for user login data"""
    email: EmailStr
    password: str


class UserCreate(UserBase):
    """Schema for creating new users"""
    password: constr(min_length=8)
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    """Schema for updating user data"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    password: Optional[constr(min_length=8)] = None
    active: Optional[bool] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class NewPassword(BaseModel):
    """Schema for setting a new password"""
    token: str
    password: constr(min_length=8)
    password_confirm: str
    
    @property
    def passwords_match(self) -> bool:
        return self.password == self.password_confirm 
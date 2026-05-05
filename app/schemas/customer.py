from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(..., max_length=150)
    email: EmailStr
    address: str = Field(..., max_length=300)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=300)


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

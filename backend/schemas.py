from datetime import datetime
from pydantic import BaseModel, Field


class EventListItem(BaseModel):
    id: int
    title: str
    category: str
    venue: str
    city: str
    starts_at: datetime
    base_price: float
    banner_url: str | None


class EventDetail(EventListItem):
    description: str
    seat_map: dict


class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str | None
    city: str | None
    vip_tier: str | None
    created_at: datetime


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    vip_tier: str | None = None


class ReservationItem(BaseModel):
    id: int
    event_id: int
    event_title: str
    seats: list
    total_amount: float
    status: str
    created_at: datetime


class ReservationCreate(BaseModel):
    user_id: int
    event_id: int
    seats: list = Field(min_length=1)


class ReservationCreateResponse(BaseModel):
    reservation_id: int
    total_amount: float
    status: str


class LoginRequest(BaseModel):
    email: str


class LoginResponse(BaseModel):
    user_id: int
    full_name: str
    vip_tier: str | None


class CheckoutRequest(BaseModel):
    reservation_id: int
    provider: str


class CheckoutResponse(BaseModel):
    reservation_id: int
    payment_status: str
    receipt: dict

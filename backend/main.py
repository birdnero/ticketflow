from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import models, schemas
from .seed import seed_data

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TicketFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def _startup() -> None:
    with SessionLocal() as db:
        seed_data(db)


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow()}


@app.get("/events", response_model=list[schemas.EventListItem])
def list_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.starts_at.asc()).all()
    return [
        schemas.EventListItem(
            id=event.id,
            title=event.title,
            category=event.category,
            venue=event.venue,
            city=event.city,
            starts_at=event.starts_at,
            base_price=event.base_price,
            banner_url=event.banner_url,
        )
        for event in events
    ]


@app.get("/events/{event_id}", response_model=schemas.EventDetail)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return schemas.EventDetail(
        id=event.id,
        title=event.title,
        category=event.category,
        venue=event.venue,
        city=event.city,
        starts_at=event.starts_at,
        base_price=event.base_price,
        banner_url=event.banner_url,
        description=event.description,
        seat_map=event.seat_map,
    )


@app.get("/users/{user_id}", response_model=schemas.UserProfile)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        city=user.city,
        vip_tier=user.vip_tier,
        created_at=user.created_at,
    )


@app.get("/users/{user_id}/reservations", response_model=list[schemas.ReservationItem])
def user_reservations(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reservations = (
        db.query(models.Reservation)
        .filter(models.Reservation.user_id == user_id)
        .order_by(models.Reservation.created_at.desc())
        .all()
    )

    return [
        schemas.ReservationItem(
            id=reservation.id,
            event_id=reservation.event_id,
            event_title=reservation.event.title,
            seats=reservation.seats,
            total_amount=reservation.total_amount,
            status=reservation.status,
            created_at=reservation.created_at,
        )
        for reservation in reservations
    ]


@app.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return schemas.LoginResponse(
        user_id=user.id,
        full_name=user.full_name,
        vip_tier=user.vip_tier,
    )


@app.post("/reservations", response_model=schemas.ReservationCreateResponse)
def create_reservation(payload: schemas.ReservationCreate, db: Session = Depends(get_db)):
    user = db.get(models.User, payload.user_id)
    event = db.get(models.Event, payload.event_id)
    if not user or not event:
        raise HTTPException(status_code=404, detail="User or event not found")

    total = event.base_price * len(payload.seats)
    reservation = models.Reservation(
        user_id=user.id,
        event_id=event.id,
        seats=payload.seats,
        total_amount=total,
        status="pending",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return schemas.ReservationCreateResponse(
        reservation_id=reservation.id,
        total_amount=reservation.total_amount,
        status=reservation.status,
    )


@app.post("/checkout", response_model=schemas.CheckoutResponse)
def checkout(payload: schemas.CheckoutRequest, db: Session = Depends(get_db)):
    reservation = db.get(models.Reservation, payload.reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = "confirmed"
    payment = models.Payment(
        reservation_id=reservation.id,
        provider=payload.provider,
        status="paid",
        amount=reservation.total_amount,
        meta={"confirmation": f"TF-{reservation.id:05d}"},
    )
    db.add(payment)
    db.commit()

    return schemas.CheckoutResponse(
        reservation_id=reservation.id,
        payment_status="paid",
        receipt={
            "confirmation": f"TF-{reservation.id:05d}",
            "amount": reservation.total_amount,
            "provider": payload.provider,
        },
    )


@app.patch("/users/{user_id}", response_model=schemas.UserProfile)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email is not None:
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.city is not None:
        user.city = payload.city
    if payload.vip_tier is not None:
        user.vip_tier = payload.vip_tier
    db.commit()
    db.refresh(user)

    return schemas.UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        city=user.city,
        vip_tier=user.vip_tier,
        created_at=user.created_at,
    )

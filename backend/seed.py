from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from . import models


def _seat_map(section: str, rows: int, seats_per_row: int) -> dict:
    layout = []
    for row_idx in range(1, rows + 1):
        row_label = f"{section}{row_idx}"
        seats = []
        for seat_idx in range(1, seats_per_row + 1):
            seat_id = f"{row_label}-{seat_idx:02d}"
            status = "available"
            if seat_idx % 9 == 0:
                status = "blocked"
            elif seat_idx % 7 == 0:
                status = "reserved"
            seats.append({"id": seat_id, "status": status})
        layout.append({"row": row_label, "seats": seats})
    return {"section": section, "rows": layout}


def seed_data(db: Session) -> None:
    if db.query(models.User).first():
        return

    users = [
        models.User(
            email="ava.bond@example.com",
            full_name="Ava Bond",
            phone="+1 415 555 0142",
            city="San Francisco",
            vip_tier="Gold",
        ),
        models.User(
            email="liam.chen@example.com",
            full_name="Liam Chen",
            phone="+1 646 555 0194",
            city="New York",
            vip_tier="Silver",
        ),
        models.User(
            email="sofia.koval@example.com",
            full_name="Sofia Koval",
            phone="+380 67 555 1020",
            city="Kyiv",
            vip_tier=None,
        ),
    ]
    db.add_all(users)
    db.flush()

    now = datetime.utcnow()
    events = [
        models.Event(
            title="Aurora Lights Live",
            description="Immersive electronic showcase with synchronized visuals and a live orchestra.",
            category="Music",
            venue="Orion Dome",
            city="San Francisco",
            starts_at=now + timedelta(days=10, hours=2),
            base_price=79.0,
            banner_url="assets/events/aurora.jpg",
            seat_map={"sections": [_seat_map("A", 4, 14), _seat_map("B", 5, 16)]},
        ),
        models.Event(
            title="City Jazz Weekender",
            description="Three-night residency from the Nova Quartet with late-night jam sessions.",
            category="Music",
            venue="Blue Note Hall",
            city="New York",
            starts_at=now + timedelta(days=18, hours=1),
            base_price=62.0,
            banner_url="assets/events/jazz.jpg",
            seat_map={"sections": [_seat_map("A", 5, 12), _seat_map("C", 3, 14)]},
        ),
        models.Event(
            title="Future Finance Summit",
            description="Keynotes and workshops on fintech, AI, and sustainable markets.",
            category="Conference",
            venue="Summit Center",
            city="Chicago",
            starts_at=now + timedelta(days=25, hours=4),
            base_price=140.0,
            banner_url="assets/events/finance.jpg",
            seat_map={"sections": [_seat_map("S", 6, 18)]},
        ),
        models.Event(
            title="Midnight Cinema: Noir Set",
            description="Curated film night with live score and themed lounge.",
            category="Film",
            venue="Luna Theater",
            city="Los Angeles",
            starts_at=now + timedelta(days=8, hours=6),
            base_price=38.0,
            banner_url="assets/events/noir.jpg",
            seat_map={"sections": [_seat_map("L", 4, 16), _seat_map("R", 4, 16)]},
        ),
        models.Event(
            title="Design Systems Lab",
            description="Hands-on masterclass focused on building scalable product UI kits.",
            category="Workshop",
            venue="Studio Forge",
            city="Austin",
            starts_at=now + timedelta(days=14, hours=3),
            base_price=95.0,
            banner_url="assets/events/design.jpg",
            seat_map={"sections": [_seat_map("D", 3, 10)]},
        ),
        models.Event(
            title="Skyline Rooftop Festival",
            description="Two-stage summer event with indie bands, street food, and art pop-ups.",
            category="Festival",
            venue="Vista Roof Park",
            city="Seattle",
            starts_at=now + timedelta(days=30, hours=5),
            base_price=55.0,
            banner_url="assets/events/festival.jpg",
            seat_map={"sections": [_seat_map("F", 5, 20)]},
        ),
    ]
    db.add_all(events)
    db.flush()

    reservations = [
        models.Reservation(
            user_id=users[0].id,
            event_id=events[0].id,
            seats=["A1-01", "A1-02"],
            total_amount=158.0,
            status="confirmed",
        ),
        models.Reservation(
            user_id=users[1].id,
            event_id=events[1].id,
            seats=["A2-05", "A2-06", "A2-07"],
            total_amount=186.0,
            status="pending",
        ),
        models.Reservation(
            user_id=users[2].id,
            event_id=events[3].id,
            seats=["L2-08"],
            total_amount=38.0,
            status="confirmed",
        ),
    ]
    db.add_all(reservations)
    db.flush()

    payments = [
        models.Payment(
            reservation_id=reservations[0].id,
            provider="card",
            status="paid",
            amount=158.0,
            meta={"card_last4": "0142", "method": "visa"},
        ),
        models.Payment(
            reservation_id=reservations[2].id,
            provider="apple_pay",
            status="paid",
            amount=38.0,
            meta={"device": "iPhone 15"},
        ),
    ]
    db.add_all(payments)

    db.commit()

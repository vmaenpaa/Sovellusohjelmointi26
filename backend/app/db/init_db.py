from app.db.session import SessionLocal
from app.services.seed import (
    seed_system_activity_types,
    seed_system_activity_unit_links,
    seed_system_unit_types,
)


def init_db() -> None:
    db = SessionLocal()
    try:
        unit_types = seed_system_unit_types(db)
        activity_types = seed_system_activity_types(db)
        db.flush()
        seed_system_activity_unit_links(db, activity_types, unit_types)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
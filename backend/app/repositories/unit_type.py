from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.unit_type import UnitType


def get_by_slug(db: Session, slug: str) -> UnitType | None:
	return db.scalar(select(UnitType).where(UnitType.slug == slug))


def get_or_create_system(
	db: Session,
	*,
	name: str,
	slug: str,
	unit_label: str,
) -> UnitType:
	unit_type = get_by_slug(db, slug)
	if unit_type is None:
		unit_type = UnitType(
			name=name,
			slug=slug,
			unit_label=unit_label,
			is_system=True,
		)
		db.add(unit_type)
	return unit_type

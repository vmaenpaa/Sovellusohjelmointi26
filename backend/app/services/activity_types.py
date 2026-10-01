import re

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.repositories.activity_type import (
	create_custom,
	get_custom_by_slug,
	list_visible_to_user,
)
from app.repositories.unit_type import get_by_ids as get_unit_types_by_ids
from app.schemas.activity_type import ActivityTypeCreate


class ActivityTypeConflictError(ValueError):
	pass


class ActivityTypeValidationError(ValueError):
	pass


def _normalize_slug(value: str) -> str:
	return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def list_activity_types(db: Session, user_id: int) -> list[ActivityType]:
	activity_types = list_visible_to_user(db, user_id)
	for activity_type in activity_types:
		activity_type.unit_links.sort(key=lambda link: link.sort_order)
	return activity_types


def create_activity_type(
	db: Session,
	user_id: int,
	activity_type_data: ActivityTypeCreate,
) -> ActivityType:
	slug_source = (
		activity_type_data.name
		if activity_type_data.slug is None
		else activity_type_data.slug
	)
	slug = _normalize_slug(slug_source)
	if not slug:
		raise ActivityTypeValidationError("Activity type slug cannot be empty")

	if get_custom_by_slug(db, user_id, slug) is not None:
		raise ActivityTypeConflictError("Activity type slug already exists")

	unit_type_ids = [link.unit_type_id for link in activity_type_data.unit_links]
	if len(set(unit_type_ids)) != len(unit_type_ids):
		raise ActivityTypeValidationError("Unit type cannot be repeated")

	unit_types = get_unit_types_by_ids(db, set(unit_type_ids))
	unit_types_by_id = {unit_type.id: unit_type for unit_type in unit_types}
	unknown_unit_type_ids = set(unit_type_ids) - unit_types_by_id.keys()
	if unknown_unit_type_ids:
		raise ActivityTypeValidationError("Unknown unit_type_id")

	try:
		activity_type = create_custom(
			db,
			user_id=user_id,
			name=activity_type_data.name,
			slug=slug,
		)
		activity_type.unit_links = [
			ActivityTypeUnitType(
				unit_type=unit_types_by_id[link.unit_type_id],
				sort_order=link.sort_order,
				is_required=link.is_required,
				per_set=int(link.per_set),
			)
			for link in activity_type_data.unit_links
		]
		db.flush()
	except IntegrityError as error:
		raise ActivityTypeConflictError("Activity type slug already exists") from error

	activity_type.unit_links.sort(key=lambda link: link.sort_order)
	return activity_type

import secrets

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .db.session import engine, settings
from .models import ActivityType, ActivityTypeUnitType, UnitType, User


class AdminAuth(AuthenticationBackend):

    def __init__(self, secret_key: str, username: str, password: str):
        super().__init__(secret_key=secret_key)
        self.username = username
        self.password = password

    async def login(self, request: Request) -> bool | RedirectResponse:
        form = await request.form()
        username, password = form["username"], form["password"]

        if not (
            secrets.compare_digest(str(username), self.username)
            and secrets.compare_digest(str(password), self.password)
        ):
            return False

        request.session.update({"token": secrets.token_urlsafe(32)})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.display_name]
    form_excluded_columns = [User.password_hash]


class ActivityTypeAdmin(ModelView, model=ActivityType):
    column_list = [
        ActivityType.id,
        ActivityType.name,
        ActivityType.slug,
        ActivityType.is_system,
        ActivityType.user_id,
    ]


class UnitTypeAdmin(ModelView, model=UnitType):
    column_list = [
        UnitType.id,
        UnitType.name,
        UnitType.slug,
        UnitType.unit_label,
        UnitType.is_system,
    ]


class ActivityTypeUnitTypeAdmin(ModelView, model=ActivityTypeUnitType):
    column_list = [
        ActivityTypeUnitType.activity_type_id,
        ActivityTypeUnitType.unit_type_id,
        ActivityTypeUnitType.sort_order,
        ActivityTypeUnitType.is_required,
        ActivityTypeUnitType.per_set,
    ]


def setup_admin(app: FastAPI) -> Admin:
    authentication_backend = AdminAuth(
        secret_key=settings.sqladmin_secret_key,
        username=settings.sqladmin_username,
        password=settings.sqladmin_password,
    )
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(ActivityTypeAdmin)
    admin.add_view(UnitTypeAdmin)
    admin.add_view(ActivityTypeUnitTypeAdmin)
    return admin

from .default import CRUDBase
from backend.models.user import User
from backend.domain.user import UserCreate, UserRead


class UserRepo(CRUDBase[User, UserCreate, UserRead]):
    pass

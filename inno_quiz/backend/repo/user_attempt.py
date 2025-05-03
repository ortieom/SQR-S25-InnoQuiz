from .default import CRUDBase
from backend.models.user_attempt import UserAttempt
from backend.domain.user_attempt import UserAttemptCreate, UserAttemptRead


class UserAttemptRepo(CRUDBase[UserAttempt, UserAttemptCreate, UserAttemptRead]):
    pass

class ServiceError(Exception):
    ...


class QuizNotFoundError(ServiceError):
    ...


class UserNotFoundError(ServiceError):
    ...

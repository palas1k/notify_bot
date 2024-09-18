class BaseError(Exception):
    def __init__(
            self,
            message='An unknown error occurred.',
    ) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class BaseErrorGroup(ExceptionGroup[BaseError]):
    def __init__(self, errors: list[BaseError], **_) -> None:
        super().__init__('Some errors occurred', errors)


class DatabaseError(BaseError):
    def __init__(
            self, message
    ) -> None:
        super().__init__(message=message)


class NotFoundError(DatabaseError):
    def __init__(self, model_name: str) -> None:
        super().__init__(
            message=f'Модель {model_name} не найдена',
        )

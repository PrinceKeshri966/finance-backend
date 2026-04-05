from fastapi import HTTPException, status


class FinanceAPIError(HTTPException):
    """
    Base class for all custom errors in this project.
    Inheriting from HTTPException means FastAPI handles these automatically.
    """
    pass


class NotFoundError(FinanceAPIError):
    def __init__(self, resource: str, resource_id: int = None):
        if resource_id is not None:
            detail = f"{resource} with id {resource_id} was not found"
        else:
            detail = f"{resource} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(FinanceAPIError):
    def __init__(self, message: str = "You don't have permission to do that"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class UnauthorizedError(FinanceAPIError):
    def __init__(self, message: str = "Authentication is required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ConflictError(FinanceAPIError):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)

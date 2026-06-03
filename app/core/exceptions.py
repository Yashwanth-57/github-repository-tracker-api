class AppError(Exception):
    pass

class NotFoundError(AppError):
    pass

class ConflictError(AppError):
    pass

class ExternalAPIError(AppError):
    pass

class ExternalAPITimeoutError(AppError):
    pass
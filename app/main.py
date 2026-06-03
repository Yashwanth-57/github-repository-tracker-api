# from fastapi import FastAPI

# from app.api.repository_rouutes import router


# app = FastAPI()

# app.include_router(router)


from fastapi import FastAPI

from app.api.repository_rouutes import router
from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    ExternalAPIError,
    ExternalAPITimeoutError,
)
from app.core.handlers import global_exception_handler


app = FastAPI()

app.include_router(router)

# 🔥 register exception handlers
app.add_exception_handler(NotFoundError, global_exception_handler)
app.add_exception_handler(ConflictError, global_exception_handler)
app.add_exception_handler(ExternalAPIError, global_exception_handler)
app.add_exception_handler(ExternalAPITimeoutError, global_exception_handler)
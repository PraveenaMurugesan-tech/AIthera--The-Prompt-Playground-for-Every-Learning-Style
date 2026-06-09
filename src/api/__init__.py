from fastapi import FastAPI

from src.auth import router as auth_router


def include_routers(app: FastAPI) -> None:
	"""Include all application routers on the FastAPI `app`.

	This helper centralizes router inclusion so the project entrypoint
	can simply call `include_routers(app)` after creating the `FastAPI` app.
	"""

	app.include_router(auth_router)

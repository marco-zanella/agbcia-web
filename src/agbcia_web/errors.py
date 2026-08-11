"""Maps agbcia's exception hierarchy to JSON error responses."""

from __future__ import annotations

from agbcia.exceptions import BuildError, GbaCiaError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def _error_body(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BuildError)
    async def _build_error_handler(_request: Request, exc: BuildError) -> JSONResponse:
        return JSONResponse(status_code=500, content=_error_body(exc.error_code, str(exc)))

    @app.exception_handler(GbaCiaError)
    async def _gba_cia_error_handler(_request: Request, exc: GbaCiaError) -> JSONResponse:
        return JSONResponse(status_code=422, content=_error_body(exc.error_code, str(exc)))

    @app.exception_handler(ValueError)
    async def _value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content=_error_body("invalid_value", str(exc)))

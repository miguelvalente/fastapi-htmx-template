from typing import Annotated

from fastapi import APIRouter, Form, Request, Response, status  # Added Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src.auth.security import create_access_token, hash_password, verify_password
from src.config import settings
from src.database import fetch_one
from src.log import logger
from src.templates import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def sign_in(
    request: Request,
    email: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
):
    print("email", email)
    user = await get_user_by_email(email)

    if not user or not await verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect email or password"},
            status_code=401,
        )

    token = create_access_token(email)
    response = Response(
        status_code=status.HTTP_200_OK,
        headers={"HX-Redirect": "/document/"},
    )
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {token}",
        httponly=True,
        secure=settings.ENVIRONMENT != "DEV",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("Authorization", path="/", httponly=True)
    return response


async def get_user_by_email(email: str):
    query = "SELECT password, email from auth_user a where a.email = %(email)s"
    return await fetch_one(query, params={"email": email})


async def insert_user(email: str, password: bytes):
    query = """
    INSERT INTO auth_user (email, password)
    VALUES (%(email)s, %(password)s)
    RETURNING email;
    """
    return await fetch_one(query, params={"email": email, "password": password})


async def seed_default_user():
    user = await get_user_by_email(settings.DEFAULT_USER_EMAIL)
    if user:
        logger.debug(
            "Default super admin already exists.", extra={"email": user["email"]}
        )
        return

    logger.debug("Creating default super admin.")
    hashed_password = hash_password(settings.DEFAULT_USER_PW)
    email = await insert_user(
        email=settings.DEFAULT_USER_EMAIL,
        password=hashed_password,
    )
    logger.debug("Default super admin created.", extra={"email": email})

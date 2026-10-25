import secrets
from fastapi import Header, HTTPException
from .config import service_key, admin_key


def require_service(x_service_key: str = Header(default="")):
    if not secrets.compare_digest(x_service_key, service_key()):
        raise HTTPException(401, "Clé de service requise.")


def require_admin(x_admin_key: str = Header(default="")):
    if not secrets.compare_digest(x_admin_key, admin_key()):
        raise HTTPException(401, "Clé administrateur requise.")

from typing import List

from fastapi import Request, Depends, HTTPException, status

from PhotoShare.app.services.auth_service import get_current_user


class Roles:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user=Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not authorizated')


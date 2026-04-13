from fastapi import Depends, HTTPException, status

from app.utils.deps import get_current_user


def role_required(allowed_roles: list):
    """Dependency factory: returns a checker that verifies the user's role."""

    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
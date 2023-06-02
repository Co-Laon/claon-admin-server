from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.util.db import db
from claon_admin.common.util.auth import get_subject
from claon_admin.model.auth import RequestUser

CurrentUser = Annotated[RequestUser, Depends(get_subject)]

Session = Annotated[AsyncSession, Depends(db.get_db)]

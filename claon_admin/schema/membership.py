from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from claon_admin.common.util.db import Base


class MembershipMember(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    start_time = Column(DateTime, nullable=False)
    expired_time = Column(DateTime, nullable=False)

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("MembershipMember"), uselist=False)
    center_fee_id = Column(String(length=255), ForeignKey("tb_center_fee.id", ondelete="CASCADE"), nullable=False)
    center_fee = relationship("CenterFee", backref=backref("MembershipMember"), uselist=False)

from datetime import datetime
from decimal import Decimal
import uuid as uuid_module

from sqlalchemy import DateTime, func, UUID, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column
from src.db.database import Base


class Wallet(Base):
    """Wallet model, which represents balance information, creation and modification dates."""

    __tablename__ = "wallets"
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid_module.uuid4,
        unique=True,
        nullable=False,
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

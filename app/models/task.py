from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from datetime import datetime

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    # completed_at: Mapped[datetime] = mapped_column(nullable=True)
    completed_at: Mapped[bool] = mapped_column(nullable=True, default=None)
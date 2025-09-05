from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer
Base = declarative_base()

class ShortLink(Base):
    __tablename__ = "short_links"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    target_type: Mapped[str] = mapped_column(String(16))
    target_id: Mapped[str] = mapped_column(String(36))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

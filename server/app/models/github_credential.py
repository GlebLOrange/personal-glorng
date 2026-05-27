from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseModelMixin


class GitHubCredential(BaseModelMixin, Base):
    """Stored GitHub OAuth token for repo access."""

    __tablename__ = "github_credentials"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    github_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    github_username: Mapped[str] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(String(512))

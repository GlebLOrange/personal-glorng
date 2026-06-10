"""Central registry of initialized database backends and repositories."""

from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.repositories.app_log import AppLogRepository
from app.db.repositories.audit import AuditRepository
from app.db.repositories.credential import CredentialRepository
from app.db.repositories.data_import import DataImportRepository
from app.db.repositories.expense import ExpenseRepository
from app.db.repositories.feedback import FeedbackRepository
from app.db.repositories.fileshare import FileShareRepository
from app.db.repositories.recipe import RecipeRepository
from app.db.repositories.search import SearchRepository
from app.db.repositories.task import TaskRepository
from app.db.repositories.telegram import TelegramRepository
from app.db.repositories.url import UrlRepository
from app.db.repositories.user import UserRepository
from app.db.repositories.weather import WeatherRepository


@dataclass
class DatabaseRegistry:
    """Holds live connections and repository instances."""

    mongo_client: AsyncIOMotorClient | None = None
    mongo_db: AsyncIOMotorDatabase | None = None
    postgres_factory: async_sessionmaker[AsyncSession] | None = None
    users: UserRepository | None = None
    tasks: TaskRepository | None = None
    recipes: RecipeRepository | None = None
    expenses: ExpenseRepository | None = None
    urls: UrlRepository | None = None
    files: FileShareRepository | None = None
    feedback: FeedbackRepository | None = None
    credentials: CredentialRepository | None = None
    weather: WeatherRepository | None = None
    telegram: TelegramRepository | None = None
    search: SearchRepository | None = None
    audit: AuditRepository | None = None
    app_logs: AppLogRepository | None = None
    data_imports: DataImportRepository | None = None
    _repos_initialized: bool = field(default=False, repr=False)

    def require_mongo(self) -> AsyncIOMotorDatabase:
        if self.mongo_db is None:
            msg = "MongoDB is not initialized"
            raise RuntimeError(msg)
        return self.mongo_db

    def has_postgres(self) -> bool:
        return self.postgres_factory is not None

    def require_postgres_factory(self) -> async_sessionmaker[AsyncSession]:
        if self.postgres_factory is None:
            msg = "PostgreSQL is not enabled"
            raise RuntimeError(msg)
        return self.postgres_factory

    def init_repositories(self) -> None:
        """Construct repository instances from initialized backends."""
        if self._repos_initialized:
            return
        mongo = self.require_mongo()
        self.users = UserRepository(mongo)
        self.tasks = TaskRepository(mongo)
        self.recipes = RecipeRepository(mongo)
        self.expenses = ExpenseRepository(mongo)
        self.urls = UrlRepository(mongo)
        self.files = FileShareRepository(mongo)
        self.feedback = FeedbackRepository(mongo)
        self.credentials = CredentialRepository(mongo)
        self.weather = WeatherRepository(mongo)
        self.telegram = TelegramRepository(mongo)
        self.search = SearchRepository(mongo)
        self.audit = AuditRepository(mongo)
        self.app_logs = AppLogRepository(mongo)
        self.data_imports = DataImportRepository(mongo)
        self._repos_initialized = True

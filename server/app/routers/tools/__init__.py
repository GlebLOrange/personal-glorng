from fastapi import APIRouter

from app.routers.tools import (
    admin_search,
    ai_chat,
    app_logs,
    audit,
    calculator,
    data_extract,
    email,
    expense_calculator,
    expenses,
    news,
    password_generator,
    recipes,
    tasks_admin,
    urlshortener,
)
from app.settings import get_settings

tools_router = APIRouter(prefix="/tools")

for router_module in (
    admin_search,
    ai_chat,
    app_logs,
    audit,
    calculator,
    data_extract,
    email,
    expense_calculator,
    expenses,
    news,
    password_generator,
    recipes,
    tasks_admin,
    urlshortener,
):
    tools_router.include_router(router_module.router)

# ponytail: skip yt-dlp / file-share / outbound probes unless explicitly enabled
# so production images do not mount those routers by default.
if get_settings().UNTRUSTED_URL_TOOLS_ENABLED:
    from app.routers.tools import fileshare, health_checker, viddownload

    for router_module in (fileshare, health_checker, viddownload):
        tools_router.include_router(router_module.router)

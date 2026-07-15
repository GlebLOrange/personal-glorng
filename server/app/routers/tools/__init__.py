from fastapi import APIRouter

from app.routers.tools import (
    ai_chat,
    app_logs,
    audit,
    calculator,
    data_extract,
    email,
    expense_calculator,
    expenses,
    fileshare,
    news,
    news_sources,
    password_generator,
    recipes,
    tasks_admin,
    urlshortener,
    viddownload,
)

tools_router = APIRouter(prefix="/tools")

for router_module in (
    ai_chat,
    app_logs,
    audit,
    calculator,
    data_extract,
    email,
    expense_calculator,
    expenses,
    fileshare,
    news,
    news_sources,
    password_generator,
    recipes,
    tasks_admin,
    urlshortener,
    viddownload,
):
    tools_router.include_router(router_module.router)

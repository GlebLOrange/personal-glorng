from importlib import import_module
from pathlib import Path

from fastapi import APIRouter

tools_router = APIRouter(prefix="/tools", tags=["tools"])

for module_file in Path(__file__).parent.glob("*.py"):
    if module_file.name.startswith("_"):
        continue
    mod = import_module(f".{module_file.stem}", package=__name__)
    if hasattr(mod, "router"):
        tools_router.include_router(mod.router)

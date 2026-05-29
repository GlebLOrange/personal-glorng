from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, DbSession, require_capability
from app.schemas.common import MessageResponse
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.services.recipe import RecipeService

router = APIRouter(
    prefix="/recipes",
    dependencies=[Depends(require_capability("recipes", "read"))],
)


@router.get("/tags", response_model=list[str])
async def list_tags(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> list[str]:
    svc = RecipeService(db)
    return await svc.get_all_tags()


@router.get("", response_model=list[RecipeResponse])
async def list_recipes(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    search: str | None = None,
    tag: str | None = None,
) -> list[RecipeResponse]:
    svc = RecipeService(db)
    return await svc.list_recipes(search=search, tag=tag)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    svc = RecipeService(db)
    return await svc.get_recipe(recipe_id)


@router.post(
    "",
    response_model=RecipeResponse,
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def create_recipe(
    data: RecipeCreate,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    svc = RecipeService(db)
    return await svc.create_recipe(data)


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    svc = RecipeService(db)
    return await svc.update_recipe(recipe_id, data)


@router.delete(
    "/{recipe_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def delete_recipe(
    recipe_id: int,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    svc = RecipeService(db)
    await svc.delete_recipe(recipe_id)
    return MessageResponse(message="Recipe deleted")

"""Recipe book API. Default: `recipes:read`; writes: `recipes:write`."""

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, RecipeServiceDep, require_capability
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(require_capability("recipes", "read"))],
)


@router.get(
    "/tags",
    response_model=list[str],
    summary="List recipe tags",
    description=requires_capability("recipes", "read"),
)
async def list_tags(
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> list[str]:
    return await svc.get_all_tags()


@router.get(
    "",
    response_model=list[RecipeResponse],
    summary="List recipes",
    description=requires_capability("recipes", "read"),
)
async def list_recipes(
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    search: str | None = None,
    tag: str | None = None,
) -> list[RecipeResponse]:
    return await svc.list_recipes(search=search, tag=tag)


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get recipe by ID",
    description=requires_capability("recipes", "read"),
)
async def get_recipe(
    recipe_id: int,
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    return await svc.get_recipe(recipe_id)


@router.post(
    "",
    response_model=RecipeResponse,
    summary="Create recipe",
    description=requires_capability("recipes", "write"),
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def create_recipe(
    data: RecipeCreate,
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    return await svc.create_recipe(data)


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Update recipe",
    description=requires_capability("recipes", "write"),
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    return await svc.update_recipe(recipe_id, data)


@router.delete(
    "/{recipe_id}",
    response_model=MessageResponse,
    summary="Delete recipe",
    description=requires_capability("recipes", "write"),
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def delete_recipe(
    recipe_id: int,
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    await svc.delete_recipe(recipe_id)
    return MessageResponse(message="Recipe deleted")

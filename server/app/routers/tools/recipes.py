from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AuthorizedUser, RecipeServiceDep, require_capability
from app.schemas.common import MessageResponse
from app.schemas.recipe import RecipeCreate, RecipeListResponse, RecipeResponse, RecipeSort, RecipeUpdate

router = APIRouter(
    prefix="/recipes",
    dependencies=[Depends(require_capability("recipes", "read"))],
)


@router.get("/tags", response_model=list[str])
async def list_tags(
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> list[str]:
    return await svc.get_all_tags()


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    search: Annotated[str | None, Query(max_length=200)] = None,
    tag: str | None = None,
    sort: RecipeSort = "updated_desc",
    page: int = 1,
    per_page: int = 24,
) -> RecipeListResponse:
    return await svc.list_recipes(
        search=search,
        tag=tag,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    svc: RecipeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> RecipeResponse:
    return await svc.get_recipe(recipe_id)


@router.post(
    "",
    response_model=RecipeResponse,
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def create_recipe(
    data: RecipeCreate,
    svc: RecipeServiceDep,
    user: AuthorizedUser,
) -> RecipeResponse:
    return await svc.create_recipe(data, actor_id=user.id)


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    svc: RecipeServiceDep,
    user: AuthorizedUser,
) -> RecipeResponse:
    return await svc.update_recipe(recipe_id, data, actor_id=user.id)


@router.delete(
    "/{recipe_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_capability("recipes", "write"))],
)
async def delete_recipe(
    recipe_id: int,
    svc: RecipeServiceDep,
    user: AuthorizedUser,
) -> MessageResponse:
    await svc.delete_recipe(recipe_id, actor_id=user.id)
    return MessageResponse(message="Recipe deleted")

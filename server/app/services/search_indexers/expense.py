from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.search_document import SearchVisibility
from app.db.models.tool_expense import ToolExpense
from app.services.search_index import (
    SearchDocumentInput,
    remove_by_source,
    upsert_document,
)
from app.services.search_source_types import SearchSourceType

EXPENSE_SOURCE_TYPE = SearchSourceType.EXPENSE


def _expense_document(expense: ToolExpense) -> SearchDocumentInput:
    body_parts = [
        expense.tool_name,
        f"{expense.amount} {expense.currency}",
        str(expense.expense_date),
    ]
    if expense.category:
        body_parts.append(f"Category: {expense.category}")
    if expense.notes:
        body_parts.append(expense.notes)

    return SearchDocumentInput(
        source_type=EXPENSE_SOURCE_TYPE,
        source_id=expense.id,
        title=f"{expense.tool_name} expense",
        body="\n".join(body_parts),
        url="/admin/tools/expenses",
        visibility=SearchVisibility.ADMIN,
    )


async def index_expense(db: AsyncSession, expense: ToolExpense) -> None:
    await upsert_document(db, _expense_document(expense))


async def remove_expense(db: AsyncSession, expense_id: int) -> None:
    await remove_by_source(db, EXPENSE_SOURCE_TYPE, expense_id)

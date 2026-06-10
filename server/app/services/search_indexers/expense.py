from app.db.documents.expense import Expense
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.services.search_index import (
    SearchDocumentInput,
    remove_by_source,
    upsert_document,
)
from app.services.search_source_types import SearchSourceType

EXPENSE_SOURCE_TYPE = SearchSourceType.EXPENSE


def _expense_document(expense: Expense) -> SearchDocumentInput:
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


async def index_expense(registry: DatabaseRegistry, expense: Expense) -> None:
    await upsert_document(registry, _expense_document(expense))


async def remove_expense(registry: DatabaseRegistry, expense_id: int) -> None:
    await remove_by_source(registry, EXPENSE_SOURCE_TYPE, expense_id)

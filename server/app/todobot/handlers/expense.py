"""Telegram commands for quick expense logging."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.logging import logger
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.registry import DatabaseRegistry
from app.schemas.expense import ExpenseCreate
from app.services.expense import ExpenseService
from app.services.expense_category import ExpenseCategoryService
from app.settings import get_settings
from app.todobot.keyboards.expense import (
    category_picker,
    confirm_expense,
    skip_place_button,
)
from app.todobot.keyboards.menu import LABEL_LOG_EXPENSE, main_menu
from app.todobot.states.expense import ExpenseCreation
from app.todobot.utils.expense_nlp import (
    DEFAULT_CATEGORY,
    parse_expense_text,
    today_in_tz,
)

router = Router()

_MONTH_NAMES = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def _current_month_value() -> str:
    today = today_in_tz()
    return f"{today.year}-{today.month:02d}"


def _format_money(amount: Decimal | str, currency: str) -> str:
    value = Decimal(str(amount)).quantize(Decimal("0.01"))
    return f"{value:,.2f} {currency}"


def _format_summary_line(summary_total: Decimal, currency: str) -> str:
    today = today_in_tz()
    month_label = f"{_MONTH_NAMES[today.month - 1]} {today.year}"
    return f"{month_label} total: {_format_money(summary_total, currency)}"


def _format_expense_line(
    *,
    amount: Decimal,
    currency: str,
    category: str,
    tool_name: str,
) -> str:
    return f"Logged: {_format_money(amount, currency)} · {category} · {tool_name}"


async def _month_summary_pln(registry: DatabaseRegistry) -> tuple[Decimal, str]:
    month = _current_month_value()
    date_from, date_to = ExpenseService.month_date_bounds(month)
    svc = ExpenseService(registry)
    summary = await svc.get_summary(
        date_from=date_from,
        date_to=date_to,
        display_currency="PLN",
    )
    return summary.total, summary.currency


async def _save_parsed(
    registry: DatabaseRegistry,
    *,
    amount: Decimal,
    currency: str,
    category: str,
    tool_name: str,
    expense_date: date,
    notes: str | None = None,
) -> str:
    svc = ExpenseService(registry)
    await svc.create_expense(
        ExpenseCreate(
            tool_name=tool_name,
            amount=amount,
            currency=currency,  # type: ignore[arg-type]
            expense_date=expense_date,
            category=category,
            notes=notes,
        ),
        source=AuditSource.TODOBOT,
        actor_type=AuditActorType.TELEGRAM,
    )
    month_total, display_currency = await _month_summary_pln(registry)
    logged = _format_expense_line(
        amount=amount,
        currency=currency,
        category=category,
        tool_name=tool_name,
    )
    return f"{logged}\n{_format_summary_line(month_total, display_currency)}"


def _format_draft_summary(data: dict) -> str:
    return (
        f"*Price:* {_format_money(data['amount'], data['currency'])}\n"
        f"*Category:* {data['category']}\n"
        f"*Product:* {data.get('tool_name') or '—'}"
    )


async def _start_guided(message: Message, state: FSMContext) -> None:
    await state.clear()
    settings = get_settings()
    await state.set_state(ExpenseCreation.waiting_for_amount)
    await message.answer(
        f"How much? (default currency: {settings.EXPENSE_DEFAULT_CURRENCY})\n"
        "Example: 89.50 or 89,50",
    )


@router.message(Command("spend"))
async def cmd_spend(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    registry: DatabaseRegistry,
) -> None:
    args = (command.args or "").strip()
    if not args:
        await _start_guided(message, state)
        return

    parsed = parse_expense_text(args)
    if not parsed.is_valid:
        await message.answer(
            parsed.parse_error or "Could not parse expense.",
            reply_markup=main_menu(),
        )
        return

    try:
        reply = await _save_parsed(
            registry,
            amount=parsed.amount,
            currency=parsed.currency,
            category=parsed.category,
            tool_name=parsed.tool_name,
            expense_date=parsed.expense_date,
        )
    except Exception:
        await message.answer(
            "Failed to save expense. Try again.", reply_markup=main_menu()
        )
        return

    await state.clear()
    await message.answer(reply, reply_markup=main_menu())


@router.message(Command("expenses"))
async def cmd_expenses(message: Message, registry: DatabaseRegistry) -> None:
    month = _current_month_value()
    date_from, date_to = ExpenseService.month_date_bounds(month)
    svc = ExpenseService(registry)
    summary = await svc.get_summary(
        date_from=date_from,
        date_to=date_to,
        display_currency="PLN",
    )
    expenses = await svc.list_expenses(date_from=date_from, date_to=date_to)
    today = today_in_tz()
    month_label = f"{_MONTH_NAMES[today.month - 1]} {today.year}"

    lines = [f"*{month_label}* — {_format_money(summary.total, summary.currency)}"]
    if not expenses:
        lines.append("\nNo expenses yet. Use /spend 45 groceries")
    else:
        lines.append("\n*Recent:*")
        for expense in expenses[:5]:
            cat = expense.category or "—"
            amount_line = _format_money(expense.amount, expense.currency)
            day = expense.expense_date.strftime("%d %b")
            lines.append(f"• {day} — {amount_line} · {cat} · {expense.tool_name}")
    await message.answer(
        "\n".join(lines), parse_mode="Markdown", reply_markup=main_menu()
    )


@router.message(F.text == LABEL_LOG_EXPENSE)
async def menu_log_expense(message: Message, state: FSMContext) -> None:
    await _start_guided(message, state)


@router.message(ExpenseCreation.waiting_for_amount)
async def guided_amount(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text:
        await message.answer("Send a number, e.g. 45 or 89.50")
        return

    parsed = parse_expense_text(message.text.strip())
    if not parsed.is_valid:
        await message.answer(parsed.parse_error or "Invalid amount")
        return

    settings = get_settings()
    await state.update_data(
        amount=str(parsed.amount),
        currency=parsed.currency or settings.EXPENSE_DEFAULT_CURRENCY,
    )
    await state.set_state(ExpenseCreation.waiting_for_category)
    cat_svc = ExpenseCategoryService(registry)
    names = await cat_svc.list_names()
    await message.answer("Pick a category:", reply_markup=category_picker(names))


@router.callback_query(
    ExpenseCreation.waiting_for_category, F.data.startswith("exp_cat:")
)
async def guided_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = (callback.data or "").split(":", 1)[1]
    await state.update_data(category=category)
    await state.set_state(ExpenseCreation.waiting_for_place)
    if callback.message:
        await callback.message.edit_text(f"Category: {category}\nWhat product?")
        await callback.message.answer("Product name:", reply_markup=skip_place_button())
    await callback.answer()


@router.callback_query(ExpenseCreation.waiting_for_place, F.data == "exp_skip_place")
async def guided_skip_place(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("category", DEFAULT_CATEGORY)
    await state.update_data(tool_name=category)
    await state.set_state(ExpenseCreation.confirming)
    if callback.message:
        await callback.message.edit_text(
            _format_draft_summary(await state.get_data()), parse_mode="Markdown"
        )
        await callback.message.answer(
            "Save this expense?", reply_markup=confirm_expense()
        )
    await callback.answer()


@router.message(ExpenseCreation.waiting_for_place)
async def guided_place(message: Message, state: FSMContext) -> None:
    place = (message.text or "").strip()
    if not place:
        await message.answer(
            "Send a product name or tap Skip.", reply_markup=skip_place_button()
        )
        return
    await state.update_data(tool_name=place[0].upper() + place[1:])
    await state.set_state(ExpenseCreation.confirming)
    await message.answer(
        _format_draft_summary(await state.get_data()),
        parse_mode="Markdown",
        reply_markup=confirm_expense(),
    )


@router.callback_query(ExpenseCreation.confirming, F.data == "exp_confirm:no")
async def guided_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text("Cancelled.")
        await callback.message.answer("Ready when you are.", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(ExpenseCreation.confirming, F.data == "exp_confirm:yes")
async def guided_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    data = await state.get_data()
    try:
        amount = Decimal(str(data["amount"])).quantize(Decimal("0.01"))
    except InvalidOperation, KeyError:
        await state.clear()
        if callback.message:
            await callback.message.answer("Invalid amount. Start again with /spend")
        await callback.answer()
        return

    category = data.get("category", DEFAULT_CATEGORY)
    tool_name = data.get("tool_name") or category
    currency = data.get("currency", get_settings().EXPENSE_DEFAULT_CURRENCY)

    try:
        reply = await _save_parsed(
            registry,
            amount=amount,
            currency=currency,
            category=category,
            tool_name=tool_name,
            expense_date=today_in_tz(),
        )
    except Exception as exc:
        logger.error(
            "Telegram expense save failed",
            error=exc,
            context={
                "category": category,
                "currency": currency,
                "tool_name": tool_name,
            },
        )
        if callback.message:
            await callback.message.answer(
                "Failed to save expense.", reply_markup=main_menu()
            )
        await callback.answer()
        return

    await state.clear()
    if callback.message:
        await callback.message.edit_text("Saved.")
        await callback.message.answer(reply, reply_markup=main_menu())
    await callback.answer()

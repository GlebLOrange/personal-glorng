"""Inline keyboards for expense logging."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_SKIP_PLACE = "exp_skip_place"
_CONFIRM_YES = "exp_confirm:yes"
_CONFIRM_NO = "exp_confirm:no"


def category_picker(category_names: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for category in category_names:
        row.append(
            InlineKeyboardButton(
                text=category,
                callback_data=f"exp_cat:{category}",
            ),
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_place_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Use category", callback_data=_SKIP_PLACE)],
        ],
    )


def confirm_expense() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Save", callback_data=_CONFIRM_YES),
                InlineKeyboardButton(text="Cancel", callback_data=_CONFIRM_NO),
            ],
        ],
    )

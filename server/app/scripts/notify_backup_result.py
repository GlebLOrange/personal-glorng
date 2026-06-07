"""Send Telegram notification after db_maintenance.sh completes."""

from __future__ import annotations

import asyncio
import sys

from app.core.logging import logger
from app.core.telegram import notify_admin


async def _notify(status: str, detail: str) -> None:
    if status == "success":
        text = f"<b>DB maintenance OK</b>\n{detail}"
    else:
        text = f"<b>DB maintenance FAILED</b>\n{detail}"

    await notify_admin(text)
    logger.info(
        "Backup notification sent",
        context={"status": status, "detail": detail},
    )


def main() -> None:
    if len(sys.argv) < 2:
        msg = (
            "Usage: python -m app.scripts.notify_backup_result "
            "<success|failure> [detail]"
        )
        raise SystemExit(msg)

    status = sys.argv[1].lower()
    if status not in {"success", "failure"}:
        raise SystemExit("status must be 'success' or 'failure'")

    detail = sys.argv[2] if len(sys.argv) > 2 else ""
    asyncio.run(_notify(status, detail))


if __name__ == "__main__":
    main()

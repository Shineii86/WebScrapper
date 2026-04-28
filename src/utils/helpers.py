"""Helper utilities for WebScrapperBot."""
import math
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import (
    FINISHED_PROGRESS_STR,
    UN_FINISHED_PROGRESS_STR,
)


async def progress_bar(current: int, total: int) -> tuple[str, str]:
    """Generate a simple text progress bar."""
    if total == 0:
        return "", "0.00"
    percentage = current / total
    finished_length = int(percentage * 10)
    unfinished_length = 10 - finished_length
    progress = (
        f"{FINISHED_PROGRESS_STR * finished_length}"
        f"{UN_FINISHED_PROGRESS_STR * unfinished_length}"
    )
    formatted_percentage = "{:.2f}".format(percentage * 100)
    return progress, formatted_percentage


async def progress_for_pyrogram(current, total, ud_type, message, start):
    """Update a Pyrogram message with upload/download progress."""
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚫 Cancel", callback_data="cb_cancel")]]
    )
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total if total else 0
        speed = current / diff if diff else 0
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \n <b>📊 Percentage:</b> {2}%\n".format(
            "".join(["■" for _ in range(math.floor(percentage / 5))]),
            "".join(["□" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )

        tmp = (
            progress
            + "<b>✅ Completed:</b> {0} \n"
            "<b>📁 Total Size:</b> {1}\n"
            "<b>🚀 Speed:</b> {2}/s\n"
            "<b>⌚️ ETA:</b> {3}\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                estimated_total_time if estimated_total_time else "0 s",
            )
        )
        try:
            await message.edit(
                text="{}\n {}".format(ud_type, tmp), reply_markup=reply_markup
            )
        except Exception:
            pass


def humanbytes(size: int) -> str:
    """Convert bytes to human-readable format."""
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    units = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}B"


def TimeFormatter(milliseconds: int) -> str:
    """Format milliseconds into human-readable time string."""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((f"{days}d, ") if days else "")
        + ((f"{hours}h, ") if hours else "")
        + ((f"{minutes}m, ") if minutes else "")
        + ((f"{seconds}s, ") if seconds else "")
        + ((f"{milliseconds}ms, ") if milliseconds else "")
    )
    return tmp[:-2] if tmp else "0 s"

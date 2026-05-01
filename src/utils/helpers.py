"""Helper utilities for WebScrapperBot."""
import math
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import (
    FINISHED_PROGRESS_STR,
    UN_FINISHED_PROGRESS_STR,
)


async def progress_bar(current: int, total: int) -> tuple:
    """Generate a simple text progress bar.
    
    Returns:
        tuple: (progress_string, percentage_string)
    """
    if total == 0:
        return UN_FINISHED_PROGRESS_STR * 10, "0.00"
    percentage = current / total
    finished_length = int(percentage * 10)
    unfinished_length = 10 - finished_length
    progress = (
        f"{FINISHED_PROGRESS_STR * finished_length}"
        f"{UN_FINISHED_PROGRESS_STR * unfinished_length}"
    )
    formatted_percentage = f"{percentage * 100:.2f}"
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

        filled = math.floor(percentage / 5)
        empty = 20 - filled
        progress = (
            f"[{'■' * filled}{'□' * empty}]\n"
            f"<b>📊 Percentage:</b> {round(percentage, 2)}%\n"
        )

        tmp = (
            f"{progress}"
            f"<b>✅ Completed:</b> {humanbytes(current)}\n"
            f"<b>📁 Total Size:</b> {humanbytes(total)}\n"
            f"<b>🚀 Speed:</b> {humanbytes(speed)}/s\n"
            f"<b>⌚️ ETA:</b> {estimated_total_time if estimated_total_time else '0 s'}\n"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n {tmp}",
                reply_markup=reply_markup,
            )
        except Exception:
            pass


def humanbytes(size: float) -> str:
    """Convert bytes to human-readable format."""
    if not size:
        return "0 B"
    power = 2 ** 10
    n = 0
    units = {0: "B", 1: "KiB", 2: "MiB", 3: "GiB", 4: "TiB"}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}"


def TimeFormatter(milliseconds: int) -> str:
    """Format milliseconds into human-readable time string."""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    if milliseconds and not parts:
        parts.append(f"{milliseconds}ms")
    return ", ".join(parts) if parts else "0 s"

"""Media downloaders (images, audio, video, PDFs)."""
import os
import asyncio
import shutil
import time
from urllib.parse import urljoin, urlparse
import aiohttp

from pyrogram import enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.scrapers.base import fetch_url, fetch_bytes, handle_errors
from src.config import BOT_OWNER, MAX_DOWNLOAD_SIZE_MB
from src.utils.helpers import progress_bar, progress_for_pyrogram

# Supported file extensions
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".ico", ".tiff", ".avif"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma", ".opus", ".webm"}
VIDEO_EXTS = {".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".m4v"}


def get_extension(url: str, valid_exts: set, default: str) -> str:
    """Extract file extension from URL, validate against known types."""
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    return ext if ext in valid_exts else default


async def download_media_file(url: str) -> bytes:
    """Download a media file and return its bytes."""
    data = await fetch_bytes(url, max_size=MAX_DOWNLOAD_SIZE_MB * 1024 * 1024)
    return data


@handle_errors
async def all_images_scraping(bot, query):
    """Download all images from a URL as a ZIP archive."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🔍 Scanning for images...", quote=True)

    content, soup = await fetch_url(message.text)
    if not soup:
        await txt.edit("❌ Failed to parse the URL.")
        return

    base_url = message.text
    image_links = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
        if src and not src.startswith("data:"):
            full_url = urljoin(base_url, src)
            image_links.append(full_url)

    # Also check CSS background images
    for tag in soup.find_all(style=True):
        style = tag["style"]
        if "url(" in style:
            start = style.index("url(") + 4
            end = style.index(")", start)
            url_str = style[start:end].strip("'\"")
            if url_str and not url_str.startswith("data:"):
                image_links.append(urljoin(base_url, url_str))

    image_links = list(dict.fromkeys(image_links))  # deduplicate preserving order

    if not image_links:
        await txt.edit("🌄 No images found on this page.")
        return

    status = await message.reply_text(f"⬇️ Starting download of {len(image_links)} images...", quote=True)
    folder_name = f"downloads-{chat_id}-images"
    os.makedirs(folder_name, exist_ok=True)

    downloaded = 0
    for idx, image_link in enumerate(image_links):
        image_data = await download_media_file(image_link)
        if image_data:
            ext = get_extension(image_link, IMAGE_EXTS, ".jpg")
            filepath = os.path.join(folder_name, f"image_{idx:03d}{ext}")
            with open(filepath, "wb") as f:
                f.write(image_data)
            downloaded += 1

        if (idx + 1) % 5 == 0 or idx + 1 == len(image_links):
            progress, percentage = await progress_bar(idx + 1, len(image_links))
            try:
                await status.edit(
                    f"⬇️ Downloading images...\n"
                    f"<b>Progress:</b> {progress}\n"
                    f"<b>Percentage:</b> {percentage}%\n"
                    f"<b>Files:</b> {downloaded}/{len(image_links)}"
                )
            except Exception:
                pass

    if downloaded == 0:
        await status.edit("❌ No images could be downloaded.")
        shutil.rmtree(folder_name, ignore_errors=True)
        await txt.delete()
        return

    await status.edit("📦 Zipping files...")
    zip_base = f"downloads-{chat_id}-images"
    zip_filename = shutil.make_archive(zip_base, "zip", folder_name)

    c_time = time.time()
    await bot.send_chat_action(chat_id, enums.ChatAction.UPLOAD_DOCUMENT)
    await message.reply_document(
        zip_filename,
        caption=f"🌄 {downloaded} images downloaded from {len(image_links)} found\n{BOT_OWNER}",
        progress=progress_for_pyrogram,
        progress_args=("Uploading", status, c_time),
    )
    await status.delete()
    await txt.delete()
    shutil.rmtree(folder_name, ignore_errors=True)
    await asyncio.sleep(1)
    if os.path.exists(zip_filename):
        os.remove(zip_filename)


@handle_errors
async def all_audio_scraping(bot, query):
    """Download all audio files from a URL as a ZIP archive."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🔍 Scanning for audio files...", quote=True)

    content, soup = await fetch_url(message.text)
    if not soup:
        await txt.edit("❌ Failed to parse the URL.")
        return

    base_url = message.text
    audio_links = []
    for audio in soup.find_all("audio"):
        src = audio.get("src")
        if not src:
            source = audio.find("source")
            if source:
                src = source.get("src")
        if src:
            audio_links.append(urljoin(base_url, src))

    # Also find linked audio files
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if any(href.lower().endswith(ext) for ext in AUDIO_EXTS):
            audio_links.append(urljoin(base_url, href))

    audio_links = list(dict.fromkeys(audio_links))

    if not audio_links:
        await txt.edit("🎵 No audio files found on this page.")
        return

    status = await message.reply_text(f"⬇️ Starting download of {len(audio_links)} files...", quote=True)
    folder_name = f"downloads-{chat_id}-audios"
    os.makedirs(folder_name, exist_ok=True)

    downloaded = 0
    for idx, audio_link in enumerate(audio_links):
        audio_data = await download_media_file(audio_link)
        if audio_data:
            ext = get_extension(audio_link, AUDIO_EXTS, ".mp3")
            filepath = os.path.join(folder_name, f"audio_{idx:03d}{ext}")
            with open(filepath, "wb") as f:
                f.write(audio_data)
            downloaded += 1

        progress, percentage = await progress_bar(idx + 1, len(audio_links))
        try:
            await status.edit(
                f"⬇️ Downloading audio...\n"
                f"<b>Progress:</b> {progress}\n"
                f"<b>Percentage:</b> {percentage}%\n"
                f"<b>Files:</b> {downloaded}/{len(audio_links)}"
            )
        except Exception:
            pass

    if downloaded == 0:
        await status.edit("❌ No audio files could be downloaded.")
        shutil.rmtree(folder_name, ignore_errors=True)
        await txt.delete()
        return

    await status.edit("📦 Zipping files...")
    zip_base = f"downloads-{chat_id}-audios"
    zip_filename = shutil.make_archive(zip_base, "zip", folder_name)

    c_time = time.time()
    await bot.send_chat_action(chat_id, enums.ChatAction.UPLOAD_DOCUMENT)
    await message.reply_document(
        zip_filename,
        caption=f"🎵 {downloaded} audio files downloaded\n{BOT_OWNER}",
        progress=progress_for_pyrogram,
        progress_args=("Uploading", status, c_time),
    )
    await status.delete()
    await txt.delete()
    shutil.rmtree(folder_name, ignore_errors=True)
    await asyncio.sleep(1)
    if os.path.exists(zip_filename):
        os.remove(zip_filename)


@handle_errors
async def all_video_scraping(bot, query):
    """Download all video files from a URL as a ZIP archive."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🔍 Scanning for videos...", quote=True)

    content, soup = await fetch_url(message.text)
    if not soup:
        await txt.edit("❌ Failed to parse the URL.")
        return

    base_url = message.text
    video_links = []
    for video in soup.find_all("video"):
        src = video.get("src")
        if not src:
            source = video.find("source")
            if source:
                src = source.get("src")
        if src:
            video_links.append(urljoin(base_url, src))

    # Also find linked video files
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if any(href.lower().endswith(ext) for ext in VIDEO_EXTS):
            video_links.append(urljoin(base_url, href))

    video_links = list(dict.fromkeys(video_links))

    if not video_links:
        await txt.edit("🎥 No videos found on this page.")
        return

    status = await message.reply_text(f"⬇️ Starting download of {len(video_links)} files...", quote=True)
    folder_name = f"downloads-{chat_id}-videos"
    os.makedirs(folder_name, exist_ok=True)

    downloaded = 0
    for idx, video_link in enumerate(video_links):
        video_data = await download_media_file(video_link)
        if video_data:
            ext = get_extension(video_link, VIDEO_EXTS, ".mp4")
            filepath = os.path.join(folder_name, f"video_{idx:03d}{ext}")
            with open(filepath, "wb") as f:
                f.write(video_data)
            downloaded += 1

        progress, percentage = await progress_bar(idx + 1, len(video_links))
        try:
            await status.edit(
                f"⬇️ Downloading videos...\n"
                f"<b>Progress:</b> {progress}\n"
                f"<b>Percentage:</b> {percentage}%\n"
                f"<b>Files:</b> {downloaded}/{len(video_links)}"
            )
        except Exception:
            pass
        await asyncio.sleep(0.3)

    if downloaded == 0:
        await status.edit("❌ No videos could be downloaded.")
        shutil.rmtree(folder_name, ignore_errors=True)
        await txt.delete()
        return

    await status.edit("📦 Zipping files...")
    zip_base = f"downloads-{chat_id}-videos"
    zip_filename = shutil.make_archive(zip_base, "zip", folder_name)

    c_time = time.time()
    await bot.send_chat_action(chat_id, enums.ChatAction.UPLOAD_DOCUMENT)
    await message.reply_document(
        zip_filename,
        caption=f"🎥 {downloaded} videos downloaded\n{BOT_OWNER}",
        progress=progress_for_pyrogram,
        progress_args=("Uploading", status, c_time),
    )
    await status.delete()
    await txt.delete()
    shutil.rmtree(folder_name, ignore_errors=True)
    await asyncio.sleep(1)
    if os.path.exists(zip_filename):
        os.remove(zip_filename)


@handle_errors
async def all_pdf_scraping(query):
    """Download all PDF links from a URL as a ZIP archive."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🔍 Scanning for PDFs...", quote=True)

    content, soup = await fetch_url(message.text)
    if not soup:
        await txt.edit("❌ Failed to parse the URL.")
        return

    base_url = message.text
    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.lower().endswith(".pdf") or "application/pdf" in link.get("type", ""):
            full_url = urljoin(base_url, href)
            pdf_links.append(full_url)

    pdf_links = list(dict.fromkeys(pdf_links))

    if not pdf_links:
        await txt.edit("📚 No PDFs found on this page.")
        return

    status = await message.reply_text(f"⬇️ Starting download of {len(pdf_links)} PDFs...", quote=True)
    folder_name = f"downloads-{chat_id}-pdfs"
    os.makedirs(folder_name, exist_ok=True)

    downloaded = 0
    for idx, pdf_link in enumerate(pdf_links):
        pdf_data = await download_media_file(pdf_link)
        if pdf_data:
            filename = os.path.basename(urlparse(pdf_link).path)
            if not filename or not filename.lower().endswith(".pdf"):
                filename = f"document_{idx:03d}.pdf"
            filepath = os.path.join(folder_name, filename)
            with open(filepath, "wb") as f:
                f.write(pdf_data)
            downloaded += 1

        progress, percentage = await progress_bar(idx + 1, len(pdf_links))
        try:
            await status.edit(
                f"⬇️ Downloading PDFs...\n"
                f"<b>Progress:</b> {progress}\n"
                f"<b>Percentage:</b> {percentage}%\n"
                f"<b>Files:</b> {downloaded}/{len(pdf_links)}"
            )
        except Exception:
            pass
        await asyncio.sleep(0.3)

    if downloaded == 0:
        await status.edit("❌ No PDFs could be downloaded.")
        shutil.rmtree(folder_name, ignore_errors=True)
        await txt.delete()
        return

    await status.edit("📦 Zipping files...")
    zip_base = f"downloads-{chat_id}-pdfs"
    zip_filename = shutil.make_archive(zip_base, "zip", folder_name)

    c_time = time.time()
    await message.reply_document(
        zip_filename,
        caption=f"📚 {downloaded} PDFs downloaded\n{BOT_OWNER}",
        progress=progress_for_pyrogram,
        progress_args=("Uploading", status, c_time),
    )
    await status.delete()
    await txt.delete()
    shutil.rmtree(folder_name, ignore_errors=True)
    await asyncio.sleep(1)
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

"""Browser-based scrapers using Selenium (screenshots, screen recording, cookies, localStorage)."""
import os
import asyncio
import shutil
import tempfile
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.scrapers.base import handle_errors
from src.config import BOT_OWNER, MAX_VIDEO_LENGTH, MAX_SCREENSHOTS
from src.utils.helpers import progress_bar

logger = logging.getLogger(__name__)


def _create_driver(url: str):
    """Create and configure a headless browser (sync, run in thread)."""
    # Try Chrome first
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        return driver
    except Exception as e_chrome:
        logger.warning(f"Chrome failed: {e_chrome}, trying Firefox...")

    # Fallback to Firefox
    try:
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        return driver
    except Exception as e_firefox:
        logger.error(f"Firefox also failed: {e_firefox}")
        return None


def _quit_driver(driver):
    """Safely quit a driver."""
    try:
        if driver:
            driver.quit()
    except Exception:
        pass


@handle_errors
async def extract_cookies(query):
    """Extract cookies from a URL using a headless browser."""
    message = query.message
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)

    driver = await asyncio.to_thread(_create_driver, message.text)
    if not driver:
        await txt.edit("❌ Failed to initialize browser. Make sure Chrome or Firefox is installed.")
        return

    try:
        await txt.edit("🍪 Extracting cookies...")
        cookies = await asyncio.to_thread(driver.get_cookies)
        await asyncio.to_thread(_quit_driver, driver)

        if not cookies:
            await txt.edit("🍪 No cookies found.")
            return

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="Cookies-"
        ) as tmp:
            for cookie in cookies:
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                domain = cookie.get("domain", "")
                path = cookie.get("path", "")
                secure = cookie.get("secure", False)
                http_only = cookie.get("httpOnly", False)
                tmp.write(f"Name: {name}\n")
                tmp.write(f"Value: {value}\n")
                tmp.write(f"Domain: {domain}\n")
                tmp.write(f"Path: {path}\n")
                tmp.write(f"Secure: {secure}\n")
                tmp.write(f"HttpOnly: {http_only}\n")
                tmp.write("-" * 40 + "\n")
            tmp_path = tmp.name

        await txt.edit("📤 Uploading...")
        await message.reply_document(
            tmp_path,
            caption=f"🍪 {len(cookies)} cookies extracted\n{BOT_OWNER}",
            quote=True,
        )
        await asyncio.sleep(1)
        os.remove(tmp_path)
        await txt.delete()
    except Exception:
        await asyncio.to_thread(_quit_driver, driver)
        raise


@handle_errors
async def extract_local_storage(query):
    """Extract local storage data from a URL using a headless browser."""
    message = query.message
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)

    driver = await asyncio.to_thread(_create_driver, message.text)
    if not driver:
        await txt.edit("❌ Failed to initialize browser.")
        return

    try:
        await txt.edit("📦 Extracting localStorage...")
        local_storage_script = """
        var storage = {};
        for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            storage[key] = localStorage.getItem(key);
        }
        return storage;
        """
        local_storage = await asyncio.to_thread(driver.execute_script, local_storage_script)
        await asyncio.to_thread(_quit_driver, driver)

        if not local_storage:
            await txt.edit("📦 No localStorage data found.")
            return

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="LocalStorage-"
        ) as tmp:
            for key, value in local_storage.items():
                tmp.write(f"{key}: {value}\n")
            tmp_path = tmp.name

        await txt.edit("📤 Uploading...")
        await message.reply_document(
            tmp_path,
            caption=f"📦 {len(local_storage)} localStorage items extracted\n{BOT_OWNER}",
            quote=True,
        )
        await asyncio.sleep(1)
        os.remove(tmp_path)
        await txt.delete()
    except Exception:
        await asyncio.to_thread(_quit_driver, driver)
        raise


@handle_errors
async def capture_screenshot(query):
    """Capture a full-page screenshot of a URL."""
    message = query.message
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)

    driver = await asyncio.to_thread(_create_driver, message.text)
    if not driver:
        await txt.edit("❌ Failed to initialize browser.")
        return

    try:
        await asyncio.sleep(2)
        await txt.edit("📷 Taking screenshot...")

        # Get full page dimensions
        total_height = await asyncio.to_thread(
            driver.execute_script,
            "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);"
        )
        total_width = await asyncio.to_thread(
            driver.execute_script,
            "return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth);"
        )

        # Limit dimensions to prevent memory issues
        total_width = min(total_width, 19200)
        total_height = min(total_height, 19200)

        await asyncio.to_thread(driver.set_window_size, total_width, total_height)
        await asyncio.sleep(1)

        screenshot_path = f"screenshot-{message.chat.id}.png"
        await asyncio.to_thread(driver.save_screenshot, screenshot_path)
        await asyncio.to_thread(_quit_driver, driver)

        await txt.edit("📤 Uploading...")
        await message.reply_photo(
            screenshot_path,
            caption=f"📷 Full page screenshot ({total_width}x{total_height})\n{BOT_OWNER}",
        )
        await asyncio.sleep(1)
        os.remove(screenshot_path)
        await txt.delete()
    except Exception:
        await asyncio.to_thread(_quit_driver, driver)
        raise


@handle_errors
async def record_screen(query):
    """Record a scrolling screen capture video of a URL."""
    message = query.message
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)

    driver = await asyncio.to_thread(_create_driver, message.text)
    if not driver:
        await txt.edit("❌ Failed to initialize browser.")
        return

    screenshot_dir = f"screenshots-{message.chat.id}"
    os.makedirs(screenshot_dir, exist_ok=True)

    try:
        await asyncio.sleep(2)

        initial_scroll_height = await asyncio.to_thread(
            driver.execute_script, "return document.body.scrollHeight;"
        )

        total_frames = min(MAX_SCREENSHOTS, max(5, initial_scroll_height // 100))
        fps = min(10, max(5, total_frames // MAX_VIDEO_LENGTH))

        await txt.edit(f"🎬 Capturing {total_frames} frames...")
        for step in range(total_frames):
            fraction = step / total_frames if total_frames else 0
            scroll_height = int(fraction * initial_scroll_height)
            await asyncio.to_thread(
                driver.execute_script, f"window.scrollTo(0, {scroll_height});"
            )
            await asyncio.sleep(0.5)
            screenshot_path = os.path.join(screenshot_dir, f"frame_{step:04d}.png")
            await asyncio.to_thread(driver.save_screenshot, screenshot_path)

            if (step + 1) % 10 == 0 or step + 1 == total_frames:
                progress, _ = await progress_bar(step + 1, total_frames)
                try:
                    await txt.edit(f"🎬 Capturing frames...\n{progress}")
                except Exception:
                    pass

        await asyncio.to_thread(_quit_driver, driver)

        await txt.edit("🎞 Converting to video...")
        video_path = f"screenrecord-{message.chat.id}.mp4"

        try:
            import imageio
            writer = imageio.get_writer(video_path, fps=fps)
            for step in range(total_frames):
                screenshot_path = os.path.join(screenshot_dir, f"frame_{step:04d}.png")
                image = imageio.imread(screenshot_path)
                writer.append_data(image)
            writer.close()
        except ImportError:
            await txt.edit("❌ imageio is required for video recording. Install with: pip install imageio[ffmpeg]")
            shutil.rmtree(screenshot_dir, ignore_errors=True)
            return

        # Cleanup screenshots
        shutil.rmtree(screenshot_dir, ignore_errors=True)

        await txt.edit("📤 Uploading video...")
        duration = total_frames // fps
        await message.reply_video(
            video_path,
            caption=f"🎬 Screen recording ({duration}s, {total_frames} frames)\n{BOT_OWNER}",
            supports_streaming=True,
        )
        await asyncio.sleep(1)
        if os.path.exists(video_path):
            os.remove(video_path)
        await txt.delete()
    except Exception:
        await asyncio.to_thread(_quit_driver, driver)
        shutil.rmtree(screenshot_dir, ignore_errors=True)
        video_path = f"screenrecord-{message.chat.id}.mp4"
        if os.path.exists(video_path):
            os.remove(video_path)
        raise


@handle_errors
async def extract_page_source(query):
    """Extract the full page source after JavaScript execution."""
    message = query.message
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)

    driver = await asyncio.to_thread(_create_driver, message.text)
    if not driver:
        await txt.edit("❌ Failed to initialize browser.")
        return

    try:
        await asyncio.sleep(2)
        await txt.edit("📄 Extracting rendered source...")

        page_source = await asyncio.to_thread(lambda: driver.page_source)
        await asyncio.to_thread(_quit_driver, driver)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, prefix="RenderedSource-"
        ) as tmp:
            tmp.write(page_source)
            tmp_path = tmp.name

        await txt.edit("📤 Uploading...")
        await message.reply_document(
            tmp_path,
            caption=f"📄 Rendered page source ({len(page_source):,} chars)\n{BOT_OWNER}",
            quote=True,
        )
        await asyncio.sleep(1)
        os.remove(tmp_path)
        await txt.delete()
    except Exception:
        await asyncio.to_thread(_quit_driver, driver)
        raise

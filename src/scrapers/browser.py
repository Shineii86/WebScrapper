"""Browser-based scrapers using Selenium (screenshots, screen recording, cookies, localStorage)."""
import os
import asyncio
import tempfile
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from src.scrapers.base import handle_errors
from src.config import BOT_OWNER, MAX_VIDEO_LENGTH, MAX_SCREENSHOTS
from src.utils.helpers import progress_bar

logger = logging.getLogger(__name__)


def init_headless_browser(url: str):
    """Initialize a headless browser (Chrome preferred, Firefox fallback)."""
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        return driver
    except Exception as e_chrome:
        logger.warning(f"Chrome failed: {e_chrome}, trying Firefox...")
        try:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")
            driver = webdriver.Firefox(options=firefox_options)
            driver.get(url)
            return driver
        except Exception as e_firefox:
            logger.error(f"Firefox also failed: {e_firefox}")
            return None


@handle_errors
async def extract_cookies(query):
    """Extract cookies from a URL using a headless browser."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)
    driver = init_headless_browser(message.text)

    if not driver:
        await txt.edit("❌ Failed to initialize browser. Make sure Chrome or Firefox is installed.")
        return

    try:
        await txt.edit("🍪 Extracting cookies...")
        cookies = driver.get_cookies()
        driver.quit()

        if not cookies:
            await txt.edit("🍪 No cookies found.")
            return

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="Cookies-"
        ) as tmp:
            for cookie in cookies:
                tmp.write(f"{cookie}\n")
            tmp_path = tmp.name

        await txt.edit("📤 Uploading...")
        await message.reply_document(
            tmp_path,
            caption=f"🍪 {len(cookies)} cookies extracted\n{BOT_OWNER}",
            quote=True,
        )
        await asyncio.sleep(1)
        os.remove(tmp_path)
    except Exception:
        driver.quit() if driver else None
        raise
    finally:
        await txt.delete()


@handle_errors
async def extract_local_storage(query):
    """Extract local storage data from a URL using a headless browser."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)
    driver = init_headless_browser(message.text)

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
        local_storage = driver.execute_script(local_storage_script)
        driver.quit()

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
    except Exception:
        driver.quit() if driver else None
        raise
    finally:
        await txt.delete()


@handle_errors
async def capture_screenshot(query):
    """Capture a full-page screenshot of a URL."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)
    driver = init_headless_browser(message.text)

    if not driver:
        await txt.edit("❌ Failed to initialize browser.")
        return

    try:
        await asyncio.sleep(2)
        await txt.edit("📷 Taking screenshot...")

        # Get full page dimensions
        total_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);"
        )
        total_width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth);"
        )

        driver.set_window_size(total_width, total_height)
        await asyncio.sleep(1)

        screenshot_path = f"{chat_id}-screenshot.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()

        await txt.edit("📤 Uploading...")
        await message.reply_photo(
            screenshot_path,
            caption=f"📷 Full page screenshot\n{BOT_OWNER}",
        )
        await asyncio.sleep(1)
        os.remove(screenshot_path)
    except Exception:
        driver.quit() if driver else None
        raise
    finally:
        await txt.delete()


@handle_errors
async def record_screen(query):
    """Record a scrolling screen capture video of a URL."""
    message = query.message
    chat_id = message.chat.id
    txt = await message.reply_text("🌐 Initializing browser...", quote=True)
    driver = init_headless_browser(message.text)

    if not driver:
        await txt.edit("❌ Failed to initialize browser.")
        return

    screenshot_dir = f"{chat_id}-screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    try:
        await asyncio.sleep(2)

        initial_scroll_height = driver.execute_script(
            "return document.body.scrollHeight;"
        )

        total_frames = min(MAX_SCREENSHOTS, initial_scroll_height // 100)
        if total_frames < 5:
            total_frames = 5
        fps = min(10, max(5, total_frames // MAX_VIDEO_LENGTH))

        await txt.edit("🎬 Capturing frames...")
        for step in range(total_frames):
            fraction = step / total_frames if total_frames else 0
            scroll_height = int(fraction * initial_scroll_height)
            driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            await asyncio.sleep(0.5)
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{step}.png")
            driver.save_screenshot(screenshot_path)

            progress, _ = await progress_bar(step + 1, total_frames)
            try:
                await txt.edit(f"🎬 Capturing frames...\n{progress}")
            except Exception:
                pass

        driver.quit()

        await txt.edit("🎞 Converting to video...")
        video_path = f"{chat_id}-screen_record.mp4"

        try:
            import imageio
            with imageio.get_writer(video_path, fps=fps) as writer:
                for step in range(total_frames):
                    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{step}.png")
                    image = imageio.imread(screenshot_path)
                    writer.append_data(image)
        except ImportError:
            await txt.edit("❌ imageio is required for video recording. Install with: pip install imageio[ffmpeg]")
            return

        # Cleanup screenshots
        for step in range(total_frames):
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{step}.png")
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        os.rmdir(screenshot_dir)

        await txt.edit("📤 Uploading video...")
        await message.reply_video(
            video_path,
            caption=f"🎬 Screen recording ({total_frames // fps}s)\n{BOT_OWNER}",
            supports_streaming=True,
        )
        await asyncio.sleep(1)
        os.remove(video_path)
    except Exception:
        driver.quit() if driver else None
        # Cleanup
        shutil.rmtree(screenshot_dir, ignore_errors=True)
        if os.path.exists(f"{chat_id}-screen_record.mp4"):
            os.remove(f"{chat_id}-screen_record.mp4")
        raise
    finally:
        await txt.delete()

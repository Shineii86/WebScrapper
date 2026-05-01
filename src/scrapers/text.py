"""Text and content scrapers."""
import os
import asyncio
import tempfile
from urllib.parse import urljoin

from src.scrapers.base import fetch_url, handle_errors
from src.config import BOT_OWNER


@handle_errors
async def raw_data_scraping(query):
    """Scrape raw HTML content from a URL."""
    message = query.message
    response, soup = await fetch_url(message.text)
    if not response:
        await message.reply_text("❌ Failed to fetch the URL.", quote=True)
        return

    content = await response.read()
    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".txt", delete=False, prefix="RawData-"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📄 Raw Content\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def html_data_scraping(query):
    """Scrape prettified HTML data from a URL."""
    message = query.message
    response, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    html_text = soup.prettify()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="HtmlData-"
    ) as tmp:
        tmp.write(html_text)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📝 HTML Data\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def all_links_scraping(query):
    """Scrape all anchor links from a URL."""
    message = query.message
    response, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    base_url = message.text
    links = []
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if href:
            full_url = urljoin(base_url, href)
            links.append(full_url)

    if not links:
        await message.reply_text("🔗 No links found on this page.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="AllLinks-"
    ) as tmp:
        for link in sorted(set(links)):
            tmp.write(f"{link}\n")
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"🔗 Found {len(set(links))} unique links\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def all_paragraph_scraping(query):
    """Scrape all paragraph text from a URL."""
    message = query.message
    response, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

    if not paragraphs:
        await message.reply_text("📃 No paragraphs found on this page.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="AllParagraphs-"
    ) as tmp:
        for para in paragraphs:
            tmp.write(f"{para}\n\n")
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📃 Found {len(paragraphs)} paragraphs\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def all_headings_scraping(query):
    """Scrape all heading tags (H1-H6) from a URL."""
    message = query.message
    response, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    headings = []
    for level in range(1, 7):
        for h in soup.find_all(f"h{level}"):
            text = h.get_text(strip=True)
            if text:
                headings.append(f"H{level}: {text}")

    if not headings:
        await message.reply_text("📌 No headings found on this page.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="AllHeadings-"
    ) as tmp:
        for heading in headings:
            tmp.write(f"{heading}\n")
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📌 Found {len(headings)} headings\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def all_tables_scraping(query):
    """Scrape all HTML tables from a URL."""
    message = query.message
    response, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    tables = soup.find_all("table")
    if not tables:
        await message.reply_text("📊 No tables found on this page.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="AllTables-"
    ) as tmp:
        for idx, table in enumerate(tables, 1):
            tmp.write(f"=== Table {idx} ===\n")
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                row_text = " | ".join(cell.get_text(strip=True) for cell in cells)
                tmp.write(f"{row_text}\n")
            tmp.write("\n")
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📊 Found {len(tables)} tables\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def extract_metadata(query):
    """Extract page metadata (title, description, keywords, Open Graph, Twitter)."""
    message = query.message
    txt = await message.reply_text("🔍 Extracting metadata...", quote=True)
    response, soup = await fetch_url(message.text)
    if not soup:
        await txt.edit("❌ Failed to parse the URL.")
        return

    # Basic metadata
    title = soup.title.string.strip() if soup.title else None
    description = None
    keywords = None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()

    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    if meta_kw and meta_kw.get("content"):
        keywords = meta_kw["content"].strip()

    # Open Graph
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    og_url = soup.find("meta", property="og:url")

    # Twitter Card
    tw_title = soup.find("meta", attrs={"name": "twitter:title"})
    tw_desc = soup.find("meta", attrs={"name": "twitter:description"})
    tw_image = soup.find("meta", attrs={"name": "twitter:image"})

    metadata_lines = ["<b>📊 Page Metadata</b>\n"]

    if title:
        metadata_lines.append(f"\n<b>📝 Title:</b> {title}")
    if description:
        metadata_lines.append(f"\n<b>📄 Description:</b> {description}")
    if keywords:
        metadata_lines.append(f"\n<b>🔑 Keywords:</b> {keywords}")

    # Open Graph section
    og_data = []
    if og_title and og_title.get("content"):
        og_data.append(f"<b>Title:</b> {og_title['content']}")
    if og_desc and og_desc.get("content"):
        og_data.append(f"<b>Description:</b> {og_desc['content']}")
    if og_image and og_image.get("content"):
        og_data.append(f"<b>Image:</b> {og_image['content']}")
    if og_url and og_url.get("content"):
        og_data.append(f"<b>URL:</b> {og_url['content']}")

    if og_data:
        metadata_lines.append("\n<b>🌐 Open Graph:</b>")
        metadata_lines.extend(og_data)

    # Twitter Card section
    tw_data = []
    if tw_title and tw_title.get("content"):
        tw_data.append(f"<b>Title:</b> {tw_title['content']}")
    if tw_desc and tw_desc.get("content"):
        tw_data.append(f"<b>Description:</b> {tw_desc['content']}")
    if tw_image and tw_image.get("content"):
        tw_data.append(f"<b>Image:</b> {tw_image['content']}")

    if tw_data:
        metadata_lines.append("\n<b>🐦 Twitter Card:</b>")
        metadata_lines.extend(tw_data)

    # Canonical link
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        metadata_lines.append(f"\n<b>🔗 Canonical:</b> {canonical['href']}")

    metadata_text = "\n".join(metadata_lines)
    if metadata_text == "<b>📊 Page Metadata</b>\n":
        metadata_text = "<b>📊 Page Metadata</b>\n\nNo metadata found."

    await message.reply_text(metadata_text, disable_web_page_preview=True)
    await txt.delete()

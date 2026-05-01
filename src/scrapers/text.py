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
    content, soup = await fetch_url(message.text)
    if not content:
        await message.reply_text("❌ Failed to fetch the URL.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".txt", delete=False, prefix="RawData-"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📄 Raw Content ({len(content):,} bytes)\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def html_data_scraping(query):
    """Scrape prettified HTML data from a URL."""
    message = query.message
    content, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    html_text = soup.prettify()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, prefix="HtmlData-"
    ) as tmp:
        tmp.write(html_text)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📝 HTML Data ({len(html_text):,} chars)\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def all_links_scraping(query):
    """Scrape all anchor links from a URL."""
    message = query.message
    content, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    base_url = message.text
    links = []
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
            full_url = urljoin(base_url, href)
            links.append(full_url)

    unique_links = sorted(set(links))
    if not unique_links:
        await message.reply_text("🔗 No links found on this page.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="AllLinks-"
    ) as tmp:
        for link in unique_links:
            tmp.write(f"{link}\n")
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"🔗 Found {len(unique_links)} unique links\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def all_paragraph_scraping(query):
    """Scrape all paragraph text from a URL."""
    message = query.message
    content, soup = await fetch_url(message.text)
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
    content, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    headings = []
    for level in range(1, 7):
        for h in soup.find_all(f"h{level}"):
            text = h.get_text(strip=True)
            if text:
                headings.append(f"[H{level}] {text}")

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
    """Scrape all HTML tables from a URL and convert to readable format."""
    message = query.message
    content, soup = await fetch_url(message.text)
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
            tmp.write(f"{'=' * 50}\n")
            tmp.write(f"  TABLE {idx}\n")
            tmp.write(f"{'=' * 50}\n\n")
            rows = table.find_all("tr")
            for row_idx, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                row_text = " | ".join(cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True))
                if row_text:
                    tmp.write(f"{row_text}\n")
                    if row_idx == 0:
                        tmp.write("-" * len(row_text) + "\n")
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
    """Extract page metadata (title, description, keywords, Open Graph, Twitter, etc.)."""
    message = query.message
    txt = await message.reply_text("🔍 Extracting metadata...", quote=True)
    content, soup = await fetch_url(message.text)
    if not soup:
        await txt.edit("❌ Failed to parse the URL.")
        return

    def get_meta_content(attrs):
        """Safely extract meta tag content."""
        tag = soup.find("meta", attrs=attrs)
        return tag.get("content", "").strip() if tag else None

    # Basic metadata
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    description = get_meta_content({"name": "description"})
    keywords = get_meta_content({"name": "keywords"})
    author = get_meta_content({"name": "author"})
    viewport = get_meta_content({"name": "viewport"})
    robots = get_meta_content({"name": "robots"})

    # Open Graph
    og_title = get_meta_content({"property": "og:title"})
    og_desc = get_meta_content({"property": "og:description"})
    og_image = get_meta_content({"property": "og:image"})
    og_url = get_meta_content({"property": "og:url"})
    og_type = get_meta_content({"property": "og:type"})
    og_site = get_meta_content({"property": "og:site_name"})

    # Twitter Card
    tw_card = get_meta_content({"name": "twitter:card"})
    tw_title = get_meta_content({"name": "twitter:title"})
    tw_desc = get_meta_content({"name": "twitter:description"})
    tw_image = get_meta_content({"name": "twitter:image"})
    tw_site = get_meta_content({"name": "twitter:site"})

    # Canonical
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical.get("href", "").strip() if canonical else None

    # Favicon
    favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower() if isinstance(x, str) else False)
    favicon_url = favicon.get("href", "").strip() if favicon else None

    metadata_lines = ["<b>📊 Page Metadata</b>\n"]

    if title:
        metadata_lines.append(f"\n<b>📝 Title:</b> {title}")
    if description:
        metadata_lines.append(f"<b>📄 Description:</b> {description}")
    if keywords:
        metadata_lines.append(f"<b>🔑 Keywords:</b> {keywords}")
    if author:
        metadata_lines.append(f"<b>👤 Author:</b> {author}")
    if viewport:
        metadata_lines.append(f"<b>📱 Viewport:</b> {viewport}")
    if robots:
        metadata_lines.append(f"<b>🤖 Robots:</b> {robots}")

    # Open Graph
    og_items = []
    if og_title: og_items.append(f"<b>Title:</b> {og_title}")
    if og_desc: og_items.append(f"<b>Description:</b> {og_desc}")
    if og_type: og_items.append(f"<b>Type:</b> {og_type}")
    if og_site: og_items.append(f"<b>Site:</b> {og_site}")
    if og_image: og_items.append(f"<b>Image:</b> {og_image}")
    if og_url: og_items.append(f"<b>URL:</b> {og_url}")

    if og_items:
        metadata_lines.append("\n<b>🌐 Open Graph:</b>")
        metadata_lines.extend(og_items)

    # Twitter Card
    tw_items = []
    if tw_card: tw_items.append(f"<b>Card:</b> {tw_card}")
    if tw_title: tw_items.append(f"<b>Title:</b> {tw_title}")
    if tw_desc: tw_items.append(f"<b>Description:</b> {tw_desc}")
    if tw_image: tw_items.append(f"<b>Image:</b> {tw_image}")
    if tw_site: tw_items.append(f"<b>Site:</b> {tw_site}")

    if tw_items:
        metadata_lines.append("\n<b>🐦 Twitter Card:</b>")
        metadata_lines.extend(tw_items)

    if canonical_url:
        metadata_lines.append(f"\n<b>🔗 Canonical:</b> {canonical_url}")
    if favicon_url:
        metadata_lines.append(f"<b>🎨 Favicon:</b> {favicon_url}")

    metadata_text = "\n".join(metadata_lines)
    if metadata_text == "<b>📊 Page Metadata</b>\n":
        metadata_text = "<b>📊 Page Metadata</b>\n\nNo metadata found."

    await message.reply_text(metadata_text, disable_web_page_preview=True)
    await txt.delete()


@handle_errors
async def extract_emails(query):
    """Extract email addresses from a URL."""
    import re
    message = query.message
    content, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    text = soup.get_text()
    email_pattern = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
    emails = sorted(set(email_pattern.findall(text)))

    if not emails:
        await message.reply_text("📧 No email addresses found on this page.", quote=True)
        return

    result = "\n".join(emails)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="Emails-"
    ) as tmp:
        tmp.write(result)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📧 Found {len(emails)} unique email addresses\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def extract_phone_numbers(query):
    """Extract phone numbers from a URL."""
    import re
    message = query.message
    content, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    text = soup.get_text()
    phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}')
    phones = sorted(set(m.strip() for m in phone_pattern.findall(text) if len(m.strip()) >= 7))

    if not phones:
        await message.reply_text("📞 No phone numbers found on this page.", quote=True)
        return

    result = "\n".join(phones)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="Phones-"
    ) as tmp:
        tmp.write(result)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📞 Found {len(phones)} phone numbers\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)


@handle_errors
async def text_content_scraping(query):
    """Extract clean readable text content from a URL (no HTML tags)."""
    message = query.message
    content, soup = await fetch_url(message.text)
    if not soup:
        await message.reply_text("❌ Failed to parse the URL.", quote=True)
        return

    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Clean up excessive whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    if not clean_text:
        await message.reply_text("📄 No readable text found on this page.", quote=True)
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="TextContent-"
    ) as tmp:
        tmp.write(clean_text)
        tmp_path = tmp.name

    await message.reply_document(
        tmp_path,
        caption=f"📄 Extracted {len(clean_text):,} characters of text\n{BOT_OWNER}",
        quote=True,
    )
    await asyncio.sleep(1)
    os.remove(tmp_path)

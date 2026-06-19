import sys
sys.path.append('../')
import re
from lxml import etree
import json
import requests as req
from ADC_function import *


def get_html_with_referer(url):
    """Fetch HTML from missav, using Referer header to bypass Cloudflare challenge."""
    proxy, timeout_val, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://missav.ws/",
    }

    s = req.Session()
    s.headers.update(headers)

    try:
        r = s.get(url, headers=headers, timeout=timeout_val, proxies=proxies)
        return r.text
    except Exception as e:
        print(f'[!] MissAV fetch failed: {e}')
        return get_html(url)


def parse_metadata_from_detail(html):
    """Parse metadata from a MissAV detail page.

    The detail page has structured <div class="text-secondary"> blocks, each containing
    a label span and a value element. We iterate through these to extract fields.
    """
    doc = etree.fromstring(html, etree.HTMLParser())

    # --- Extract OG meta tags for structured data ---
    og_image_url = doc.xpath("//meta[@property='og:image']/@content")
    og_release_date = doc.xpath("//meta[@property='og:video:release_date']/@content")
    og_duration_seconds = doc.xpath("//meta[@property='og:video:duration']/@content")

    # --- Parse structured metadata divs ---
    metadata_blocks = doc.xpath("//div[@class='text-secondary']")

    result = {
        'number': '',
        'title': '',
        'actor': [],       # list of actress names (female only, with ♀)
        'actor_male': [],  # male actors
        'studio': '',
        'label': '',
        'release': '',
        'runtime': '',
        'director': '',
        'tag': [],         # genre tags
        '_og_image': og_image_url[0] if og_image_url else '',
    }

    for block in metadata_blocks:
        label_span = block.xpath('.//span[1]/text()')
        if not label_span:
            continue
        label_text = ''.join(label_span).strip().rstrip(':')

        if label_text == '品番':
            result['number'] = get_value_from_block(block)
        elif label_text in ('配信開始日', '公開日'):
            time_el = block.xpath('.//time/@datetime')
            if time_el:
                m = re.search(r'(\d{4}-\d{2}-\d{2})', time_el[0])
                result['release'] = m.group(1) if m else get_value_from_block(block)
            else:
                result['release'] = get_value_from_block(block)
        elif label_text == '女優':
            links = block.xpath('.//a/text()')
            result['actor'] = [link.strip() for link in links if link.strip()]
        elif label_text == '男優':
            links = block.xpath('.//a/text()')
            result['actor_male'] = [link.strip() for link in links if link.strip()]
        elif label_text == 'ジャンル':
            tags = block.xpath('.//a/text()')
            result['tag'] = [t.strip() for t in tags if t.strip()]
        elif label_text == 'メーカー':
            links = block.xpath('.//a/text()')
            result['studio'] = links[0].strip() if links else get_value_from_block(block)
        elif label_text == 'レーベル':
            links = block.xpath('.//a/text()')
            result['label'] = links[0].strip() if links else get_value_from_block(block)
        elif label_text in ('監督', '导演'):
            links = block.xpath('.//a/text()')
            result['director'] = links[0].strip() if links else get_value_from_block(block)

    # --- Build title from OG meta if available ---
    og_title = doc.xpath("//meta[@property='og:title']/@content")
    if og_title:
        result['title'] = og_title[0].strip()

    # --- Handle duration ---
    if og_duration_seconds:
        try:
            total_minutes = int(og_duration_seconds[0]) // 60
            result['runtime'] = str(total_minutes) + ' min'
        except (ValueError, TypeError):
            pass

    return result


def get_value_from_block(block):
    """Get the value text from a metadata block.

    The structure is: <div class="text-secondary"><span>Label:</span><span class="font-medium">value</span></div>
    We skip the first span (label) and take remaining text content.
    """
    # Try to get text from <span class="font-medium"> elements
    spans = block.xpath('.//span[@class="font-medium"]/text()')
    if spans:
        return spans[0].strip()

    # Fallback: collect all text nodes, skip the first one (label)
    texts = block.xpath('.//text()[normalize-space()]')
    result_parts = []
    for t in texts:
        t = t.strip()
        if not t:
            continue
        # Skip label-like text (contains colon or known labels)
        if ':' in t and len(t) < 20:
            continue
        result_parts.append(t)

    return ', '.join(result_parts).strip()


def main(number):
    try:
        number = number.upper()

        # --- Step 1: Try direct URL first (missav supports direct dvd_id URLs) ---
        detail_url = f'https://missav.ws/ja/{number}'
        html = get_html_with_referer(detail_url)

        if not html or 'not found' in html.lower():
            # Fallback: search page
            search_url = f'https://missav.ws/search/{number}'
            html = get_html_with_referer(search_url)

        # --- Step 2: Parse metadata from detail page ---
        meta = parse_metadata_from_detail(html)

        # --- Step 3: Build output dictionary ---
        cover_small = ''
        if meta['title']:
            cover_small = f'https://fourhoi.com/{number.lower()}/cover-t.jpg'

        dic = {
            'actor': ', '.join(meta['actor']),
            'title': meta['title'],
            'studio': meta['studio'],
            'outline': '',  # MissAV doesn't provide outline on detail page
            'runtime': meta['runtime'],
            'director': meta['director'],
            'release': meta['release'],
            'number': meta['number'],
            'cover': meta.get('_og_image', f'https://fourhoi.com/{number.lower()}/cover-n.jpg'),
            'cover_small': cover_small if cover_small else '',
            'imagecut': 1,  # Default cut image since we have cover
            'tag': ', '.join(meta['tag']),
            'label': meta['label'],
            'year': get_year_from_release(meta['release']),
            'actor_photo': {},
            'website': f'https://missav.ws/ja/{number.lower()}',
            'source': 'missav.py',
        }

    except Exception as e:
        dic = {"title": ""}
        print(f'[!] MissAV error: {e}')

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
    return js


def get_year_from_release(release_str):
    """Extract year from release date string."""
    if not release_str:
        return ''
    m = re.search(r'(\d{4})', str(release_str))
    return m.group(1) if m else ''


if __name__ == "__main__":
    print(main('CAWD-969'))

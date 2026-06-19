# MissAV Crawler Analysis

## URL Structure
- Detail page: `https://missav.ws/ja/<dvd_id>` (e.g., `/ja/cawd-969`)
- Search page: `https://missav.ws/search/<keyword>` (e.g., `/search/cawd-969`)
- Cover images: `https://fourhoi.com/<dvd_id>/cover-n.jpg` (normal), `cover-t.jpg` (thumbnail)
- Video preview: `https://fourhoi.com/<dvd_id>/preview.mp4`

## HTTP Requirements
- Must use proxy (`curl -x http://127.0.0.1:1080`)
- Must set Referer header to `https://missav.ws/`
- User-Agent should be a modern browser UA (Chrome 128+ / Edge)

## HTML Structure Analysis (Detail Page)

### Metadata Fields (lines ~3041-3069 in detail page)
The metadata is rendered inside `<div class="space-y-2">` with each field as:
```html
<div class="text-secondary">
    <span>品番:</span>
    <span class="font-medium">CAWD-969</span>
</div>
<div class="text-secondary">
    <span>女優:</span>
    <a href="..." class="text-nord13 font-medium">山下紗和</a>
</div>
```

Fields and their labels:
| Label (Japanese) | English | Notes |
|---|---|---|
| 品番: | Movie Number | Direct text in `<span class="font-medium">` |
| 配信開始日: | Release Date | In `<time datetime="..." class="font-medium">` element |
| 女優: | Actress(es) | Links to actress pages; **only female actors with "♀" suffix** |
| 男優: | Actor(s) | Male actor links (not needed for metadata) |
| ジャンル: | Genre/Tags | Multiple comma-separated `<a>` tags |
| メーカー: | Studio/Maker | Single link |
| レーベル: | Label | Single link |
| 監督: | Director | Single link |

### XPath/CSS Selectors for Detail Page
- All metadata rows: `//div[@class='text-secondary']` — each contains a `<span>` label and value
- Movie number (品番): Find row with `<span>品番:</span>`, get sibling span text
- Release date (配信開始日): Find row with `<span>配信開始日:</span>`, extract from `<time datetime="...">` attribute or visible text
- Actress list: Find row with `<span>女優:</span>`, get all link texts
- Actor list: Find row with `<span>男優:</span>`, get all link texts  
- Genre tags: Find row with `<span>ジャンル:</span>`, extract all `<a>` text content
- Studio (メーカー): Find row with `<span>メーカー:</span>`, get link text
- Label (レーベル): Find row with `<span>レーベル:</span>`, get link text
- Director (監督): Find row with `<span>監督:</span>`, get link text

### Cover Image
- OG meta tag: `<meta property="og:image" content="https://fourhoi.com/<dvd_id>/cover-n.jpg">`
- Also available via preload link: `href="https://fourhoi.com/<dvd_id>/cover-n.jpg"`
- Thumbnail version: replace `cover-n.jpg` with `cover-t.jpg`

### Duration
- OG meta tag: `<meta property="og:video:duration" content="6928">` (seconds)
- Convert to minutes: divide by 60, round down

### Release Date
- OG meta tag: `<meta property="og:video:release_date" content="2026-04-03">` (ISO format YYYY-MM-DD)
- Also in detail page: `<time datetime="2026-04-03T00:00:00+08:00" class="font-medium">2026-04-03</time>`

### Title
- Page title tag contains the full title with number + description + actress name
- OG meta: `<meta property="og:title" content="CAWD-969 毎日ぶっかけ...">`

## Search Page Structure
- Results are rendered as card grid items
- Each result has: cover image (`cover-t.jpg`), video preview, title text, duration badge
- URL pattern for each result: `https://missav.ws/<locale>/<dvd_id>` or `https://missav.ws/<dvd_id>` (no locale prefix)
- Multiple variants may exist for same DVD ID (e.g., Chinese subtitle version)

## Key Differences from javdb/javbus/fanza
1. **No age gate** — MissAV does not require age confirmation
2. **Direct URL by number** — `https://missav.ws/ja/<dvd_id>` works directly
3. **Cloudflare challenge on first visit** — requires Referer header to bypass
4. **Metadata in structured divs** — each field is a separate `<div class="text-secondary">` block
5. **OG meta tags provide structured data** — duration, release_date, actor, director all available

## Crawler Strategy
1. Construct URL: `https://missav.ws/ja/<dvd_id>` (or try without locale prefix)
2. Fetch with Referer header set to `https://missav.ws/`
3. Parse detail page for metadata using the structured div layout
4. Extract cover from og:image meta tag
5. For search fallback: use `/search/<keyword>` and match by dvd_id

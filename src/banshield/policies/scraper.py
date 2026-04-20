"""Playwright-based policy scraper with text extraction and chunking."""

from datetime import datetime, timezone

from playwright.async_api import async_playwright

from banshield.policies.sources import POLICY_SOURCES


class PolicyScraper:
    """Scrapes advertising policy pages and chunks the content."""

    _CHUNK_SIZE = 2000  # ~500 tokens at ~4 chars per token
    _OVERLAP = 200  # ~50 tokens overlap

    async def scrape_url(self, url: str, platform: str) -> list[dict]:
        """Fetch a single URL, extract clean text, and chunk it."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")

            text = await page.evaluate(
                """() => {
                    const selectors = [
                        'nav', 'footer', 'script', 'style', 'header',
                        'aside', '[role="navigation"]', '[role="banner"]',
                        'noscript', 'iframe', 'svg'
                    ];
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => el.remove());
                    });
                    return document.body.innerText.trim();
                }"""
            )

            await browser.close()

        chunks = self._chunk_text(text)
        scraped_at = datetime.now(timezone.utc).isoformat()

        return [
            {
                "platform": platform,
                "url": url,
                "chunk": chunk,
                "chunk_index": idx,
                "scraped_at": scraped_at,
            }
            for idx, chunk in enumerate(chunks)
        ]

    async def scrape_all(self) -> list[dict]:
        """Scrape all configured policy sources."""
        results: list[dict] = []
        for platform, urls in POLICY_SOURCES.items():
            for url in urls:
                chunks = await self.scrape_url(url, platform)
                results.extend(chunks)
        return results

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks by character count."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self._CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk.strip())
            if end >= len(text):
                break
            start = end - self._OVERLAP
        return [c for c in chunks if c]

import pytest
from playwright.async_api import async_playwright

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_synthetic_generation_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501/synthetic", timeout=15000)
        # assert UI contains generator controls
        content = await page.content()
        assert "Gerar Nota" in content or "Sintética" in content
        await browser.close()

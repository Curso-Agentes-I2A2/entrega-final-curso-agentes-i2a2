import pytest
from playwright.async_api import async_playwright
from tests.fixtures.mock_data import VALID_INVOICE_XML

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_uploads_and_audits_invoice():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto("http://localhost:8501", timeout=30000)
        # wait file input and upload
        await page.wait_for_selector('input[type="file"]', timeout=15000)
        await page.set_input_files('input[type="file"]', {
            "name": "nf.xml",
            "mimeType": "application/xml",
            "buffer": VALID_INVOICE_XML.encode("utf-8")
        })
        # click start audit (adjust selector to your UI)
        await page.click('text=Iniciar Auditoria', timeout=10000)
        # wait for results
        await page.wait_for_selector('text=Resultado', timeout=30000)
        assert "Resultado" in await page.content()
        await browser.close()

"""以可视模式打开应用"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            args=["--window-size=420,900"]
        )
        ctx = await browser.new_context(viewport={"width": 390, "height": 844})
        page = await ctx.new_page()
        
        await page.goto("http://localhost:5173/", wait_until="networkidle", timeout=15000)
        await page.evaluate('''async () => {
            const resp = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: 'test', password: '123456'})
            });
            if (resp.ok) {
                const data = await resp.json();
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('userInfo', JSON.stringify(data.user));
            }
        }''')
        
        await page.goto("http://localhost:5173/life-kline", wait_until="networkidle", timeout=15000)
        
        print("浏览器已打开，人生K线页面已加载。窗口保持60秒...")
        await asyncio.sleep(60)
        await browser.close()

asyncio.run(main())

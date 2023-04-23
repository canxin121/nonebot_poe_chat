import asyncio
import json
from playwright.async_api import async_playwright
from .config import Config
config = Config()
async def clear_bot(page, botname):
    try:
        await page.goto(f'https://poe.com/{botname}')
        
        # 等待元素出现
        element = await page.wait_for_selector('div.ChatMessageInputView_paintbrushWraper__DHMNW')
        await asyncio.sleep(1)
        await element.wait_for_selector('svg.ChatMessageInputView_paintbrushIcon__Turkx')
        svg_element = await page.query_selector(".ChatMessageInputView_paintbrushIcon__Turkx")

        # Get the bounding box of the SVG element
        bbox = await svg_element.bounding_box()
        x = bbox["x"] + 10   # Replace with your desired x coordinate
        y = bbox["y"] - 10   # Replace with your desired y coordinate
        await page.mouse.click(x=x,y=y)
        
        return True
    except:
        return False
    finally:
        await page.close()
        
async def poe_clear(cookie_path,botname):
    async with async_playwright() as p:
        server = config.server
        username = config.username
        passwd = config.passwd
        proxy_config = {}
        if server is not None:
            proxy_config["server"] = server
        if username is not None:
            proxy_config["username"] = username
        if passwd is not None:
            proxy_config["password"] = passwd

        if proxy_config:
            browser = await p.chromium.launch(proxy=proxy_config)
        else:
            browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        with open(cookie_path, 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies=cookies)
        is_cleared = await clear_bot(page, botname)
        await context.close()
        await browser.close()
        return is_cleared
    
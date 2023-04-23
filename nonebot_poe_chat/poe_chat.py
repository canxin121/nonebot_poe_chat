import asyncio
import json
import re
from playwright.async_api import async_playwright
from playwright.sync_api import Page
from .config import Config
config = Config()
async def send_message_async(page: Page, botname: str, input_str: str):
    # 定义重试次数和重试间隔时间
    retry_count = 5
    retry_interval = 0.5

    # 定义当前重试次数和报错次数
    current_retry = 0
    error_count = 0

    while current_retry < retry_count:

        try:
            # 打开目标网页
            await page.goto(f'https://poe.com/{botname}')
            text = "This bot has been deleted for violating our"
            content = await page.content()
            if text in content:
                return "banned"
            # 找到输入框元素
            input_box = await page.wait_for_selector('.ChatMessageInputView_textInput__Aervw',timeout=2000)

            # 将字符串发送到输入框中
            await input_box.fill(input_str)

            # 找到发送按钮元素并点击,容易点不到，多等一次
            await page.wait_for_selector('button.Button_primary__pIDjn',timeout=1000)
            send_button = await page.wait_for_selector('button.Button_primary__pIDjn',timeout=1000)
            # await asyncio.sleep(0.5)
            await send_button.click()
            # 发送成功后退出循环
            break
        except:
            # 如果出现超时异常，打印错误信息并稍等一段时间后重试
            error_count += 1
            if error_count >= 1:
                await asyncio.sleep(retry_interval)
            current_retry += 1
            continue
    if current_retry == retry_count:
        return False

async def get_message_async(page,botname, sleep):
    consecutive_errors = 0  # initialize a counter for consecutive errors
    while True:
        await asyncio.sleep(sleep)
        try:
            await page.goto(f'https://poe.com/{botname}')
            response = await page.content()
            text = "This bot has been deleted for violating our"
            if text in response:
                return "banned"
            match_text = re.search(r'<script id="__NEXT_DATA__" type="application/json">*(.*?)</script>', response, re.DOTALL)
            json_data_text = match_text.group(1)
            json_obj_text = json.loads(json_data_text)

            chat_list_raw = json_obj_text["props"]["pageProps"]["payload"]["chatOfBotDisplayName"]["messagesConnection"]["edges"]

            chat_list_raw = [a["node"] for a in chat_list_raw]
            chat_list_text = [a["text"] for a in chat_list_raw]
            if chat_list_text[-1]:
                match_suggest = re.search(r'<section class="ChatMessageSuggestedReplies_suggestedRepliesContainer__JgW12">*(.*?)</section>', response, re.DOTALL)
                string_list = re.findall(r'>\s*([^<>\n]+)\s*<', match_suggest.group(1))
                if len(string_list) == 4:
                    return chat_list_text, string_list
        except :
            consecutive_errors += 1
            if consecutive_errors >= 5:
                return False
        else:
            consecutive_errors = 0

async def poe_chat(cookie_path,botname,question):
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
        is_banned = await send_message_async(page, botname, question)
        if is_banned == "banned":
            return "banned"
        result = await get_message_async(page, botname, sleep=3)
        if isinstance(result, tuple):
            answers, suggests = result
            return answers[-1],suggests
        elif isinstance(result, str):
            is_banned = result
            return "banned"
        elif isinstance(result, bool):
            is_got = result
            return is_got
        else:
            raise ValueError("Unexpected return type from get_message_async")
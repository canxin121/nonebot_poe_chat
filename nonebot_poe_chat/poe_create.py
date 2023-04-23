import json
from playwright.async_api import async_playwright, ElementHandle
from .config import Config
config = Config()
async def create_bot_async(page, botname, base_bot_index, prompt, retries=2):
    try:
        for i in range(retries):
            await page.goto('https://poe.com/create_bot')

            # 定位输入框并清空原有的默认值
            name_input: ElementHandle = await page.wait_for_selector('input[name="name"]')
            await name_input.fill('')

            # 输入新的值
            await name_input.fill(botname)

            await page.wait_for_selector('select[name="baseBot"]')
            
            if base_bot_index == 1:
                value = "chinchilla"
            elif base_bot_index ==2:
                value = "a2"
            # 根据索引选择选项
            await page.select_option('.BotInfoForm_select__lFCl0', value=value)
            
            # 添加预设
            prompt_textarea = await page.wait_for_selector('textarea[name="prompt"]')
            await prompt_textarea.fill(prompt)

            chevron_button = await page.wait_for_selector('.BotInfoForm_chevronDown__LFWWC')
            await chevron_button.click()

            # 点击"Suggest replies"复选框的<label>元素
            checkbox_label: ElementHandle = await page.wait_for_selector('//div[contains(text(), "Suggest replies")]/following-sibling::label')
            await checkbox_label.click()

            # 点击"Linkify bot responses"复选框的<label>元素
            checkbox_label = await page.wait_for_selector('//div[contains(text(), "Linkify bot responses")]/following-sibling::label')
            await checkbox_label.click()

            # 点击"Create bot"按钮
            create_bot_button = await page.wait_for_selector('button.Button_primary__pIDjn')
            await create_bot_button.click()

            # 等待新页面加载完成
            try:
                await page.wait_for_selector('textarea.ChatMessageInputView_textInput__Aervw', timeout=5000)
                return True
            except:
                pass

        return False
    finally:
        await page.close()
# cookie_path = r"C:\Users\Administrator\Desktop\nonebot2\cccc\src\plugins\nonebot_poe_chat\data\poe_cookie.json"                      
async def poe_create(cookie_path,botname, base_bot_index, prompt):
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
        is_created = await create_bot_async(page,botname, base_bot_index, prompt, retries=5)
        await context.close()
        await browser.close()
        return is_created


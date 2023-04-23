import asyncio
import json

async def submit_email(page,email):
    for i in range(5):
        try:
            await page.goto("https://poe.com")
            # 点击 "Use email" 按钮
            use_email_button = await page.query_selector('button:has-text("Use email")')
            await use_email_button.click()

            # 填写 email 地址
            email_input = await page.wait_for_selector('input.EmailInput_emailInput__4v_bn')
            await email_input.fill(email)

            # 点击 "Go" 按钮
            go_button = await page.query_selector('button:has-text("Go")')
            await go_button.click()

            # 等待跳转并检查输入框是否存在
            await page.wait_for_selector('input.VerificationCodeInput_verificationCodeInput__YD3KV')
            return True
        except:
            await page.reload()
    return False


async def submit_code(page, code, path):
    retry_count = 0
    while retry_count < 3:
        try:
            # 填写验证码
            code_input = await page.wait_for_selector('input.VerificationCodeInput_verificationCodeInput__YD3KV')
            await code_input.fill('') # 清空输入框
            await code_input.fill(code)

            # 点击 "Log In" 按钮
            login_button = await page.query_selector('button:has-text("Log In")')
            await login_button.click()

            # 等待页面跳转，并检查页面是否有指定的输入框元素
            await page.wait_for_selector('textarea.ChatMessageInputView_textInput__Aervw')

            # 获取当前页面的 cookie，并保存 poe.com 域名下的 cookie 到本地文件中
            cookies = await page.context.cookies()
            poe_cookies = [cookie for cookie in cookies if cookie['domain'] == 'poe.com']
            with open(path, 'w') as f:
                json.dump(poe_cookies, f)

            return True
        except:
            # 如果页面上没有指定的输入框元素，就认为是失败了
            if not await page.query_selector('textarea.ChatMessageInputView_textInput__Aervw'):
                retry_count += 1
                # 等待一段时间后再次尝试输入验证码并点击 "Log In" 按钮
                await asyncio.sleep(1)
            else:
                raise
    return False
    
    
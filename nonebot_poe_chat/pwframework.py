from playwright.async_api import async_playwright, Page
from .config import Config
config = Config()

#用元类实现单例，提供一个创建新页面的函数
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PlaywrightFramework(metaclass=Singleton):
    def __init__(self):
        self.context = None
        self.playwright = None
        self.browser = None

    async def init_framework(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            is_cookie_exsits = config.is_cookie_exists
            cookies = config.cookie_dict
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
                self.browser = await self.playwright.chromium.launch(proxy=proxy_config,headless=False)
            else:
                self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            print("创建context")
            if is_cookie_exsits:
                await self.context.add_cookies(cookies=[cookies])

    async def close_framework(self):
        if self.context:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
            self.context = None
            self.browser = None
            self.playwright = None

    async def new_page(self) -> Page:
        if not self.context:
            await self.init_framework()
        return await self.context.new_page()
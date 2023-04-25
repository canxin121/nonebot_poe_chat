import json
import os
import nonebot
from pathlib import Path    
def check_cookie(self):
    if os.path.exists(self.cookie_path):
        try:
            with open(self.cookie_path, 'r') as f:
                cookie = json.load(f)
                if all(key in cookie for key in ('domain', 'name', 'path')) and 'value' in cookie:
                    if cookie['domain'] == 'poe.com' and cookie['name'] == 'p-b' and cookie['path'] == '/':
                        return True
        except:
            pass
    try:
        if not os.path.exists(self.cookie_path):
            with open(self.cookie_path, 'w') as f:
                f.write('{}')
                print('poe_cookie.json 创建成功')
        poe_ck = nonebot.get_driver().config.poe_cookie
        cookie_parms = [
        {
            "domain": "poe.com",
            "name": "p-b",
            "path": "/",
            "value": f"{poe_ck}"
        }
        ] 
        is_env_ck = True
    except:
        is_env_ck = False

    if is_env_ck:
        with open(self.cookie_path, 'w') as f:
            json.dump(cookie_parms, f)
        return True
    return False


class Config:
    def __init__(self):
        self.path_ = str(Path()) + "/data/poe_chat"
        self.user_path = str(self.path_ + r'/user_dict.json')
        self.prompt_path = str(self.path_ + r'/poe_prompt.json')
        self.cookie_path = str(self.path_ + r'/poe_cookie.json')
        self.url_able = True
        self.pic_able = True
        self.server = None
        self.username = None
        self.passwd = None
        
        self.superusers = []
        self.cookie_dict = {}
        self.user_dict = {}
        self.prompts_dict = {}
        self.is_cookie_exists = check_cookie(self)
        if self.is_cookie_exists:
            with open(self.cookie_path, 'r') as f:
                cookies = json.load(f)
                self.cookie_dict =cookies
        # 加载超级用户配置
        try:
            self.superusers = nonebot.get_driver().config.poe_superusers
        except:
            pass
        try:
            if nonebot.get_driver().config.poe_picable == "False":
                self.pic_able = False
        except:
            pass
        try:
            self.server = nonebot.get_driver().config.poe_server
        except:
            pass
        try:
            self.username = nonebot.get_driver().config.poe_username
        except:
            pass
        try:
            self.passwd = nonebot.get_driver().config.poe_passwd
        except:
            pass
        try:
            if nonebot.get_driver().config.poe_urlable == "False":
                self.url_able = False
        except:
            pass
        
        # 加载用户配置文件
        if not os.path.exists(self.user_path):
            # 获取目录路径
            dir_path = os.path.dirname(self.user_path)
            # 如果目录不存在，则创建目录
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(self.user_path, 'w') as f:
                f.write('{}')
                print('user_dict.json 创建成功')
            
        try:
            with open(self.user_path, 'r') as f:
                self.user_dict = json.load(f)
        except:
            pass
        
        if not os.path.exists(self.prompt_path):
            # 获取目录路径
            dir_path = os.path.dirname(self.prompt_path)
            # 如果目录不存在，则创建目录
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(self.prompt_path, 'w') as f:
                f.write('{"\u9ed8\u8ba4": "\u4e00\u4e2aai\u8bed\u8a00\u6a21\u578b"}')
                print('prompt_dict.json 创建成功')
            
        
        with open(self.prompt_path, 'r') as f:
            self.prompts_dict = json.load(f)



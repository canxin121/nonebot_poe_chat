import json
import os
import nonebot
from nonebot import logger
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
                logger.info('poe_cookie.json 创建成功')
        poe_ck = nonebot.get_driver().config.poe_cookie
        cookie_parms = {
            "domain": "poe.com",
            "name": "p-b",
            "path": "/",
            "value": f"{poe_ck}"
        }
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
        self.superuser_dict_path = str(self.path_ + r'/superuser_dict.json')
        self.pic_able = True
        self.url_able = True
        self.qr_able = True
        self.suggest_able = True
        self.server = None
        self.username = None
        self.passwd = None
        self.superuser_dict = {}
        self.superusers = []
        self.blacklist = []
        self.whitelist = []
        self.mode = "black"
        self.cookie_dict = {}
        self.user_dict = {}
        self.prompts_dict = {}
        self.is_cookie_exists = check_cookie(self)
        if self.is_cookie_exists:
            with open(self.cookie_path, 'r') as f:
                cookies = json.load(f)
                self.cookie_dict =cookies
                
        get_config = nonebot.get_driver().config

        self.superusers = get_config.poe_superusers if hasattr(get_config, 'poe_superusers') else None
        self.blacklist = get_config.poe_blacklist if hasattr(get_config, 'poe_blacklist') else None
        self.whitelist = get_config.poe_whitelist if hasattr(get_config, 'poe_whitelist') else None

        self.mode = get_config.poe_mode if hasattr(get_config, 'poe_mode') and get_config.poe_mode in ['white', 'black'] else 'black'

        self.pic_able = getattr(get_config, 'poe_picable', True)
        self.url_able = getattr(get_config, 'poe_urlable', True)
        self.suggest_able = getattr(get_config, 'poe_suggestable', True)
        self.qr_able = getattr(get_config, 'poe_qrable', True)

        self.server = getattr(get_config, 'poe_server', None)
        self.username = getattr(get_config, 'poe_username', None)
        self.passwd = getattr(get_config, 'poe_passwd', None)
        # 加载用户配置文件
        if not os.path.exists(self.user_path):
            # 获取目录路径
            dir_path = os.path.dirname(self.user_path)
            # 如果目录不存在，则创建目录
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(self.user_path, 'w') as f:
                f.write('{}')
                logger.info('user_dict.json 创建成功')
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
                f.write('{"\u9ed8\u8ba4": "\u4e00\u4e2a\u667a\u80fd\u52a9\u7406", "\u732b\u5a18": "\u73b0\u5728\u4f60\u5c06\u6a21\u4eff\u4e00\u53ea\u732b\u5a18\uff0c\u4e0e\u6211\u5bf9\u8bdd\u6bcf\u4e00\u53e5\u8bdd\u540e\u9762\u90fd\u8981\u52a0\u4e0a\u201c\u55b5\u201d\uff0c\u5982\u679c\u4f60\u80fd\u660e\u767d\u6211\u7684\u610f\u601d\uff0c\u8bf7\u56de\u590d\u201c\u55b5~\u4f60\u597d\u4e3b\u4eba\u201d"}')
                logger.info('prompt_dict.json 创建成功')
            
        
        with open(self.prompt_path, 'r') as f:
            self.prompts_dict = json.load(f)
            
        if not os.path.exists(self.superuser_dict_path):
            # 获取目录路径
            dir_path = os.path.dirname(self.superuser_dict_path)
            # 如果目录不存在，则创建目录
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(self.superuser_dict_path, 'w') as f:
                f.write('{"auto_default":"\u9ed8\u8ba4","blacklist":[]}')
                logger.info('superuser_dict.json 创建成功')            
                        
        with open(self.superuser_dict_path, 'r') as f:
            self.superuser_dict = json.load(f)


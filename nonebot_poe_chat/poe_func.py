from typing import Union
import re, uuid, asyncio,string,random
import aiohttp
import qrcode
from .config import Config
from nonebot import logger, require
require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message,MessageEvent,MessageSegment
from .txt2img import Txt2Img
config = Config()
txt2img = Txt2Img()
is_suggest_able = config.suggest_able
is_pic_able = config.pic_able
is_url_able = config.url_able
is_qr_able = config.qr_able
num_limit = config.num_limit
def reply_out(event: MessageEvent, content: Union[MessageSegment,Message,str,bytes]) -> Message:
    """返回一个回复消息"""
    if isinstance(event, GuildMessageEvent):
        return Message(content)
    if type(content) == bytes:
        return MessageSegment.reply(event.message_id) + MessageSegment.image(content)
    if content[0:9] == 'base64://':
        return MessageSegment.reply(event.message_id) + MessageSegment.image(content)
    return MessageSegment.reply(event.message_id) + content

#生成一个由qq号和nickname共同决定的uuid作为真名，防止重名
def generate_uuid(s) ->str:
    # 将字符串转换为 UUID 对象
    uuid_object = uuid.uuid3(uuid.NAMESPACE_DNS, s)
    # 获取 UUID 对象的 bytes 值
    uuid_bytes = uuid_object.bytes
    # 将 bytes 值转换为字符串
    uuid_str = uuid_bytes.hex()[:14]
    return uuid_str

def generate_random_string(length=8) -> str:
    """生成指定长度的随机字符串"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def is_email(email) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

async def delete_messages(bot, user_id:str, dict_list:dict):
    if user_id in dict_list:
        if isinstance(dict_list[user_id], list):
            for eachmsg in dict_list[user_id]:
                await bot.delete_msg(message_id=eachmsg['message_id'])
            del dict_list[user_id]
        else:
            await bot.delete_msg(message_id=dict_list[user_id]['message_id'])

async def mdlink_2_str(md_text):
    result = []
    pattern = r'\[([^\]]+)\]\(([^)]+)\)(\s*-\s*([^[]+))?' # 匹配超链接及其描述
    matches = re.findall(pattern, md_text)
    for i, match in enumerate(matches):
        # 提取标题
        title = match[0].strip() if not match[3] else match[3].strip()
        # 组合字符串
        result.append(f"{i+1}. {title} - {match[1].strip()}")

    output_str = '\n\n'.join(result)
    return output_str

def is_useable(event,mode = config.mode):
    if mode == "black":
        try:
            if str(event.user_id) in config.blacklist:
                return False
        except:
            pass
        try:
            if str(event.group_id) in config.blacklist:
                return False
        except:
            pass
        return True
    elif mode == "white":
        try:
            if str(event.user_id) in config.whitelist:
                return True
        except:
            pass
        try:
            if str(event.group_id) in config.whitelist:
                return True
        except:
            pass
        return False
async def close_page(page):
    try:
        await page.close()
    except:
        pass
async def send_msg(result, matcher, event):
    msgid_container = {}
    suggest_container = []
    async def send_message(msg):
        if is_pic_able is not None:
            if is_pic_able == 'True':
                if is_qr_able == 'True':
                    pic, url = await txt2img.draw(title=" ", text=msg)
                    if is_url_able == 'True':
                        msgid_container = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        msgid_container = await matcher.send(reply_out(event, pic))
                else:
                    pic, _ = await txt2img.draw(title=" ", text=msg)
                    msgid_container = await matcher.send(reply_out(event, pic))
            else:
                    msgid_container = await matcher.send(reply_out(event, msg))
        else:
            if len(msg) > num_limit:
                pic, url = await txt2img.draw(title=" ", text=msg)
                msgid_container = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))    
            else:
                msgid_container = await matcher.send(reply_out(event, msg))
        return msgid_container
    
    if isinstance(result, tuple):
        last_answer, suggest_container = result
        is_successful = True
    elif isinstance(result, str):
        if "banned" == result:
            await matcher.send(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
            matcher.finish()
            return msgid_container,[]
    elif isinstance(result, bool):
        is_successful = result
    else:
        raise ValueError("Unexpected return type from get_message_async")
        
    if is_successful:
        suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(suggest_container)])
        if is_suggest_able == 'True':
            msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
        else:
            msg = f"{last_answer}\n"
        
        msgid_container = await send_message(msg)
        return msgid_container,suggest_container
    else:
        await matcher.send(reply_out(event, "出错了，多次出错请联系机器人管理员"))
        return msgid_container,suggest_container
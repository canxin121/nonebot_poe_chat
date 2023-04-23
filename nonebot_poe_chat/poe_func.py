import base64
from io import BytesIO
from typing import Union
import re, uuid, asyncio,string,random
import aiohttp
import qrcode
from nonebot import require
require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message,MessageEvent,MessageSegment

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

async def get_qr_img(text):
    """将 Markdown 文本保存到 Mozilla Pastebin，并获得 URL"""
    async with aiohttp.ClientSession() as session:
        payload = {'expires': '86400', 'format': 'url', 'lexer': '_markdown', 'content': text}
        try:
            async with session.post('https://pastebin.mozilla.org/api/',
                                    data=payload) as resp:
                resp.raise_for_status()
                url = await resp.text()
                url = url[0:-1]
        except Exception as e:
            url = f"上传失败：{str(e)}"
        image = qrcode.make(url)
        return image,url

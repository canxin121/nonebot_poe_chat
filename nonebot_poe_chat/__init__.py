import re, json, uuid, asyncio
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.plugin import on_command, on
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageEvent,MessageSegment
from nonebot.internal.rule import Rule
from playwright.async_api import async_playwright
from .poe_chat import poe_chat
from .poe_create import poe_create
from .poe_clear import poe_clear
from .poe_login import submit_email, submit_code
from .config import Config
#一些配置
config = Config()
user_dict = config.user_dict
prompts_dict = config.prompts_dict
user_path = config.user_path
prompt_path = config.prompt_path
cookie_path = config.cookie_path
superusers = config.superusers
is_cookie_exists = config.is_cookie_exists

def reply_out(event: MessageEvent, content: MessageSegment | Message | str) -> Message:
    """返回一个回复消息"""
    if isinstance(event, GuildMessageEvent):
        return Message(content)

    return MessageSegment.reply(event.message_id) + content
######################################################
#生成一个由qq号和nickname共同决定的uuid作为真名，防止重名
def generate_uuid(s):
    # 将字符串转换为 UUID 对象
    uuid_object = uuid.uuid3(uuid.NAMESPACE_DNS, s)
    # 获取 UUID 对象的 bytes 值
    uuid_bytes = uuid_object.bytes
    # 将 bytes 值转换为字符串
    uuid_str = uuid_bytes.hex()[:14]
    return uuid_str

poe_create_ = on_command(
    "poecreate",
    aliases={
        "创建bot",
        "pc"
        },
    priority=4,
    block=False)
@poe_create_.handle()
async def __(matcher:Matcher,state: T_State,event: Event):
    state["user_id"] = str(event.user_id)
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    else:
        if len(prompts_dict)>0:
            str_prompts = str()
            for key, _ in prompts_dict.items():
                str_prompts += f"{key}\n"
            await matcher.send(reply_out(event, f"当前预设有：\n{str_prompts}"))
        else:
            await matcher.send(reply_out(event, "当前没有本地预设"))

@poe_create_.got('model',prompt='请输入\n1.机器人名称,\n2.基础模型选项，可选项为（gpt3_5输入1,claude输入2）,\n3.自定义预设（预设内容中间不要有空格） 或 "." + 可用本地预设名\n三个参数中间用空格隔开\n最终格式示例:\n示例一：chat 2 一个智能助理\n示例二： claude 1 .默认\n输入取消 或 算了可以终止创建')
async def __poe_create___(matcher:Matcher,event:Event,state: T_State, infos: str = ArgStr("model")):
    if infos in ["取消", "算了"]:
        await matcher.finish(reply_out(event, "取消创建"))
    infos = infos.split(" ")
    if not (len(infos) == 3 and infos[1] in ['1', '2']):
        await matcher.reject(reply_out(event, "输入信息有误，请检查后重新输入"))
    #获取创建所需信息
    userid = str(state['user_id'])
    nickname = str(infos[0])
    truename = str(generate_uuid(str(userid + infos[0])))
    prompt = str(infos[2])
    bot_index = str(infos[1])
    if prompt.startswith("."):
        prompt_name = prompt[1:]
        if prompt_name in prompts_dict:
            prompt = prompts_dict[prompt_name]
        else:
            await matcher.reject(reply_out(event, "输入的本地预设名不正确，请重新输入"))
    
    if not userid in user_dict:
        user_dict[userid] = {}
    if 'all' not in user_dict[userid]:
        user_dict[userid]['all'] = {}
    if 'now' not in user_dict[userid]:
        user_dict[userid]['now'] = {}
    #查看对应用户下是不是有重名的bot
    if  nickname in user_dict[userid]['all']:
        await matcher.reject(reply_out(event, "已经有同名的bot了，换一个名字重新输入吧"))
    else:
        is_created = await poe_create(cookie_path,truename,int(bot_index),prompt)
        if is_created:
            # # 将更新后的字典写回到JSON文件中
            user_dict[userid]['all'][nickname] = truename
            
            if user_dict[userid]['now']:
                user_dict[userid]['now'] = {}
            user_dict[userid]['now'][nickname] = truename
            
            with open(user_path, 'w') as f:
                json.dump(user_dict, f)
            await matcher.finish(reply_out(event, "创建成功并切换到新建bot"))
        else:
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))

######################################################    
#保留上一个回答的chatsuggest
chat_lock = asyncio.Semaphore(3)
chat_suggest = {}
waitque = []
poe_chat_ = on_command(
    "poetalk",
    aliases={
        "ptalk",
        "pt"
        },
    priority=1,
    block=False)
@poe_chat_.handle()
async def __chat_bot__(matcher:Matcher,event: Event, args: Message = CommandArg()):
    global chat_lock,chat_suggest
    userid = str(event.user_id)
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    if userid not in user_dict:
        truename = str(generate_uuid(str(userid + "default")))
        is_created = await poe_create(cookie_path,truename,1,"一个智能助理")
        if is_created:
            user_dict[userid] = {}        
            user_dict[userid]['all'] = {}
            user_dict[userid]['all']["default"] = truename
            user_dict[userid]['now'] = {}
            user_dict[userid]['now']["default"] = truename
            with open(user_path, 'w') as f:
                json.dump(user_dict, f)
            await matcher.send(reply_out(event, "自动创建default gpt3.5成功"))
        else:
            await matcher.send(reply_out(event, "自动创建default gpt3.5失败，多次失败请联系机器人管理员"))
    if userid in chat_suggest and len(str(args[0])) == 1 and str(args[0]) in ['1','2','3','4']:
        text = chat_suggest[userid][int(str(args[0]))-1]
    else:
        text = str(args[0])
    botname = str(list(user_dict[userid]["now"].values())[0])
    if userid in waitque:
        await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后再发送"))
    if chat_lock.locked():
        await matcher.send(reply_out(event, "请稍等,你前面已有3个用户,你的回答稍后就来"))
    async with chat_lock:
        waitque.append(userid)
        result = await poe_chat(cookie_path, botname, text)
        if isinstance(result, tuple):
            last_answer, chat_suggest[userid] = result
            is_successful = True
        elif isinstance(result, str):
            if "banned" == result:
                waitque.remove(userid)
                await matcher.finish(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
        elif isinstance(result, bool):
            is_successful = result
        else:
            #这个应该不可能出现
            raise ValueError("Unexpected return type from get_message_async")

        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(chat_suggest[userid])])
            msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            waitque.remove(userid)
            await matcher.finish(reply_out(event, msg))
        else:
            waitque.remove(userid)
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))

######################################################
#判断是不是同一个对话中
async def _is_reply_(event:MessageEvent,bot:Bot):
    if bool(event.reply):
        reply = event.reply
        user_id = str(event.user_id)
        bot_id = bot.self_id
        sender_id = str(reply.sender.user_id)
        lastsuggest = str(reply.message).split("\n")[-1][3:]
        if user_id in chat_suggest and sender_id == bot_id and lastsuggest == chat_suggest[user_id][-1]:
            return True
    return False
is_reply = Rule(_is_reply_)

_poe_continue_ = on(rule=is_reply)
@_poe_continue_.handle()
async def __poe_continue__(matcher: Matcher,event:MessageEvent):
    userid = str(event.user_id)
    raw_message = str(event.message)
    if userid in waitque:
        await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后在发送"))
    if userid in chat_suggest and len(raw_message) == 1 and raw_message in ['1','2','3','4']:
            text = chat_suggest[userid][int(raw_message)-1]
    else:
        text = raw_message
    
    global chat_lock
    if chat_lock.locked():
        await matcher.send(reply_out(event, '请稍等,你前面已有3个用户'))
        
    botname = str(list(user_dict[userid]["now"].values())[0])
        
    async with chat_lock:
        waitque.append(userid)
        result = await poe_chat(cookie_path, botname, text)
        if isinstance(result, tuple):
            last_answer, chat_suggest[userid] = result
            is_successful = True
        elif isinstance(result, str):
            if "banned" == result:
                waitque.remove(userid)
                await matcher.finish(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
        elif isinstance(result, bool):
            is_successful = result
        else:
            raise ValueError("Unexpected return type from get_message_async")

        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(chat_suggest[userid])])
            msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            waitque.remove(userid)
            await matcher.finish(reply_out(event, msg))
        else:
            waitque.remove(userid)
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
    
######################################################   
poe_clear_ = on_command(
    "poedump",
    aliases={
        "poe清除",
        "pd"
        },
    priority=4,
    block=False)
@poe_clear_.handle()
async def __poe_clear___(event: Event,matcher:Matcher):
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "机器人管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    
    if userid not in user_dict:
        await matcher.finish(reply_out(event, "你还没有创建任何bot"))
    botname = str(list(user_dict[userid]["now"].values())[0])
    nickname = str(list(user_dict[userid]["now"].keys())[0])
    is_cleared = await poe_clear(cookie_path,botname)
    if is_cleared:
        msg = f"成功清除了{nickname}的历史消息"
    else:
        msg = "出错了，多次错误请联系机器人主人"
    await matcher.finish(reply_out(event, msg))
    
######################################################
poe_switch = on_command(
    "poeswitch",
    aliases={
        "切换bot",
        "ps"
        },
    priority=4,
    block=False)
@poe_switch.handle()
async def __poe_switch__(matcher:Matcher,event: Event):
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    if userid not in user_dict:
        await matcher.finish(reply_out(event, "你还没创建任何bot"))
    bots = list(user_dict[userid]["all"].keys())
    bot_str = '\n'.join(str(bot) for bot in bots)
    # bot_truname = str(list(user_dict[userid]["now"].values())[0])
    nickname = str(list(user_dict[userid]["now"].keys())[0])
    if len(bots)==1:
        await matcher.finish(reply_out(event, f"当前只有一个bot:{nickname}"))
    msg = "你已经创建的的bot有：\n" + bot_str +f"\n当前使用的bot是{nickname}"
    await matcher.finish(reply_out(event, msg))

@poe_switch.got('nickname',prompt='请输入要切换的机器人名称')
async def __poe_switch____(matcher:Matcher,event: Event, infos: str = ArgStr("nickname")):
    userid = str(event.user_id)
    bots = list(user_dict[userid]["all"].keys())
    if infos in ["取消", "算了"]:
        await matcher.finish(reply_out(event, "终止切换"))
    infos = infos.split(" ")
    nickname = infos[0]
    if not (nickname in bots):
        await matcher.reject(reply_out(event, "输入信息有误，请检查后重新输入"))
    to_truename = user_dict[userid]["all"][nickname]
    del user_dict[userid]["now"]
    user_dict[userid]["now"] = {}
    user_dict[userid]["now"][nickname] = to_truename
    with open(user_path, 'w') as f:
        json.dump(user_dict, f)
    msg = f"已切换为{nickname}"
    await matcher.finish(reply_out(event, msg))
    
######################################################
poe_remove = on_command(
    "poeremove",
    aliases={
        "删除bot",
        "pr"
        },
    priority=4,
    block=False)
@poe_remove.handle()
async def __poe_remove__(matcher:Matcher,event: Event):
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    if userid not in user_dict:
        await matcher.finish(reply_out(event, "你还没创建任何bot"))
    bots = list(user_dict[userid]["all"].keys())
    bot_str = '\n'.join(str(bot) for bot in bots)
    # bot_truname = str(list(user_dict[userid]["now"].values())[0])
    nickname = str(list(user_dict[userid]["now"].keys())[0])
    msg = "你已经创建的的bot有：\n" + bot_str +f"\n当前使用的bot是{nickname}"
    await matcher.send(reply_out(event, msg))

@poe_remove.got('nickname',prompt='请输入要删除的机器人名称')
async def __poe_remove____(matcher:Matcher,event: Event, infos: str = ArgStr("nickname")):
    userid = str(event.user_id)
    bots = list(user_dict[userid]["all"].keys())
    if infos in ["取消", "算了"]:
        await matcher.finish(reply_out(event, "终止切换"))
    infos = infos.split(" ")
    nickname_delete = infos[0]
    nickname_now = str(list(user_dict[userid]["now"].keys())[0])
    if not (nickname_delete in bots): 
        await matcher.reject(reply_out(event, "输入信息有误，请检查后重新输入"))
    if nickname_delete == nickname_now:
        await matcher.finish(reply_out(event, "不能删除正在使用的bot哦"))
    del user_dict[userid]["all"][nickname_delete]
    with open(user_path, 'w') as f:
        json.dump(user_dict, f)
    await matcher.finish(reply_out(event, f"已删除{nickname_delete}"))
    
#####################################################

def is_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


poe_login = on_command(
    "poelogin",
    aliases={
        "poe登陆",
        "pl"
        },
    priority=4,
    block=False)

global_playwright = None
#创建一个全局的浏览器，在两个def中使用
async def create_playwright_instance():
    global global_playwright
    if not global_playwright:
        global_playwright = await async_playwright().start()
    return global_playwright

@poe_login.got('mail', prompt='请输入邮箱')
async def __poe_login____(event: Event, state: T_State, infos: str = ArgStr("mail")):
    global driver, global_playwright
    userid = str(event.user_id)
    if infos in ["取消", "算了"]:
        await poe_login.finish("终止登陆")
    infos = infos.split(" ")
    if len(infos) != 1 or not is_email(infos[0]):
        await poe_login.reject("你输入的邮箱有误，请重新输入")

    playwright = await create_playwright_instance()
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()

    state["playwright"] = playwright
    state["browser"] = browser
    state["context"] = context
    state["page"] = page

    is_submitted_email = await submit_email(page, infos[0])
    if is_submitted_email:
        await poe_login.send("填写邮箱成功")
    else:
        await poe_login.finish("出错了，可以换个邮箱试试，多次失败请自行提取cookie")

@poe_login.got('code', prompt='请输入验证码')
async def __poe_login____(event: Event, state: T_State, infos: str = ArgStr("code")):
    global is_cookie_exists, global_playwright
    if infos in ["取消", "算了"]:
        await poe_login.finish("终止登陆")
    infos = infos.split(" ")
    if len(infos) != 1 or len(infos[0]) != 6:
        await poe_login.finish("你输入的验证码有误，请重新登陆")

    playwright = state["playwright"]
    page = state["page"]
    browser = state["browser"]
    context = state["context"]
    is_submitted_code = await submit_code(page, infos[0], cookie_path)
    if is_submitted_code:
        await browser.close()
        is_cookie_exists = True
        await poe_login.finish("登陆成功")
    else:
        await browser.close()
        await poe_login.finish("出错了，可以换个邮箱试试，多次失败请自行提取cookie")
        
######################################################
poe_addprompt = on_command(
    "poeaddprompt",
    aliases={
        "添加预设",
        "pap"
        },
    priority=4,
    block=False)

@poe_addprompt.handle()
async def __poe_addprompt__(event: Event):
    userid = str(event.user_id)
    if userid not in superusers:
        await poe_addprompt.finish("你不是管理员哦")

@poe_addprompt.got('name',prompt='请输入预设名称')
async def __poe_addprompt____(event: Event, state: T_State, infos: str = ArgStr("name")):
    global driver
    userid = str(event.user_id)
    if infos in ["取消", "算了"]:
        await poe_addprompt.finish("终止添加")
    infos = infos.split(" ")
    if len(infos) != 1:
        await poe_addprompt.reject("你输入的信息有误，请检查后重新输入")
    state["key"] = infos[0]
    
@poe_addprompt.got('prompt',prompt='请输入预设')
async def __poe_addprompt____(event: Event, state: T_State, infos: str = ArgStr("prompt")):
    global driver
    userid = str(event.user_id)
    if infos in ["取消", "算了"]:
        await poe_addprompt.finish("终止添加")
    infos = infos.split(" ")
    name = state["key"]
    prompt = infos[0]
    # # 将更新后的字典写回到JSON文件中
    prompts_dict[name] = prompt
    with open(prompt_path, 'w') as f:
        json.dump(prompts_dict, f)
    await poe_addprompt.finish("成功添加prompt")
    
######################################################
poe_removeprompt = on_command(
    "poeremoveprompt",
    aliases={
        "删除预设",
        "prp"
        },
    priority=4,
    block=False)

@poe_removeprompt.handle()
async def __poe_removeprompt__(event: Event):
    userid = str(event.user_id)
    if userid not in superusers:
        await poe_removeprompt.finish("你不是管理员哦")
    else:
        str_prompts = str()
        for key, _ in prompts_dict.items():
            str_prompts += f"{key}\n"
        await poe_removeprompt.send(f"当前预设有：\n{str_prompts}")

@poe_removeprompt.got('name',prompt='请输入预设名称')
async def __poe_removeprompt____(event: Event, infos: str = ArgStr("name")):
    global driver
    userid = str(event.user_id)
    if infos in ["取消", "算了"]:
        await poe_removeprompt.finish("终止添加")
    infos = infos.split(" ")
    if len(infos) != 1 or infos[0] not in prompts_dict:
        await poe_removeprompt.reject("你输入的信息有误，请检查后重新输入")
    del prompts_dict[infos[0]]
    with open(prompt_path, 'w') as f:   
        json.dump(prompts_dict, f)
    await poe_removeprompt.finish(f"成功删除预设{infos[0]}")
    
######################################################
poe_help = on_command(
    "poehelp",
    aliases={
        "poe帮助",
        "ph"
        },
    priority=4,
    block=False)
@poe_help.handle()
async def __poe_help__(event: Event):
    msg = (
    "-poe功能大全\n"
    "--注意所有功能都是用户独立的，每个用户只能操作自己的内容\n"
    "--所有分步操作都可以用 取消 或 算了来终止,并且支持错误重输\n"
    "--如果未创建机器人，对话命令将默认创建gpt3.5\n"
    "--可以直接回复机器人给你的回答来继续对话，无需命令\n"
    "--可以使用数字索引来使用建议回复\n\n"
    "--以下命令前面全部要加 / \n"
    "~对话:poetalk / ptalk / pt\n"
    "~清空历史对话:poedump / pdump / pd\n"
    "~创建机器人:poecreate / 创建bot / pc\n"
    "~删除机器人:poeremove / 删除bot / pr\n"
    "~切换机器人:poeswitch / 切换bot / ps\n\n"
    "************************\n"
    "--以下功能仅限poe管理员使用\n"
    "~登录:poelogin / plogin / pl\n"
    "~添加预设:poeaddprompt / 添加预设 / pap\n"
    "~删除预设:poeremoveprompt / 删除预设 / prp"
    )
    await poe_help.finish(msg)
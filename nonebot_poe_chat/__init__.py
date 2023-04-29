import datetime
import json,asyncio
from typing import Annotated
from nonebot.plugin import on_command, on, on_message 
from nonebot.params import ArgStr, CommandArg, RawCommand
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageEvent,MessageSegment
from nonebot.internal.rule import Rule
from nonebot import logger
from .config import Config
from .poe_func import reply_out,generate_uuid,generate_random_string,is_email,delete_messages,mdlink_2_str,is_useable
from .poe_api import poe_chat,poe_create,poe_clear,submit_email, submit_code
from .txt2img import Txt2Img
from .pwframework import PlaywrightFramework
#初始化两个需要使用的实例
pwfw = PlaywrightFramework()
txt2img = Txt2Img()

#一些配置
config = Config()
user_dict = config.user_dict
prompts_dict = config.prompts_dict
superuser_dict = config.superuser_dict
user_path = config.user_path
prompt_path = config.prompt_path
cookie_path = config.cookie_path
superuser_path = config.superuser_dict_path
suggest_able = config.suggest_able
superusers = config.superusers
blacklist = config.blacklist
is_cookie_exists = config.is_cookie_exists
is_pic_able = config.pic_able
is_url_able = config.url_able
is_qr_able = config.qr_able
######################################################
creat_lock = asyncio.Lock()        
create_msgs = {}
create_pages = {}
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
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    create_msgs[userid] = []
    state["user_id"] = userid
    if len(prompts_dict)>0:
        str_prompts = str()
        for key, _ in prompts_dict.items():
            str_prompts += f"{key}\n"
        # create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, f"当前预设有：\n{str_prompts}")))
        msg = f"当前预设有：\n{str_prompts}\n请输入\n1.机器人名称,\n2.基础模型选项，可选项为（gpt3_5输入1,claude输入2）,\n3.自定义预设（预设内容中间不要有空格） 或 \".\" + 可用本地预设名\n三个参数中间用空格隔开\n最终格式示例:\n示例一：chat 2 一个智能助理\n示例二： chat 1 .默认\n输入取消 或 算了可以终止创建"
        create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, msg)))
    else:
        create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, "")))
        msg = f"当前没有可用本地预设\n\n请输入\n1.机器人名称,\n2.基础模型选项，可选项为（gpt3_5输入1,claude输入2）,\n3.自定义预设（预设内容中间不要有空格） 或 \".\" + 可用本地预设名\n三个参数中间用空格隔开\n最终格式示例:\n示例一：chat 2 一个智能助理\n示例二： chat 1 .默认\n输入取消 或 算了可以终止创建"
        create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, msg)))

@poe_create_.got('model')
async def __poe_create___(bot: Bot,matcher: Matcher,event: Event,state: T_State, infos: str = ArgStr("model")):
    if infos in ["取消", "算了"]:
        create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, "取消创建")))
        await asyncio.sleep(1)
        await delete_messages(bot,str(event.user_id),create_msgs)
        await poe_create_.finish()
    infos = infos.split(" ",2)
    if not (len(infos) == 3 and infos[1] in ['1', '2']):
        create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, "输入信息有误，请检查后重新输入")))
        await poe_create_.reject()
    #获取创建所需信息
    userid = str(state['user_id'])
    nickname = str(infos[0])
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    truename = str(generate_uuid(str(userid + current_time_str +infos[0])))
    prompt = str(infos[2])
    bot_index = str(infos[1])
    if prompt.startswith("."):
        prompt_name = prompt[1:]
        if prompt_name in prompts_dict:
            prompt = prompts_dict[prompt_name]
        else:
            create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, "输入的本地预设名不正确，请重新输入")))
            await poe_create_.reject()
    
    if not userid in user_dict:
        user_dict[userid] = {}
    if 'all' not in user_dict[userid]:
        user_dict[userid]['all'] = {}
    if 'now' not in user_dict[userid]:
        user_dict[userid]['now'] = {}
    #查看对应用户下是不是有重名的bot
    if  nickname in user_dict[userid]['all']:
        create_msgs[str(event.user_id)].append(await matcher.send(reply_out(event, "已经有同名的bot了，换一个名字重新输入吧")))
        await poe_create_.reject()
    else:
        if creat_lock.locked():
            waitmsg = await matcher.send(reply_out(event, "有人正在创建中，稍后自动为你创建"))
        async with creat_lock:
            create_pages[userid] = await pwfw.new_page()
            is_created = await poe_create(page=create_pages[userid],botname=truename,base_bot_index=int(bot_index),prompt=prompt)
            try:
                await create_pages[userid].close()
            except:
                pass
            del create_pages[userid]
            if is_created:
                # # 将更新后的字典写回到JSON文件中
                user_dict[userid]['all'][nickname] = truename
                
                if user_dict[userid]['now']:
                    user_dict[userid]['now'] = {}
                user_dict[userid]['now'][nickname] = truename
                
                with open(user_path, 'w') as f:
                    json.dump(user_dict, f)
                try:
                    await bot.delete_msg(message_id=waitmsg['message_id'])
                except:
                    pass
                await matcher.send(reply_out(event, "创建成功并切换到新建bot"))
                await asyncio.sleep(1)
                await delete_messages(bot,userid,create_msgs)
                await poe_switch.finish()
            else: 
                await matcher.send(reply_out(event, "出错了，多次出错请联系机器人管理员"))
                await asyncio.sleep(1)
                await delete_messages(bot,userid,create_msgs)
                await poe_switch.finish()



######################################################    

chat_lock = asyncio.Semaphore(3)
#像这样的全局变量都是临时的
chat_suggest = {}
last_messageid = {}
chat_pages = {}

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
    global chat_lock,chat_suggest,last_messageid,chat_pages,create_pages
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if userid not in user_dict:
        random = generate_random_string()
        truename = str(generate_uuid(str(userid + random)))
        prompt = prompts_dict[superuser_dict["auto_default"]]
        create_pages[userid] = await pwfw.new_page()
        is_created = await poe_create(create_pages[userid],truename,1,prompt)
        try:
            await create_pages[userid].close()
        except:
            pass
        del create_pages[userid]
        
        if is_created:
            user_dict[userid] = {}        
            user_dict[userid]['all'] = {}
            user_dict[userid]['all']["default"] = truename
            user_dict[userid]['now'] = {}
            user_dict[userid]['now']["default"] = truename
            with open(user_path, 'w') as f:
                json.dump(user_dict, f)
            await matcher.send(reply_out(event, "自动创建gpt3.5成功"))
        else:
            await matcher.finish(reply_out(event, "自动创建gpt3.5失败，多次失败请联系机器人管理员"))
    if userid in chat_suggest and len(str(args[0])) == 1 and str(args[0]) in ['1','2','3','4']:
        text = chat_suggest[userid][int(str(args[0]))-1]
    else:
        try:
            text = str(args[0])
        except:
            await matcher.finish()
    botname = str(list(user_dict[userid]["now"].values())[0])
    if userid in chat_pages:
        await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后再发送"))
    if chat_lock.locked():
        await matcher.send(reply_out(event, "请稍等,你前面已有3个用户,你的回答稍后就来"))
    async with chat_lock:
        chat_pages[userid] = await pwfw.new_page()
        result = await poe_chat(botname, text, chat_pages[userid])
        if isinstance(result, tuple):
            last_answer, chat_suggest[userid] = result
            is_successful = True
        elif isinstance(result, str):
            if "banned" == result:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                await matcher.finish(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
        elif isinstance(result, bool):
            is_successful = result
        else:
            #这个应该不可能出现
            raise ValueError("Unexpected return type from get_message_async")

        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(chat_suggest[userid])])
            if suggest_able:
                msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            else:
                msg = f"{last_answer}\n"
            if is_pic_able:
                if is_qr_able:
                    pic,url = await txt2img.draw(title=" ",text=msg)
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    if is_url_able:
                        last_messageid[userid] = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        last_messageid[userid] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
                else:
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    pic,_ = await txt2img.draw(title=" ",text=msg)
                    last_messageid[userid] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
            else:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                last_messageid[userid] = await matcher.send(reply_out(event, msg))
                await matcher.finish()
        else:
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))

######################################################
#判断是不是同一个对话中
async def _is_reply_(event:MessageEvent,bot:Bot):
    if bool(event.reply):
        bot_id = bot.self_id
        reply = event.reply
        user_id = str(event.user_id)
        sender_id = str(reply.sender.user_id)
        try:
            if sender_id == bot_id and user_id in chat_suggest and last_messageid[user_id]["message_id"]==reply.message_id:
                return True
        except:
            return False
is_reply = Rule(_is_reply_)

_poe_continue_ = on(rule=is_reply)
@_poe_continue_.handle()
async def __poe_continue__(matcher: Matcher,event:MessageEvent):
    global chat_lock,last_messageid,chat_pages
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    raw_message = str(event.message)
    if userid in chat_pages:
        await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后在发送"))
        
    if raw_message in ["清除对话","清空对话","清除历史","清空历史","poedump","pdump","pd"]:
        botname = str(list(user_dict[userid]["now"].keys())[0])
        truename = str(list(user_dict[userid]["now"].values())[0])
        async with chat_lock:
            chat_pages[userid] = await pwfw.new_page()
            is_cleared = await poe_clear(chat_pages[userid],truename)
            del chat_pages[userid]
            if is_cleared:
                msg = f"成功清除了{botname}的历史消息"
            else:
                msg = "出错了，多次错误请联系机器人主人"
            await matcher.finish(reply_out(event, msg)) 
    
    if userid in chat_suggest and len(raw_message) == 1 and raw_message in ['1','2','3','4']:
            text = chat_suggest[userid][int(raw_message)-1]
    else:
        text = raw_message

    if chat_lock.locked():
        await matcher.send(reply_out(event, '请稍等,你前面已有3个用户'))
        
    botname = str(list(user_dict[userid]["now"].values())[0])
        
    async with chat_lock:
        chat_pages[userid] = await pwfw.new_page()
        result = await poe_chat(botname, text, chat_pages[userid])
        if isinstance(result, tuple):
            last_answer, chat_suggest[userid] = result
            is_successful = True
        elif isinstance(result, str):
            if "banned" == result:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                await matcher.finish(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
        elif isinstance(result, bool):
            is_successful = result
        else:
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            raise ValueError("Unexpected return type from get_message_async")
        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(chat_suggest[userid])])
            if suggest_able:
                msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            else:
                msg = f"{last_answer}\n"
            if is_pic_able:
                if is_qr_able:
                    pic,url = await txt2img.draw(title=" ",text=msg)
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    if is_url_able:
                        last_messageid[userid] = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        last_messageid[userid] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
                else:
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    pic,_ = await txt2img.draw(title=" ",text=msg)
                    last_messageid[userid] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
            else:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                last_messageid[userid] = await matcher.send(reply_out(event, msg))
                await matcher.finish()
        else:
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
######################################################
neeva_lock = asyncio.Lock()
poe_neeva_ = on_command(
    "poeneeva",
    aliases={
        "pneeva",
        "pn"
        },
    priority=1,
    block=False)
@poe_neeva_.handle()
async def __poe_neeva__(matcher:Matcher,event: Event, args: Message = CommandArg()):
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    global last_messageid
    try:
        text = str(args[0])
    except:
        await matcher.finish()
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if neeva_lock.locked():
        await matcher.send(reply_out(event, "请稍等,正有一个人在使用ai搜索"))
    async with neeva_lock:
        neeva_page= await pwfw.new_page()
        result = await poe_chat("NeevaAI", text, neeva_page,nosuggest=True)
        
        if isinstance(result, tuple):
            last_answer,_ = result
            is_successful = True
        elif isinstance(result, bool):
            is_successful = result
        else:
            raise ValueError("Unexpected return type from get_message_async")

        if is_successful:
            msg = f"{last_answer}\n"
            msg = await mdlink_2_str(msg)
            try:
                await neeva_page.close()
            except:
                pass
            last_messageid[userid] = await matcher.send(reply_out(event, msg))
            await matcher.finish()
        else:
            try:
                await neeva_page.close()
            except:
                pass
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
######################################################   
gpt_share_lock = asyncio.Lock()
gpt_user_number = 0
#先留着，后面用再说
gpt_share_lastmsgid = str

gpt_share_suggests = []
poe_share_gpt_ = on_command(
    "poesharegpt",
    aliases={
        "psharegpt",
        "psg"
        },
    priority=1,
    block=False)
@poe_share_gpt_.handle()
async def __poe_share_gpt__(bot:Bot,matcher:Matcher,event: Event, args: Message = CommandArg()):
    global gpt_share_lastmsgid,gpt_share_suggests,gpt_user_number
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    try:
        text = str(args[0])
    except:
        await matcher.finish()
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if gpt_share_lock.locked() and gpt_user_number <= 4:
        gpt_waitmsg = await matcher.send(reply_out(event, "还没回答完上一个问题，稍等马上回复你"))
    if gpt_user_number>4:
        await matcher.finish(reply_out(event, "我还有5个问题没回答呢，你等会再用吧"))
    gpt_user_number += 1
    async with gpt_share_lock:
        gpt_share_page = await pwfw.new_page()
        result = await poe_chat("ChatGPT", text, gpt_share_page)
        if isinstance(result, tuple):
            last_answer, gpt_share_suggests = result
            is_successful = True
        elif isinstance(result, bool):
            is_successful = result
        else:
            try:
                await gpt_share_page.close()
            except:
                pass
            raise ValueError("Unexpected return type from get_message_async")
        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(gpt_share_suggests)])
            if suggest_able:
                msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            else:
                msg = f"{last_answer}\n"
            if is_pic_able:
                if is_qr_able:
                    pic,url = await txt2img.draw(title=" ",text=msg)
                    try:
                        await gpt_share_page.close()
                    except:
                        pass
                    if is_url_able:
                        gpt_share_lastmsgid = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        gpt_share_lastmsgid = await matcher.send(reply_out(event, pic))
                    try:
                        await bot.delete_msg(message_id=gpt_waitmsg['message_id'])
                    except:
                        pass
                    gpt_user_number -= 1
                    await matcher.finish()
                else:
                    try:
                        await gpt_share_page.close()
                    except:
                        pass
                    pic,_ = await txt2img.draw(title=" ",text=msg)
                    gpt_share_lastmsgid = await matcher.send(reply_out(event, pic))
                    try:
                        await bot.delete_msg(message_id=gpt_waitmsg['message_id'])
                    except:
                        pass
                    gpt_user_number -= 1
                    await matcher.finish()
            else:
                try:
                    await gpt_share_page.close()
                except:
                    pass
                gpt_share_lastmsgid = await matcher.send(reply_out(event, msg))
                try:
                    await bot.delete_msg(message_id=gpt_waitmsg['message_id'])
                except:
                    pass
                gpt_user_number -= 1
                await matcher.finish()
        else:
            try:
                await gpt_share_page.close()
            except:
                pass
            gpt_user_number -= 1
            try:
                await bot.delete_msg(message_id=gpt_waitmsg['message_id'])
            except:
                pass
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
######################################################   
poe_gpt_clear_ = on_command(
    "poegptdump",
    aliases={
        "poegpt清除",
        "pgd"
        },
    priority=4,
    block=False)
@poe_gpt_clear_.handle()
async def __poe_gpt_clear___(event: Event,matcher:Matcher):
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "机器人管理员还没填写可用的poe_cookie或登陆"))
    if gpt_share_lock.locked():
        await matcher.finish(reply_out(event, "我还有一个问题没回答完呢"))
    gpt_clear_page = await pwfw.new_page()
    is_cleared = await poe_clear(page=gpt_clear_page,botname="ChatGPT")
    try:
        await gpt_clear_page.close()
    except:
        pass
    if is_cleared:
        msg = f"成功清除了ChatGPT的历史消息"
    else:
        msg = "出错了，多次错误请联系机器人主人"
    await matcher.finish(reply_out(event, msg))  
######################################################   
claude_share_lock = asyncio.Lock()
claude_user_number = 0
#先留着，后面用再说
claude_share_lastmsgid = str

claude_share_suggests = []
poe_share_claude_ = on_command(
    "poeshareclaude",
    aliases={
        "pshareclaude",
        "psc"
        },
    priority=1,
    block=False)
@poe_share_claude_.handle()
async def __poe_share_claude__(bot:Bot,matcher:Matcher,event: Event, args: Message = CommandArg()):
    global claude_share_lastmsgid,claude_share_suggests,claude_user_number
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    try:
        text = str(args[0])
    except:
        await matcher.finish()
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if claude_share_lock.locked() and claude_user_number <= 4:
        claude_waitmsg = await matcher.send(reply_out(event, "还没回答完上一个问题，稍等马上回复你"))
    if claude_user_number>4:
        await matcher.finish(reply_out(event, "我还有5个问题没回答呢，你等会再用吧"))
    claude_user_number += 1
    async with claude_share_lock:
        claude_share_page = await pwfw.new_page()
        result = await poe_chat("Claude-instant", text, claude_share_page)
        if isinstance(result, tuple):
            last_answer, claude_share_suggests = result
            is_successful = True
        elif isinstance(result, bool):
            is_successful = result
        else:
            try:
                await claude_share_page.close()
            except:
                pass
            raise ValueError("Unexpected return type from get_message_async")
        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(claude_share_suggests)])
            if suggest_able:
                msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            else:
                msg = f"{last_answer}\n"
            if is_pic_able:
                if is_qr_able:
                    pic,url = await txt2img.draw(title=" ",text=msg)
                    try:
                        await claude_share_page.close()
                    except:
                        pass
                    if is_url_able:
                        claude_share_lastmsgid = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        claude_share_lastmsgid = await matcher.send(reply_out(event, pic))
                    try:
                        await bot.delete_msg(message_id=claude_waitmsg['message_id'])
                    except:
                        pass
                    claude_user_number -= 1
                    await matcher.finish()
                else:
                    try:
                        await claude_share_page.close()
                    except:
                        pass
                    pic,_ = await txt2img.draw(title=" ",text=msg)
                    last_messageid[userid] = await matcher.send(reply_out(event, pic))
                    try:
                        await bot.delete_msg(message_id=claude_waitmsg['message_id'])
                    except:
                        pass
                    claude_user_number -= 1
                    await matcher.finish()
            else:
                try:
                    await claude_share_page.close()
                except:
                    pass
                claude_share_lastmsgid = await matcher.send(reply_out(event, msg))
                try:
                    await bot.delete_msg(message_id=claude_waitmsg['message_id'])
                except:
                    pass
                claude_user_number -= 1
                await matcher.finish()
        else:
            try:
                await claude_share_page.close()
            except:
                pass
            claude_user_number -= 1
            try:
                await bot.delete_msg(message_id=claude_waitmsg['message_id'])
            except:
                pass
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
######################################################   
poe_claude_clear_ = on_command(
    "poeclaudedump",
    aliases={
        "poeclaude清除",
        "pcd"
        },
    priority=4,
    block=False)
@poe_claude_clear_.handle()
async def __poe_claude_clear___(event: Event,matcher:Matcher):
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "机器人管理员还没填写可用的poe_cookie或登陆"))
    if claude_share_lock.locked():
        await matcher.finish(reply_out(event, "我还有一个问题没回答完呢"))
    claude_clear_page = await pwfw.new_page()
    is_cleared = await poe_clear(page=claude_clear_page,botname="Claude-instant")
    try:
        await claude_clear_page.close()
    except:
        pass
    if is_cleared:
        msg = f"成功清除了Claude-instant的历史消息"
    else:
        msg = "出错了，多次错误请联系机器人主人"
    await matcher.finish(reply_out(event, msg))
######################################################
clear_pages = {}
poe_clear_ = on_command(
    "poedump",
    aliases={
        "poe清除",
        "pd"
        },
    priority=4,
    block=False)
@poe_clear_.handle()
async def __poe_clear___(event: Event,matcher:Matcher,args: Message = CommandArg()):
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "机器人管理员还没填写可用的poe_cookie或登陆"))
    if userid not in user_dict:
        await matcher.finish(reply_out(event, "你还没有创建任何bot"))
    if userid in chat_pages:
        await matcher.finish(reply_out(event, "你现在有一个回话在进行中，不能清除历史记录"))
    try:
        nickname = str(args[0])
        if nickname not in user_dict[userid]["all"]:
            await matcher.finish("没有这个机器人呢")
        botname = user_dict[userid]["all"][nickname]
    except:
        botname = str(list(user_dict[userid]["now"].values())[0])
        nickname = str(list(user_dict[userid]["now"].keys())[0])
    clear_pages[userid] = await pwfw.new_page()
    is_cleared = await poe_clear(page=clear_pages[userid],botname=botname)
    try:
        await clear_pages[userid].close()
    except:
        pass
    del clear_pages[userid] 
    if is_cleared:
        msg = f"成功清除了{nickname}的历史消息"
    else:
        msg = "出错了，多次错误请联系机器人主人"
    await matcher.finish(reply_out(event, msg))
    
######################################################  
switch_msgs = {}
poe_switch = on_command(
    "poeswitch",
    aliases={
        "切换bot",
        "ps"
        },
    priority=4,
    block=False)
@poe_switch.handle()
async def __poe_switch__(bot:Bot ,matcher:Matcher,event: Event,args: Message = CommandArg()):
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    switch_msgs[userid] = []
    if userid not in user_dict:
        await matcher.finish(reply_out(event, "你还没创建任何bot"))
    try:
        raw_text = str(args[0])
    except:
        raw_text = False
    if raw_text:
        if raw_text not in user_dict[userid]["all"]:
            await matcher.finish("没有这个机器人呢")
        botname = user_dict[userid]["all"][raw_text]
        del user_dict[userid]["now"]
        user_dict[userid]["now"] = {}
        user_dict[userid]["now"][raw_text] = botname
        with open(user_path, 'w') as f:
            json.dump(user_dict, f)
        msg = f"已切换为{raw_text}"
        await matcher.send(reply_out(event, msg))
        await asyncio.sleep(1)
        await delete_messages(bot,userid,switch_msgs)
        await poe_switch.finish()
        
    bots = list(user_dict[userid]["all"].keys())
    bot_str = '\n'.join(str(bot) for bot in bots)
    # bot_truname = str(list(user_dict[userid]["now"].values())[0])
    nickname = str(list(user_dict[userid]["now"].keys())[0])
    if len(bots)==1:
        await matcher.finish(reply_out(event, f"当前只有一个bot:{nickname},无法切换"))
    msg = "你已经创建的的bot有：\n" + bot_str +f"\n当前使用的bot是{nickname}\n\n请输入要切换的机器人名称\n输入取消 或 算了可以终止创建"
    switch_msgs[userid].append(await matcher.send(reply_out(event, msg)))

@poe_switch.got('nickname')
async def __poe_switch____(bot:Bot,matcher:Matcher,event: Event, infos: str = ArgStr("nickname")):
    userid = str(event.user_id)
    bots = list(user_dict[userid]["all"].keys())
    if infos in ["取消", "算了"]:
        switch_msgs[userid].append(await matcher.send(reply_out(event, "中断切换")))
        await asyncio.sleep(1)
        await delete_messages(bot,userid,switch_msgs)
        await poe_switch.finish()
    infos = infos.split(" ")
    nickname = infos[0]
    if not (nickname in bots):
        switch_msgs[userid].append(await matcher.send(reply_out(event, "输入信息有误，请检查后重新输入")))
        await poe_switch.reject()
    to_truename = user_dict[userid]["all"][nickname]
    del user_dict[userid]["now"]
    user_dict[userid]["now"] = {}
    user_dict[userid]["now"][nickname] = to_truename
    with open(user_path, 'w') as f:
        json.dump(user_dict, f)
    msg = f"已切换为{nickname}"
    await matcher.send(reply_out(event, msg))
    await asyncio.sleep(1)
    await delete_messages(bot,userid,switch_msgs)
    await poe_switch.finish()
remove_list = {}    
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
async def __poe_remove__(bot:Bot,matcher:Matcher,event: Event, args: Message = CommandArg()):
    if not is_cookie_exists:
        await matcher.finish(reply_out(event, "管理员还没填写可用的poe_cookie或登陆"))
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    remove_list[userid] = []
    if userid not in user_dict:
        await matcher.finish(reply_out(event, "你还没创建任何bot"))
    try:
        raw_text = str(args[0])
    except:
        raw_text = False
    if raw_text:
        nickname = str(args[0])
        if nickname not in user_dict[userid]["all"]:
            await matcher.finish(reply_out(event, "没有这个机器人呢"))
        if nickname == str(list(user_dict[userid]["now"].keys())[0]):
            await matcher.finish(reply_out(event, "不能删除正在使用的bot哦"))
        del user_dict[userid]["all"][nickname]
        with open(user_path, 'w') as f:
            json.dump(user_dict, f)
        msg = f"已删除{nickname}"
        await matcher.send(reply_out(event, msg))
        await asyncio.sleep(1)
        await delete_messages(bot,userid,switch_msgs)
        await poe_switch.finish()
    
    bots = list(user_dict[userid]["all"].keys())
    if len(bots) == 1:
        await matcher.finish(reply_out(event, f"当前只有一个机器人:{bots[0]},不能删除"))
    bot_str = '\n'.join(str(bot) for bot in bots)
    # bot_truname = str(list(user_dict[userid]["now"].values())[0])
    nickname = str(list(user_dict[userid]["now"].keys())[0])
    msg = "你已经创建的的bot有：\n" + bot_str +f"\n当前使用的bot是{nickname}\n\n请输入要删除的机器人名称\n输入取消 或 算了可以终止创建"
    remove_list[userid].append(await matcher.send(reply_out(event, msg)))

@poe_remove.got('nickname')
async def __poe_remove____(bot:Bot,matcher:Matcher,event: Event, infos: str = ArgStr("nickname")):
    userid = str(event.user_id)
    bots = list(user_dict[userid]["all"].keys())
    if infos in ["取消", "算了"]:
        remove_list[userid].append(await matcher.send(reply_out(event, "终止切换")))
        await asyncio.sleep(1)
        await delete_messages(bot,userid,remove_list)
        await matcher.finish()
    infos = infos.split(" ")
    nickname_delete = infos[0]
    nickname_now = str(list(user_dict[userid]["now"].keys())[0])
    if not (nickname_delete in bots): 
        remove_list[userid].append(await matcher.send(reply_out(event, "输入信息有误，请检查后重新输入")))
        await poe_remove.reject()
    if nickname_delete == nickname_now:
        remove_list[userid].append(await matcher.send(reply_out(event, "不能删除正在使用的bot哦")))
        await asyncio.sleep(1)
        await delete_messages(bot,userid,remove_list)
        await poe_remove.finish()
    del user_dict[userid]["all"][nickname_delete]
    with open(user_path, 'w') as f:
        json.dump(user_dict, f)
    await matcher.send(reply_out(event, f"已删除{nickname_delete}"))
    await delete_messages(bot, userid, remove_list)
    await matcher.finish()
#####################################################

poe_login = on_command(
    "poelogin",
    aliases={
        "poe登陆",
        "pl"
        },
    priority=4,
    block=False)

@poe_login.got('mail', prompt='请输入邮箱')
async def __poe_login____(event: Event, state: T_State, infos: str = ArgStr("mail")):
    if infos in ["取消", "算了"]:
        await poe_login.finish("终止登陆")
    infos = infos.split(" ")
    if len(infos) != 1 or not is_email(infos[0]):
        await poe_login.reject("你输入的邮箱有误，请重新输入")
    page = await pwfw.new_page()
    state["page"] = page
    is_submitted_email = await submit_email(page, infos[0])
    if is_submitted_email:
        await poe_login.send("填写邮箱成功")
    else:
        await poe_login.finish("出错了，可以换个邮箱试试，多次失败请自行提取cookie")

@poe_login.got('code', prompt='请输入验证码')
async def __poe_login____(event: Event, state: T_State, infos: str = ArgStr("code")):
    global is_cookie_exists
    if infos in ["取消", "算了"]:
        await poe_login.finish("终止登陆")
    infos = infos.split(" ")
    if len(infos) != 1 or len(infos[0]) != 6:
        await poe_login.finish("你输入的验证码有误，请重新登陆")
    page = state["page"]
    is_submitted_code = await submit_code(page, infos[0], cookie_path)
    if is_submitted_code:
        try:
            await page.close()
        except:
            pass
        is_cookie_exists = True
        await poe_login.finish("登陆成功")
    else:
        try:
            await page.close()
        except:
            pass
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
async def __poe_addprompt__(matcher:Matcher,event: Event):
    userid = str(event.user_id)
    if userid not in superusers:
        await poe_addprompt.finish("你不是管理员哦")

@poe_addprompt.got('name',prompt='请输入预设名称\n输入取消 或 算了可以终止创建')
async def __poe_addprompt____(event: Event, state: T_State, infos: str = ArgStr("name")):
    global driver
    userid = str(event.user_id)
    if infos in ["取消", "算了"]:
        await poe_addprompt.finish("终止添加")
    infos = infos.split(" ")
    if len(infos) != 1:
        await poe_addprompt.reject("你输入的信息有误，请检查后重新输入")
    state["key"] = infos[0]
    
@poe_addprompt.got('prompt',prompt='请输入预设\n输入取消 或 算了可以终止创建')
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
######################################################
poe_auto_change_prompt = on_command(
    "poechangeprompt",
    aliases={
        "切换自动预设",
        "pcp"
        },
    priority=4,
    block=False)

@poe_auto_change_prompt.handle()
async def __poe_auto_change_prompt__(event: Event):
    userid = str(event.user_id)
    if userid not in superusers:
        await poe_auto_change_prompt.finish("你不是管理员哦")
    now = superuser_dict["auto_default"]
    str_prompts = str()
    for key, _ in prompts_dict.items():
        str_prompts += f"{key}\n"
    await poe_auto_change_prompt.send(f"现在的自动创建预设是{now}\n当前可用预设有：\n{str_prompts}")
@poe_auto_change_prompt.got('name',prompt='请输入要切换到的预设名称\n输入取消 或 算了可以终止创建')
async def __poe_auto_change_prompt____(event: Event, state: T_State, infos: str = ArgStr("name")):
    if infos in ["取消", "算了"]:
        await poe_auto_change_prompt.finish("终止切换")

    infos = infos.split(" ")
    if len(infos) != 1:
        await poe_auto_change_prompt.reject("你输入的信息有误，请检查后重新输入")
    # # 将更新后的字典写回到JSON文件中
    superuser_dict["auto_default"] = infos[0]
    with open(superuser_path, 'w') as f:
        json.dump(superuser_dict, f)
    await poe_auto_change_prompt.finish("成功切换默认自动创建prompt")
    
######################################################
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

@poe_removeprompt.got('name',prompt='请输入要删除的预设名称\n输入取消 或 算了可以终止创建')
async def __poe_removeprompt____(event: Event, infos: str = ArgStr("name")):
    global driver
    userid = str(event.user_id)
    if infos in ["取消", "算了"]:
        await poe_removeprompt.finish("终止删除")
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
async def __poe_help__(bot: Bot,matcher:Matcher,event: Event):
    userid = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    msg = (
    "共享的机器人供多人共同使用\n"  
    "用户隔离的机器人每个人都是相互独立的\n"  
    "--以下命令前面全部要加 / \n"
    "************************\n"
    "--以下命令均支持用户隔离\n"
    "~对话:poetalk / ptalk / pt + 你要询问的内容\n"
    "  >如果没创建机器人，对话将自动创建默认机器人\n"
    "  >可以通过回复机器人给你的最后一个回答来继续对话，而无需命令\n"
    "  >可以回复 \"(清除/清空)(对话/历史)\"或\"pd\",\"poedump\",\"pdump\"来清空对话\n"
    "  >可以通过建议回复的数字索引来使用建议回复\n"
    "~创建机器人:poecreate / 创建bot / pc\n"
    "~删除机器人:poeremove / 删除bot / pr (+ 机器人名称)\n"
    "~切换机器人:poeswitch / 切换bot / ps (+ 机器人名称)\n"
    "~清空当前机器人历史对话:poedump / pdump / pd\n\n"
    "~指定对话:/ + 你的机器人的名字 (+ 空格) + 你要询问的内容\n"
    "  >可以通过回复机器人给你的最后一个回答来继续对话，而无需命令\n"
    "  >可以回复 \"(清除/清空)(对话/历史)\"或\"pd\",\"poedump\",\"pdump\"来清空对话\n"
    "  >可以通过建议回复的数字索引来使用建议回复\n"
    "************************\n"
    "--以下命令均是多用户共享的\n"
    "~NeevaAI搜索引擎:poeneeva / pneeva / pn + 你要搜索的内容\n"
    " >搜索引擎返回的是链接及标题\n"
    "~共享的gpt对话:poesharegpt / psharegpt / psg + 你要询问的内容\n"
    "~清空共享的gpt的对话历史:poegptdump / poegpt清除 / pgd\n"
    "~共享的claude对话:poeshareclaude / pshareclaude / psc + 你要询问的内容\n"
    "~清空共享的claude的对话历史:poeclaudedump / poeclaude清除 / pcd\n"
    "************************\n"
    "--以下功能仅限poe管理员使用\n"
    "~登录:poelogin / plogin / pl\n"
    "~添加预设:poeaddprompt / 添加预设 / pap\n"
    "~删除预设:poeremoveprompt / 删除预设 / prp\n"
    "~切换自动创建的默认预设:poechangeprompt / 切换自动预设 / pcp"
    )
    if is_pic_able:
        pic, url= await txt2img.draw(title="poe功能大全",text=msg)
        helpmsg = await poe_help.send(MessageSegment.image(pic))
    else:
        helpmsg = await poe_help.send(MessageSegment.text("*poe功能大全\n") + MessageSegment.text(msg))
    await asyncio.sleep(60)
    await bot.delete_msg(message_id=helpmsg['message_id'])
    await poe_help.finish()
######################################################
last_active_messageid = {}
active_chat_suggest = {}
poe_active = on_message(priority=1,block=False)
@poe_active.handle()
async def poe_activate_(matcher:Matcher,event: MessageEvent):
    global last_active_messageid,active_chat_suggest
    if not is_useable(event):
        await matcher.finish()
    userid = event.get_user_id()
    msg = event.get_plaintext()
    bot = None
    
    if userid in chat_pages:
        await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后再发送"))
        
    if chat_lock.locked():
        await matcher.send(reply_out(event, "请稍等,你前面已有3个用户,你的回答稍后就来"))
        
    try:
        bots = list(user_dict[userid]["all"].keys())
        for each in bots:
            if "/" + each in msg:
                bot = each
                botname = user_dict[userid]["all"][each]
                break
    except:
        matcher.finish()
        
    if not bot:
        await matcher.finish()
    msg = msg.replace("/" + bot + ' ',"").replace("/" + bot,"")
    
    if msg in ["清除对话","poedump","pdump","pd"]:
        async with chat_lock:
            chat_pages[userid] = await pwfw.new_page()
            is_cleared = await poe_clear(chat_pages[userid],botname)
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            if is_cleared:
                msg = f"成功清除了{bot}的历史消息"
            else:
                msg = "出错了，多次错误请联系机器人主人"
            await matcher.finish(reply_out(event, msg)) 
    
    if userid in active_chat_suggest and len(msg) == 1 and msg in ['1','2','3','4']:
        text = active_chat_suggest[userid][bot][int(msg)-1]
    else:
        text = msg
     
    if userid not in active_chat_suggest:
        active_chat_suggest[userid] = {}
    if userid not in last_active_messageid:
        last_active_messageid[userid] = {}
    async with chat_lock:
        chat_pages[userid] = await pwfw.new_page()
        result = await poe_chat(botname, text, chat_pages[userid])
        if isinstance(result, tuple):
            last_answer, active_chat_suggest[userid][bot] = result
            is_successful = True
        elif isinstance(result, str):
            if "banned" == result:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                await matcher.finish(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
        elif isinstance(result, bool):
            is_successful = result
        else:
            #这个应该不可能出现
            raise ValueError("Unexpected return type from get_message_async")

        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(active_chat_suggest[userid][bot])])
            if suggest_able:
                msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            else:
                msg = f"{last_answer}\n"
            if is_pic_able:
                if is_qr_able:
                    pic,url = await txt2img.draw(title=" ",text=msg)
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    if is_url_able:
                        last_active_messageid[userid][bot] = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        last_active_messageid[userid][bot] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
                else:
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    pic,_ = await txt2img.draw(title=" ",text=msg)
                    last_active_messageid[userid][bot] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
            else:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                last_active_messageid[userid][bot] = await matcher.send(reply_out(event, msg))
                await matcher.finish()
        else:
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
######################################################
#判断是不是同一个对话中
async def _is_active_reply_(event:MessageEvent,bot:Bot):
    if bool(event.reply):
        bot_id = bot.self_id
        reply = event.reply
        user_id = str(event.user_id)
        sender_id = str(reply.sender.user_id)
        # 遍历所有键值对
        if sender_id != bot_id:
            return False
        try:
            for key, value in last_active_messageid[user_id].items():
                # 找到匹配的值
                if list(value.values())[0] == reply.message_id:
                    bot = key
                    return bot
        except:
            pass
        return False

_poe_active_continue_ = on_message(priority=1,block=False,rule=_is_active_reply_)
@_poe_active_continue_.handle()
async def __poe_continue__(bot:Bot,matcher: Matcher,event:MessageEvent):
    global chat_lock,last_messageid,chat_pages
    if not is_useable(event):
        await matcher.finish()
    userid = str(event.user_id)
    raw_message = str(event.message)
    if userid in chat_pages:
        await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后在发送"))
    botname = await _is_active_reply_(event,bot)
    if not botname:
        await matcher.finish()
    truename = user_dict[userid]["all"][botname]
    if userid in active_chat_suggest and len(raw_message) == 1 and raw_message in ['1','2','3','4']:
            text = active_chat_suggest[userid][botname][int(raw_message)-1]
    else:
        text = raw_message

    if raw_message in ["清除对话","清空对话","清除历史","清空对话","poedump","pdump","pd"]:
        async with chat_lock:
            chat_pages[userid] = await pwfw.new_page()
            is_cleared = await poe_clear(chat_pages[userid],truename)
            del chat_pages[userid]
            if is_cleared:
                msg = f"成功清除了{botname}的历史消息"
            else:
                msg = "出错了，多次错误请联系机器人主人"
            await matcher.finish(reply_out(event, msg)) 
    
    if chat_lock.locked():
        await matcher.send(reply_out(event, '请稍等,你前面已有3个用户'))
        
    async with chat_lock:
        chat_pages[userid] = await pwfw.new_page()
        result = await poe_chat(truename, text, chat_pages[userid])
        if isinstance(result, tuple):
            last_answer, active_chat_suggest[userid][botname] = result
            is_successful = True
        elif isinstance(result, str):
            if "banned" == result:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                await matcher.finish(reply_out(event, '你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设'))
        elif isinstance(result, bool):
            is_successful = result
        else:
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            raise ValueError("Unexpected return type from get_message_async")
        if is_successful:
            suggest_str = '\n'.join([f"{i+1}: {s}" for i, s in enumerate(active_chat_suggest[userid][botname])])
            if suggest_able:
                msg = f"{last_answer}\n\n建议回复：\n{suggest_str}"
            else:
                msg = f"{last_answer}\n"
            if is_pic_able:
                if is_qr_able:
                    pic,url = await txt2img.draw(title=" ",text=msg)
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    if is_url_able:
                        last_active_messageid[userid][botname] = await matcher.send(reply_out(event, pic)+MessageSegment.text(url))
                    else:
                        last_active_messageid[userid][botname] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
                else:
                    try:
                        await chat_pages[userid].close()
                    except:
                        pass
                    del chat_pages[userid]
                    pic,_ = await txt2img.draw(title=" ",text=msg)
                    last_active_messageid[userid][botname] = await matcher.send(reply_out(event, pic))
                    await matcher.finish()
            else:
                try:
                    await chat_pages[userid].close()
                except:
                    pass
                del chat_pages[userid]
                last_active_messageid[userid][botname] = await matcher.send(reply_out(event, msg))
                await matcher.finish()
        else:
            try:
                await chat_pages[userid].close()
            except:
                pass
            del chat_pages[userid]
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
######################################################

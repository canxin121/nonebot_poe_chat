<p align="center">
<a href="https://github.com/canxin121/nonebot_poe_chat"><img src="https://github.com/canxin121/nonebot_paddle_ocr/blob/main/demo/logo_transparent.png" width="200" height="200" alt="nonebot_poe_chat"></a>
</p>
<div align="center">

# nonebot_poe_chat

✨*基于Nonebot和playwright，可以将poe.com接入qq*✨

</div>

<p align="center">
    <a href="https://pypi.python.org/pypi/nonebot-poe-chat">
    <img src="https://img.shields.io/pypi/v/nonebot-poe-chat" alt="pypi">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/nonebot-poe-chat" alt="python">
    <img src="https://img.shields.io/pypi/dm/nonebot-poe-chat" alt="pypi">
    <br />
    <a href="https://onebot.dev/">
    <img src="https://img.shields.io/badge/OneBot-v11-black?style=social&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="onebot">
    <a href="https://github.com/canxin121/nonebot_poe_chat/releases/">
    <img src="https://img.shields.io/github/last-commit/canxin121/nonebot_poe_chat" alt="github">
    </a>
</p>
<div align="left">
 
## 功能特性
--可以使用gpt3.5和claude两种模型，支持自定义预设和本地预设  
--有完备的等待队列，又支持每次几名用户同时请求  
--注意所有功能都是用户独立的，每个用户只能操作自己的内容  
--所有分步操作都可以用 取消 或 算了来终止,并且支持错误重输  
--如果未创建机器人，对话命令将默认创建gpt3.5  
--可以直接回复机器人给你的回答来继续对话，无需命令  
--可以使用数字索引来使用建议回复  
--机器人的回答会以回复形式发送，支持发送带二维码的图片格式和相应的链接  
--机器人的时效性回复都会自动撤回，防止刷屏  
--插件储存数据放置在./data/poe_chat中  
--支持填写代理地址http,https,socks，及其username,password
## 功能使用
--以下命令前面全部要加 /   
************************  
--以下命令均支持用户隔离  
~对话:poetalk / ptalk / pt  
~清空历史对话:poedump / pdump / pd  
~创建机器人:poecreate / 创建bot / pc  
~删除机器人:poeremove / 删除bot / pr  
~切换机器人:poeswitch / 切换bot / ps\n  
************************  
--以下命令均是多用户共享的  
~搜索引擎返回的是链接及标题  
~NeevaAI搜索引擎:poeneeva / pneeva / pn  
~共享的gpt对话:poesharegpt / psharegpt / psg  
~清空共享的gpt的对话历史:poegptdump / poegpt清除 / pgd  
~共享的claude对话:poeshareclaude / pshareclaude / psc  
~清空共享的claude的对话历史:poeclaudedump / poeclaude清除 / pcd  
************************  
--以下功能仅限poe管理员使用  
~登录:poelogin / plogin / pl  
~添加预设:poeaddprompt / 添加预设 / pap  
~删除预设:poeremoveprompt / 删除预设 / prp"
# 安装  
## step.1  
### nb安装  
```
nb plugin install nonebot-poe-chat
```
### 或者pip安装并添加到pyproject.toml的plugins列表中  
```
pip install nonebot-poe-chat
```
 
## step.2  
```
playwright install chromium
```
## step.3  
打开poe官网（poe.com），注册账号登录并填写profile（点击create bot可能会弹出让你填写），提取cookie（见后文截图）  
## 配置（在.env中修改）  


```
#poe_cookie,poe网站的ck，见后文截图，也可以不填，而使用/pl命令登陆
#（pl登录暂时不稳定，可以自行尝试一下，不行就手动填cookie）
#1.    
poe_cookie = "f87HlVW~~%3D%3D"
#poe_superusers，poe插件管理员qq号
poe_superusers = ["123456","132145"]
#默认True，表示是否以图片形式回复
#2.
poe_picable = True
#默认True, 表示是否在图片形式回复后跟上二维码的链接
#3.
poe_urlable = True
#代理地址如果你的电脑直接就能访问外网，也就是系统代理，请不填写，不要留空，直接不填
#如果你只开启了局域网代理，则填写响应信息
#代理地址以及验证信息，以下只是示例，请根据需求填写
#4.
poe_server = socks://127.0.0.1:7890
#如果没有验证用的账号密码，不要写下面这两项
#5.
poe_name = canxin
#6.
poe_passwd = passwd

```
![ck获取](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/ck.png)
## 示例

| Image 1 | Image 2 |
|:-------:|:-------:|
| ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(1).PNG) | ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(2).PNG) |
| Image 3 | Image 4 |
| ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(3).PNG) | ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(4).PNG) |
| Image 5 | Image 6 |
| ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(5).PNG) | ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(6).PNG) |
| Image 7 | Image 8 |
| ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(7).PNG) | ![](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/demo%20(8).PNG) |

## 更新
2023/4/27:  
    1.修复cookie致命bug  
    2./pl登录可能暂时不好用了，因为poe在检测机器人登录，请自行填写ck  
    3.新增neevaAi搜索功能  
    4.新增共享的gpt和claude聊天  
    5.修复自定义预设中间有空格造成错误的bug  
    6.补上了创建bot的代码的lock  
    7.恢复正常的suggest，并修复了一个由suggest引起的死循环bug  
2023/4/26:  
    1.单例模式重构，只创建一个context，稍微减轻性能消耗  
    2.暂时修复poe官网suggest消失造成死循环的bug  

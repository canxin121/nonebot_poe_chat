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
---    
[![残心小站-文档库](https://github.com/canxin121/nonebot_poe_chat/blob/main/resource/cx.png )](https://canxin121.github.io/docs/docs/nonebot-poe-chat.html )
    
> 详细教程 点击链接跳转👇 点击图片跳转☝️   
> [残心小站-文档库](https://canxin121.github.io/docs/docs/nonebot-poe-chat.html )
---
## 功能特性

- 可以使用gpt3.5和claude两种模型，支持自定义预设和本地预设  
- 可以使用neeva ai搜索引擎  
- 有共享的机器人供多人共同使用(仅支持命令来对话，不支持以下特性)  
- 有用户隔离的个人机器人使用,支持下面两个功能  
- > 可以直接回复机器人给你的回答来继续对话，无需命令  
- > 可以使用数字索引来使用建议回复  
- 有完备的等待队列，又支持每次几名用户同时请求  
- 所有分步操作都可以用 取消 或 算了来终止,并且支持错误重输  
- 如果未创建机器人，对话命令将默认创建gpt3.5,而默认预设可以由管理员来切换  
- 机器人的回答会以回复形式发送，支持发送带二维码的图片格式和相应的链接  
- 机器人的给普通用户的时效性回复都会自动撤回，防止刷屏  
- 插件储存数据放置在./data/poe_chat中  
- 支持填写代理地址http,https,socks，及其username,password

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

- 2023/4/27 v1.1.1:  
    1.支持管理员切换自动创建的预设  
    2.支持在配置中开启和关闭建议回复和图片中二维码，详情看上文 配置  
- 2023/4/26 v1.0.9:  
    1.修复cookie致命bug  
    2./pl登录可能暂时不好用了，因为poe在检测机器人登录，请自行填写ck  
    3.新增neevaAi搜索功能  
    4.新增共享的gpt和claude聊天  
    5.修复自定义预设中间有空格造成错误的bug  
    6.补上了创建bot的代码的lock  
    7.恢复正常的suggest，并修复了一个由suggest引起的死循环bug  
- 2023/4/26 v1.0.8:  
    1.单例模式重构，只创建一个context，稍微减轻性能消耗  
    2.暂时修复poe官网suggest消失造成死循环的bug  

<p align="center">
<a href="https://github.com/canxin121/nonebot_poe_chat"><img src="https://github.com/canxin121/nonebot_paddle_ocr/blob/main/demo/logo_transparent.png" width="200" height="200" alt="nonebot_poe_chat"></a>
</p>
<div align="center">

# nonebot_poe_chat

✨*基于Nonebot和playwright，可以将poe.com接入qq*✨

<div align="left">
 
## 功能特性
--可以使用gpt3.5和claude两种模型，支持自定义预设和本地预设  
--有完备的等待队列，又支持每次几名用户同时请求  
--注意所有功能都是用户独立的，每个用户只能操作自己的内容  
--所有分步操作都可以用 取消 或 算了来终止,并且支持错误重输  
--如果未创建机器人，对话命令将默认创建gpt3.5  
--可以直接回复机器人给你的回答来继续对话，无需命令  
--可以使用数字索引来使用建议回复  
--机器人的回答会以回复形式发送  
## 功能使用
--以下命令前面全部要加 /   
~对话:poetalk / ptalk / pt  
~清空历史对话:poedump / pdump / pd  
~创建机器人:poecreate / 创建bot / pc  
~删除机器人:poeremove / 删除bot / pr  
~切换机器人:poeswitch / 切换bot / ps  
  
************************  
--以下功能仅限poe管理员使用  
~登录:poelogin / plogin / pl  
~添加预设:poeaddprompt / 添加预设 / pap  
~删除预设:poeremoveprompt / 删除预设 / prp  
  
## pip安装并添加到pyproject.toml的plugins列表中  
```
pip install nonebot-poe-chat
```
##然后  
```
playwright install chromuim
```
## 配置（在.env中修改）  

```
#poe_cookie,poe网站的ck，见后文截图，也可以不填，而是用/pl命令登陆
poe_cookie = "f87HlVW~~%3D%3D"
#poe_superusers，poe插件管理员qq号
poe_superusers = ["123456","132145"]
```
## 示例

| Image 1 | Image 2 |
|:-------:|:-------:|
| ![](https://github.com/canxin121/nonebot_api_paddle/blob/main/demo/demo%20(1).png) | ![](https://github.com/canxin121/nonebot_api_paddle/blob/main/demo/demo%20(1).jpg) |
| Image 3 | Image 4 |
| ![](https://github.com/canxin121/nonebot_api_paddle/blob/main/demo/demo%20(2).png) | ![](https://github.com/canxin121/nonebot_api_paddle/blob/main/demo/demo%20(3).png) |

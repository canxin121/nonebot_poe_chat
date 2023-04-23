import asyncio
from poe_func import get_qr_img
from txt2img import Txt2Img
txt2img = Txt2Img()

async def main():
    msg = '''是的，我还在。有什么问题我可以帮助您解答吗？

建议回复：
1: Tell me more.
2: 我有一个问题，你能帮我查找一下吗？
3: 我想了解一下你能提供哪些服务。
4: 你能告诉我如何使用你的功能吗？'''
    pic = await txt2img.draw(title=" ",text = msg)
    print(pic)
# asyncio.run(main())


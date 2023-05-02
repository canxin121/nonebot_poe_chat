import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="nonebot_poe_chat",  # 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="1.1.7",  # 程序版本
    package_data={"nonebot_poe_chat":["TXT2IMG/font/*.ttf","TXT2IMG/image/*.png"]},
    author="canxin",  # 项目作者
    author_email="1969730106@qq.com",  # 作者邮件
    description="nonebot_poe_chat",  # 项目的一句话描述
    long_description=long_description,  # 加长版描述
    long_description_content_type="text/markdown",  # 描述使用Markdown
    url="https://github.com/canxin121/nonebot_poe_chat",  # 项目地址
    packages=setuptools.find_packages(),  # 无需修改
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU Affero General Public License v3",  # 开源协议
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'nonebot2>=2.0.0rc3',
        'nonebot-adapter-onebot>=2.0.0b1',
        'nonebot_plugin_guild_patch>=0.2.3',
        'playwright>=1.32.1',
        'aiohttp>=3.8.4',
        'Pillow>=9.5.0',
        'qrcode>=7.4.2'

    ]
)

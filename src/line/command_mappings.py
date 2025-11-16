INDEX_COMMANDS = {
    "大盤": ("^TWII", "TW"),
    "日股": ("^N225", "US"),
    "韓股": ("^KS11", "US"),
    "美股": [
        ("^GSPC", "US"),
        ("^DJI", "US"),
        ("^IXIC", "US"),
        ("^SOX", "US")
    ]
}

CURRENCY_COMMANDS = {
    "美元": ("TWD=X", "US"),
    "日元": ("JPYTWD=X", "US")
}

COMEX_COMMANDS = {
    "黃金": ("GC=F", "US"),
    "白銀": ("SI=F", "US"),
    "貴金屬": [
        ("GC=F", "US"),
        ("SI=F", "US")
    ],
    "石油": ("CL=F", "US")
}

BONDS_COMMANDS = {
    "債券": [
        ("^FVX", "US"),
        ("^TNX", "US"),
        ("^TYX", "US")
    ]
}

COIN_COMMANDS = {
    "比特幣": ("BTC-USD", "US"),
    "以太幣": ("ETH-USD", "US"),
    "虛擬幣": [
        ("BTC-USD", "US"),
        ("ETH-USD", "US")
    ]
}


def format_command_help(commands:dict):
    return ", ".join(map(lambda key: f"#{key}", commands.keys()))


HELP_COMMANDS = {
    "指令": "\n".join([
        f"指數: {format_command_help(INDEX_COMMANDS)}",
        "個股: #股票代號 (ex: #2330), #公司名稱 (ex: #台積電)",
        f"外匯: {format_command_help(CURRENCY_COMMANDS)}",
        f"原物料: {format_command_help(COMEX_COMMANDS)}",
        f"債券: {format_command_help(BONDS_COMMANDS)}",
        f"虛擬幣: {format_command_help(COIN_COMMANDS)}"
    ])
}

ALL_COMMANDS = {
    **INDEX_COMMANDS,
    **CURRENCY_COMMANDS,
    **COMEX_COMMANDS,
    **BONDS_COMMANDS,
    **COIN_COMMANDS,
    **HELP_COMMANDS
}


def get_all_commands():
    return ALL_COMMANDS

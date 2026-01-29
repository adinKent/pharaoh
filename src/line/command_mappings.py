INDEX_COMMANDS = {
    "大盤": ("IX0001", "TW_IND"),
    "櫃買": ("IX0043", "TW_IND"),
    "日股": ("^N225", "IND"),
    "韓股": ("^KS11", "IND"),
    "亞股": [
        ("IX0001", "TW_IND"),
        ("^N225", "IND"),
        ("^KS11", "IND")
    ],
    "美股": [
        ("^GSPC", "IND"),
        ("^DJI", "IND"),
        ("^IXIC", "IND"),
        ("^SOX", "IND")
    ]
}

INDEX_FUTURE_COMMANDS = {
    "美股期": [
        ("ES=F", "IND"),
        ("YM=F", "IND"),
        ("NQ=F", "IND"),
        ("SOX=F", "IND")
    ]
}

CURRENCY_COMMANDS = {
    "外匯": [
        ("TWD=X", "FUT"),
        ("JPYTWD=X", "FUT"),
        ("AUDTWD=X", "FUT")
    ],
    "美元": ("TWD=X", "FUT"),
    "美金": ("TWD=X", "FUT"),
    "日元": ("JPYTWD=X", "FUT"),
    "日幣": ("JPYTWD=X", "FUT"),
    "澳元": ("AUDTWD=X", "FUT"),
    "澳幣": ("AUDTWD=X", "FUT")
}

COMEX_COMMANDS = {
    "黃金": ("GC=F", "FUT"),
    "白銀": ("SI=F", "FUT"),
    "貴金屬": [
        ("GC=F", "FUT"),
        ("SI=F", "FUT")
    ],
    "原油": ("CL=F", "FUT")
}

BONDS_COMMANDS = {
    "債券": [
        ("^FVX", "FUT"),
        ("^TNX", "FUT"),
        ("^TYX", "FUT")
    ]
}
BONDS_COMMANDS["美債"] = BONDS_COMMANDS["債券"]

COIN_COMMANDS = {
    "比特幣": ("BTC-USD", "FUT"),
    "以太幣": ("ETH-USD", "FUT"),
    "虛擬幣": [
        ("BTC-USD", "FUT"),
        ("ETH-USD", "FUT")
    ]
}


def format_command_help(commands:dict):
    return ", ".join(map(lambda key: f"#{key}", commands.keys()))


HELP_COMMANDS = {
    "指令": "\n".join([
        f"指數: {format_command_help(INDEX_COMMANDS)}",
        "個股: #股票代號 (ex: #2330), #公司名稱 (ex: #台積電)",
        "當日走勢: P股票代號 (ex: P2330), P公司名稱 (ex: P台積電)",
        "技術分析: A大盤 A股票代號 (ex: A2330), A公司名稱 (ex: A台積電)",
        "三大法人買賣超: F大盤 F股票代號 (ex: F2330), F公司名稱 (ex: F台積電)",
        f"美股期: {format_command_help(INDEX_FUTURE_COMMANDS)}",
        f"外匯: {format_command_help(CURRENCY_COMMANDS)}",
        f"原物料: {format_command_help(COMEX_COMMANDS)}",
        f"債券: {format_command_help(BONDS_COMMANDS)}",
        f"虛擬幣: {format_command_help(COIN_COMMANDS)}"
    ])
}

ALL_COMMANDS = {
    **INDEX_COMMANDS,
    **INDEX_FUTURE_COMMANDS,
    **CURRENCY_COMMANDS,
    **COMEX_COMMANDS,
    **BONDS_COMMANDS,
    **COIN_COMMANDS,
    **HELP_COMMANDS
}


def get_all_commands():
    return ALL_COMMANDS

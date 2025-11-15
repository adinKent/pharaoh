def get_ups_or_downs(current_price, previous_close):
    """
    Determine if the stock price is up, down, or unchanged.
    Returns 1 for up, -1 for down, 0 for unchanged.
    """
    if current_price > previous_close:
        return 1
    elif current_price < previous_close:
        return -1
    else:
        return 0

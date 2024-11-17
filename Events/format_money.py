def format_money(amount):
    if isinstance(amount, int):
        return f"{amount:,}"
    elif isinstance(amount, float):
        return f"{amount:,.0f}"
    else:
        return "Unbekannt"

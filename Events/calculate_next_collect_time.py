import pytz
from datetime import datetime, timedelta

def calculate_next_collect_time(last_collect_time, cooldown_hours):
    if last_collect_time is None:
        return datetime.now(pytz.utc)

    last_collect_time = datetime.fromisoformat(last_collect_time).replace(tzinfo=pytz.utc)
    return last_collect_time + timedelta(hours=cooldown_hours)
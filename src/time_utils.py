import datetime as dt


def convert_to_unix(ts, offset=0) -> float:
    try:
        return (
            dt.datetime(
                int(ts[:4]),
                int(ts[5:7]),
                int(ts[8:10]),
                int(ts[11:13]),
                int(ts[14:16]),
                int(ts[17:19]),
                tzinfo=dt.timezone.utc,
            )
            + dt.timedelta(hours=offset)
        ).timestamp()
    except ValueError:
        return dt.datetime(
            int(ts[:4]), int(ts[5:7]), int(ts[8:10]), tzinfo=dt.timezone.utc
        ).timestamp()


def in_period_of_time(ts, leftbond, rightbond) -> bool:
    if convert_to_unix(ts) >= leftbond and convert_to_unix(ts) <= rightbond:
        return True
    else:
        return False

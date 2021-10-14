import datetime as dt


def convert_to_unix(timestamp: str, offset=0) -> float:
    """Converts timestamp in "YYYY.MM.DD-hh.mm.ss" format
    to Unix time (Epoch time, Posix time)

    Example:
        ``convert_to_unix("2021.12.30", offset=-1)``
        returns ``1640822400.0``

    :param timestamp: timestamp in ``"YYYY.MM.DD-hh.mm.ss"`` format
        the ``-hh.mm.ss`` is optional
    :type timestamp: str
    :param offset: [description], defaults to 0
    :type offset: int, optional
    :return: timestamp in Unix time
    :rtype: float
    """
    # e.g. GatherData.set_bonds(self, earliest, latest)
    # self.leftbond = time_utils.convert_to_unix(earliest, -1)
    # self.rightbond = time_utils.convert_to_unix(latest, -1)
    # timestamp in "YYYY.MM.DD-hh.mm.ss" format

    # TODO: WHY THE OFFSET, LUKAS?!?

    # creates a datetime object from the input date string,
    # gets the Unix time from that datetime object and returns it

    unix_time: float
    try:
        unix_time = (
            dt.datetime(
                int(timestamp[:4]),  # YYYY
                int(timestamp[5:7]),  # MM
                int(timestamp[8:10]),  # DD
                int(timestamp[11:13]),  # hh
                int(timestamp[14:16]),  # mm
                int(timestamp[17:19]),  # ss
                # UTC timezone because Spotify saves date in UTC
                tzinfo=dt.timezone.utc,
            )
            + dt.timedelta(hours=offset)
        ).timestamp()
    except ValueError:
        unix_time = dt.datetime(
            int(timestamp[:4]),  # YYYY
            int(timestamp[5:7]),  # MM
            int(timestamp[8:10]),  # DD
            tzinfo=dt.timezone.utc,
        ).timestamp()

    return unix_time


def in_period_of_time(timestamp, leftbond, rightbond) -> bool:
    if (
        convert_to_unix(timestamp) >= leftbond
        and convert_to_unix(timestamp) <= rightbond
    ):
        return True
    else:
        return False

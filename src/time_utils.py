import datetime as dt

from errors import WrongDate


def convert_to_unix(timestamp: str, tzoffset_to_utc=0) -> float:
    """Converts timestamp in "YYYY.MM.DD-hh.mm.ss" format
    to Unix time (Epoch time, Posix time)

    Example:
        ``convert_to_unix("2021.12.30-10.00.00", offset=-1)``
        returns ``1640858400.0``

    :param timestamp: timestamp in ``"YYYY.MM.DD-hh.mm.ss"`` format
        the ``-hh.mm.ss`` is optional
    :type timestamp: str
    :param offset: difference (UTC - your timezone) because Spotify
        saves UTC date but you may want to input your own timezone, defaults to 0
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

    unix_time: float = 0.0
    try:
        date: dt.datetime
        # YYYY.MM.DD
        if len(timestamp) == 10:
            date = dt.datetime(
                int(timestamp[:4]),  # YYYY
                int(timestamp[5:7]),  # MM
                int(timestamp[8:10]),  # DD
                # UTC timezone because Spotify saves date in UTC
                tzinfo=dt.timezone.utc,
            )
        # YYYY.MM.DD-hh.mm.ss - 19
        # Spotify endsong.json e.g. 2017-04-16T15:41:22Z - 20
        elif len(timestamp) == 19 or len(timestamp) == 20:
            date = dt.datetime(
                int(timestamp[:4]),  # YYYY
                int(timestamp[5:7]),  # MM
                int(timestamp[8:10]),  # DD
                int(timestamp[11:13]),  # hh
                int(timestamp[14:16]),  # mm
                int(timestamp[17:19]),  # ss
                # UTC timezone because Spotify saves date in UTC
                tzinfo=dt.timezone.utc,
            )
        else:
            # if it's not in the correct format
            raise WrongDate(timestamp)

        # difference (UTC - your timezone)
        # if you live in CET (UTC+1) it would be -1
        # not all that useful, but for accuracy's sake
        # bc Spotify saves date in UTC and may want to
        # view dates from your own timezone
        if tzoffset_to_utc != 0:
            date += dt.timedelta(hours=tzoffset_to_utc)

        unix_time = date.timestamp()

    # dt.datetime raises a ValueError if the value is not in range
    # e.g. hours>24; min,sec>60, month>12 etc.
    # => account for other errors as well, also this assumes the part
    # before "-hh.mm.ss" is correct -> make it better

    # if the "-hh.mm.ss" part is either missing, wrong or incomplete
    # it defaults to just the date
    # except ValueError:
    #     unix_time = (
    #         dt.datetime(
    #             int(timestamp[:4]),  # YYYY
    #             int(timestamp[5:7]),  # MM
    #             int(timestamp[8:10]),  # DD
    #             tzinfo=dt.timezone.utc,
    #         )
    #         + dt.timedelta(hours=tzoffset_to_utc if tzoffset_to_utc != 0 else 0)
    #     ).timestamp()

    except TypeError:
        # if the input is not a string
        print("'" + str(timestamp) + "' is not a string!")
    except WrongDate:
        print(
            "The suppplied date '"
            + str(timestamp)
            + "' is either wrong/non-existent or not in the 'YYYY.MM.DD-hh.mm.ss' format"
        )

    except Exception as e:
        print(e)

    return unix_time


def in_period_of_time(timestamp: str, leftbound: float, rightbound: float) -> bool:
    """Returns if the given stream entry is in the bounds

    :param timestamp: Spotify endsong.json stream entry timestamp
        in "2017-04-16T15:41:22Z" format
    :type timestamp: str
    :param leftbound: left bound
    :type leftbound: float
    :param rightbound: right bound
    :type rightbound: float
    :return: True if the entry is in the bounds, False if otherwise
    :rtype: bool
    """
    if (
        convert_to_unix(timestamp) >= leftbound
        and convert_to_unix(timestamp) <= rightbound
    ):
        return True
    else:
        return False

#!/usr/bin/python3

import datetime as dt
import json
from math import floor, log10
from enum import Enum, auto

import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import numpy as np

# docstrings: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html

# TODO: add examples to docstrings??
# TODO: run pylint and make the code achieve a good score!
#   also: maybe setup a GitHub Actions pylint workflow?
#   https://github.com/Filip-Tomasko/endsong-parser-python/actions/new

class Aspect(Enum):
    TRACK = auto()
    ALBUM = auto()
    ARTIST = auto()
    # use this somehow https://youtu.be/LrtnLEkOwFE

class GatherData:
    """Used for parsing data from endsong.json to a Python list of dictionaries

    **WARNING**: ``uri=False`` *MAY* mix stuff up if artists have the same name

    :param path: absolute path or list of absolute paths to ``endsong.json`` files
    :type path: str or list
    :param uri: if *True*: songs are identified by Spotify ID;
        if *False*: by name and artist
        (album and single versions are identified as one), defaults to *True*
    :type uri: bool, optional
    """

    __slots__ = ["__info", "__leftbond", "__rightbond"]

    def __init__(self, path, uri=True) -> None:
        self.__info = []
        self.__leftbond = 0
        self.__rightbond = 2147483647
        self.__collect_data(path, uri)

    def __collect_data(self, path, uri) -> None:
        if isinstance(path, (list, tuple)):
            lpath = path
        else:
            lpath = [path]

        for e in lpath:
            with open(e, "r", encoding="utf-8") as jsonFile:
                file = json.load(jsonFile)
                jsonFile.close()

            for f in file:
                if uri:
                    if f["spotify_track_uri"]:
                        i = 0
                        match = False
                        while i < len(self.__info) and not match:
                            if self.__info[i]["id"] == f["spotify_track_uri"]:
                                self.__info[i]["timestamps"] += [f["ts"]]
                                match = True
                            i += 1
                        if not match:
                            self.__info += [
                                {
                                    "id": f["spotify_track_uri"],
                                    "title": f["master_metadata_track_name"],
                                    "artist": f["master_metadata_album_artist_name"],
                                    "streams": 1,
                                    "album": f["master_metadata_album_album_name"],
                                    "timestamps": [f["ts"]],
                                }
                            ]
                else:
                    if (
                        f["master_metadata_track_name"]
                        or f["master_metadata_album_artist_name"]
                    ):
                        i = 0
                        match = False
                        while i < len(self.__info) and not match:
                            if (
                                self.__info[i]["title"]
                                == f["master_metadata_track_name"]
                                and self.__info[i]["artist"]
                                == f["master_metadata_album_artist_name"]
                            ):
                                self.__info[i]["timestamps"] += [f["ts"]]
                                match = True
                            i += 1
                        if not match:
                            self.__info += [
                                {
                                    "id": f["spotify_track_uri"],
                                    "title": f["master_metadata_track_name"],
                                    "artist": f["master_metadata_album_artist_name"],
                                    "streams": 1,
                                    "album": f["master_metadata_album_album_name"],
                                    "timestamps": [f["ts"]],
                                }
                            ]

        for i in range(len(self.__info)):
            self.__info[i]["streams"] = len(self.__info[i]["timestamps"])

    def get_streams_of(self, aspect="title") -> list:
        """Returns all of a specfic aspect from dataset ordered by
        number of streams.

        Use "set_bonds" to set a specific date range

        :param aspect: desired aspect, can be "title", "album"
            or "artist", defaults to "title"
        :type aspect: str, optional
        :return: array of dictionaries, where each dictionary is a single
            song with attributes "title", "artist", "album" and "streams"
        :rtype: list[dict]
        """

        streams_of = [[aspect, self.__leftbond, self.__rightbond]]
        for e in self.__info:
            i = 1
            match = False
            while i < len(streams_of) and not match:
                if e[aspect] == streams_of[i][aspect]:
                    for j in range(len(e["timestamps"])):
                        if self.__in_period_of_time(e["timestamps"][j]):
                            streams_of[i]["streams"] += 1
                    if aspect == "artist":
                        streams_of[i]["title"] += [
                            [e["title"], e["streams"], e["album"]]
                        ]
                    elif aspect == "album":
                        streams_of[i]["title"] += [[e["title"], e["streams"]]]
                    match = True
                i += 1

            if not match:
                if aspect == "title":
                    streams_of += [
                        {
                            "title": e["title"],
                            "artist": e["artist"],
                            "album": e["album"],
                            "streams": 0,
                        }
                    ]
                elif aspect == "artist":
                    streams_of += [
                        {"artist": e["artist"], "streams": 0, "title": [], "album": []}
                    ]
                elif aspect == "album":
                    streams_of += [
                        {
                            "album": e["album"],
                            "artist": e["artist"],
                            "streams": 0,
                            "title": [],
                        }
                    ]
                for j in range(len(e["timestamps"])):
                    if self.__in_period_of_time(e["timestamps"][j]):
                        streams_of[-1]["streams"] += 1
                if aspect == "artist":
                    streams_of[-1]["title"] += [[e["title"], e["streams"], e["album"]]]
                elif aspect == "album":
                    streams_of[-1]["title"] += [[e["title"], e["streams"]]]
                if streams_of[-1]["streams"] == 0:
                    del streams_of[-1]

        if aspect == "artist" or aspect == "album":
            for e in streams_of[1:]:
                for _ in range(len(e["title"]) - 1):
                    for i in range(len(e["title"]) - 1):
                        if e["title"][i][1] < e["title"][i + 1][1]:
                            e["title"][i], e["title"][i + 1] = (
                                e["title"][i + 1],
                                e["title"][i],
                            )
        if aspect == "artist":
            for e in streams_of[1:]:
                albums = []
                for f in e["title"]:
                    i = 0
                    match = False
                    while i < len(albums) and not match:
                        if f[2] == albums[i][0]:
                            albums[i][1] += f[1]
                            match = True
                        i += 1
                    if not match:
                        albums += [[f[2], f[1]]]
                e["album"] = albums
            for e in streams_of[1:]:
                for _ in range(len(e["album"]) - 1):
                    for i in range(len(e["album"]) - 1):
                        if e["album"][i][1] < e["album"][i + 1][1]:
                            e["album"][i], e["album"][i + 1] = (
                                e["album"][i + 1],
                                e["album"][i],
                            )
        # returns list of dicts
        return self.__sort_by_streams(streams_of)

    def __sort_by_streams(self, items) -> list:
        for _ in range(1, len(items) - 1):
            for i in range(1, len(items) - 1):
                if items[i]["streams"] < items[i + 1]["streams"]:
                    items[i], items[i + 1] = items[i + 1], items[i]
        return items

    def get_sum(self) -> int:
        """Return sum of streams in the given time period

        :return: sum of streams
        :rtype: int
        """
        sum_listened = 0
        for e in self.__info:
            for i in range(len(e["timestamps"])):
                if self.__in_period_of_time(e["timestamps"][i]):
                    sum_listened += 1
        return sum_listened

    def __convert_to_unix(self, ts, offset=0) -> float:
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

    def __in_period_of_time(self, ts) -> bool:
        if (
            self.__convert_to_unix(ts) >= self.__leftbond
            and self.__convert_to_unix(ts) <= self.__rightbond
        ):
            return True
        else:
            return False

    def set_bonds(self, earliest, latest) -> None:
        """Set the desired time frame

        ``-hh.mm.ss`` is optional

        :param earliest: date in "yyyy.mm.dd-hh.mm.ss" format
        :type earliest: str
        :param latest: date in "yyyy.mm.dd-hh.mm.ss" format
        :type latest: str
        """
        self.__leftbond = self.__convert_to_unix(earliest, -1)
        self.__rightbond = self.__convert_to_unix(latest, -1)

    def restore_bonds(self) -> None:
        """Restores default bonda for date range
        (Unix time min and max)
        """
        self.__leftbond = 0
        self.__rightbond = 2147483647

    def get_first_ever(self) -> tuple:
        """Returns first ever streamed song listed in endsong.json

        :return: tuple of first ever streamed song with the song dictionary
            and the date as Unix timestamp;
            Note: "timestamps" value is a list of dates
        :rtype: tuple[dict, float]
        """
        earliest = 2147483647
        for i in range(len(self.__info)):
            for j in range(len(self.__info[i]["timestamps"])):
                if self.__convert_to_unix(self.__info[i]["timestamps"][j]) < earliest:
                    earliest = self.__convert_to_unix(self.__info[i]["timestamps"][j])
                    ret = self.__info[i]
        return (ret, earliest)

    def get_last_of_data(self) -> tuple:
        """Returns the most recently streamed song listed in endsong.json

        :return: tuple of the most recently streamed song with the song
            dictionary and the date as Unix timestamp;
            Note: "timestamps" value is a list of dates
        :rtype: tuple[dict, float]
        """
        latest = 0
        for i in range(len(self.__info)):
            for j in range(len(self.__info[i]["timestamps"])):
                if self.__convert_to_unix(self.__info[i]["timestamps"][j]) > latest:
                    latest = self.__convert_to_unix(self.__info[i]["timestamps"][j])
                    ret = self.__info[i]
        return (ret, latest)

    def list_with_names(self) -> None:
        """Creates a .txt file that contains all track names, artists and albums"""

        # so that you can look up how a particular song/arist is written

        titles, artists, albums = [], [], []
        for e in self.__info:
            titles += [e["title"]]
            ai = False
            for f in artists:
                if f == e["artist"]:
                    ai = True
            if not ai:
                artists += [e["artist"]]
            ai = False
            for f in albums:
                if f == e["album"]:
                    ai = True
            if not ai:
                albums += [e["album"]]

        file = open("names.txt", "a", encoding="utf8")
        file.write("ALL TITLES\n")
        for e in titles:
            file.write(e + "\n")
        file.write("\nALL ARTISTS\n")
        for e in artists:
            file.write(e + "\n")
        file.write("\nALL ALBUMS\n")
        for e in albums:
            file.write(e + "\n")
        file.close()
        print("saved as names.txt")

    def prepare_graph(self, aspect, name) -> list:
        """prepares data to put in a graph \n
        aspects are "title", "artist" and "album" \n
        name of the aspect
        """
        times = []
        string = []
        for e in self.__info:
            if e[aspect] == name:
                for f in e["timestamps"]:
                    if self.__in_period_of_time(f):
                        times += [f]
                string += [e["artist"]]
                if aspect == "album" or aspect == "title":
                    string += [e["album"]]
                if aspect == "title":
                    string += [e["title"]]
        for _ in range(len(times) - 1):
            for i in range(len(times) - 1):
                if times[i] > times[i + 1]:
                    times[i], times[i + 1] = times[i + 1], times[i]
        for i in range(len(times)):
            times[i] = dt.datetime.utcfromtimestamp(
                self.__convert_to_unix(times[i])
            ) + dt.timedelta(hours=+1)
        return [
            [
                dt.datetime.utcfromtimestamp(self.get_first_ever()[1])
                + dt.timedelta(hours=+1)
            ]
            + times
            + [
                dt.datetime.utcfromtimestamp(self.get_last_of_data()[1])
                + dt.timedelta(hours=+1)
            ],
            aspect,
            string,
        ]

    def all_timestamps(self) -> list:
        """Returns list of all timestamps

        :return: list of all timestamps in endsong.json
        :rtype: list
        """
        timestamps = []
        for e in self.__info:
            for f in e["timestamps"]:
                timestamps += [self.__convert_to_unix(f)]
        return timestamps


class DisplayData:
    """Used for visualizing the endsong.json data parsed in :class:`GatherData`

    :param gatheredData: object created using :class:`GatherData` class
    :type gatheredData: GatherData
    """

    def __init__(self, gatheredData) -> None:
        self.data = gatheredData
        self.sum_all = self.data.get_sum()
        self.first = self.data.get_first_ever()
        self.last = self.data.get_last_of_data()
        self.all_timestamps = self.data.all_timestamps()

    def print_top(
        self,
        aspect="title",
        title=False,
        artist=True,
        album=False,
        streams=True,
        primaryNum=10,
        secondaryNum=5,
        percent=False,
    ) -> None:
        """Prints top list of aspect

        :param str aspect: Can be ``"title"``, ``"artist"`` or ``"album"``
        :param bool title: For aspects "artist" and "album": prints top
            secondaryNum songs of that aspect
        :param bool artist: For aspects "title" and "album": prints the
            artist of that aspect
        :param bool album: For aspect "title": prints the album the track is a part of;
            For aspect "artist": prints the top secondaryNum albums of that artist
        :param bool streams: Whether to show amount of total streams of chosen aspect
        :param int primaryNum: Show top primaryNum of chosen aspect
        :param int secondaryNum: see title and album parameters
        :param bool percent: whether to show proportion of total
            streams to amount of streams of chosen aspect,
            defaults to False
        """

        def topOrder(order, maxNum) -> str:
            """Formats position of aspect for better display.
            If it were to display e.g. 100 tracks,
            this function would change ``"#1"`` to ``"  #1"`` to match up with ``"#100"``

            :param int order: actual position of aspect
            :param int maxNum: top maxNum of aspect
            :return: nicely formatted position string for better display
            :rtype: str
            """

            orderFormat = ""

            # https://stackoverflow.com/a/6769458/6694963
            numOfZero = floor(log10(maxNum))

            # efficient way to get number of digits of a number
            # https://stackoverflow.com/a/2189827/6694963
            digits = int(log10(order)) + 1

            while numOfZero != 0:
                if digits <= numOfZero:
                    orderFormat += " "
                numOfZero -= 1

            orderFormat += "#" + str(order) + ": "

            return orderFormat

        dataArray = self.data.get_streams_of(aspect)
        print(
            "Between {0} and {1}:".format(
                dt.datetime.utcfromtimestamp(dataArray[0][1]) + dt.timedelta(hours=+1),
                dt.datetime.utcfromtimestamp(dataArray[0][2]) + dt.timedelta(hours=+1),
            )
        )
        if dataArray[0][0] == "title":
            print("--- TOP TRACKS ---")
            for i in range(1, primaryNum + 1):
                # for a nicer, more uniform list
                outputString = topOrder(i, primaryNum)

                if artist:
                    outputString += dataArray[i]["artist"] + " - "
                outputString += dataArray[i]["title"]
                if album and title:
                    outputString += " | " + dataArray[i]["album"]
                if streams:
                    outputString += " | Streams: " + str(dataArray[i]["streams"])
                if percent:
                    outputString += self.percent(dataArray[i]["streams"])
                print(outputString)
        elif dataArray[0][0] == "artist":
            print("--- TOP ARTISTS ---")
            for i in range(1, primaryNum + 1):
                # for a nicer, more uniform list
                outputString = topOrder(i, primaryNum)

                outputString += dataArray[i]["artist"]
                if streams:
                    outputString += " | Streams: " + str(dataArray[i]["streams"])
                if percent:
                    outputString += self.percent(dataArray[i]["streams"])
                if title:
                    outputString += (
                        "\n\tMost Played Songs: \n\t\t1. " + dataArray[i]["title"][0][0]
                    )
                    if album:
                        outputString += " | " + dataArray[i]["title"][0][2]
                    if streams:
                        outputString += " | Streams: " + str(
                            dataArray[i]["title"][0][1]
                        )
                    try:
                        for j in range(1, secondaryNum):
                            outputString += (
                                "\n\t\t"
                                + str(j + 1)
                                + ". "
                                + dataArray[i]["title"][j][0]
                            )
                            if album:
                                outputString += " | " + dataArray[i]["title"][j][2]
                            if streams:
                                outputString += " | Streams: " + str(
                                    dataArray[i]["title"][j][1]
                                )
                    except IndexError:
                        pass
                if album:
                    outputString += (
                        "\n\tMost Played Albums: \n\t\t1. "
                        + dataArray[i]["album"][0][0]
                    )
                    if streams:
                        outputString += " | Streams: " + str(
                            dataArray[i]["album"][0][1]
                        )
                    try:
                        for j in range(1, secondaryNum):
                            outputString += (
                                "\n\t\t"
                                + str(j + 1)
                                + ". "
                                + dataArray[i]["album"][j][0]
                            )
                            if streams:
                                outputString += " | Streams: " + str(
                                    dataArray[i]["album"][j][1]
                                )
                    except IndexError:
                        pass
                print(outputString)
        elif dataArray[0][0] == "album":
            print("--- TOP ALBUMS ---")
            for i in range(1, primaryNum + 1):
                # for a nicer, more uniform list
                outputString = topOrder(i, primaryNum)

                if artist:
                    outputString += dataArray[i]["artist"] + " - "
                outputString += dataArray[i]["album"]
                if streams:
                    outputString += " | Streams: " + str(dataArray[i]["streams"])
                if percent:
                    outputString += self.percent(dataArray[i]["streams"])
                if title:
                    outputString += (
                        "\n\tMost Played Songs: \n\t\t1. " + dataArray[i]["title"][0][0]
                    )
                    if streams:
                        outputString += " | Streams: " + str(
                            dataArray[i]["title"][0][1]
                        )
                    try:
                        for j in range(1, secondaryNum):
                            outputString += (
                                "\n\t\t"
                                + str(j + 1)
                                + ". "
                                + dataArray[i]["title"][j][0]
                            )
                            if streams:
                                outputString += " | Streams: " + str(
                                    dataArray[i]["title"][j][1]
                                )
                    except:
                        pass
                print(outputString)

    def print_sum(self) -> None:
        """
        Prints total amount of listens
        """
        # https://queirozf.com/entries/python-number-formatting-examples#use-commas-as-thousands-separator
        # e.g. 1000000 -> 1,000,000
        print("You have listened to {:,} songs!".format(self.sum_all))

    def print_first_last(self, fl=True) -> None:
        """first song true, last song false"""
        if fl:
            song = self.first
        elif not fl:
            song = self.last
        print(
            "Song "
            + song[0]["title"]
            + " from "
            + song[0]["artist"]
            + " from "
            + song[0]["album"]
            + ", Streams: "
            + str(song[0]["streams"])
            + ", first/last listened at "
            + str(dt.datetime.utcfromtimestamp(song[1]) + dt.timedelta(hours=+1))
        )

    def print_aspect(
        self,
        aspect,
        name,
        title=True,
        artist=True,
        album=False,
        streams=True,
        num=5,
        percent=False,
    ) -> None:
        """Prints a summary of an aspect

        For ``aspect="title"`` by default prints the name of the song,
        the artist and amount of listens

        With ``aspect="artist"``, it can print top ``num`` tracks if
        ``title=True`` and albums if ``album=True``

        With ``aspect="album"``, it can print top ``num`` tracks if
        ``title=True``

        :param aspect: Can be ``"title"``, ``"artist"`` or ``"album"``
        :type aspect: str
        :param name: Name of aspect, e.g. name of song or artist
        :type name: str
        :param title: whether to show top ``num`` tracks, defaults to True
        :type title: bool, optional
        :param artist: if aspect is ``"title"`` or ``"album"``:
            whether to show artist, defaults to True
        :type artist: bool, optional
        :param album: for ``aspect="title"``: whether to show track's album;
            for ``aspect="artist"``: whether to show top ``num`` albums,
            defaults to False
        :type album: bool, optional
        :param streams: whether to show amount of streams for aspect
            and top lists, defaults to True
        :type streams: bool, optional
        :param num: depth of top list, defaults to 5
        :type num: int, optional
        :param percent: whether to show proportion of total streams to
            amount of streams of chosen aspect, defaults to False
        :type percent: bool, optional
        """

        # ERROR with num=1

        dataArray = self.data.get_streams_of(aspect)
        match = False
        for e in dataArray[1:]:
            if e[dataArray[0][0]] == name:
                if dataArray[0][0] == "title":
                    outputString = ""
                    if artist:
                        outputString += e["artist"] + " - "
                    outputString += name
                    if album:
                        outputString += " | " + e["album"]
                    if streams:
                        outputString += " | Streams: " + str(e["streams"])
                    if percent:
                        outputString += self.percent(e["streams"])
                    print(outputString)
                elif dataArray[0][0] == "artist":
                    outputString = name
                    if streams:
                        outputString += " | Streams: " + str(e["streams"])
                    if percent:
                        outputString += self.percent(e["streams"])
                    if title:
                        outputString += (
                            "\n\tMost Played Songs: \n\t\t1. " + e["title"][0][0]
                        )
                        if album:
                            outputString += " | " + e["title"][0][2]
                        if streams:
                            outputString += " | Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1, num):
                                outputString += (
                                    "\n\t\t" + str(j + 1) + ". " + e["title"][j][0]
                                )
                                if album:
                                    outputString += " | " + e["title"][j][2]
                                if streams:
                                    outputString += " | Streams: " + str(
                                        e["title"][j][1]
                                    )
                        except IndexError:
                            pass
                    if album:
                        outputString += (
                            "\n\tMost Played Albums: \n\t\t1. " + e["album"][0][0]
                        )
                        if streams:
                            outputString += " | Streams: " + str(e["album"][0][1])
                        try:
                            for j in range(1, num):
                                outputString += (
                                    "\n\t\t" + str(j + 1) + ". " + e["album"][j][0]
                                )
                                if streams:
                                    outputString += " | Streams: " + str(
                                        e["album"][j][1]
                                    )
                        except IndexError:
                            pass
                    print(outputString)
                elif dataArray[0][0] == "album":
                    outputString = ""
                    if artist:
                        outputString += e["artist"] + " - "
                    outputString += name
                    if streams:
                        outputString += " | Streams: " + str(e["streams"])
                    if percent:
                        outputString += self.percent(e["streams"])
                    if title:
                        outputString += (
                            "\n\tMost Played Songs: \n\t\t1. " + e["title"][0][0]
                        )
                    if streams:
                        outputString += " | Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1, num):
                                outputString += (
                                    "\n\t\t" + str(j + 1) + ". " + e["title"][j][0]
                                )
                                if streams:
                                    outputString += " | Streams: " + str(e["title"][j][1])
                        except IndexError:
                            pass
                    print(outputString)
                match = True
        if not match:
            print(name + " not found")

    def __prep_graphs(self, aspect, name, mode) -> None:
        fig, ax = plt.subplots()
        ts = self.data.prepare_graph(aspect, name)

        pylab.gcf().canvas.manager.set_window_title(mode + " streams over time")
        if ts[1] == "title":
            title = ts[2][1] + " - " + ts[2][2] + " (" + ts[2][0] + ")"
        elif ts[1] == "artist":
            title = ts[2][0]
        elif ts[1] == "album":
            title = ts[2][0] + " - " + ts[2][1]
        fig.autofmt_xdate()
        ax.set_title(title)
        ax.set_ylabel(mode + " streams")
        ax.set_xlim((ts[0][0], ts[0][-1]))
        plt.grid()

        return ax, ts[0]

    def graph_abs(self, aspect, name) -> None:
        """aspects are "title", "artist" and "album" \n
        name of the aspect\n
        graph absolute listened over time
        """
        ax, x = self.__prep_graphs(aspect, name, "absolute")

        y = list(np.linspace(0, len(x) - 2, len(x) - 1)) + [len(x) - 2]
        ax.plot_date(x, y, "k")

        ax.set_ylim(0)
        plt.show()

    def graph_rel(self, aspect, name) -> None:
        """aspects are "title", "artist" and "album" \n
        name of the aspect \n
        graph relative listened over time
        """
        ax, x = self.__prep_graphs(aspect, name, "relative")

        all_dy = []
        for i in range(len(x)):
            dy = 0
            for e in self.all_timestamps:
                if e < x[i].timestamp():
                    dy += 1
            all_dy += [dy]

        y = list(np.linspace(0, len(x) - 2, len(x) - 1)) + [len(x) - 2]
        for i in range(len(all_dy)):
            if all_dy[i] == 0:
                y[i] = 0
            else:
                y[i] = y[i] / all_dy[i] * 100

        ax.plot_date(x, y, "k")

        ax.set_ylim(0)
        plt.show()

    def set_bonds(self, earliest, latest) -> None:
        """Set the desired time frame

        ``-hh.mm.ss`` is optional

        :param earliest: date in "yyyy.mm.dd-hh.mm.ss" format
        :type earliest: str
        :param latest: date in "yyyy.mm.dd-hh.mm.ss" format
        :type latest: str
        """
        self.data.set_bonds(earliest, latest)

    def restore_bonds(self) -> None:
        """restores default"""
        self.data.restore_bonds()

    def list_with_names(self) -> None:
        """creates a file that contains all titles, artists and albums"""
        self.data.list_with_names()

    def percent(self, streams) -> str:
        # maybe make this method private?
        """Internal method used for calculating percentage of total
        streams of an aspect and formatting it nicely

        Rounds percentage to 5 decimal places

        :param streams: amount of streams
        :type streams: int
        :return: a string in ``" | <percentage>% of all"`` format
        :rtype: str
        """
        return " | " + str(round(streams / self.sum_all * 100, 5)) + "%" + " of all"


def init(paths, uri=False):
    """The function used for creating an object used for further
    visualization of data

    Creates a :class:`GatherData` object with ``paths`` argument and
    passes it to create a :class:`DisplayData` object. Returns the
    created object to be used for further data visualization by
    using its methods.

    :param paths: Either a single absolute path to endsong.json
        or list of paths to multiple endsong_x.json files
    :type paths: str or list
    :param uri: see :class:`GatherData`
    :type uri: bool, optional
    :return: a DisplayData object used to visualize data
    :rtype: DisplayData
    """
    return DisplayData(GatherData(paths))


## methods are:
## print_top prints most played songs, artists or albums,
## print_aspect prints one name of aspect (eg. aspect="artist",name="Eminem" prints everything of Eminem),
## print_sum prints the total amount of listened tracks,
## print_first_last prints first or last song of the data,
## graph_abs graphs absolute listened of aspect over time,
## graph_rel graphs realtive listened of aspect over time,
## set_bonds sets a timeframe,
## restore_bonds restores the default timeframe,
## list_with_names creates a list with all names

if __name__ == "__main__":

    paths = "/home/filip/Other/SpotifyData/2021-07/endsong_0.json"
    pathsWin = "D:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_0.json"

    # paths = [
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_0.json",
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_1.json",
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_2.json",
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_3.json",
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_4.json",
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_5.json",
    #     "/home/filip/Other/SpotifyData/2021-07/endsong_6.json",
    # ]

    d = init(paths)

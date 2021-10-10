#!/usr/bin/python3
import datetime as dt
import json
from enum import auto
from enum import Enum
from math import floor
from math import log10
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import matplotlib.pylab as pylab  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np

# docstrings: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html

# TODO: add examples to docstrings??
# TODO: run pylint and make the code achieve a good score!
#   also: maybe setup a GitHub Actions pylint workflow?
#   https://github.com/Filip-Tomasko/endsong-parser-python/actions/new
# TODO: enums
#   https://youtu.be/zmWf_cHyo8s
#   https://youtu.be/gPPDXgCMZ0k
# TODO: matplotlib type hints, stub files etc. for mypy
#   https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-type-hints-for-third-party-library


class Aspect(Enum):
    """Possible aspects used in arguments of methods

    track: Aspect.TRACK
    album: Aspect.ALBUM
    artist: Aspect.ARTIST
    """

    TRACK = "title"
    ALBUM = "album"
    ARTIST = "artist"
    # use this somehow https://youtu.be/LrtnLEkOwFE


class Field(Enum):
    ID = "id"
    STREAMS = "streams"
    TS = "timestamps"


class GatherData:
    """Used for parsing data from endsong.json to a Python list of dictionaries

    **WARNING**: it's highly likely to mix stuff up if artists have the same name -> to be tested!

    :param path: absolute path or list of absolute paths to ``endsong.json`` files
    :type path: str or list
    :param uri: if *True*: songs are identified by Spotify ID;
        if *False*: by name and artist
        (album and single versions are identified as one), defaults to *True*
    :type uri: bool, optional
    """

    # __slots__ = ["__info", "__leftbond", "__rightbond"]

    # __info: List[Dict[str, Union[str, int, List[str]]]]
    # TODO: correct type annotation for __info
    info: Any

    def __init__(self, path: Union[str, List[str]], uri: bool = True) -> None:
        self.info = []
        self.leftbond: float = 0.0
        self.rightbond: float = 2147483647.0
        self.collect_data(path, uri)

    def collect_data(self, path: Union[str, List[str]], uri: bool) -> None:
        # TODO: type checking of path without isintance, maybe using @property? setters?
        # https://www.youtube.com/watch?v=wf-BqAjZb8M
        if isinstance(path, list):
            lpath = path
        else:
            lpath = [path]

        for e in lpath:
            with open(e, "r", encoding="utf-8") as json_file:
                file = json.load(json_file)
                json_file.close()

            for f in file:
                if uri:
                    if f["spotify_track_uri"]:
                        i = 0
                        match = False
                        while i < len(self.info) and not match:
                            if self.info[i]["id"] == f["spotify_track_uri"]:
                                self.info[i]["timestamps"] += [f["ts"]]
                                match = True
                            i += 1
                        if not match:
                            self.info += [
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
                        while i < len(self.info) and not match:
                            if (
                                self.info[i]["title"] == f["master_metadata_track_name"]
                                and self.info[i]["artist"]
                                == f["master_metadata_album_artist_name"]
                            ):
                                self.info[i]["timestamps"] += [f["ts"]]
                                match = True
                            i += 1
                        if not match:
                            self.info += [
                                {
                                    "id": f["spotify_track_uri"],
                                    "title": f["master_metadata_track_name"],
                                    "artist": f["master_metadata_album_artist_name"],
                                    "streams": 1,
                                    "album": f["master_metadata_album_album_name"],
                                    "timestamps": [f["ts"]],
                                }
                            ]

        for i in range(len(self.info)):
            self.info[i]["streams"] = len(self.info[i]["timestamps"])

    # https://stackoverflow.com/a/38727786/6694963
    # args static typing with default value
    # PEP 3107
    def get_streams_of(self, aspect: Aspect = Aspect.TRACK) -> list:
        """Returns all of a specfic aspect from dataset ordered by
        number of streams.

        Use "set_bonds" to set a specific date range

        :param aspect: desired aspect, can be Aspect.TRACK, Aspect.ALBUM
            and Aspect.ARTIST
        :type aspect: Aspect, optional
        :return: array of dictionaries, where each dictionary is a single
            song with attributes "title", "artist", "album" and "streams"
        :rtype: list[dict]
        """

        # https://stackoverflow.com/a/62577297/6694963 for static typing
        # https://stackoverflow.com/a/37087556/6694963
        # streams_of: List[Union[Dict[Any], List[Any]]] = [
        #     [aspect.value, self.__leftbond, self.__rightbond]
        # ]
        # TODO: correct type annotation.. !!!!!!!!!!!1
        streams_of: Any = [[aspect.value, self.leftbond, self.rightbond]]

        for e in self.info:
            i = 1
            match = False
            while i < len(streams_of) and not match:
                if e[aspect.value] == streams_of[i][aspect.value]:
                    for j in range(len(e["timestamps"])):
                        if Time().in_period_of_time(
                            e["timestamps"][j], self.leftbond, self.rightbond
                        ):
                            streams_of[i]["streams"] += 1
                    if aspect == Aspect.ARTIST:
                        streams_of[i]["title"] += [
                            [e["title"], e["streams"], e["album"]]
                        ]
                    elif aspect == Aspect.ALBUM:
                        streams_of[i]["title"] += [[e["title"], e["streams"]]]
                    match = True
                i += 1

            if not match:
                if aspect == Aspect.TRACK:
                    streams_of += [
                        {
                            "title": e["title"],
                            "artist": e["artist"],
                            "album": e["album"],
                            "streams": 0,
                        }
                    ]
                elif aspect == Aspect.ARTIST:
                    streams_of += [
                        {"artist": e["artist"], "streams": 0, "title": [], "album": []}
                    ]
                elif aspect == Aspect.ALBUM:
                    streams_of += [
                        {
                            "album": e["album"],
                            "artist": e["artist"],
                            "streams": 0,
                            "title": [],
                        }
                    ]
                for j in range(len(e["timestamps"])):
                    if Time().in_period_of_time(
                        e["timestamps"][j], self.leftbond, self.rightbond
                    ):
                        streams_of[-1]["streams"] += 1
                if aspect == Aspect.ARTIST:
                    streams_of[-1]["title"] += [[e["title"], e["streams"], e["album"]]]
                elif aspect == Aspect.ALBUM:
                    streams_of[-1]["title"] += [[e["title"], e["streams"]]]
                if streams_of[-1]["streams"] == 0:
                    del streams_of[-1]

        if aspect == Aspect.ARTIST or aspect == Aspect.ALBUM:
            for e in streams_of[1:]:
                for _ in range(len(e["title"]) - 1):
                    for i in range(len(e["title"]) - 1):
                        if e["title"][i][1] < e["title"][i + 1][1]:
                            e["title"][i], e["title"][i + 1] = (
                                e["title"][i + 1],
                                e["title"][i],
                            )
        if aspect == Aspect.ARTIST:
            for e in streams_of[1:]:
                # TODO: make the type annotation better
                albums: List[Any] = []
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
        return self.sort_by_streams(streams_of)

    def sort_by_streams(self, items) -> list:
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
        for e in self.info:
            for i in range(len(e["timestamps"])):
                if Time().in_period_of_time(
                    e["timestamps"][i], self.leftbond, self.rightbond
                ):
                    sum_listened += 1
        return sum_listened

    def set_bonds(self, earliest, latest) -> None:
        """Set the desired time frame

        ``-hh.mm.ss`` is optional

        :param earliest: date in "yyyy.mm.dd-hh.mm.ss" format
        :type earliest: str
        :param latest: date in "yyyy.mm.dd-hh.mm.ss" format
        :type latest: str
        """
        self.leftbond = Time().convert_to_unix(earliest, -1)
        self.rightbond = Time().convert_to_unix(latest, -1)

    def restore_bonds(self) -> None:
        """Restores default bonda for date range
        (Unix time min and max)
        """
        self.leftbond = 0.0
        self.rightbond = 2147483647.0

    def get_first_ever(self) -> tuple:
        """Returns first ever streamed song listed in endsong.json

        :return: tuple of first ever streamed song with the song dictionary
            and the date as Unix timestamp;
            Note: "timestamps" value is a list of dates
        :rtype: tuple[dict, float]
        """
        earliest = 2147483647.0
        for i in range(len(self.info)):
            for j in range(len(self.info[i]["timestamps"])):
                if Time().convert_to_unix(self.info[i]["timestamps"][j]) < earliest:
                    earliest = Time().convert_to_unix(self.info[i]["timestamps"][j])
                    ret = self.info[i]
        return (ret, earliest)

    def get_last_of_data(self) -> tuple:
        """Returns the most recently streamed song listed in endsong.json

        :return: tuple of the most recently streamed song with the song
            dictionary and the date as Unix timestamp;
            Note: "timestamps" value is a list of dates
        :rtype: tuple[dict, float]
        """
        latest = 0.0
        for i in range(len(self.info)):
            for j in range(len(self.info[i]["timestamps"])):
                if Time().convert_to_unix(self.info[i]["timestamps"][j]) > latest:
                    latest = Time().convert_to_unix(self.info[i]["timestamps"][j])
                    ret = self.info[i]
        return (ret, latest)

    def list_with_names(self) -> None:
        """Creates a .txt file that contains all track names, artists and albums"""

        # so that you can look up how a particular song/arist is written

        titles: List[str]
        artists: List[str]
        albums: List[str]
        titles, artists, albums = [], [], []
        for e in self.info:
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

    def all_timestamps(self) -> list:
        """Returns list of all timestamps

        :return: list of all timestamps in endsong.json
        :rtype: list
        """
        timestamps = []
        for e in self.info:
            for f in e["timestamps"]:
                timestamps += [Time().convert_to_unix(f)]
        return timestamps


class Time:
    def __init__(self) -> None:
        pass

    def convert_to_unix(self, ts, offset=0) -> float:
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

    def in_period_of_time(self, ts, leftbond, rightbond) -> bool:
        if (
            self.convert_to_unix(ts) >= leftbond
            and self.convert_to_unix(ts) <= rightbond
        ):
            return True
        else:
            return False


class Graph:
    def __init__(self, gatheredData: GatherData) -> None:
        self.data = gatheredData

    def prepare_graph(self, aspect: Aspect, name: str) -> list:
        """prepares data to put in a graph \n
        aspects are "title", "artist" and "album" \n
        name of the aspect
        """
        times = []
        string = []
        for e in self.data.info:
            if e[aspect.value] == name:
                for f in e["timestamps"]:
                    if Time().in_period_of_time(
                        f, self.data.leftbond, self.data.rightbond
                    ):
                        times += [f]
                string += [e["artist"]]
                if aspect.value == "album" or aspect.value == "title":
                    string += [e["album"]]
                if aspect.value == "title":
                    string += [e["title"]]
        for _ in range(len(times) - 1):
            for i in range(len(times) - 1):
                if times[i] > times[i + 1]:
                    times[i], times[i + 1] = times[i + 1], times[i]
        for i in range(len(times)):
            times[i] = dt.datetime.utcfromtimestamp(
                Time().convert_to_unix(times[i])
            ) + dt.timedelta(hours=+1)
        return [
            [
                dt.datetime.utcfromtimestamp(self.data.get_first_ever()[1])
                + dt.timedelta(hours=+1)
            ]
            + times
            + [
                dt.datetime.utcfromtimestamp(self.data.get_last_of_data()[1])
                + dt.timedelta(hours=+1)
            ],
            aspect.value,
            string,
        ]

    def prep_graphs(self, aspect: Aspect, name: str, mode: str) -> Any:
        # TODO: fix type annotation, for return as well
        fig, ax = plt.subplots()
        ts = self.prepare_graph(aspect, name)

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

    def graph_abs(self, aspect: Aspect, name: str) -> None:
        """aspects are "title", "artist" and "album" \n
        name of the aspect\n
        graph absolute listened over time
        """
        ax, x = self.prep_graphs(aspect, name, "absolute")

        y = list(np.linspace(0, len(x) - 2, len(x) - 1)) + [len(x) - 2]
        ax.plot_date(x, y, "k")

        ax.set_ylim(0)
        plt.show()

    def graph_rel(self, aspect, name) -> None:
        """aspects are "title", "artist" and "album" \n
        name of the aspect \n
        graph relative listened over time
        """
        ax, x = self.prep_graphs(aspect, name, "relative")

        all_dy = []
        for i in range(len(x)):
            dy = 0
            # GatherData.all_timestamps() oder DisplayData.all_timestamps?
            # ursprünglich GatherData
            for e in self.data.all_timestamps():
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
        aspect: Aspect = Aspect.TRACK,
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
                output_string = topOrder(i, primaryNum)

                if artist:
                    output_string += dataArray[i]["artist"] + " - "
                output_string += dataArray[i]["title"]
                if album and title:
                    output_string += " | " + dataArray[i]["album"]
                if streams:
                    output_string += " | Streams: " + str(dataArray[i]["streams"])
                if percent:
                    output_string += self.percent(dataArray[i]["streams"])
                print(output_string)
        elif dataArray[0][0] == "artist":
            print("--- TOP ARTISTS ---")
            for i in range(1, primaryNum + 1):
                # for a nicer, more uniform list
                output_string = topOrder(i, primaryNum)

                output_string += dataArray[i]["artist"]
                if streams:
                    output_string += " | Streams: " + str(dataArray[i]["streams"])
                if percent:
                    output_string += self.percent(dataArray[i]["streams"])
                if title:
                    output_string += (
                        "\n\tMost Played Songs: \n\t\t1. " + dataArray[i]["title"][0][0]
                    )
                    if album:
                        output_string += " | " + dataArray[i]["title"][0][2]
                    if streams:
                        output_string += " | Streams: " + str(
                            dataArray[i]["title"][0][1]
                        )
                    try:
                        for j in range(1, secondaryNum):
                            output_string += (
                                "\n\t\t"
                                + str(j + 1)
                                + ". "
                                + dataArray[i]["title"][j][0]
                            )
                            if album:
                                output_string += " | " + dataArray[i]["title"][j][2]
                            if streams:
                                output_string += " | Streams: " + str(
                                    dataArray[i]["title"][j][1]
                                )
                    except IndexError:
                        pass
                if album:
                    output_string += (
                        "\n\tMost Played Albums: \n\t\t1. "
                        + dataArray[i]["album"][0][0]
                    )
                    if streams:
                        output_string += " | Streams: " + str(
                            dataArray[i]["album"][0][1]
                        )
                    try:
                        for j in range(1, secondaryNum):
                            output_string += (
                                "\n\t\t"
                                + str(j + 1)
                                + ". "
                                + dataArray[i]["album"][j][0]
                            )
                            if streams:
                                output_string += " | Streams: " + str(
                                    dataArray[i]["album"][j][1]
                                )
                    except IndexError:
                        pass
                print(output_string)
        elif dataArray[0][0] == "album":
            print("--- TOP ALBUMS ---")
            for i in range(1, primaryNum + 1):
                # for a nicer, more uniform list
                output_string = topOrder(i, primaryNum)

                if artist:
                    output_string += dataArray[i]["artist"] + " - "
                output_string += dataArray[i]["album"]
                if streams:
                    output_string += " | Streams: " + str(dataArray[i]["streams"])
                if percent:
                    output_string += self.percent(dataArray[i]["streams"])
                if title:
                    output_string += (
                        "\n\tMost Played Songs: \n\t\t1. " + dataArray[i]["title"][0][0]
                    )
                    if streams:
                        output_string += " | Streams: " + str(
                            dataArray[i]["title"][0][1]
                        )
                    try:
                        for j in range(1, secondaryNum):
                            output_string += (
                                "\n\t\t"
                                + str(j + 1)
                                + ". "
                                + dataArray[i]["title"][j][0]
                            )
                            if streams:
                                output_string += " | Streams: " + str(
                                    dataArray[i]["title"][j][1]
                                )
                    except:
                        pass
                print(output_string)

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
                    output_string = ""
                    if artist:
                        output_string += e["artist"] + " - "
                    output_string += name
                    if album:
                        output_string += " | " + e["album"]
                    if streams:
                        output_string += " | Streams: " + str(e["streams"])
                    if percent:
                        output_string += self.percent(e["streams"])
                    print(output_string)
                elif dataArray[0][0] == "artist":
                    output_string = name
                    if streams:
                        output_string += " | Streams: " + str(e["streams"])
                    if percent:
                        output_string += self.percent(e["streams"])
                    if title:
                        output_string += (
                            "\n\tMost Played Songs: \n\t\t1. " + e["title"][0][0]
                        )
                        if album:
                            output_string += " | " + e["title"][0][2]
                        if streams:
                            output_string += " | Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1, num):
                                output_string += (
                                    "\n\t\t" + str(j + 1) + ". " + e["title"][j][0]
                                )
                                if album:
                                    output_string += " | " + e["title"][j][2]
                                if streams:
                                    output_string += " | Streams: " + str(
                                        e["title"][j][1]
                                    )
                        except IndexError:
                            pass
                    if album:
                        output_string += (
                            "\n\tMost Played Albums: \n\t\t1. " + e["album"][0][0]
                        )
                        if streams:
                            output_string += " | Streams: " + str(e["album"][0][1])
                        try:
                            for j in range(1, num):
                                output_string += (
                                    "\n\t\t" + str(j + 1) + ". " + e["album"][j][0]
                                )
                                if streams:
                                    output_string += " | Streams: " + str(
                                        e["album"][j][1]
                                    )
                        except IndexError:
                            pass
                    print(output_string)
                elif dataArray[0][0] == "album":
                    output_string = ""
                    if artist:
                        output_string += e["artist"] + " - "
                    output_string += name
                    if streams:
                        output_string += " | Streams: " + str(e["streams"])
                    if percent:
                        output_string += self.percent(e["streams"])
                    if title:
                        output_string += (
                            "\n\tMost Played Songs: \n\t\t1. " + e["title"][0][0]
                        )
                    if streams:
                        output_string += " | Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1, num):
                                output_string += (
                                    "\n\t\t" + str(j + 1) + ". " + e["title"][j][0]
                                )
                                if streams:
                                    output_string += " | Streams: " + str(
                                        e["title"][j][1]
                                    )
                        except IndexError:
                            pass
                    print(output_string)
                match = True
        if not match:
            print(name + " not found")

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

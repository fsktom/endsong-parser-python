import datetime as dt
import json

import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import numpy as np


class Gain_Data:
    """absolute path or list of absolute paths to "endsong.json" files \n
    if uri is True songs are identified by spotify id \n
    else songs are identified by name und artist \n
    with uri false album and single version will be interpreted as one
    """

    __slots__ = ["__info", "__leftbond", "__rightbond"]

    def __init__(self, path, uri=True):
        self.__info = []
        self.__leftbond = 0
        self.__rightbond = 2147483647
        self.__collect_data(path, uri)

    def __collect_data(self, path, uri):
        if isinstance(path, (list, tuple)):
            lpath = path
        else:
            lpath = [path]

        for e in lpath:
            with open(e, encoding="utf-8") as jsonFile:
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

    def get_streams_of(self, aspect="title"):
        """return all of aspect ordered by number of streams \n
        aspects are "title", "artist" and "album" \n
        set specific period of time via "set_bonds"
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
        return self.__sort_by_streams(streams_of)

    def __sort_by_streams(self, items):
        for _ in range(1, len(items) - 1):
            for i in range(1, len(items) - 1):
                if items[i]["streams"] < items[i + 1]["streams"]:
                    items[i], items[i + 1] = items[i + 1], items[i]
        return items

    def get_sum(self):
        """return the sum of all streams in given period"""
        sum_listened = 0
        for e in self.__info:
            for i in range(len(e["timestamps"])):
                if self.__in_period_of_time(e["timestamps"][i]):
                    sum_listened += 1
        return sum_listened

    def __convert_to_unix(self, ts, offset=0):
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

    def __in_period_of_time(self, ts):
        if (
            self.__convert_to_unix(ts) >= self.__leftbond
            and self.__convert_to_unix(ts) <= self.__rightbond
        ):
            return True
        else:
            return False

    def set_bonds(self, earliest, latest):
        """set a time frame \n
        format: yyyy.mm.dd-hh.mm.ss \n
        default is 1970.01.01 till time ends \n
        hh.mm.ss is optional
        """
        self.__leftbond = self.__convert_to_unix(earliest, -1)
        self.__rightbond = self.__convert_to_unix(latest, -1)

    def restore_bonds(self):
        """restores default"""
        self.__leftbond = 0
        self.__rightbond = 2147483647

    def get_first_ever(self):
        """returns first streamed song of endsong.json"""
        earliest = 2147483647
        for i in range(len(self.__info)):
            for j in range(len(self.__info[i]["timestamps"])):
                if self.__convert_to_unix(self.__info[i]["timestamps"][j]) < earliest:
                    earliest = self.__convert_to_unix(self.__info[i]["timestamps"][j])
                    ret = self.__info[i]
        return (ret, earliest)

    def get_last_of_data(self):
        """returns last streamed song of endsong.json"""
        latest = 0
        for i in range(len(self.__info)):
            for j in range(len(self.__info[i]["timestamps"])):
                if self.__convert_to_unix(self.__info[i]["timestamps"][j]) > latest:
                    latest = self.__convert_to_unix(self.__info[i]["timestamps"][j])
                    ret = self.__info[i]
        return (ret, latest)

    def list_with_names(self):
        """creates a file that contains all titles, artists and albums"""
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

    def prepare_graph(self, aspect, name):
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

    def all_timestamps(self):
        """returns list of all timestamps"""
        timestamps = []
        for e in self.__info:
            for f in e["timestamps"]:
                timestamps += [self.__convert_to_unix(f)]
        return timestamps


class output_Data:
    """class to visualize data from endsong.json files"""

    def __init__(self, paths, uri=True):
        """absolute path or list of absolute paths to "endsong.json" files \n
        if uri is True songs are identified by spotify id \n
        else songs are identified by name und artist \n
        with uri false album and single version will be interpreted as one
        """
        self.data = Gain_Data(paths, uri)
        self.sum_all = self.data.get_sum()
        self.first = self.data.get_first_ever()
        self.last = self.data.get_last_of_data()
        self.all_timestamps = self.data.all_timestamps()

    def print_top_songs(
        self,
        aspect,
        title=True,
        artist=True,
        album=False,
        streams=True,
        mainindex=10,
        secindex=5,
        percentages=False,
    ):
        """prints most played songs, artists or albums \n
        aspects are "title", "artist" and "album" \n
        shows most played songs of chosen aspect \n
        whether to show titles, artists, albums and number of streams \n
        top n of chosen aspect and top m tracks \n
        whether to show percentages
        """
        array = self.data.get_streams_of(aspect)
        sum_all = self.sum_all
        print(
            "Between "
            + str(dt.datetime.utcfromtimestamp(array[0][1]) + dt.timedelta(hours=+1))
            + " and "
            + str(dt.datetime.utcfromtimestamp(array[0][2]) + dt.timedelta(hours=+1))
            + ":"
        )
        if array[0][0] == "title":
            for i in range(1, mainindex + 1):
                string = str(i)
                string += ". Title: " + array[i]["title"]
                if artist:
                    string += " from " + array[i]["artist"]
                if album:
                    string += " from " + array[i]["album"]
                if streams:
                    string += ", Streams: " + str(array[i]["streams"])
                if percentages:
                    string += (
                        " ("
                        + str(round(array[i]["streams"] / sum_all * 100, 5))
                        + "% of all)"
                    )
                print(string)
        elif array[0][0] == "artist":
            for i in range(1, mainindex + 1):
                string = str(i)
                string += ". Artist: " + array[i]["artist"]
                if streams:
                    string += ", Streams: " + str(array[i]["streams"])
                if percentages:
                    string += (
                        " ("
                        + str(round(array[i]["streams"] / sum_all * 100, 5))
                        + "% of all)"
                    )
                if title:
                    string += ", Most Played Songs: {1. " + array[i]["title"][0][0]
                    if album:
                        string += " from " + array[i]["title"][0][2]
                    if streams:
                        string += ", Streams: " + str(array[i]["title"][0][1])
                    try:
                        for j in range(1, secindex):
                            string += "; " + str(j + 1) + ". " + array[i]["title"][j][0]
                            if album:
                                string += " from " + array[i]["title"][j][2]
                            if streams:
                                string += ", Streams: " + str(array[i]["title"][j][1])
                    except IndexError:
                        pass
                    string += "}"
                if album:
                    string += ", Most Played Albums: {1. " + array[i]["album"][0][0]
                    if streams:
                        string += ", Streams: " + str(array[i]["album"][0][1])
                    try:
                        for j in range(1, secindex):
                            string += "; " + str(j + 1) + ". " + array[i]["album"][j][0]
                            if streams:
                                string += ", Streams: " + str(array[i]["album"][j][1])
                    except IndexError:
                        pass
                    string += "}"
                print(string)
        elif array[0][0] == "album":
            for i in range(1, mainindex + 1):
                string = str(i)
                string += ". album: " + array[i]["album"]
                if artist:
                    string += " from " + array[i]["artist"]
                if streams:
                    string += ", Streams: " + str(array[i]["streams"])
                if percentages:
                    string += (
                        " ("
                        + str(round(array[i]["streams"] / sum_all * 100, 5))
                        + "% of all)"
                    )
                if title:
                    string += ", Most Played Songs: {1. " + array[i]["title"][0][0]
                    if streams:
                        string += ", Streams: " + str(array[i]["title"][0][1])
                    try:
                        for j in range(1, secindex):
                            string += "; " + str(j + 1) + ". " + array[i]["title"][j][0]
                            if streams:
                                string += ", Streams: " + str(array[i]["title"][j][1])
                    except:
                        pass
                    string += "}"
                print(string)

    def print_sum(self):
        """prints total amount of listened tracks"""
        print("You listened to " + str(self.sum_all) + " songs")

    def print_first_last(self, fl=True):
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
        index=5,
        percentages=False,
    ):
        """prints one name of aspect (eg. aspect="artist",name="Eminem" prints everything of Eminem) \n
        aspects are "title", "artist" and "album" \n
        name of the aspect \n
        whether to show titles, artists, albums and number of streams \n
        top n tracks \n
        whether to show percentages
        """
        array = self.data.get_streams_of(aspect)
        sum_all = self.sum_all
        match = False
        for e in array[1:]:
            if e[array[0][0]] == name:
                if array[0][0] == "title":
                    string = name
                    if artist:
                        string += " from " + e["artist"]
                    if album:
                        string += " from " + e["album"]
                    if streams:
                        string += ", Streams: " + str(e["streams"])
                    if percentages:
                        string += (
                            " ("
                            + str(round(e["streams"] / sum_all * 100, 5))
                            + "% of all)"
                        )
                    print(string)
                elif array[0][0] == "artist":
                    string = name
                    if streams:
                        string += ", Streams: " + str(e["streams"])
                    if percentages:
                        string += (
                            " ("
                            + str(round(e["streams"] / sum_all * 100, 5))
                            + "% of all)"
                        )
                    if title:
                        string += ", Most Played Songs: {1. " + e["title"][0][0]
                        if album:
                            string += " from " + e["title"][0][2]
                        if streams:
                            string += ", Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1, index):
                                string += "; " + str(j + 1) + ". " + e["title"][j][0]
                                if album:
                                    string += " from " + e["title"][j][2]
                                if streams:
                                    string += ", Streams: " + str(e["title"][j][1])
                        except IndexError:
                            pass
                        string += "}"
                    if album:
                        string += ", Most Played Albums: {1. " + e["album"][0][0]
                        if streams:
                            string += ", Streams: " + str(e["album"][0][1])
                        try:
                            for j in range(1, index):
                                string += "; " + str(j + 1) + ". " + e["album"][j][0]
                                if streams:
                                    string += ", Streams: " + str(e["album"][j][1])
                        except IndexError:
                            pass
                        string += "}"
                    print(string)
                elif array[0][0] == "album":
                    string = name
                    if artist:
                        string += " from " + e["artist"]
                    if streams:
                        string += ", Streams: " + str(e["streams"])
                    if percentages:
                        string += (
                            " ("
                            + str(round(e["streams"] / sum_all * 100, 5))
                            + "% of all)"
                        )
                    if title:
                        string += ", Most Played Songs: {1. " + e["title"][0][0]
                        if streams:
                            string += ", Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1, index):
                                string += "; " + str(j + 1) + ". " + e["title"][j][0]
                                if streams:
                                    string += ", Streams: " + str(e["title"][j][1])
                        except IndexError:
                            pass
                        string += "}"
                    print(string)
                match = True
        if not match:
            print(name + " not found")

    def __prep_graphs(self, aspect, name, mode):
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

    def graph_abs(self, aspect, name):
        """aspects are "title", "artist" and "album" \n
        name of the aspect\n
        graph absolute listened over time
        """
        ax, x = self.__prep_graphs(aspect, name, "absolute")

        y = list(np.linspace(0, len(x) - 2, len(x) - 1)) + [len(x) - 2]
        ax.plot_date(x, y, "k")

        ax.set_ylim(0)
        plt.show()

    def graph_rel(self, aspect, name):
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

    def set_bonds(self, earliest, latest):
        """set a time frame \n
        format: yyyy.mm.dd-hh.mm.ss \n
        default is 1970.01.01 till time ends \n
        hh.mm.ss is optional
        """
        self.data.set_bonds(earliest, latest)

    def restore_bonds(self):
        """restores default"""
        self.data.restore_bonds()

    def list_with_names(self):
        """creates a file that contains all titles, artists and albums"""
        self.data.list_with_names()


paths = [
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_0.json",
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_1.json",
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_2.json",
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_3.json",
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_4.json",
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_5.json",
    "d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_6.json",
]

## methods are:
## print_top_songs prints most played songs, artists or albums,
## print_aspect prints one name of aspect (eg. aspect="artist",name="Eminem" prints everything of Eminem),
## print_sum prints the total amount of listened tracks,
## print_first_last prints first or last song of the data,
## graph_abs graphs absolute listened of aspect over time,
## graph_rel graphs realtive listened of aspect over time,
## set_bonds sets a timeframe,
## restore_bonds restores the default timeframe,
## list_with_names creates a list with all names

d = output_Data(paths, False)


# if __name__ == "__main__":
# d.graph_rel("artist", "Survive Said The Prophet")

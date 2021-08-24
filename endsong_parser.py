import json
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import numpy as np

class Gain_Data():
    """absolute path or list of absolute paths to "endsong.json" files \n
    if uri is True songs are identified by spotify id \n
    else False songs are identified by name und artist \n
    """
    __slots__ = ["__info", "__leftbond", "__rightbond"]

    def __init__(self,path,uri=True):
        self.__info = []
        self.__leftbond = 0
        self.__rightbond = 2147483647
        self.__collect_data(path,uri)
        
    def __collect_data(self,path,uri):
        if isinstance(path, (list,tuple)): lpath = path
        else: lpath = ([path])

        for e in lpath:
            with open(e,"r",encoding="utf-8") as jsonFile:
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
                            self.__info += [{"id": f["spotify_track_uri"],"title": f["master_metadata_track_name"],"artist": f["master_metadata_album_artist_name"],"streams": 1,"album": f["master_metadata_album_album_name"],"timestamps": [f["ts"]]}]
                else:
                    if f["master_metadata_track_name"] or f["master_metadata_album_artist_name"]:
                        i = 0
                        match = False
                        while i < len(self.__info) and not match:
                            if self.__info[i]["title"] == f["master_metadata_track_name"] and self.__info[i]["artist"] == f["master_metadata_album_artist_name"]:
                                self.__info[i]["timestamps"] += [f["ts"]]
                                match = True
                            i += 1
                        if not match:
                            self.__info += [{"id": f["spotify_track_uri"],"title": f["master_metadata_track_name"],"artist": f["master_metadata_album_artist_name"],"streams": 1,"album": f["master_metadata_album_album_name"],"timestamps": [f["ts"]]}]

        for i in range(len(self.__info)):
            self.__info[i]["streams"] = len(self.__info[i]["timestamps"])

    def get_streams_of(self,aspect="title"):
        """return number of streams \n
        aspects are "title", "artist" and "album"
        set specific period of time via "set_bonds"
        """
        streams_of = [[aspect,self.__leftbond,self.__rightbond]]
        for e in self.__info:
            i = 1
            match = False
            while i < len(streams_of) and not match:
                if e[aspect] == streams_of[i][aspect]:
                    for j in range(len(e["timestamps"])):
                        if self.__in_period_of_time(e["timestamps"][j]):
                            streams_of[i]["streams"] += 1
                    if aspect == "artist":
                        streams_of[i]["title"] += [[e["title"],e["streams"],e["album"]]]
                    elif aspect == "album":
                        streams_of[i]["title"] += [[e["title"],e["streams"]]]
                    match = True
                i += 1

            if not match:
                if aspect == "title": 
                    streams_of += [{"title": e["title"],"artist": e["artist"],"album": e["album"],"streams": 0}]
                elif aspect == "artist": 
                    streams_of += [{"artist": e["artist"],"streams": 0,"title": []}]
                elif aspect == "album": 
                    streams_of += [{"album": e["album"],"artist": e["artist"],"streams": 0,"title": []}]
                for j in range(len(e["timestamps"])):
                    if self.__in_period_of_time(e["timestamps"][j]):
                        streams_of[-1]["streams"] += 1
                if aspect == "artist":
                    streams_of[-1]["title"] += [[e["title"],e["streams"],e["album"]]]
                elif aspect == "album":
                    streams_of[-1]["title"] += [[e["title"],e["streams"]]]
                if streams_of[-1]["streams"] == 0:
                    del streams_of[-1]

        if aspect == "artist" or aspect == "album":
            for e in streams_of[1:]:
                for _ in range(len(e["title"])-1):
                    for i in range(len(e["title"])-1):
                        if e["title"][i][1] < e["title"][i+1][1]:
                            e["title"][i], e["title"][i+1] = e["title"][i+1], e["title"][i]
        return self.__sort_by_streams(streams_of)

    def __sort_by_streams(self,items):
        for _ in range(1,len(items)-1):
            for i in range(1,len(items)-1):
                if items[i]["streams"] < items[i+1]["streams"]:
                    items[i], items[i+1] = items[i+1], items[i]
        return items
    
    def get_sum(self):
        """return the sum of all streams in given period
        """
        sum_listened = 0
        for e in self.__info:
            for i in range(len(e["timestamps"])):
                if self.__in_period_of_time(e["timestamps"][i]):
                    sum_listened += 1
        return sum_listened

    def __convert_to_unix(self,ts,offset=0):
        try:
            return (dt.datetime(int(ts[:4]),int(ts[5:7]),int(ts[8:10]),int(ts[11:13]),int(ts[14:16]),int(ts[17:19]),tzinfo=dt.timezone.utc) + dt.timedelta(hours=offset)).timestamp()
        except ValueError:
            return dt.datetime(int(ts[:4]),int(ts[5:7]),int(ts[8:10]),tzinfo=dt.timezone.utc).timestamp()

    def __in_period_of_time(self,ts):
        if self.__convert_to_unix(ts) >= self.__leftbond and self.__convert_to_unix(ts) <= self.__rightbond: return True
        else: return False

    def set_bonds(self,earliest,latest):
        """set a time frame \n
        format: yyyy.mm.dd-hh.mm.ss \n
        default is 1970.01.01 till time ends \n
        hh.mm.ss is optional
        """
        self.__leftbond = self.__convert_to_unix(earliest,-1)
        self.__rightbond = self.__convert_to_unix(latest,-1)

    def restore_bonds(self):
        """restores default
        """
        self.__leftbond = 0
        self.__rightbond = 2147483647

    def get_first_ever(self):
        """returns first streamed song of all time
        """
        earliest = 2147483647
        for i in range(len(self.__info)):
            for j in range(len(self.__info[i]["timestamps"])):
                if self.__convert_to_unix(self.__info[i]["timestamps"][j]) < earliest:
                    earliest = self.__convert_to_unix(self.__info[i]["timestamps"][j])
                    ret = self.__info[i]
        return (ret, earliest)

    def get_last_of_data(self):
        """returns last streamed song of the endsong.json
        """
        latest = 0
        for i in range(len(self.__info)):
            for j in range(len(self.__info[i]["timestamps"])):
                if self.__convert_to_unix(self.__info[i]["timestamps"][j]) > latest:
                    latest = self.__convert_to_unix(self.__info[i]["timestamps"][j])
                    ret = self.__info[i]
        return (ret, latest)

    def list_with_names(self):
        """creates a file that contains all titels, artists and albums
        """
        titels, artists, albums = [], [], []
        for e in self.__info:
            titels += [e["title"]]
            ai = False
            for f in artists:
                if f == e["artist"]:
                    ai = True
            if not ai: artists += [e["artist"]]
            ai = False
            for f in albums:
                if f == e["album"]:
                    ai = True
            if not ai: albums += [e["album"]]
        
        file = open("names.txt", "a", encoding="utf8")
        file.write("ALL TITLES\n")
        for e in titels:
            file.write(e + "\n")
        file.write("\nALL ARTISTS\n")
        for e in artists:
            file.write(e + "\n")
        file.write("\nALL ALBUMS\n")
        for e in albums:
            file.write(e + "\n")
        file.close()
        print("saved as names.txt")

    def prepare_graph(self,aspect,name):
        times = []
        string = []
        for e in self.__info:
            if e[aspect] == name:
                for f in e["timestamps"]:
                    if self.__in_period_of_time(f):
                        times += [f]
                string += [e["artist"]]
                if aspect == "album" or aspect == "title": string += [e["album"]]
                if aspect == "title": string += [e["title"]]
        for _ in range(len(times)-1):
            for i in range(len(times)-1):
                if times[i] > times[i+1]:
                    times[i], times[i+1] = times[i+1], times[i]
        for i in range(len(times)):
            times[i] = dt.datetime.utcfromtimestamp(self.__convert_to_unix(times[i])) + dt.timedelta(hours=+1)
        return [[dt.datetime.utcfromtimestamp(self.get_first_ever()[1]) + dt.timedelta(hours=+1)] + times + [dt.datetime.utcfromtimestamp(self.get_last_of_data()[1]) + dt.timedelta(hours=+1)],aspect,string]


class output_Data():
    """class to print out the data gathered
    """
    def __init__(self):
        pass

    def print_console(self,array,title=True,artist=True,album=False,streams=True,mainindex=10,secindex=5,percentages=None):
        """array returned by "Gain_Data.get_streams_of" \n
        wheter to show titels, artists, albums and number of streams \n
        how many to print of mainaspect and how many titels of artist or album \n
        number of all listened to print percentages of
        """
        print("Between " + str(dt.datetime.utcfromtimestamp(array[0][1]) + dt.timedelta(hours=+1)) + " and " + str(dt.datetime.utcfromtimestamp(array[0][2]) + dt.timedelta(hours=+1)) + ":")
        if array[0][0] == "title":
            for i in range(1,mainindex+1):
                string = str(i)
                string += ". Title: " + array[i]["title"]
                if artist: string += " from " + array[i]["artist"]
                if album: string += " from " + array[i]["album"]
                if streams: string += ", Streams: " + str(array[i]["streams"])
                if percentages: string += " (" + str(round(array[i]["streams"] / percentages * 100,5)) + "% of all)"
                print(string)
        elif array[0][0] == "artist":
            for i in range(1,mainindex+1):
                string = str(i)
                string += ". Artist: " + array[i]["artist"]
                if streams: string += ", Streams: " + str(array[i]["streams"])
                if percentages: string += " (" + str(round(array[i]["streams"] / percentages * 100,5)) + "% of all)"
                if title: 
                    string += ", Most Played Songs: {1. " + array[i]["title"][0][0]
                    if album: string += " from " + array[i]["title"][0][2]
                    string += ", Streams: " + str(array[i]["title"][0][1])
                    try:
                        for j in range(1,secindex):
                            string += "; " + str(j+1) + ". " + array[i]["title"][j][0]
                            if album: string += " from " + array[i]["title"][j][2]
                            string += ", Streams: " + str(array[i]["title"][j][1])
                    except IndexError:
                        pass
                    string += "}"
                print(string)
        elif array[0][0] == "album":
            for i in range(1,mainindex+1):
                string = str(i)
                string += ". album: " + array[i]["album"]
                if artist: string += " from " + array[i]["artist"]
                if streams: string += ", Streams: " + str(array[i]["streams"])
                if percentages: string += " (" + str(round(array[i]["streams"] / percentages * 100,5)) + "% of all)"
                if title: 
                    string += ", Most Played Songs: {1. " + array[i]["title"][0][0]
                    string += ", Streams: " + str(array[i]["title"][0][1])
                    try:
                        for j in range(1,secindex):
                            string += "; " + str(j+1) + ". " + array[i]["title"][j][0]
                            string += ", Streams: " + str(array[i]["title"][j][1])
                    except:
                        pass
                    string += "}"
                print(string)

    def print_sum(self,sum_of):
        """enter sum of all listened
        """
        print("You listened to " + str(sum_of) + " songs")

    def print_first_last(self,fl):
        """enter first/last song
        """
        print("Song " + fl[0]["title"] + " from " + fl[0]["artist"] + " from " + fl[0]["album"] + ", Streams: " + str(fl[0]["streams"]) + ", first/last listened at " + str(dt.datetime.utcfromtimestamp(fl[1]) + dt.timedelta(hours=+1)))

    def print_aspect(self,array,name,title=True,artist=True,album=False,streams=True,index=5,percentages=None):
        """array returned by "Gain_Data.get_streams_of" \n
        wheter to show titels, artists, albums and number of streams \n
        how many to print of most played titels \n
        number of all listened to print percentages of
        """
        match = False
        for e in array[1:]:
            if e[array[0][0]] == name:
                if array[0][0] == "title": 
                    string = name
                    if artist: string += " from " + e["artist"]
                    if album: string += " from " + e["album"]
                    if streams: string += ", Streams: " + str(e["streams"])
                    if percentages: string += " (" + str(round(e["streams"] / percentages * 100,5)) + "% of all)"
                    print(string)
                elif array[0][0] == "artist":
                    string = name
                    if streams: string += ", Streams: " + str(e["streams"])
                    if percentages: string += " (" + str(round(e["streams"] / percentages * 100,5)) + "% of all)"
                    if title: 
                        string += ", Most Played Songs: {1. " + e["title"][0][0]
                        if album: string += " from " + e["title"][0][2]
                        string += ", Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1,index):
                                string += "; " + str(j+1) + ". " + e["title"][j][0]
                                if album: string += " from " + e["title"][j][2]
                                string += ", Streams: " + str(e["title"][j][1])
                        except IndexError:
                            pass
                        string += "}"
                    print(string)
                elif array[0][0] == "album":
                    string = name
                    if artist: string += " from " + e["artist"]
                    if streams: string += ", Streams: " + str(e["streams"])
                    if percentages: string += " (" + str(round(e["streams"] / percentages * 100,5)) + "% of all)"
                    if title: 
                        string += ", Most Played Songs: {1. " + e["title"][0][0]
                        string += ", Streams: " + str(e["title"][0][1])
                        try:
                            for j in range(1,index):
                                string += "; " + str(j+1) + ". " + e["title"][j][0]
                                string += ", Streams: " + str(e["title"][j][1])
                        except IndexError:
                            pass
                        string += "}"
                    print(string)
                match = True
        if not match:
            print(name + " not found")
    
    def graph(self,ts):
        """array returned by "prepare_graph" \n
        graph absolute listened with time
        """
        fig, ax = plt.subplots()
        pylab.gcf().canvas.manager.set_window_title("absolute streams | time")
        if ts[1] == "title": title = ts[2][2] + " from " + ts[2][0] + " from " + ts[2][1]
        elif ts[1] == "artist": title = ts[2][0]
        elif ts[1] == "album": title = ts[2][1] + " from " + ts[2][0]
        fig.autofmt_xdate()
        y = list(np.linspace(0,len(ts[0])-2,len(ts[0])-1)) + [len(ts[0])-2]
        ax.plot_date(ts[0],y,"k")
        ax.set_title(title)
        ax.set_ylabel("Streams")
        ax.set_xlim((ts[0][0],ts[0][-1]))
        ax.set_ylim(0)
        plt.grid()
        plt.show()


paths = ["c:\\Users\\Lulas\\Downloads\\MyData\\endsong_0.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_1.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_2.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_3.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_4.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_5.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_6.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_7.json"]

data = Gain_Data(paths,False)
#topalben = data.get_streams_of("title")
output_Data().graph(data.prepare_graph("album","A Thousand Suns"))
#print(data.prepare_graph("album","amo"))
#output_Data().print_aspect(topalben,"Believer",album=True)
#output_Data().print_first_last(data.get_last_of_data())
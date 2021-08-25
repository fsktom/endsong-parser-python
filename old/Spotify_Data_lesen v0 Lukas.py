import json
import datetime as dt

class Gain_Data():
    """must start with either "collect_data_id" or "collect_data_names"
    """
    __slots__ = ["__info", "__leftbond", "__rightbond"]

    def __init__(self):
        self.__info = []
        self.__leftbond = 0
        self.__rightbond = 2147483647

    def collect_data_id(self,path): #verstecken und in init aufrufen
        """enter absolute path or list of absolute paths to "endsong.json" files \n
        collects data to songs \n
        identifies unique songs via its id
        """
        if isinstance(path, (list,tuple)): lpath = path
        else: lpath = ([path])

        for e in lpath:
            with open(e,"r",encoding="utf-8") as jsonFile:
                file = json.load(jsonFile)
                jsonFile.close()

            for f in file:
                if f["spotify_track_uri"]:
                    i = 0
                    match = False
                    while i < len(self.__info) and not match:
                        if self.__info[i]["ID"] == f["spotify_track_uri"]:
                            self.__info[i]["AnzahlStreams"] += 1 #am ende durch länge der zeitpunkte?
                            self.__info[i]["Zeitpunkte"] += [f["ts"]]
                            match = True
                        i += 1
                    if not match:
                        self.__info += [{"ID": f["spotify_track_uri"],"Titel": f["master_metadata_track_name"],"Künstler": f["master_metadata_album_artist_name"],"AnzahlStreams": 1,"Album": f["master_metadata_album_album_name"],"Zeitpunkte": [f["ts"]]}]

    def collect_data_names(self,path):
        """enter absolute path or list of absolute paths to "endsong.json" files \n
        collects data to songs \n
        identifies unique songs via its name and artist
        """
        if isinstance(path, (list,tuple)): lpath = path
        else: lpath = ([path])

        for e in lpath:
            with open(e,"r",encoding="utf-8") as jsonFile:
                file = json.load(jsonFile)
                jsonFile.close()

            for f in file:
                if f["master_metadata_track_name"] or f["master_metadata_album_artist_name"]:
                    i = 0
                    match = False
                    while i < len(self.__info) and not match:
                        if self.__info[i]["Titel"] == f["master_metadata_track_name"] and self.__info[i]["Künstler"] == f["master_metadata_album_artist_name"]:
                            self.__info[i]["AnzahlStreams"] += 1
                            self.__info[i]["Zeitpunkte"] += [f["ts"]]
                            match = True
                        i += 1
                    if not match:
                        self.__info += [{"Titel": f["master_metadata_track_name"],"Künstler": f["master_metadata_album_artist_name"],"AnzahlStreams": 1,"Album": f["master_metadata_album_album_name"],"Zeitpunkte": [f["ts"]]}]

    # def get_streams_of_songs(self):
    #     streams_of_song = []
    #     for e in self.__info:
    #         i = 0
    #         match = False
    #         while i < len(streams_of_song) and not match:
    #             if e["Titel"] == streams_of_song[i][0]:
    #                 for j in range(len(e["Zeitpunkte"])):
    #                     if self.__in_period_of_time(self.__leftbond,self.__rightbond,e["Zeitpunkte"][j]):
    #                         streams_of_song[i][1] += 1
    #                 match = True
    #             i += 1
    #         if not match:
    #             streams_of_song += [[e["Titel"],0]]
    #             for j in range(len(e["Zeitpunkte"])):
    #                 if self.__in_period_of_time(self.__leftbond,self.__rightbond,e["Zeitpunkte"][j]):
    #                     streams_of_song[-1][1] += 1
    #             if streams_of_song[-1][1] == 0:
    #                 del streams_of_song[-1]
    #     return self.__sortlist(streams_of_song)

    # def get_streams_of_artist(self):
    #     streams_of_artist = []
    #     for e in self.__info:
    #         i = 0
    #         match = False
    #         while i < len(streams_of_artist) and not match:
    #             if e["Künstler"] == streams_of_artist[i][0]:
    #                 for j in range(len(e["Zeitpunkte"])):
    #                     if self.__in_period_of_time(self.__leftbond,self.__rightbond,e["Zeitpunkte"][j]):
    #                         streams_of_artist[i][1] += 1
    #                 match = True
    #             i += 1
    #         if not match:
    #             streams_of_artist += [[e["Künstler"],0]]
    #             for j in range(len(e["Zeitpunkte"])):
    #                 if self.__in_period_of_time(self.__leftbond,self.__rightbond,e["Zeitpunkte"][j]):
    #                     streams_of_artist[-1][1] += 1
    #             if streams_of_artist[-1][1] == 0:
    #                 del streams_of_artist[-1]
    #     return self.__sortlist(streams_of_artist)

    # def get_streams_of_album(self):
    #     streams_of_album = []
    #     for e in self.__info:
    #         i = 0
    #         match = False
    #         while i < len(streams_of_album) and not match:
    #             if e["Album"] == streams_of_album[i][0]:
    #                 for j in range(len(e["Zeitpunkte"])):
    #                     if self.__in_period_of_time(self.__leftbond,self.__rightbond,e["Zeitpunkte"][j]):
    #                         streams_of_album[i][1] += 1
    #                 match = True
    #             i += 1
    #         if not match:
    #             streams_of_album += [[e["Album"],0]]
    #             for j in range(len(e["Zeitpunkte"])):
    #                 if self.__in_period_of_time(self.__leftbond,self.__rightbond,e["Zeitpunkte"][j]):
    #                     streams_of_album[-1][1] += 1
    #             if streams_of_album[-1][1] == 0:
    #                 del streams_of_album[-1]
    #     return self.__sortlist(streams_of_album)

    # def __sortlist(self,items):
    #     for _ in range(len(items)-1):
    #         for i in range(len(items)-1):
    #             if items[i][1] < items[i+1][1]:
    #                 items[i], items[i+1] = items[i+1], items[i]
    #     return items

    def get_streams_of(self,aspect="Titel"):
        """return number of streams \n
        aspects are "Titel", "Album" and "Künstler"
        set specific period of time via "set_bonds"
        """
        streams_of = []
        for e in self.__info:
            i = 0
            match = False
            while i < len(streams_of) and not match:
                if e[aspect] == streams_of[i][aspect]:
                    for j in range(len(e["Zeitpunkte"])):
                        if self.__in_period_of_time(e["Zeitpunkte"][j]):
                            streams_of[i]["AnzahlStreams"] += 1
                    match = True
                i += 1
            if not match:
                streams_of += [{"Titel": e["Titel"],"Künstler": e["Künstler"],"Album": e["Album"],"AnzahlStreams": 0}]
                for j in range(len(e["Zeitpunkte"])):
                    if self.__in_period_of_time(e["Zeitpunkte"][j]):
                        streams_of[-1]["AnzahlStreams"] += 1
                if streams_of[-1]["AnzahlStreams"] == 0:
                    del streams_of[-1]
        return self.__sort_by_streams(streams_of)

    def __sort_by_streams(self,items):
        for _ in range(len(items)-1):
            for i in range(len(items)-1):
                if items[i]["AnzahlStreams"] < items[i+1]["AnzahlStreams"]:
                    items[i], items[i+1] = items[i+1], items[i]
        return items

    def get_sum(self):
        """return the sum of all streams in given period
        """
        sum_listened = 0
        for e in self.__info:
            for i in range(len(e["Zeitpunkte"])):
                if self.__in_period_of_time(e["Zeitpunkte"][i]):
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

    def set_bonds(self):
        """set a time frame \n
        default is 1970.01.01 till time ends \n
        hh.mm.ss is optional
        """
        self.__leftbond = self.__convert_to_unix(input("Linke Grenze (yyyy.mm.dd-hh.mm.ss): "),2)
        self.__rightbond = self.__convert_to_unix(input("Rechte Grenze (yyyy.mm.dd-hh.mm.ss): "),2)

    def restore_bonds(self):
        """restores default
        """
        self.__leftbond = 0
        self.__rightbond = 2147483647

data = Gain_Data()
# data.collect_data_names(["c:\\Users\\Lulas\\Downloads\\MyData\\endsong_0.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_1.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_2.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_3.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_4.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_5.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_6.json","c:\\Users\\Lulas\\Downloads\\MyData\\endsong_7.json"])
data.collect_data_names(["d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_0.json","d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_1.json","d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_2.json","d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_3.json","d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_4.json","d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_5.json","d:\\SPOTIFY DATA\\my_spotify_data 2021-07\\endsong_6.json"])

topsongs = data.get_streams_of()[:20]



class output_Data():
    def __init__(self):
        pass

    def print_console(self,array,Titel=True,Künstler=True,Album=False,Streams=True):
        for i in range(len(topsongs)):
            string = str(i+1)
            if Titel: string += ". Titel: " + topsongs[i]["Titel"]
            if Künstler: string += ", Künstler: " + topsongs[i]["Künstler"]
            if Album: string += ", Album: " + topsongs[i]["Album"]
            if Streams: string += ", Streams: " + str(topsongs[i]["AnzahlStreams"])
            print(string)

output_Data().print_console(topsongs)
print(data.get_sum())

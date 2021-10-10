from typing import List
from typing import Tuple
from typing import Union

from endsong_parser import Aspect
from endsong_parser import DisplayData
from endsong_parser import GatherData
from endsong_parser import Graph


def init(paths: Union[str, List[str]], uri: bool = True) -> Tuple[DisplayData, Graph]:
    """The function used for creating an object used for further
    visualization of data

    Creates a :class:`GatherData` object with ``paths`` argument and
    passes it to create a :class:`DisplayData` object. Returns the
    created object to be used for further data visualization by
    using its methods.

    :param paths: Either a single absolute path to endsong.json
        or list of paths to multiple endsong_x.json files
    :type paths: str or list[str]
    :param uri: if *True*: songs are identified by Spotify ID;
        if *False*: by name and artist
        (album and single versions are identified as one)
    :type uri: bool, optional, defaults to True
    :return: a DisplayData object used to visualize data
    :rtype: DisplayData
    """
    data = GatherData(paths, uri)
    return DisplayData(data), Graph(data)


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

    d, g = init(paths)

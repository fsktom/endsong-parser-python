from endsong_parser import DisplayData
from endsong_parser import GatherData


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

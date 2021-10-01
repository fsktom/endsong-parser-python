# Problems and Ideas

Well, this script is not perfect. Here I will write about the problems that may come up, bugs and suggestions on what to add/change.

## Possible problems

- if two artists have the same name
  - possible solution: using the Spotify API

## Suggestions / Ideas

- export the .json to a compaible format for [Last.fm Scrubbler](https://github.com/SHOEGAZEssb/Last.fm-Scrubbler-WPF) -> ListenBrainz
- add the ability the view total time listened (in minutes/hours...)
- change "title" aspect to "track"
- change how the list is showed
- podcast support (podcast listens are in `endsong.json` but are ignored by the script)
  - maybe support for endvideo.json?
- faster relative graphs and parsing of data
  - Cython or this other library?
  - more approximating for relative graphs
- GUI
- Spotify API
- transformation into web app/mobile app
  - obviously not using Python
- comparison of two graphs
  - e.g. comparison of all-time listens of one artist vs the other
  - or one artist vs a specific song of that artist (to see what proportion that song has graphically)
  - the larger scale would be taken
- input of paths via a `+paths.txt` or similar (see https://github.com/instaloader/instaloader for comparison) where each line is a separate path
- add a `requirements.txt` file [gallery-dl example](https://github.com/mikf/gallery-dl/blob/master/requirements.txt)
- add a `--help` argument (see https://github.com/mikf/gallery-dl or https://github.com/instaloader/instaloader)
- https://github.com/tartley/colorama for colored text in terminal
  - maybe to separate track, artist, album, no.?

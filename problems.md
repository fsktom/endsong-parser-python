# Problems

Well, this script is not perfect. Here I will write about the problems that may come up, bugs and suggestions on what to add/change.

## Possible problems

- if two artists have the same name
  - possible solution: using the Spotify API

## Suggestions

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

# Python Endsong Parser

Parser for Spotify `endsong.json` files made with Python

Required libaries:

- matplotlib
- numpy

This project uses Black for [Python](https://github.com/psf/black), [Prettier](https://github.com/prettier/prettier) for Markdown formatting and [Markdownlint](https://github.com/markdownlint/markdownlint) for linting markdown. The disabled rules are specified in [.markdownlint.json](.markdownlint.json)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)

## Internal links

- [Problems and Ideas](problems-and-ideas.md)

## Why

Lukas didn't want to use the [Spotistats app](https://spotistats.app/) to make the `endsong.json` files usable. So, in order extract the data and do something with it he wrote this script. At first it could only display the top artist/tracks, later you could search for specific tracks and now you can even view graphs showing the changes over time. I decided to modify this script to my own liking and here we are.

## Usage guide

1. Install the required libraries in `requirements.txt`

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Download the `endsong_parser.py` file
3. Open it in a text editor and at the end change the `path` array to match your paths
4. Open the script in an interactive python shell

   ```bash
   python3 -i endsong_parser.py
   ```

5. Wait for the script to parse the data
6. Use the many commands available! If you ever need help, use `help(d.<method>)` where `<method>` is the name of the method you need help with.

`aspect` can be either `"artist"`, `"album"` or `"title"`

`name` is the name of the artist, album or track

### Getting endsong.json

Follow the [Spotistats guide](https://support.spotistats.app/import/guide/) ([backup link](https://web.archive.org/web/20210824223644/https://support.spotistats.app/import/guide/)) to get the files.

### How to use it

See [usage guide](usage.md)

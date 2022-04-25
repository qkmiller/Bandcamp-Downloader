# Bandcamp Album Downloader
A quick and easy python script for downloading bandcamp albums.

## Requirements
- python3
- python3 __requests__ which can be installed by running the following command:
```shell
python3 -m pip install requests
```

## Downloading Albums
- Copy a bandcamp album url which will look like __https://artistname.bandcamp.com/album/albumname__
- Run the script with the album url as an argument:
```shell
./bandcampdl.py https://artistname.bandcamp.com/album/albumname
```
- The album will be saved to ```./artist/albumname``` located in your current working directory (the directory you were in when you ran the script).

## Downloading Multiple Albums
- You can also download multiple albums by running the script with ```-f```.
- Create a new file then paste each album URL on a new line.
- Provide the file path as an argument to the -f flag:
```shell
./python3 bandcampdl.py -f albumlist.txt
```

## Issues
- If the album contains tracks that are unavailable for streaming, the whole album will be skipped.

## License
Copyright (c) 2022 Quinn Miller

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import textwrap
import html
import json
import os
import re
import requests
import sys
import threading
import time


class Track():
    def __init__(self):
        self.title = ""
        self.url = ""


class Album():
    def __init__(self):
        self.artist = ""
        self.art_url = ""
        self.title = ""
        self.tracks = []


class BandcampDL():
    __url_reg =     r"[a-zA-Z0-9_\-*()+,;'&$!@\[\]#?\/:~=%.]*"
    __artist_reg =  r"https:\/\/" + __url_reg + r"\.bandcamp\.com[\/]?$"
    __album_reg =   __artist_reg[:-6] + r"\/album\/" + __url_reg + r"[\/]?$"

    __message = {"invalid_album":    "\033[31mInvalid album URL: {}\033[0m",
                 "invalid_artist":   "\033[31mInvalid artist URL: {}\033[0m",
                 "unavailable":      "\033[31mResource unavailable: {}\033[0m",
                 "dl_album":         "*\033[33mDownloading album: {}...\033[0m",
                 "downloading":       "--\033[33mDownloading: {}.mp3...\033[0m",
                 "write_error":      "\033[31mError writing to {}\033[0m",
                 "done":             "\033[36mDone!\033[0m", 
                 "abort":            "\033[31mAborting!\033[0m",
                 "building":         "\033[33mBuilding albums...\033[0m"}

    __filter_map = {'&': 'and', 
                    '+': 'plus',
                    '=': 'equals',
                    '/': ' and ',
                    '|': ' ',
                    ':': '-'}

    __wait_sequence = {"-":    "\\",
                       "\\":   "|",
                       "|":    "/",
                       "/":    "-"}


    def __init__(self):
        self.albums = []


    def __build_album(self, html):
        album = Album()
        album_json = None
        for line in html:
            if album.art_url == "":
                if "class=\"popupImage\"" in line:
                    album.art_url = line.split("href=\"")[1].split("\">")[0]
            if album_json is None:
                if line.find("<script") != -1 and line.find('mp3-128') != -1:
                    line = line.split("data-tralbum=\"")[1].split("\"")[0].replace("&quot;", "\"")
                    album_json = json.loads(line)
        album.artist = self.__filter(album_json["artist"])
        album.title = self.__filter(album_json["current"]["title"])
        for t in album_json["trackinfo"]:
            track = Track()
            track.title = self.__filter(t["title"])
            track.url = t["file"]["mp3-128"]
            album.tracks.append(track)
        self.albums.append(album)
            

    def __get_html(self, url):
        res = requests.get(url)
        if res.status_code != 200:
            err = "Status code {}: {}".format(res.status_code, url)
            raise Exception(err)
        return res.text.split('\n')


    def __filter(self, name):
        for k, v in self.__filter_map.items():
            name = name.replace(k, v)
        return re.sub("[~\"#%*<>?\\{}]", '', name)


    def __get_album_urls(self, base_url, html):
        album_urls = []
        for line in html:
            if "<a href=\"/album" in line:
                tail = line.split("href=\"")[1].split("\">")[0]
                album_urls.append(base_url + tail)
        return album_urls


    def __get_albums(self, out_path="./Music"):
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        for album in self.albums:
            print(self.__message["dl_album"].format(album.title))
            artist_path = "{}/{}".format(out_path, album.artist)
            album_path = "{}/{}".format(artist_path, album.title)
            if not os.path.exists(artist_path):
                os.mkdir(artist_path)
            if not os.path.exists(album_path):
                os.mkdir(album_path)
            art_path = album_path + "/cover.jpg"
            self.__download(art_path, album.art_url, "cover.jpg")
            for track in album.tracks:
                track_path = album_path + "/{}.mp3".format(track.title)
                self.__download(track_path, track.url, track.title)


    def __is_album(self, url):
        if not re.match(self.__album_reg, url):
            print(self.__message["invalid_album"].format(url))
            print(self.__message["abort"])
            exit(1)


    def __is_artist(self, url):
        if not re.match(self.__artist_reg, url):
            print(self.__message["invalid_artist"].format(url))
            print(self.__message["abort"])
            exit(1)


    def __download(self, path, url, name):
        print(self.__message["downloading"].format(name), end='', flush=True)
        res = requests.get(url)
        if res.status_code != 200:
            print("\n", self.__message["unavailable"].format(url))
            return
        with open(path, 'wb') as file:
            try:
                file.write(res.content)
            except IOError:
                print("\n", self.__message["write_error"].format(path))
            finally:
                print(self.__message["done"])


    def __waiting(self, wait_char):
        print("\b" + wait_char, end='', flush=True)
        return self.__wait_sequence[wait_char]


    def get_from_list(self, url_list, out_path):
        for url in url_list:
            self.__is_album(url)
        wait_char = "-"
        print(self.__message["building"] + wait_char, end='', flush=True)
        for url in url_list:
            wait_char = self.__waiting(wait_char)
            html = self.__get_html(url)
            self.__build_album(html)
        print("\b" + self.__message["done"])
        self.__get_albums()


    def get_from_artist(self, url, out_path):
        self.__is_artist(url)
        html = self.__get_html(url)
        album_urls = self.__get_album_urls(url, html)
        self.get_from_list(album_urls, out_path)

            
if __name__ == '__main__':
    example_1 = "python3 bandcampdl.py https://ARTISTNAME.bandcamp.com/album/ALBUMNAME"
    example_2 = "python3 bandcampdl.py -a https://ARTISTNAME.bandcamp.com"
    example_3 = "python3 bandcampdl.py -f albumlist.txt -o ~/Music"
    examples = "Examples:\n  {}\n  {}\n  {}".format(example_1, 
                                                    example_2, 
                                                    example_3)
    parser = argparse.ArgumentParser(prog="bandcampdl",
                                     description="Downloads albums from Bandcamp",
                                     epilog=examples,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("url", 
                       type=str, 
                       metavar="<ALBUM_URL>", 
                       nargs="?", 
                       help="URL for a specific Bandcamp album")
    group.add_argument("-f", "--file",
                        type=str,
                        metavar="<FILE>",
                        help="file containing multiple Bandcamp album URLs")
    group.add_argument("-a", "--artist",
                       type=str,
                       metavar="<ARTIST_URL>",
                       help="Bandcamp URL for an artist, download all albums by artist")
    parser.add_argument("-o", "--out",
                        nargs="?",
                        type=str,
                        metavar="<PATH>",
                        default="./Music",
                        help="""base path to save albums into.
                        Files will be saved in the following format:
                        <PATH>/artist/album""")
    args = parser.parse_args()


    if (args.url):
        BandcampDL().get_from_list([args.url], args.out)
    if (args.file):
        url_list = open(args.file, "r").read().split("\n")[:-1]
        BandcampDL().get_from_list(url_list, args.out)
    if (args.artist):
        BandcampDL().get_from_artist(args.artist, args.out)
    exit(0)

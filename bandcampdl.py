import html
import os
import re
import requests
import sys


class BandcampDL():
    message = {"unavailable": "\033[31mSome tracks in this album"
               "aren't available. Skipping...\033[0m",
               "invalid": "\033[31mInvalid album URL: {}\033[0m",
               "dl_album": "\033[33mDownloading album: {}\033[0m",
               "dl_track": "\033[33mDownloading track: {}\033[0m"
               }


    def __init__(self):
        self.album_title = ""
        self.artist = ""
        self.album_urls = []
        self.tracks = []
        self.cover_art_url = ""
        self.html = []
        self.albums = []


    def __unescape(self, s):
        return html.unescape(html.unescape(s))


    def __parse_album_info(self, album_html):
        i = 0
        while i < len(album_html):
            if "<meta name=\"description\"" in album_html[i]:
                j = i + 3
                while album_html[j] != "":
                    title_raw = ' '.join(album_html[j].split(" ")[1:])
                    title = self.__filter_name(self.__unescape(title_raw))
                    self.tracks.append(title)
                    j += 1
            if "<meta name=\"title\"" in album_html[i]:
                info = album_html[i].split("content=\"")
                info = info[1].split("\"")[0].split(", by ")
                self.album_title = self.__filter_name(self.__unescape(info[0]))
                self.artist = self.__filter_name(self.__unescape(info[1]))
            if "class=\"popupImage\"" in album_html[i]:
                cover_art = album_html[i].split("href=\"")[1].split("\">")[0]
                print("Cover art: " + cover_art)
                self.cover_art_url = cover_art

                break
            i += 1


    def __parse_track_urls(self):
        mp3_script = None
        for i in self.html:
            if i.find("<script") != -1 and i.find('mp3-128') != -1:
                mp3_script = i
                break
        track_urls = mp3_script.split("{&quot;mp3-128&quot;:&quot;")[1:]
        if len(track_urls) != len(self.tracks):
            return(False)
        i = 0
        while i < len(track_urls):
            url = track_urls[i].split('&quot;}')[0].replace('amp;', '')
            self.tracks[i] = {"title": self.tracks[i], "url": url}
            i += 1
        return(True)


    def __get_html(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Status code {}: {}"
                            .format(response.status_code, 
                                    url))
        self.html = response.text.split('\n')


    def __filter_name(self, name):
        key = {'&': 'and',
               '+': 'plus',
               '=': 'equals',
               '/': ' and ',
               '|': ' ',
               ':': '-'
               }
        for k, v in key.items():
            name = name.replace(k, v)
        return re.sub("[~\"#%*<>?\\{}]", '', name)


    def __check_music_path(self):
        if not os.path.exists("./Music"):
            os.mkdir("./Music")
        if not os.path.exists("./Music/{}".format(self.artist)):
            os.mkdir("./Music/{}" .format(self.artist))
        if not os.path.exists("./Music/{}/{}".format(self.artist,
                                                     self.album_title)):
            os.mkdir("./Music/{}/{}".format(self.artist,
                                            self.album_title))

    def __get_track(self, title, url):
        print(self.message["dl_track"].format(title), end="...")
        track_data = requests.get(url)
        file_path = "./Music/{}/{}/{}.mp3".format(self.artist,
                                                  self.album_title,
                                                  title)
        with open(file_path, 'wb') as file:
            try:
                file.write(track_data.content)
            except IOError:
                print("\nCouldn't write to {}".format(file_path))
            finally:
                print("\033[36mDone!\033[0m")


    def __get_album(self, album_url):
        self.__check_music_path()
        cover_art_data = requests.get(self.cover_art_url)
        cover_art_path = "./Music/{}/{}/cover.jpg".format(self.artist,
                                                          self.album_title)
        with open(cover_art_path, 'wb') as file:
            file.write(cover_art_data.content)
        for t in self.tracks:
            self.__get_track(t["title"], t["url"])


    def __is_album(self, url):
        urlchars = r"[a-zA-Z0-9_\-*()+,;'&$!@\[\]#?/:~=%.]"
        fmt_str = r"https:\/\/{}*\.bandcamp\.com\/album\/{}*"
        if re.match(fmt_str.format(urlchars, urlchars), url):
            return True
        return False


    def __is_artist(self, url):
        urlchars = r"[a-zA-Z0-9_\-*()+,;'&$!@\[\]#?/:~=%.]"
        fmt_str = r"https:\/\/{}*\.bandcamp\.com$"
        if re.match(fmt_str.format(urlchars, urlchars), url):
            return True
        return False


    def get_from_list(self, url_list):
        for url in url_list:
            if not self.__is_album(url):
                print(self.message["invalid"].format(url))
                exit(1)
        for url in url_list:
            url = url.replace('\n', '')
            print(self.message["dl_album"].format(url))
            self.__get_html(url)
            self.__parse_album_info(self.html)
            has_tracks = self.__parse_track_urls()
            if has_tracks:
                self.__get_album(url)
            else:
                print(self.message["Album is unavailable"])
            self.__init__()


    def get_from_url(self, url):
        if self.__is_album(url):
            print(self.message["dl_album"].format(url))
            url = url.replace('\n', '')
            self.__get_html(url)
            self.__parse_album_info(self.html)
            has_tracks = self.__parse_track_urls()
            if has_tracks:
                self.__get_album(url)
            else:
                print(self.message["Album is unavailable"])
            self.__init__()
        else:
            print(self.message["invalid"].format(url))
            exit(1)


    def get_from_artist(self, url):
        if not self.__is_artist(url):
            print(self.message["invalid"].format(url))
            exit(1)
        self.artist_url = url
        self.__get_html(url)
        self.__get_album_urls(url, self.html)

            
    def __get_album_urls(self, base_url, html):
        album_urls = []
        for line in html:
            if "<a href=\"/album" in line:
                tail = line.split("href=\"")[1].split("\">")[0]
                album_urls.append(base_url + tail)
        self.album_urls = album_urls



if __name__ == '__main__':
    bcdl = BandcampDL()
    def usage():
        print("Bandcamp album downloader")
        print("Usage:")
        print("./python3 bandcampdl.py [album URL]")
        print("./python3 bandcampdl.py -f [file containing multiple URLs]")
        print("./python3 bandcampdl.py -a [artist page]")
    if (len(sys.argv) < 2 or len(sys.argv) > 3):
        usage()
    elif (sys.argv[1] == '-h'):
        usage()
    elif (sys.argv[1] == '-f'):
        print("Getting urls from", sys.argv[2])
        url_list = open(sys.argv[2], "r").readlines()
        bcdl.get_from_list(url_list)
    elif (sys.argv[1] == '-a'):
        bcdl.get_from_artist(sys.argv[2])
        bcdl.get_from_list(bcdl.album_urls)
    else:
        bcdl.get_from_url(sys.argv[1])

import sys
import os
import re
import requests
import html

class BandcampDL():
    def __init__(self):
        self.album = ""
        self.artist = ""
        self.tracks = []
        self.album_url = ""
        self.cover_art_url = ""
        self.html = []

    def __unescape(self, s):
        return html.unescape(html.unescape(s))

    def __parse_album_info(self):
        i = 0
        while i < len(self.html):
            if self.html[i].startswith("    <meta name=\"description\""):
                j = i + 3
                while self.html[j] != "":
                    title_raw = ' '.join(self.html[j].split(" ")[1:])
                    self.tracks.append(self.__filter_name(self.__unescape(title_raw)))
                    j += 1
            if self.html[i].startswith("        <meta name=\"title\""):
                info = self.html[i].split("content=\"")[1].split("\"")[0].split(", by ")
                self.album = self.__filter_name(self.__unescape(info[0]))
                self.artist = self.__filter_name(self.__unescape(info[1]))
            if self.html[i].startswith("            <a class=\"popupImage\""):
                self.cover_art_url = self.html[i].split("href=\"")[1].split("\">")[0]
                break
            i += 1

    def __parse_track_urls(self):
        mp3_script = None
        for i in self.html:
            if i.find("<script") != -1 and i.find('mp3-128') != -1:
                mp3_script = i
                break
        track_urls = mp3_script.split("{&quot;mp3-128&quot;:&quot;")[1:]
        i = 0
        while i < len(track_urls):
            url = track_urls[i].split('&quot;}')[0].replace('amp;', '')
            self.tracks[i] = {"title": self.tracks[i], "url": url}
            i += 1

    def __get_html(self):
        response = requests.get(self.album_url)
        if response.status_code != 200:
            raise Exception("Status code {}: {}".format(response.status_code, self.album_url))
        self.html = response.text.split('\n')

    def __filter_name(self, name):
        key = {'&': 'and', 
               '+': 'plus',
               '=': 'equals',
               '/': ' ',
               '|': ' ',
               ':': '-'
               }
        for k, v in key.items():
            name = name.replace(k, v)
        return re.sub("[~\"#%*<>?\\{}]", '', name)

    def __get_album(self, album_url):
        self.album_url = album_url
        self.__get_html()
        self.__parse_album_info()
        self.__parse_track_urls()
        if not os.path.exists("./Music"):
            os.mkdir("./Music")
        if not os.path.exists("./Music/{}".format(self.artist)):
            os.mkdir("./Music/{}".format(self.artist))
        if not os.path.exists("./Music/{}/{}".format(self.artist, self.album)):
            os.mkdir("./Music/{}/{}".format(self.artist, self.album))
        cover_art_data = requests.get(self.cover_art_url)
        with open("./Music/{}/{}/cover.jpg".format(self.artist, self.album), 'wb') as file:
            file.write(cover_art_data.content)
        for t in self.tracks:
            print("Downloading track: {}".format(t["title"]))
            track_data = requests.get(t["url"])
            with open("./Music/{}/{}/{}.mp3".format(self.artist, self.album, t["title"]), 'wb') as file:
                file.write(track_data.content)


    def get(self, resource, file=False):
        if file:
            with open(resource, 'r') as album_list:
                for album in album_list:
                    if self.__is_album(album):
                        print("Downloading album: {}".format(album.replace('\n', '')))
                        self.__get_album(album.replace('\n', ''))
                        self.__init__()
                    else:
                        print("Invalid album URL: {}".format(album))
                        exit(1)
        else:
            if self.__is_album(resource):
                self.__get_album(resource)
            else:
                print("Invalid album URL: {}".format(resource))
                exit(1)


    def __is_album(self, url):
        urlchars = "[a-zA-Z0-9_\-*()+,;'&$!@\[\]#?/:~=%.]"
        if re.match("https:\/\/{}*\.bandcamp\.com\/album\/{}*".format(urlchars, urlchars), url):
            return True
        return False

if __name__ == '__main__':
    bcdl = BandcampDL()
    if (sys.argv[1] == '-f'):
        bcdl.get(sys.argv[2], file=True)
    else:
        bcdl.get(sys.argv[1])

import sys
import os
import re
import requests

class BandcampDL():
    def __init__(self):
        self.album = ""
        self.artist = ""
        self.tracks = []
        self.album_url = ""
        self.cover_art_url = ""
        self.html = []


    def __parse_album_info(self):
        i = 0
        while i < len(self.html):
            if self.html[i].startswith("    <meta name=\"description\""):
                j = i + 3
                while self.html[j] != "":
                    self.tracks.append(self.__filter_name(' '.join(self.html[j].split(" ")[1:])))
                    j += 1
            if self.html[i].startswith("        <meta name=\"title\""):
                info = self.html[i].split("content=\"")[1].split("\"")[0].split(", by ")
                self.album = self.__filter_name(info[0])
                self.artist = self.__filter_name(info[1])
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
        return re.sub("[~\"#%&*:<>?/\\{|}]+", '_', name)

    def get_album(self, album_url):
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
            print("Downloading {}".format(t["title"]))
            track_data = requests.get(t["url"])
            with open("./Music/{}/{}/{}.mp3".format(self.artist, self.album, t["title"]), 'wb') as file:
                file.write(track_data.content)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Missing 1 argument. Please provide a bandcamp album link")
        exit(1)
    if re.match("https:\/\/\w*\.bandcamp\.com\/album\/\w*", sys.argv[1]) is None:
        print("Please provide a valid bandcamp album link")
        exit(1)
    bcdl = BandcampDL()
    bcdl.get_album(sys.argv[1])

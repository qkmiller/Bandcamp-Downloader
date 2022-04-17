import sys
import os
import re
import requests

class BandcampDL():
    def __init__(self):
        self.album = ""
        self.artist = ""
        self.tracks = []
        self.url = ""
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
            url = track_urls[i].split('&quot;}')[0].split('?')
            url = url[0] + "?token=" + url[1].split("token=")[1]
            self.tracks[i] = {"title": self.tracks[i], "url": url}
            i += 1

    def __get_html(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception("Status code {}: {}".format(response.status_code, self.url))
        self.html = response.text.split('\n')

    def __filter_name(self, name):
        return re.sub("[~\"#%&*:<>?/\\{|}]+", '_', name)

    def get_album(self, album_url):
        self.url = album_url
        self.__get_html()
        self.__parse_album_info()
        self.__parse_track_urls()
        if not os.path.exists("./{}".format(self.artist)):
            os.mkdir("./{}".format(self.artist))
        if not os.path.exists("./{}/{}".format(self.artist, self.album)):
            os.mkdir("./{}/{}".format(self.artist, self.album))
        for t in self.tracks:
            data = requests.get(t["url"])
            with open("./{}/{}/{}.mp3".format(self.artist, self.album, t["title"]), 'wb') as file:
                file.write(data.content)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Missing 1 argument. Please provide a bandcamp album link")
        exit(1)
    if re.match("https:\/\/\w*\.bandcamp\.com\/album\/\w*", sys.argv[1]) is None:
        print("Please provide a valid bandcamp album link")
        exit(1)
    bcdl = BandcampDL()
    bcdl.get_album(sys.argv[1])

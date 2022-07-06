import sys
from BandcampDL import BandcampDL

if __name__ == '__main__':
    bcdl = BandcampDL()

    def usage():
        print("Bandcamp album downloader")
        print("Usage:")
        print("./python3 bandcampdl.py [album url]")
        print("./python3 bandcampdl.py -f [file]")

    if (len(sys.argv) < 2 or len(sys.argv) > 3):
        usage()
    elif (sys.argv[1] == '-h'):
        usage()
    elif (sys.argv[1] == '-f'):
        bcdl.get_from_file(sys.argv[2])
    else:
        bcdl.get_from_url(sys.argv[1])

#!/usr/bin/python3
from spotify import Spotify
from youtube import Youtube
from editor import TagEditor
from lastfm import LastFM
from apple import AppleMusic
import sys, getopt, shutil
import os, re, random
import notify2
from pygame import mixer


class MusicDownloader(object):


    def __init__(self):
        self.__youtube = Youtube()
        self.__spotify = Spotify()
        self.__editor = TagEditor()
        self.__last = LastFM()
        self.__apple = AppleMusic()

    def __downloadMusicFromYoutube(self, name, uri, dur):

        #finding song on youtube
        self.__youtube.get(name, dur)

        #downloading video from youtube
        if self.__youtube.download(
            url=self.__youtube.getResult(),
            path=uri,
            filename=uri
        ):
            #converting video to mp3 file
            self.__youtube.convertVideoToMusic(
                uri=uri
            )
            return True
        else:
            return False

    def __getSongInfoFromSpotify(self, uri):

        try:
            return self.__spotify.getSongInfo(uri)
        except:
            return None

    def getNameFromYoutube(self, url):
        return self.__youtube.getNameFromYoutube(url)

    def getData(self, uri):
        try:
            return self.__spotify.getSongInfo(uri)
        except:
            return None

    def getLastFMTags(self, name):
        return self.__last.get(name)

    def getYoutubeMusicInfo(self, url):
        return self.__youtube.getNameFromYoutube(url)

    def downloadBySpotifyUri(self, uri):

        #get info
        info = self.__getSongInfoFromSpotify(uri)

        if info:

            fixed_name = f'{info["artist"][0]} - {info["name"]}'
            fixed_name = fixed_name.replace('.','')
            fixed_name = fixed_name.replace(',','')
            fixed_name = fixed_name.replace("'",'')
            fixed_name = fixed_name.replace("/","")

            #finding and download from YouTube and tagging
            if self.__downloadMusicFromYoutube(fixed_name, info['uri'], info['duration_ms']):

                self.__editor.setTags(
                    data=info
                )

                cachepath = os.getcwd() + '/cache'
                fullpath = os.getcwd() + '/Downloads'

                if not os.path.exists(fullpath):
                    os.makedirs(fullpath)

                name = f'{info["artist"][0]} - {info["name"]}'

                os.rename(
                    f"{cachepath}/{info['uri']}/{info['uri']}.mp3",
                    f"{fullpath}/{getCorrect(name)}.mp3"
                )

                #deleting cache
                try:shutil.rmtree(f"cache/{info['uri']}")
                except:pass

                notify.send(f'{info["artist"][0]} - {info["name"]}')
                return True
        return False

    def downloadBySearchQuery(self, query):

        #get info
        info = self.__spotify.search(query=query)

        if not info:
            info = self.__last.get(query)

        if info:

            fixed_name = f'{info["artist"][0]} - {info["name"]}'
            fixed_name = fixed_name.replace('.','')
            fixed_name = fixed_name.replace(',','')
            fixed_name = fixed_name.replace("'",'')
            fixed_name = fixed_name.replace("/","")

            #finding and download from YouTube and tagging
            self.__downloadMusicFromYoutube(fixed_name, info['uri'], info['duration_ms'])

            self.__editor.setTags(
                data=info
            )

            cachepath = os.getcwd() + '/cache'
            fullpath = os.getcwd() + '/Downloads'

            if not os.path.exists(fullpath):
                os.makedirs(fullpath)

            name = f'{info["artist"][0]} - {info["name"]}'

            os.rename(
                f"{cachepath}/{info['uri']}/{info['uri']}.mp3",
                f"{fullpath}/{getCorrect(name)}.mp3"
            )

            #deleting cache
            try:
                shutil.rmtree(f"cache/{info['uri']}")
            except:
                pass

            notify.send(f'{info["artist"][0]} - {info["name"]}')
            return True, info
        else:
            return False, None

    def downloadBySpotifyUriFromFile(self, filename):
        try:

            with open(filename, 'r') as f:
                data = f.readlines()

        except FileNotFoundError:

            print(f'No such file or directory: "{filename}"')
            exit(2)

        #normalize
        try:data.remove('\n')
        except:pass
        links = [ str(item).replace('\n','') for item in data ]

        for i,song in zip(range(len(links)),links):
            print(f'[{i+1}] - {song}')
            try:
                state = self.downloadBySpotifyUri(str(song).split(':')[-1])
                if not state:
                    notify.send(f'Failed to download',True)
            except:
                print('Something went wrong!')

    def downloadBySpotifyUriPlaylistMode(self, playlist_uri):

        user = Spotify.User()
        playlist = user.getPlaylistTracks(playlist_uri)

        for info, i in zip(playlist,range(len(playlist))):

            print(f'Downloading {i+1} of {len(playlist)}')

            fixed_name = f'{info["artist"][0]} - {info["name"]}'
            fixed_name = fixed_name.replace('.','')
            fixed_name = fixed_name.replace(',','')
            fixed_name = fixed_name.replace("'",'')
            fixed_name = fixed_name.replace("/","")

            #finding and download from YouTube and tagging
            self.__downloadMusicFromYoutube(fixed_name, info['uri'], info['duration_ms'])

            self.__editor.setTags(
                data=info
            )

            cachepath = os.getcwd() + '/cache'
            fullpath = os.getcwd() + '/Downloads'

            if not os.path.exists(fullpath):
                os.makedirs(fullpath)

            name = f'{info["artist"][0]} - {info["name"]}'

            os.rename(
                f"{cachepath}/{info['uri']}/{info['uri']}.mp3",
                f"{fullpath}/{getCorrect(name)}.mp3"
            )

            #deleting cache
            try: shutil.rmtree(f"cache/{info['uri']}")
            except: pass

            notify.send(f'{info["artist"][0]} - {info["name"]}')

    def downloadFromYoutubeMusic(self, url, info):

        uri = info['uri']

        #downloading video from youtube
        if self.__youtube.download(
            url=url,
            path=uri,
            filename=uri
        ):

            #converting video to mp3 file
            self.__youtube.convertVideoToMusic(
                uri=uri
            )

            self.__editor.setTags(
                data=info
            )

            cachepath = os.getcwd() + '/cache'
            fullpath = os.getcwd() + '/Downloads'

            if not os.path.exists(fullpath):
                os.makedirs(fullpath)

            name = f'{info["artist"][0]} - {info["name"]}'

            os.rename(
                f"{cachepath}/{info['uri']}/{info['uri']}.mp3",
                f"{fullpath}/{getCorrect(name)}.mp3"
            )

            #deleting cache
            try:shutil.rmtree(f"cache/{info['uri']}")
            except:pass

            notify.send(f'{info["artist"][0]} - {info["name"]}')
            return True, info
        else:
            return False, None

    def search(self, query):
        return self.__spotify.search(query=query)


class CLI(object):

    @staticmethod
    def help():

        print('')
        print('\t Spotify Music Downlader (SMD)\n')
        print('./main.py [without any parameters] - normal startup\n')
        print('./main.py [parameter][argument] - startup with arguments\n')
        print('Parameters\n')
        print('  -h, --help       Print a help message and exit.\n')
        print('  -s, --song       Spotify song URI.\n')
        print('  -p, --playlist   Spotify playlist URI.\n')
        print('  -q, --query      Search query.\n')
        print('  -y, --youtube    YouTube Music url.')
        print('                   Note that your link should be with quotation marks - "your_url"!\n')
        print('  -v, --video      YouTube url.(You will get a song but without any tags)')
        print('                   Note that your link should be with quotation marks - "your_url"!\n')
        print('  -a, --apple      Apple Music url.\n')
        print('  -f, --file       File with song URIs. (Spotify only)\n')

    @staticmethod
    def main(argv):
        try:

            opts, args = getopt.getopt(
                 argv,
                 "hs:p:q:y:v:a:f:",
                 [
                     "help=",
                     "song=",
                     "playlist=",
                     "query=",
                     "youtube=",
                     "video=",
                     "apple=",
                     "file="
                 ])

        except getopt.GetoptError:

           CLI.help()
           exit(0)

        for parameter, argument in opts:

            if parameter in ("-h", "--help"):

                CLI.help()
                sys.exit(0)

            elif parameter in ("-s", "--song"):
                #song uri
                try:
                    md = MusicDownloader()
                    state = md.downloadBySpotifyUri(argument)
                    if not state:
                        notify.send(f'Failed to download',True)
                except KeyboardInterrupt:
                    sys.exit(0)
                sys.exit(0)

            elif parameter in ("-p", "--playlist"):
                #playlist uri
                try:
                   md = MusicDownloader()
                   md.downloadBySpotifyUriPlaylistMode(argument)
                except KeyboardInterrupt:
                  sys.exit(0)
                sys.exit(0)

            elif parameter in ("-q", "--query"):
                #query
                try:
                   md = MusicDownloader()
                   state, data = md.downloadBySearchQuery(argument)
                   if not state:
                       notify.send(f'Failed to download',True)
                except KeyboardInterrupt:
                   sys.exit(0)
                sys.exit(0)

            elif parameter in ("-y", "--youtube"):
                 #YouTube Music
                 try:
                     link = ''.join(str(argument).split('music.')).split('&')[0]

                     md = MusicDownloader()
                     name = md.getYoutubeMusicInfo(link)
                     tags = md.getLastFMTags(name)

                     state = md.downloadFromYoutubeMusic(url=link, info=tags)
                     if not state:
                         notify.send(f'Failed to download',True)
                 except KeyboardInterrupt:
                     sys.exit(0)
                 sys.exit(0)

            elif parameter in ("-v", "--video"):
                 #YouTube Music
                 try:

                     md = MusicDownloader()
                     name = md.getNameFromYoutube(argument)

                     uri = random.randint(1000000000,10000000000)
                     uri = 's' + str(uri) + 't'

                     info =  {
                         'uri' : uri,
                         'name' : str(name).split('-')[-1],
                         'artist' : str(name).split('-')[0],
                         'album' : 'YouTube',
                         'image' : '',
                         'duration_ms' : 0
                     }

                     state = md.downloadFromYoutubeMusic(url=argument, info=info)

                     if not state:
                        notify.send(f'Failed to download',True)
                 except KeyboardInterrupt:
                     sys.exit(0)
                 sys.exit(0)

            elif parameter in ("-a", "--apple"):
                 #Apple Music
                 try:
                     md = MusicDownloader()
                     apple = AppleMusic()
                     name = apple.getName(argument)
                     state = md.downloadBySearchQuery(query=name)
                     if not state:
                         notify.send(f'Failed to download',True)
                 except KeyboardInterrupt:
                     sys.exit(0)
                 sys.exit(0)

            elif parameter in ("-f", "--file"):
                #from file
                try:
                    md = MusicDownloader()
                    md.downloadBySpotifyUriFromFile(argument)
                except KeyboardInterrupt:
                   exit(0)
                sys.exit()

            else:
                #normal startup
                try:
                    while True:
                       md = MusicDownloader()
                       state = md.downloadBySpotifyUri(input('[smd]>SONG URI:'))
                       if not state:
                          notify.send(f'Failed to download',True)
                except KeyboardInterrupt:
                    sys.exit(0)


class notify(object):

    image = os.getcwd() + '/Data/icon.png'
    sound_info = os.getcwd() + '/Data/i.mp3'
    sound_warn = os.getcwd() + '/Data/w.mp3'
    try:notify2.init("Spotify Music Downloader Notifier")
    except:pass

    @staticmethod
    def sound(error=False):
        mixer.init()
        mixer.music.load(notify.sound_warn if error else notify.sound_info)
        mixer.music.play()

    @staticmethod
    def send(message, error=False):
        try:
            ns = notify2.Notification('Spotify Music Downloader', message=message, icon=notify.image)
            # Set the urgency level
            ns.set_urgency(notify2.URGENCY_NORMAL)
            # Set the timeout
            ns.set_timeout(1000)
            notify.sound(error)
            ns.show()
        except:pass


def getCorrect(name):
    return re.sub(r"[\"#/@;:<>{}`+=~|.!?$%^&*№&]", string=name, repl='')


if __name__ == '__main__':

    CLI.main(sys.argv[1:])

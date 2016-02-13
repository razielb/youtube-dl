#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import socket
socket.setdefaulttimeout(99 * 99)
import urllib2
import re
import os
import argparse
from time import sleep
from urllib import urlencode, urlretrieve

'''
	coded by R4z		[raziel.b7@gmail.com]
'''


class Youtube:
    _OUTPUT = u''
    _FORMAT = r''
    _HEADERS = {'Accept-Language'	: r'en-US,en;q=0.5',
                'User-Agent'		: r'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36', }
    _BUFFER_SIZE = (32 * 1024)

    @staticmethod
    def __init__(output, format):
        _OUTPUT = output
        _FORMAT = format

    @staticmethod
    def release_the_kraken(list, path=""):
        ''' A public method for downloading a playlist and saving it as a directory(the playlist name).
            list       - a playlist id
        '''
        print r"[+] Getting playlist info.."
        try:
            name, videos = Youtube._get_playlist_details(list)
        except:
            print r"[-] Couldn't get playlist details :("
            return False
        counter = 0
        try:
            os.makedirs(name)  # Create a new directory with the playlist name
        except OSError:
            print u"[-] Directory `%s` already exist" % name
        path += u"%s/" % name
        for video_id in videos:
            counter += 1
            print r"[+] Downloading %s (%d/%d)" % (video_id, counter, len(videos))
            Youtube.download_video(video_id, path)
            sleep(1.337)

    @staticmethod
    def download_video(video_id, path=""):
        ''' A private method for downloading content and saving it in specific path, if the download fails it will try again.
                        url      - a fully qualified path of the remove file to download
                        filename - file name for output file (will be created if not exists)
        '''
        video = Youtube.get_video_details(video_id)
        Youtube._download(video[1], u'%s.mp3' % (path + video[0]))

    @staticmethod
    # Source:
    # https://github.com/elicn/sdarot.tv_downloader/blob/master/sdarot-dl.py
    def _download(url, filename):
        ''' A private method for downloading content and saving it to a local
        file.
                        url      - a fully qualified path of the remove file to download
                        filename - file name for output file (will be created if not exists)
        '''

        # res = urllib2.urlopen(url, timeout = 60)
        # res = urllib2.urlopen(url, timeout = 360)
        res = urllib2.urlopen(url)

        total_size = int(res.info().getheaders('Content-Length')[0])
        curr_size = 0
        buffer = True

        with open(filename, 'wb') as outfile:
            while buffer:
                buffer = res.read(Youtube._BUFFER_SIZE)

                if buffer:
                    curr_size += len(buffer)

                    status = '%3.02f%%' % (curr_size / float(total_size) * 100)
                    print '%s%s' % (status, '\x08' * (len(status) + 1)),

                    outfile.write(buffer)
            print

    @staticmethod
    def _get_playlist_details(list):
        ''' A private method that fetch the details from youtube playlist
            list       - a playlist id
        '''
        data = Youtube._http_request(
            "https://www.youtube.com/playlist?list=%s" % list)
        name = re.findall(
            '<h1 class="pl-header-title" tabindex="0">\n(.*?)\n  </h1>', data)[0].decode('utf8').strip()
        videos = re.findall(
            '<a class="pl-video-title-link yt-uix-tile-link yt-uix-sessionlink  spf-link " dir="rtl" href="/watch\?v=([-\w]+).*?"', data)
        return (name, videos)

    @staticmethod
    def _http_request(url):
        ''' A private method for fetching internet resources using urllib '''
        request = urllib2.Request(url, headers=Youtube._HEADERS)
        handler = urllib2.urlopen(request)
        data = handler.read()
        handler.close()
        return data

    @staticmethod
    def get_video_details(video_id, format="mp3"):
        ''' A public method for extracting youtube video details(title, dl link)
            video_id       - the video id
            format         - output file format
        '''
        payload = {'url': "https://www.youtube.com/watch?v=%s" % video_id,
                   'format': format, 'quality': '1', '85tvb5': '1583570'}
        request = urllib2.Request("http://convert2mp3.net/en/index.php?p=convert",
                                  data=urlencode(payload), headers=Youtube._HEADERS)
        handler = urllib2.urlopen(request)
        data = handler.read()
        handler.close()
        iframe = re.findall('<iframe id="convertFrame" src="(.*?)"', data)[0]
        data = Youtube._http_request(iframe)
        new_url = re.findall(
            '<a href="(.*?)" target="_parent">Continue</a>', data)[0]
        id, key = re.findall("id=(.*?)&key=(.*)", new_url)[0]
        result = Youtube._http_request(new_url)
        server = re.findall(
            '<param name="FlashVars" value="mp3=http://(.*?).convert2mp3.net', result)[0]
        title = Youtube._slugify(re.findall('<title>(.*?) - YouTube</title>', Youtube._http_request(
            "https://www.youtube.com/watch?v=%s" % video_id))[0].decode('utf8'))
        return [title, "http://%s.convert2mp3.net/download.php?id=%s&key=%s&d=y" % (server, id, key)]

    @staticmethod
    def _slugify(value):
        ''' A private method for  a valid filename constructed from the string.
            value       - the string
        '''
        return"".join(c for c in re.sub("&(.*?);", "", value) if c not in "\/:*?<>|")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--playlist', help='youtube playlist id')
    parser.add_argument('-v', '--video_id', help='youtube video id')
    parser.add_argument('-o', '--output', help='output path', default="")
    parser.add_argument(
        '-f', '--format', help='format for the output files(mp3 as default)', default="mp3")
    args = parser.parse_args()
    Youtube.__init__(args.output, args.format)
    if not args.playlist and not args.video_id:
        parser.error("One of --playlist or --video_id must be given")
    if args.playlist:
        Youtube.release_the_kraken(args.playlist)
    else:
        Youtube.download_video(args.video_id)

if __name__ == "__main__":
    main()

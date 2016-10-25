"""
Created on 7/9/16
@author: Vincent AIRIAU
Version V0.1
"""
import argparse
import os
import shutil
import sys
import urllib
import urllib2
from zipfile import ZipFile
import logging

import requests
from lxml import html

logger = logging.basicConfig(format='%(asctime)s - %(module)s: %(message)s', filename='subscene_g.log', filemode='w',
                             level=logging.DEBUG)


def opensubscene_rls_page(showname):
    # Gets the search page content for one show or whatever the file of the name is=
    url = 'https://subscene.com/subtitles/release'
    values = {'q': showname, 'l': ''}
    cookiefilter = '__cfduid=d9867ef87b10f433cd70a0efb36c01d471473252835; _ga=GA1.2.1129327024.1473252838; ' \
                   'LanguageFilter=13; HearingImpaired=0; ForeignOnly=False; ' \
                   '__gads=ID=a9b6ddb36e78eb76:T=1473252861:S=ALNI_MYgAIy-JwZk3SaXGDbgRdjR6545wQ; _gat=1'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
    headers = {'User-Agent': user_agent, 'Cookie': cookiefilter}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    content = response.read()
    return content


class Subscene:
    def __init__(self, path):
        print "This is the path entered: " + path
        # Retrieve filename (for example TV.SHOW.XViD-EVO), so remove path and extension
        episodename = os.path.basename(path).replace('.avi', '').replace('.mkv', '').replace('.mpg', '')
        localpath = os.path.dirname(path)
        zipfile_path = path.replace('.avi', '.zip').replace('.mkv', '.zip').replace('.mpg', '.zip')


    def downloadfirstsub(self):
        sublist = self.getsubtitlelist(self.episodename)
        # If no subtitles, display a NOK message
        if not sublist:
            logger.ERROR("No subtitles are available for this release.")
        # If subtitles are present, download and unpack the first one
        else:
            self.getsubtitlefile(sublist[0], self.zipfile_path)
            print self.zipfile_path
            with ZipFile(self.zipfile_path, 'r') as subtitle_zipfile:
                logger.INFO("extraction")
                subtitle_zipfile.extractall(path=self.localpath)
                os.remove(subtitle_zipfile)
            os.rename(self.localpath + "\\" + subtitle_zipfile.namelist()[0], self.localpath + "\\" + self.episodename + ".srt")

    def displaysubtitlelist(self):
        sublist = self.getsubtitlelist(self.episodename)


    @staticmethod
    def getsubtitlelist(episodename):
        '''

        :param episodename: regex
        :return: sub_list_links: a table with subtitle URLs or 0 if no subtitle
        '''
        # TODO: use regex to get the good or not take any

        tree = html.fromstring(opensubscene_rls_page(episodename))
        # sub_list_names = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/span[2]/text()')

        sub_list_links = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/@href')
        del sub_list_links[1::2]
        return sub_list_links

    @staticmethod
    def getsubtitlefile(subtitlerelativeURL, localpath):

        base_url = 'https://subscene.com'
        full_url = base_url + subtitlerelativeURL

        user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
        headers = {'User-Agent': user_agent}
        req = urllib2.Request(full_url, '', headers)
        response = urllib2.urlopen(req)
        content = response.read()
        tree = html.fromstring(content)
        logger.INFO(content)
        subtitle_link = tree.xpath('//a[@id="downloadButton"]/@href')[0]
        subtitle_link = base_url + subtitle_link
        logger.INFO(subtitle_link)
        r = requests.get(subtitle_link, stream=True, headers={'User-Agent': user_agent})
        if r.status_code == 200:
            with open(localpath, 'wb') as f:
                # r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                f.close()
                logger.ERROR("archive enregistree")
        else:
            print "Subtitle couldn't be downloaded."
            return 1
        return 0


def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The path to the video file. Takes only avi, mpg and mkv files.")
    parser.add_argument("-l", action="store_true", help="Use to list all the available subtitles and take the one you want.")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parseArguments()
    if args.l:
        Subscene(args.file).displaysubtitlelist()
    else:
        Subscene(args.file).downloadfirstsub()

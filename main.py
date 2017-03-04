# coding=utf-8
"""
Created on 7/9/16
@author: Vincent AIRIAU
Version V0.1
"""
import argparse
import logging
import os
import re
import shutil
import urllib
import urllib2
from zipfile import ZipFile

import requests
from lxml import html

logging.basicConfig(format='%(asctime)s - %(module)s: %(message)s', filename='subscene_g.log', filemode='w',
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
        self.episodename = os.path.splitext(os.path.basename(path))[0]
        self.localpath = os.path.dirname(path)
        self.zipfile_path = os.path.splitext(path)[0] + '.zip'
        self.strDestSubPath = self.localpath + "\\" + self.episodename + ".srt"

    def downloadfirstsub(self):
        sublist = self.getsubtitle(self.episodename)
        # If no subtitles, display a NOK message
        if not sublist or sublist == 0:
            logging.error("No subtitles are available for this release.")
            print "No subtitles are available for this release."
        # If subtitles are present, download and unpack the first one
        else:
            self.getsubtitlefile(sublist, self.zipfile_path)
            # print self.zipfile_path
            if os.path.exists(self.strDestSubPath):
                os.remove(self.strDestSubPath)
            with ZipFile(self.zipfile_path, 'r') as subtitle_zipfile:
                logging.info("extraction")
                subtitle_zipfile.extractall(path=self.localpath)
                subtitle_zipfile.close()
                os.remove(self.zipfile_path)
            strRetrievedSubPath = self.localpath + "\\" + subtitle_zipfile.namelist()[0]
            print strRetrievedSubPath
            os.rename(strRetrievedSubPath, self.strDestSubPath)

    def displaysubtitlelist(self):
        sublist = self.getsubtitle(self.episodename)

    @staticmethod
    def getsubtitle(episodename):
        '''

        :param episodename: regex
        :return: sub_list_links: a table with subtitle URLs or 0 if no subtitle
        '''
        # TODO: use regex to get the good or not take any
        tree = html.fromstring(opensubscene_rls_page(episodename))
        first_word = episodename.split(".",1)[0]
        # sub_list_names = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/span[2]/text()')
        i = 1
        sub_link = 0

        while 1:
            sub_name = str(tree.xpath('//div[@class="content"]/table/tbody/tr[' + str(i) + ']/td[@class="a1"]/a/span[2]/text()[1]')[0]).strip()
            # print "sub_name : " + sub_name
            if sub_name == episodename:
                sub_link = tree.xpath('//div[@class="content"]/table/tbody/tr[' + str(i) + ']/td[@class="a1"]/a/@href')[0]
                # print "sub_list_links : " + sub_link
                break
            elif re.compile(first_word).search(sub_name):
                sub_link = tree.xpath('//div[@class="content"]/table/tbody/tr[' + str(i) + ']/td[@class="a1"]/a/@href')[0]
                # print "sub_list_links : " + sub_link
                break
            elif not sub_name:
                break
            else:
                i += 1
                if not tree.xpath('//div[@class="content"]/table/tbody/tr[' + str(i) + ']/td[@class="a1"]/a/span[2]/text()[1]'):
                    break

        return sub_link

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
        # logging.info(content)
        subtitle_link = tree.xpath('//a[@id="downloadButton"]/@href')[0]
        subtitle_link = base_url + subtitle_link
        logging.info("Link to the subtitle is: " + subtitle_link)
        r = requests.get(subtitle_link, stream=True, headers={'User-Agent': user_agent})
        if r.status_code == 200:
            with open(localpath, 'wb') as f:
                # r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                f.close()
                logging.info("archive enregistrée")
        else:
            logging.error("Subtitle couldn't be downloaded.")
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
        grabber = Subscene(args.file)
        grabber.downloadfirstsub()

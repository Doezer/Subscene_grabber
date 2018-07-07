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
from urllib.parse import urlencode
from zipfile import ZipFile

import requests
import sys

import time
from lxml import html

cookiefilter = '__cfduid=d9867ef87b10f433cd70a0efb36c01d471473252835; _ga=GA1.2.1129327024.1473252838; ' \
               'LanguageFilter=13; HearingImpaired=0; ForeignOnly=False; ' \
               '__gads=ID=a9b6ddb36e78eb76:T=1473252861:S=ALNI_MYgAIy-JwZk3SaXGDbgRdjR6545wQ; _gat=1'
user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"


class Subscene(object):
    def __init__(self, path):
        logging.info("This is the path entered: " + path)
        # Retrieve filename (for example TV.SHOW.XViD-EVO), so remove path and extension
        self.episodename = os.path.splitext(os.path.basename(path))[0]  # Name of the file
        self.localpath = os.path.dirname(path)  # Path to the file
        self.zipfile_path = os.path.splitext(path)[0] + '.zip'  # Path to the zipfile
        self.strDestSubPath = self.localpath + "\\" + self.episodename + ".srt"  # Path to the subtitle file

    def downloadfirstsub(self):
        sublist = self.getsubtitle()
        # If no subtitles, display a NOK message
        if not sublist or sublist == 0:
            logging.error("No subtitles are available for this release.")
        # If subtitles are present, download and unpack the first one
        else:
            self.getsubtitlefile(sublist)
            # if the SRT file exists already, delete it
            if os.path.exists(self.strDestSubPath):
                os.remove(self.strDestSubPath)

            # Extract the downloaded file, then remove it
            with ZipFile(self.zipfile_path, 'r') as subtitle_zipfile:
                logging.info("Extracting...")
                subtitle_zipfile.extractall(path=self.localpath)
                subtitle_zipfile.close()
                os.remove(self.zipfile_path)

            str_retrieved_sub_path = self.localpath + "\\" + subtitle_zipfile.namelist()[0]
            logging.info(f'Original subtitle: {str_retrieved_sub_path}')
            os.rename(str_retrieved_sub_path, self.strDestSubPath)

    def displaysubtitlelist(self):
        sublist = self.getsubtitle()
        print(sublist)

    def opensubscene_rls_page(self):
        # Gets the search page content for one show or whatever the file of the name is=
        url = 'https://subscene.com/subtitles/release'
        values = {'q': self.episodename, 'l': ''}

        headers = {'User-Agent': user_agent, 'Cookie': cookiefilter}
        data = urlencode(values)
        time.sleep(1)
        req = requests.get(url, params=data, headers=headers)
        logging.debug("url : {}".format(url))
        logging.debug("data : {}".format(data))
        logging.debug("headers : {}".format(headers))
        content = req.text
        with open('debug_opensubscene_rls_page_content.txt', mode='w+', encoding='utf-8') as f:
            f.write(content)
        return content

    def getsubtitle(self):
        """Get subtitle from episodename

        :return: sub_list_links: a table with subtitle URLs or 0 if no subtitle
        """
        # TODO: use regex to get the good or not take any
        tree = html.fromstring(self.opensubscene_rls_page())

        try:
            episode_pattern = r'[sS]\d+[eE]\d+'
            current_episode = re.compile(episode_pattern).findall(self.episodename)[0]
            logging.debug('current_episode is {}'.format(current_episode))
        except:
            logging.info("This is not a TV show")
            current_episode = self.episodename

        i = 1
        sub_link = 0

        # Browse every line of the html
        while 1:
            sub_name = tree.xpath(f'//div[@class="content"]/table/tbody/tr[{i}]/td[@class="a1"]/a/span[2]/text()')[0].strip()
            logging.debug("Current subtitle line name : " + sub_name)
            logging.debug("The subtitle name we are searching for : {}".format(self.episodename))
            if self.episodename.upper() is sub_name.upper():
                logging.debug("Exact match found")
                sub_link = tree.xpath(f'/div[@class="content"]/table/tbody/tr[{i}]/td[@class="a1"]/a/@href')[0]
                logging.debug(f"Relative URL for the selected subtile : {sub_link}")
                break
            elif current_episode.upper() in sub_name.upper():
                logging.debug("Inexact match found")
                sub_link = tree.xpath(f'//div[@class="content"]/table/tbody/tr[{i}]/td[@class="a1"]/a/@href')[0]
                logging.debug(f"Relative URL for the selected subtile : {sub_link}")
                break
            elif not sub_name:
                break
            else:
                i += 1
                if not tree.xpath('//div[@class="content"]/table/tbody/tr[{i}]/td[@class="a1"]/a/span[2]/text()[1]'):
                    break

        return sub_link

    def getsubtitlefile(self, subtitlerelativeURL):
        localpath = self.zipfile_path
        base_url = 'https://subscene.com'
        url = base_url + subtitlerelativeURL

        headers = {'User-Agent': user_agent}
        time.sleep(1)
        req = requests.get(url, headers=headers)
        logging.debug("url : {}".format(url))
        logging.debug("headers : {}".format(headers))
        content = req.text
        with open('debug_getsubtitlefile_content.txt', mode='w+', encoding='utf-8') as f:
            f.write(content)
        tree = html.fromstring(content)
        subtitle_link = tree.xpath('//a[@id="downloadButton"]/@href')[0]
        subtitle_link = base_url + subtitle_link
        logging.info("Link to the subtitle is: " + subtitle_link)
        time.sleep(1)
        r = requests.get(subtitle_link, stream=True, headers={'User-Agent': user_agent})
        if r.status_code == 200:
            with open(localpath, 'wb') as f:
                # r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                f.close()
                logging.info("Archive recorded")
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
    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stdout,
        format="%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s <%(lineno)d>",
    )
    if args.l:
        Subscene(args.file).displaysubtitlelist()
    else:
        grabber = Subscene(args.file)
        grabber.downloadfirstsub()
    input("PRESS ENTER TO CONTINUE.")

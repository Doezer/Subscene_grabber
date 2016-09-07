'''
Created on 7/9/16
@author: Vincent AIRIAU
Version V0.1
'''

import urllib
import urllib2
from lxml import html
import sys
import requests


class Subscene():
    def __init__(self, path):
        print path
        # Retrieve filename (for example TV.SHOW.XViD-EVO), so remove path and extension
        showname = self.getfilename(path)
        # Retrieve corresponding subtitles list on subscene

        # If no subtitles, display a NOK message
        if self.getsubtitlelist(showname) == 0:
            print "NO SUBTITLES"
        # If subtitles are present, download and unpack the first one

        return

    def opensubscene(self, showname):
        # Gets the search page content for one show or whatever the file of the name is

        showname = 'Brooklyn.Nine-Nine.S03E03.HDTV.x264-FLEET.avi'
        url = 'https://subscene.com/subtitles/release'
        values = {'q': showname, 'l': ''}
        host = "subscene.com"
        cookiefilter = '__cfduid=d9867ef87b10f433cd70a0efb36c01d471473252835; _ga=GA1.2.1129327024.1473252838; LanguageFilter=13; HearingImpaired=0; ForeignOnly=False; __gads=ID=a9b6ddb36e78eb76:T=1473252861:S=ALNI_MYgAIy-JwZk3SaXGDbgRdjR6545wQ; _gat=1'
        user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
        #headers = {'User-Agent': user_agent, 'Cookie': cookiefilter, "Host": "subscene.com", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://u.subscene.com/filter?returnUrl=pm_O4prxOi6sDoEIFIf0e-c_hf7BgALPxPlMl83JgUgH2x4_0nME8hrOLeQRGPHNoPnMRmuwIFTU_zvlYXkoPJdrEKiFYLXf8rghOK4vrBEuesta_7MQanKOsolNpje89RpHlI47RplfH-Bv52bHH4vzeFI93Ibtm2oYU3obywLWqFkmYMpohpw5XjHRTrNP0", "Connection": "keep-alive"}
        headers = {'User-Agent': user_agent,'Cookie': cookiefilter}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        content = response.read()

        return content

    def getsubtitlelist(self, showname):
        # We have to get the subtitles list using urllib2 and using only english/NO HI settings
        # Returns a table with Subtitle | Subtitle URL
        # Or 0 if no subtitle
        print "2. We want to get the subtitle list off the website."
        the_page = self.opensubscene(showname)
        #print the_page
        tree = html.fromstring(the_page)
        sub_list_names = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/span[2]/text()')
        sub_list_links = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/@href')
        print sub_list_names
        del sub_list_links[1::2]
        print sub_list_links

        sub_list = {sub_list_names: sub_list_links}
        print sub_list

        return

    def getfilename(self, path):

        print "1. We're getting the file name first. It's the release name that will be used to query subscene."

        return 0

    def getsubtitlefile(self, subtitleURL):

        print "this function should get the first subtitle"

        return 0


toto=Subscene(str(sys.argv[1]))
'''
Created on 7/9/16
@author: Vincent AIRIAU
Version V0.1
'''

import urllib
import urllib2
from lxml import html
import sys
import os
import requests
import shutil

class Subscene():
    def __init__(self, path):
        print "This is the path entered: " + path
        # Retrieve filename (for example TV.SHOW.XViD-EVO), so remove path and extension
        showname = os.path.basename(path).replace('.avi', '').replace('.mkv', '').replace('.mpg', '')
        localpath= path.replace('.avi', '.zip').replace('.mkv', '.zip').replace('.mpg', '.zip')

        # Retrieve corresponding subtitles list on subscene
        sublist = self.getsubtitlelist(showname)
        # If no subtitles, display a NOK message
        if sublist == []:
            print "NO SUBTITLES"
        # If subtitles are present, download and unpack the first one
        else:
            self.getsubtitlefile(sublist[0], localpath)

    def opensubscene_rls_page(self, showname):
        # Gets the search page content for one show or whatever the file of the name is

        url = 'https://subscene.com/subtitles/release'
        values = {'q': showname, 'l': ''}
        host = "subscene.com"
        cookiefilter = '__cfduid=d9867ef87b10f433cd70a0efb36c01d471473252835; _ga=GA1.2.1129327024.1473252838; LanguageFilter=13; HearingImpaired=0; ForeignOnly=False; __gads=ID=a9b6ddb36e78eb76:T=1473252861:S=ALNI_MYgAIy-JwZk3SaXGDbgRdjR6545wQ; _gat=1'
        user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
        # headers = {'User-Agent': user_agent, 'Cookie': cookiefilter, "Host": "subscene.com", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://u.subscene.com/filter?returnUrl=pm_O4prxOi6sDoEIFIf0e-c_hf7BgALPxPlMl83JgUgH2x4_0nME8hrOLeQRGPHNoPnMRmuwIFTU_zvlYXkoPJdrEKiFYLXf8rghOK4vrBEuesta_7MQanKOsolNpje89RpHlI47RplfH-Bv52bHH4vzeFI93Ibtm2oYU3obywLWqFkmYMpohpw5XjHRTrNP0", "Connection": "keep-alive"}
        headers = {'User-Agent': user_agent, 'Cookie': cookiefilter}
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
        the_page = self.opensubscene_rls_page(showname)
        # print the_page
        tree = html.fromstring(the_page)
        sub_list_names = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/span[2]/text()')
        sub_list_links = tree.xpath('//div[@id="content"]/div[2]/div/div/table/tbody/tr/td/a/@href')
        print sub_list_names
        del sub_list_links[1::2]
        print sub_list_links
        return sub_list_links

    def getsubtitlefile(self, subtitlerelativeURL, localpath):

        print "3. We're getting the actual subtitle file"

        base_url = 'https://subscene.com'
        full_url = base_url + subtitlerelativeURL

        cookiefilter = '__cfduid=d9867ef87b10f433cd70a0efb36c01d471473252835; _ga=GA1.2.1129327024.1473252838; LanguageFilter=13; HearingImpaired=0; ForeignOnly=False; __gads=ID=a9b6ddb36e78eb76:T=1473252861:S=ALNI_MYgAIy-JwZk3SaXGDbgRdjR6545wQ'
        user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
        headers = {'User-Agent': user_agent, 'Cookie': cookiefilter}
        req = urllib2.Request(full_url, '',headers)
        response = urllib2.urlopen(req)
        # response = urllib2.urlopen(full_url)
        content = response.read()
        tree = html.fromstring(content)
        #print content
        subtitle_link = tree.xpath('//a[@id="downloadButton"]/@href')[0]
        subtitle_link = base_url + subtitle_link
        # retrieve zip file

        r = requests.get(subtitle_link, stream=True, headers={'User-Agent': user_agent})
        if r.status_code == 200:
            with open(localpath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)



        # req = urllib2.Request(subtitle_link)
        # req.add_header('User-Agent', user_agent)
        # response = urllib2.urlopen(req)

        # extract sub

        return 0


Subscene(str(sys.argv[1]))

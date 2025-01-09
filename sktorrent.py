#VERSION: 0.2
#AUTHORS: wahibre (wahibre@gmx.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

max_searched_pages = 20
sktorrent_credentials = {
    'uid':  '123456',
    'pass': '0123456789abcdef0123456789abcdef'
}

from html.parser import HTMLParser
import re
import urllib
import os
import tempfile
# qBittorrent
import helpers
from novaprinter import prettyPrinter

class sktorrent(object):
    """
    CATEGORY (sktorrent.eu)
    0   ----
    9   xXx
    23  Knihy a casopisy
    25  Ostatni
        Movie hall
    1   Filmy CZ/SK dabing
    5   Filmy Kreslene
    14  Filmy Kamera
    15  Filmy s titulkama
    20  Filmy DVD
    31  Filmy bez titulku
        HD - BluRay - 3D - UHD
    3   3D Filmy
    19  HD Filmy
    28  Blu-ray Filmy
    29  3D Blu-ray Filmy
    43  UHD Filmy
        Game hall
    18  Hry na Windows
    30  Hry na Konzole
    37  Hry na Linux
    59  Hry na Mac
    60  xXx hry (18+)
    63  VR Hry
        TV
    16  Serial
    17  Dokument
    42  TV Porad
    44  Sport
        Audio - video hall
    2   Hudba
    22  Hudba DJ's Mix
    24  Mluvene slovo
    26  Hudebni videa
    45  Soundtrack
        Soft - app
    21  Programy
    27  Mobil, PDA
    58  Neschvalene
        Externe
    62  SkTSocial
    """

    url = 'http://sktorrent.eu'       # sktorrent.url and MyHtmlParser.engine must be equal!
    name = 'SK Torrent'
    supported_categories = {
        'all':      [0], 
        'movies':   [1, 15, 20, 31, 19, 28, 3, 29, 43, 14], 
        'tv':       [16, 17, 42, 44],
        'music':    [2, 22, 24, 26, 45], 
        'games':    [18, 37, 30, 59, 63, 60],
        'anime':    [5], 
        'software': [21, 27, 58], 
        'pictures': [25], 
        'books':    [23]
    }
    debug = False
##    log_file_name = os.path.join(tempfile.gettempdir(), "qbittorrent_sktorrent_plugin.log")

##    def log(self, msg):
##        if self.debug:
##            log_file = open(self.log_file_name, "a")
##            log_file.write(msg)
##            log_file.close()
##            print(msg)

    class MyHtmlParser(HTMLParser):
        download_prefix = 'http://sktorrent.eu/torrent/'
        engine = 'http://sktorrent.eu'                     # sktorrent.url and MyHtmlParser.engine must be equal!
        found_table_lista = 0
        found_td_lista= 0
        found_td_kat= 0
        found_td_kat_a= 0
        found_td_kat_a_b= 0
        found_td_dl= 0
        found_td_seeds = 0
        found_td_seeds_a = 0
        found_td_leech = 0
        found_td_leech_a = 0
        found_torr_row = 0
        td_col_nr = 0
        found_td_nazov = 0
        td_a_href = ""
        td_a_title = ""
        item_category = ""
        current_item = None
        
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url

        def handle_starttag(self, tag, attrs):
            if self.found_td_kat_a == 1 and tag == "b":
                    self.found_td_kat_a_b = 1

            if self.found_td_lista == 1:
                if tag == "a":
                    if self.found_td_kat == 1:
                        self.found_td_kat_a = 1

                    if self.found_td_seeds == 1:
                        self.found_td_seeds_a = 1

                    if self.found_td_leech == 1:
                        self.found_td_leech_a = 1

                    for (k,v) in attrs:
                        if k == "href" and v != "#":
                            self.td_a_href = v
                        if k == "title":
                            self.td_a_title = v
                #if tag == "img" and ('src', 'sktorrent_files/download.gif') in attrs:
                if tag == "img" and ('alt', 'torrent') in attrs:
                    self.found_torr_row = 1
                    self.current_item['link'] = self.download_prefix + self.td_a_href

                if self.found_td_nazov==1:
                    self.current_item['name'] = self.td_a_title
                    self.current_item['desc_link'] = self.download_prefix + self.td_a_href
                    self.current_item['engine_url'] = self.engine
            else:
                if self.found_table_lista == 1:
                    if tag == "tr":
                        found_tr = 1
                    #if tag == "td" and ('class', 'lista') in attrs :
                    if tag == "td" :
                        self.found_td_lista = 1
                        self.td_col_nr += 1
                        if self.td_col_nr == 1:
                            self.found_td_kat = 1
                        if self.td_col_nr == 2:
                            self.found_td_dl = 1
                        if self.td_col_nr == 3:
                            self.found_td_nazov = 1
                        if self.td_col_nr == 5:
                            self.found_td_seeds = 1
                        if self.td_col_nr == 6:
                            self.found_td_leech = 1
                else:
                    if tag == "table" and ('class', 'lista') in attrs :
                        self.found_table_lista = 1
                        self.current_item = dict()


        def handle_endtag(self, tag):

            if self.found_td_kat_a_b == 1 and tag == "b":
                self.found_td_kat_a_b = 0
                return

            if self.found_torr_row == 1 and tag == "tr":
                self.found_torr_row = 0

                """
                print("---------------------------------")
                print("Category:   "+self.item_category)
                print("Link:       "+self.current_item['link'])
                print("Name:       "+self.current_item['name'])
                print("Size:       "+self.current_item['size'])
                print("Seeds:      "+self.current_item['seeds'])
                print("Leech:      "+self.current_item['leech'])
                print("Engine url: "+self.current_item['engine_url'])
                print("Desc link:  "+self.current_item['desc_link'])
                #print("Pub. date:  "+self.current_item['pub_date'])
                """
                prettyPrinter(self.current_item)

            if self.found_td_kat_a == 1 and tag == "a":
                self.found_td_kat_a = 0

            if self.found_td_seeds_a == 1 and tag == "a":
                self.found_td_seeds_a = 0

            if self.found_td_leech_a == 1 and tag == "a":
                self.found_td_leech_a = 0

            if self.found_td_kat == 1 and tag == "td":
                self.found_td_kat = 0

            if self.found_td_dl == 1 and tag == "td":
                self.found_td_dl = 0

            if self.found_td_nazov == 1 and tag == "td":
                self.found_td_nazov = 0

            if self.found_td_seeds == 1 and tag == "td":
                self.found_td_seeds = 0

            if self.found_td_leech == 1 and tag == "td":
                self.found_td_leech = 0

            if self.found_td_lista== 1 and tag == "td":
                self.found_td_lista= 0
                self.td_a_href = ""
                self.td_a_title = ""
                return

            if self.found_table_lista == 1 :
                if tag == "tr":
                    self.found_tr = 0
                    self.td_col_nr = 0
                if tag == "table":
                    self.found_table_lista = 0
                    self.found_td_lista= 0


        def handle_data(self, data):
            if self.found_td_kat_a_b == 1:
                self.item_category = data.strip()
            else:
                if self.found_torr_row == 1:
                    d = data.strip()
                    if self.found_td_nazov == 1:
                        if d.startswith('Velkost'):
                            self.current_item['size'] = re.search('Velkost\s([0-9.]+\s[KMGTkmgtBb]{1,2})', d,).group(1)
                    if self.found_td_seeds_a == 1:
                        self.current_item['seeds'] = d
                    if self.found_td_leech_a == 1:
                        self.current_item['leech'] = d


    def get_sktorrent_page(self, url):
        return self.get_page_content_with_cookies(url, 'uid=%s; pass=%s'%(sktorrent_credentials["uid"], sktorrent_credentials["pass"]))

    def get_page_content_with_cookies(self, url, cookies=None):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
        headers = {'User-Agent': user_agent}
        if cookies is not None:
            headers["Cookie"] = cookies
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        return response.read()

    def search(self, what, cat='all'):
        kat_list = self.supported_categories[cat]
        for kat_i in kat_list:
            kat = str(kat_i)
            for page in range(0, max_searched_pages):
                #imgage version: query = "https://sktorrent.eu/torrent/torrents_v2.php?search="+what+'&category='+kat+'&zaner=&active=0&page='+str(page)
                #text version:   
                query = "https://sktorrent.eu/torrent/torrents.php?search="+what+'&category='+kat+'&zaner=&active=0&page='+str(page)
                #file version:   query = "file:///tmp/sktorrent.html"

                dat = self.get_sktorrent_page(query)
                response = dat.decode('utf-8', 'replace')
                """
                f = open("/tmp/sktorrent.html", "w")
                f.write(response)
                f.close()
                """
                parser = self.MyHtmlParser("url")
                parser.feed(response)
                parser.close()
                if not parser.current_item:
                    break;
        
    def download_torrent(self, url):
        torr = self.get_sktorrent_page(url)
        file, path = tempfile.mkstemp('.torrent')
        file = os.fdopen(file, "wb")
        file.write(torr)
        file.close()
        print(path+" "+url)

## test
if __name__ == "__main__":
    s = sktorrent()
    #s.debug = True
    search_phrase = "teorie"
    s.search(search_phrase)
    #s.search(search_phrase, "movies")
    #s.search(search_phrase, "tv")
    #s.search(search_phrase, "music")

#VERSION: 0.1
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
    url = 'http://sktorrent.eu'       # sktorrent.url and MyHtmlParser.engine must be equal!
    name = 'SK Torrent'

    #Possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')  
    supported_categories = {'all': '0', 'movies': '18', 'tv': '16', 'music': '2', 'games': '18', 'anime': '5', 'software': '21', 'pictures': '25', 'books': '23'}  # 25 - others

    max_searched_pages = 10
    debug = False
##    log_file_name = os.path.join(tempfile.gettempdir(), "qbittorrent_sktorrent_plugin.log")

    class DownloadHtmlParser(HTMLParser):
        download_prefix = 'http://sktorrent.eu/torrent/'
        download_link = None
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url            
        
        def handle_starttag(self, tag, attrs):
            if tag == "a" and ("title","Stiahnut") in attrs:
                d = dict(attrs)
                self.download_link = self.download_prefix + d["href"]
                    
##    def log(self, msg):
##        if self.debug:
##            log_file = open(self.log_file_name, "a")
##            log_file.write(msg)
##            log_file.close()

    class MyHtmlParser(HTMLParser):
        download_prefix = 'http://sktorrent.eu/torrent/'
        engine = 'http://sktorrent.eu'                     # sktorrent.url and MyHtmlParser.engine must be equal!
        found_list = 0
        found_href = 0
        found_br = 0
        found_image = 0
        torrentlink = ""
        torrentname = ""
        torrenttitle=""
        current_item = None
        
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url

        def handle_starttag(self, tag, attrs):
            if self.found_list:
                if self.found_href:
                    if self.found_image == 0:
                        if tag == "img":
                            self.found_image=1

                            self.current_item['link'] = self.download_prefix + self.torrentlink
                            self.current_item['name'] = self.torrenttitle   # e.g. 'Stiahni si Filmy Kamera Rampage / Nicitele (2018)[CAM]'
                            #self.current_item['name'] = self.torrentname   # e.g. 'Rampage / Nicitele (2018) (NEW HD-TS X264) (1080p) + CZ Titulky = CSFD 69%'
                            self.current_item['engine_url'] = self.engine
                            self.current_item['link'] = self.download_prefix + self.torrentlink
                            self.current_item['desc_link'] = self.download_prefix + self.torrentlink
                
                else:
                    if tag == "a":
                        self.found_href=1
                        d = dict(attrs)
                        self.torrenttitle= d["title"]
                        self.torrentlink = d["href"]
                    elif tag == "br":
                        self.found_br = 1

            else:
                if tag == "div" and ("style", "display: inline-block;") in attrs:
                    self.found_list = 1
                    self.current_item = dict()
        
        def handle_endtag(self, tag):
            if self.found_list:
                if self.found_href:
                    if tag == "a":
                        self.found_href = 0
                        self.found_image = 0
                        self.torrenttitle = ""
                        self.torrentlink = ""
                else:
                    if tag == "div":
                        self.found_list = 0
                        self.found_br = 0
##                        print(self.current_item)			# test
                        prettyPrinter(self.current_item)

                        
        def handle_data(self, data):
            if self.found_image:
                self.torrentname = data
            if self.found_br:
                d = data.strip()
                if d.startswith('Velkost'):
                    self.current_item['size'] = re.search('Velkost\s([0-9.]+\s[KMGTkmgtBb]{1,2})', d,).group(1)
                elif d.startswith('Odosielaju'):
                    self.current_item['seeds'] = re.search('Odosielaju\s:\s(\d+)', d,).group(1)
                elif d.startswith('Stahuju'):
                    self.current_item['leech'] = re.search('Stahuju\s:\s(\d+)', d,).group(1)

    def search(self, what, cat='all'):
        for page in range(0, self.max_searched_pages-1):
            query = "http://sktorrent.eu/torrent/torrents_v2.php?search="+what+'&category='+self.supported_categories[cat]+'&zaner=&active=0&page='+str(page)
            response = helpers.retrieve_url(query)
            parser = self.MyHtmlParser(self.url)
            parser.feed(response)
            parser.close()
            if not parser.current_item:
                break;
        
    def download_torrent(self, url):
        # Find torrent url
        response = helpers.retrieve_url(url)
        parser = self.DownloadHtmlParser(url)
        parser.feed(response)
        parser.close()        
        torr_file_url = parser.download_link        
        # download the .torrent file
        req = urllib.request.Request(torr_file_url)
        req.add_header("Cookie", 'uid=%s; pass=%s'%(sktorrent_credentials["uid"], sktorrent_credentials["pass"]))
        response = urllib.request.urlopen(req)
        data = response.read()
        # write to disk
        file, path = tempfile.mkstemp('.torrent')
        file = os.fdopen(file, "wb")
        file.write(data)
        file.close()
        print(path+" "+url)


## test
if __name__ == "__main__":
    s = sktorrent()
##    s.debug = True
    s.search("rampage", "movies")

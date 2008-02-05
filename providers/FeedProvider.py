from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLinkFromHTMLSource
import urllib, urlparse
import time

from Utilities import _info
import Cache

class FeedAtom(object):
    def __init__(self, provider, url):
        self.provider = provider
        self.url = url
        self.feed = None
        self.stale = True
        self.error = None
        self.dead = False

        self.getFeedUrl()
    
    def getFeedUrl(self):
        # it's very unlikely that the feed source will move
        # TODO - check stale cache first. Man, the feed provider is too complicated.
        Cache.getContentOfUrlAndCallback( self.gotMainPage, self.url, timeout = self.timeout() * 10, wantStale = False, failure = self.failed ) # TODO - use stale version somehow
    
    def gotMainPage( self, data, stale ):
        rss = getRSSLinkFromHTMLSource(data)
        if rss:
            feed_url = urlparse.urljoin( self.url, rss )
            self.getFeed( feed_url )
        else:
            self.dead = True
            self.provider.changed()
    
    def getFeed(self, feed_url, username = None, password = None):
        Cache.getContentOfUrlAndCallback( self.gotFeed, feed_url, username, password, timeout = self.timeout(), wantStale = True, failure = self.failed )

    def gotFeed( self, data, stale ):
        feed = feedparser.parse( data )
        if feed and 'feed' in feed and 'title' in feed.feed:
            self.feed = feed
            self.stale = stale
            self.provider.changed()
        else:
            self.dead = True
            self.provider.changed()
        
    def failed( self, error ):
        self.error = error
        self.provider.changed()

    def content(self):
        if self.dead:
            return ""
        elif self.error:
            return "<pre>%s</pre>"%urllib.quote( self.error )
        elif self.feed:
            return self.htmlForFeed( url = self.url, feed = self.feed, stale = self.stale )
        else:
            return self.htmlForPending( url = self.url, stale = self.stale )




    def timeout(self):
        return 60 * 20

    def htmlForPending( self, url, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.provider.spinner()
        else:
            spinner_html = ""
        return "<h3><a href='%s'>%s%s</a></h3>"%(url,url,spinner_html)
   
    
    def htmlForFeed( self, url, feed, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.provider.spinner()
        else:
            spinner_html = ""
        html = "<h3><a href='%s'>%s%s</a></h3>"%( url, feed.feed.title, spinner_html )
        entries = feed.entries
        for item in entries[0:4]:
            if 'published_parsed' in item:
                html += '<span class="feed-date">%s</span>'%( time.strftime("%b %d", item.published_parsed ) )
            elif 'updated_parsed' in item:
                html += '<span class="feed-date">%s</span>'%( time.strftime("%b %d", item.updated_parsed ) )
            html += '<p class="feed-title"><a href="%s">%s</a></p>'%( item.link, item.title )
            detail = None
            if 'content' in item and len(item.content) > 0:
                detail = item.content[0].value
            elif 'summary' in item and len(item.summary) > 0:
                detail = item.summary
            if detail:
                raw = re.sub(r'<.*?>', '', detail) # strip tags
                trimmed = " ".join( re.split(r'\s+', raw.strip())[0:10] )
                html += '<p class="feed-content">%s&nbsp;<a href="%s">...</a></p>'%( trimmed, item.link )
        return html


class FeedProvider( Provider ):
    
    def content(self):
        return "".join([ atom.content() for atom in self.atoms ])
    
    def atomClass(self):
        return FeedAtom

    def provide( self ):
        todo = self.urls() # if we're claiming from boring_urls, do it first
        if not todo: return

        self.atoms = [ self.atomClass()( self, url ) for url in todo ]

    # override these
    def urls(self):
        return self.person.boring_urls
    
    
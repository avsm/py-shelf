from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLink

class FeedProvider( Provider ):

    def about( self, person ):
        info = []

        urls = person.urls()
        for url in urls:
            NSLog("Looking at %s for feed"%url)
            rss = getRSSLink( url )
            if rss:
                NSLog("Found feed url %s"%( rss ))
                feed = feedparser.parse( rss )
                if feed['feed']:
                    NSLog( "Parsed feed as %s"%feed['feed']['title'] )
                    html = "<h3>%s</h3>"%feed['feed']['title']
                    entries = feed.entries
                    for item in entries[0:4]:
                        html += '<p><a href="%s">%s</a></p>'%( item.link, item.title )
                    info.append(html)
                else:
                    NSLog(" Can't parse feed" )
            else:
                NSLog("No feed" )

        return info


Provider.PROVIDERS.append( FeedProvider() )
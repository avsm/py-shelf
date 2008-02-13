from Provider import *
import urllib
import re
import simplejson
from datetime import datetime
from time import time, strftime, gmtime

from Utilities import *
import Cache

class DopplrProvider( Provider ):

    def provide( self ):
        self.token = NSUserDefaults.standardUserDefaults().stringForKey_("dopplrToken")
        dopplrs = self.clue.takeUrls(r'dopplr\.com/traveller')
        if not dopplrs or not self.token: return
        
        return # We have an SSL error right now - can't do anything.
    
        self.username = re.search(r'/traveller/([^/]+)', dopplrs[0]).group(1)
        self.atoms = [ "<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a>&nbsp;%s</h3>"%( self.username, self.spinner() ) ]
        self.changed()

        url = "https://www.dopplr.com/api/traveller_info.js?token=%s&traveller=%s"%( self.token, self.username )
        Cache.getContentOfUrlAndCallback( callback = self.gotDopplrData, url = url, timeout = 3600, wantStale = True, failure = self.failed )
    
    def failed(self, error):
        self.atoms[1:] = [ html_escape(unicode(error)) ]
        self.changed()
    
    def gotDopplrData(self, data, stale):
        try:
            doc = simplejson.loads( data )
            doc['traveller']['status']
        except ValueError, KeyError:
            return # no service?
        
        # dopplr api coveniently provides offset from UTC :-)
        self.offset = int(str(doc['traveller']['current_city']['utcoffset']))

        self.atoms = []
        self.atoms.append("<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a></h3>"%( self.username ))
        self.atoms.append("<p>%s %s.</p>"%(
            self.clue.displayName(),
            doc['traveller']['status']
        ))
        self.atoms.append("")

        self.performSelector_withObject_afterDelay_( 'updateClock', None, 0 )
        
        self.changed()

    def updateClock(self):
        self.performSelector_withObject_afterDelay_( 'updateClock', None, 20 )

        epoch = time() + self.offset
        self.atoms[2] = "<p class='time'>Time in %s is %s.</p>"%(
            doc.traveller.current_city.country,
            strftime("%a&nbsp;%l:%M&nbsp;%p", gmtime(epoch))
        )
        self.changed()


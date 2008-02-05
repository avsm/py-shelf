from Provider import *
import urllib
import re
import xmltramp
from datetime import datetime
from time import time, strftime, gmtime

from Utilities import _info
import Cache

class DopplrProvider( Provider ):

    def provide( self ):
        self.token = NSUserDefaults.standardUserDefaults().stringForKey_("dopplrToken")
        dopplrs = self.person.takeUrls(r'dopplr\.com/traveller')
        if not dopplrs or not self.token: return
    
        self.username = re.search(r'/traveller/([^/]+)', dopplrs[0]).group(1)
        self.atoms = [ "<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a>&nbsp;%s</h3>"%( self.username, self.spinner() ) ]
        self.changed()

        url = "https://www.dopplr.com/api/traveller_info.xml?token=%s&traveller=%s"%( self.token, self.username )
        Cache.getContentOfUrlAndCallback( self.gotDopplrData, url, timeout = 3600, wantStale = True, failure = self.failed )
    
    def failed(self, error):
        self.atoms[1:] = [ unicode(error) ]
        self.changed()
    
    def gotDopplrData(self, data, stale):
        try:
            doc = xmltramp.parse( data )
            doc.traveller.status
        except AttributeError:
            return # no service?
        
        # dopplr api coveniently provides offset from UTC :-)
        self.offset = int(str(doc.traveller.current_city.utcoffset))

        self.atoms = []
        self.atoms.append("<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a></h3>"%( self.username ))
        self.atoms.append("<p>%s %s.</p>"%(
            self.person.displayName(),
            doc.traveller.status
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

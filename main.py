#
#  main.py
#  PyShelf
#
#  Created by Tom Insam on 06/01/2008.
#  Copyright __MyCompanyName__ 2008. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit
import os

# put external deps here where py2app can find them
import PyObjCTools
import WebKit
import json
import urllib2
import sgmllib
import cgi
import xml.dom.minidom
import HTMLParser

from PyObjCTools import AppHelper

# import sparkle framework
base_path = os.path.join(os.path.dirname(os.getcwd()), 'Frameworks')
bundle_path = os.path.abspath(os.path.join(base_path, 'Sparkle.framework'))
objc.loadBundle('Sparkle', globals(), bundle_path=bundle_path)

NSUserDefaults.standardUserDefaults().registerDefaults_({
    'googleSocial':False,
    'googleSocialContext':False,
    'bringAppForward':True,
    'alwaysOnTop':True,
    'firstRun':True,
    'debug':False
})

# import modules containing classes required to start application and load MainMenu.nib
import PyShelfApplication
import PyShelfWindowController

# pass control to AppKit
AppHelper.runEventLoop()

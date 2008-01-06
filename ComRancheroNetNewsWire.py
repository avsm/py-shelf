from ScriptingBridge import *
from Extractor import *

class ComRancheroNetNewsWire(Extractor):

    def __init__(self):
        super( ComRancheroNetNewsWire, self ).__init__()
        self.nnw = SBApplication.applicationWithBundleIdentifier_("com.ranchero.NetNewsWire")

    def clues(self):
        if self.nnw.selectedHeadline().exists() == 0: return [] 
        url = self.nnw.selectedHeadline().subscription().homeURL()
        return self.clues_from_url( url )
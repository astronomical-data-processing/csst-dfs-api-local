import logging

log = logging.getLogger('csst')

class RefFitsApi(object):
    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
    
    def fetch(self, **kwargs):
        pass

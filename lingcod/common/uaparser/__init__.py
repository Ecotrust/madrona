import regexes, parser
import clientos

class browser_platform():
    def __init__(self,ua):
        a = parser.UserAgent(ua)
        b = clientos.client_os(ua) 
        self.family = a.family
        self.v1 = int(a.v1)
        self.v2 = int(a.v2)
        self.v3 = int(a.v3)
        self.platform = b['platform']
        self.full_platform = b['full_platform']
    
    def __repr__(self):
        return "%s %d.%d.%d on %s" % (self.family,self.v1,self.v2,self.v3,self.platform)

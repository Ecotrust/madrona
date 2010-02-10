from lingcod.common import uaparser

fh = open('top50.txt','r')

for ua in [x.strip() for x in fh.readlines()]:
    print uaparser.browser_platform(ua)


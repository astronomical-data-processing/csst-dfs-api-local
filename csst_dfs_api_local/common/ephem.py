from urllib import request
import json

class EphemSearchApi(object):
    def __init__(self):
        self.data = []
        self.url = 'http://172.31.248.218:30180/search/v2'
    
    def gaia_query(self, ra: float, dec: float, radius: float, mag: float, limit: int):
        req = request.Request(url = self.url, method="post")
        req.add_header('Content-Type', 'application/json')
        data = { "ra":ra, "dec":dec, "radius":radius, "mag": mag, "limit": limit}
        data = json.dumps(data)

        data = data.encode()
        res = request.urlopen(req, data=data)
        content = res.read()
        print(content)
        return content
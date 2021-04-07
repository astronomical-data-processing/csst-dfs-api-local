from urllib import request
import json

class CatalogApi(object):
    def __init__(self):
        self.data = []
        self.url = 'http://172.31.248.218:30180/search/v2'
    
    def gaia3_query(self, ra: float, dec: float, radius: float, min_mag: float,  max_mag: float,  obstime: int, limit: int):
        req = request.Request(url = self.url, method="post")
        req.add_header('Content-Type', 'application/json')
        data = { "ra":ra, "dec":dec, "radius":radius, "min_mag": min_mag, "max_mag": max_mag, "obstime": obstime, "limit": limit}
        data = json.dumps(data)
        data = data.encode()
        res = request.urlopen(req, data=data)
        content = res.read()
        print(content)
        return content
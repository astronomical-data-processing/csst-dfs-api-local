import urllib
import json
from csst_dfs_commons.models import Result

class CatalogApi(object):
    def __init__(self):
        self.data = []
        self.url = r'http://csst.astrolab.cn:30180/search/v2'
    
    def gaia3_query(self, ra: float, dec: float, radius: float, min_mag: float,  max_mag: float,  obstime: int, limit: int):
        data = { "ra":ra, "dec":dec, "radius":radius, "catalog_name": "gaia3", "min_mag": min_mag, "max_mag": max_mag, "obstime": obstime, "limit": limit}
        return self.rest_request(data)
    
    def rest_request(self, data):
        try:
            Headers = {"Content-type": "application/x-www-form-urlencoded"}

            data = urllib.parse.urlencode(data).encode("utf-8") 
            req =  urllib.request.Request(self.url,data,Headers)
            response = urllib.request.urlopen(req, timeout=30)
            html = response.read().decode("utf-8") 
            resp = json.loads(html)

            if resp["code"] == 0:
                return Result.ok_data(data=resp["data"]).append("totalCount", resp["object"]["totalCount"])
            else:
                return Result.error(message = resp.message)

        except Exception as e:
            return Result.error(message=repr(e))        
       
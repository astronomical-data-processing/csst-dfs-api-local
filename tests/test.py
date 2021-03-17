import logging

from csst_dfs_api_local.ifs import FitsApi

api = FitsApi()
# api.scan2db()
c, r = api.db.select_one(
    "select * from t_rawfits where id=?",
    ('CCD1_Flat_img.fits', )
)
print(r)
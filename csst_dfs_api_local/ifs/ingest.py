import os, sys
import argparse
import logging
from astropy.io import fits
import datetime
import shutil

from csst_dfs_api_local.common.db import DBClient
from csst_dfs_commons.utils.fits import get_header_value

log = logging.getLogger('csst-dfs-api-local')

def ingest():
    
    parser = argparse.ArgumentParser(prog=f"{sys.argv[0]}", description="ingest the local files")
    parser.add_argument('-i','--infile', dest="infile", help="a file or a directory")
    parser.add_argument('-m', '--copyfiles', dest="copyfiles", action='store_true', default=False, help="whether copy files after import")
    args = parser.parse_args(sys.argv[1:])

    import_root_dir = args.infile
    if import_root_dir is None or (not os.path.isfile(import_root_dir) and not os.path.isdir(import_root_dir)):
        parser.print_help()
        sys.exit(0)

    db = DBClient()
    if os.path.isfile(import_root_dir):
        log.info(f"prepare import {import_root_dir}")
        ingest_one(import_root_dir, db, args.copyfiles)
    if os.path.isdir(import_root_dir):
        for (path, _, file_names) in os.walk(import_root_dir):
            for filename in file_names:
                if filename.find(".fits") > 0:
                    file_full_path = os.path.join(path, filename)
                    log.info(f"prepare import {file_full_path}")
                    try:
                        ingest_one(file_full_path, db, args.copyfiles)
                    except Exception as e:
                        print(f"{file_full_path} import error!!!")
                        log.error(e)

    db.close()

def ingest_one(file_path, db, copyfiles):
    dest_root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")

    hdul = fits.open(file_path)
    header = hdul[0].header
    header1 = hdul[1].header

    obs_id = header["OBSID"]
    exp_start_time = f"{header['DATE-OBS']}"
    exp_time = header['EXPTIME']
    
    module_id = header["INSTRUME"]
    obs_type = header["OBSTYPE"]
    object_name = header["OBJECT"]
    qc0_status = -1
    prc_status = -1
    time_now = datetime.datetime.now()
    create_time = time_now.strftime('%Y-%m-%d %H:%M:%S')

    facility_status_id = 0
    module_status_id = 0

    existed = db.exists("select * from t_observation where obs_id=?", (obs_id,))
    if not existed:
        db.execute("insert into t_observation \
            (obs_id,obs_time,exp_time,module_id,obs_type,facility_status_id, module_status_id, qc0_status, prc_status,create_time) \
            values (?,?,?,?,?,?,?,?,?,?)",
        (obs_id,exp_start_time,exp_time,module_id,obs_type,facility_status_id,module_status_id,qc0_status, prc_status,create_time))
        db.end()
    #level0
    detector = get_header_value("DETNAM", header1, "-")
    filename = header["FILENAME"]
    version = get_header_value("IMG_VER", header, "-")
    
    existed = db.exists(
            "select * from ifs_level0_data where filename=?",
            (filename,)
        )
    if existed:
        log.warning('%s has already been imported' %(file_path, ))
        db.end()
        return    

    detector_status_id = 0

    file_full_path = file_path

    if copyfiles:
        file_dir = f"{dest_root_dir}/{module_id}/{obs_type.upper()}/{header['EXPSTART']}/{obs_id}/MS"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_full_path = f"{file_dir}/{filename}.fits"

    level0_id = f"{obs_id}{detector}"  

    c = db.execute("insert into ifs_level0_data \
        (level0_id, obs_id, detector_no, obs_type, obs_time, exp_time,detector_status_id, filename, file_path,qc0_status, prc_status,create_time) \
        values (?,?,?,?,?,?,?,?,?,?,?,?)",
        (level0_id, obs_id, detector, obs_type, exp_start_time, exp_time, detector_status_id, filename, file_full_path, qc0_status, prc_status,create_time))
    db.end()
    level0_id_id = db.last_row_id()
    #level0-header
    ra_obj = header["OBJ_RA"]
    dec_obj = header["OBJ_DEC"]
    db.execute("delete from ifs_level0_header where id=?",(level0_id_id,))    
    db.execute("insert into ifs_level0_header \
        (id, ra, `dec`, object_name, version) \
        values (?,?,?,?,?)",
        (level0_id_id, ra_obj, dec_obj, object_name, version))
    
    if copyfiles:
        #copy files
        shutil.copyfile(file_path, file_full_path)

    db.end()

    print(f"{file_path} imported")

if __name__ == "__main__":
    ingest()
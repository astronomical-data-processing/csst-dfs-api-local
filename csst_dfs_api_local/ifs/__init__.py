from .fits import FitsApi
from .reffits import RefFitsApi
from .result0 import Result0Api
from .result1 import Result1Api

def ingest():
    import os
    root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
    paths = {}
    fitsApi = FitsApi()
    refApi = RefFitsApi()

    for (path, _, file_names) in os.walk(root_dir):
        for filename in file_names:
            if filename.find(".fits") > 0:
                file_full_path = os.path.join(path, filename)
                
                file_type = 'None'
                if 'obs' in filename.lower():
                    file_type = 'obs'
                elif 'flat' in filename.lower():
                    file_type = 'flat'
                elif 'bias' in filename.lower():
                    file_type = 'bias'
                elif 'hgar' in filename.lower():
                    file_type = 'arc'
                elif 'sky' in filename.lower():
                    file_type = 'sky'

                if file_type in ['obs']:
                    fitsApi.import2db(file_path = file_full_path.replace(root_dir, '')[1:])
                    print("%s [type:%s] imported" %(file_full_path, file_type))

                if file_type in ['flat', 'bias', 'arc','hgar', 'sky']:
                    refApi.import2db(file_path = file_full_path.replace(root_dir, '')[1:])     
                    print("%s [type:%s] imported" %(file_full_path, file_type))               
    return paths

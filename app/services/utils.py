import glob
import os

def resultfile_delete(delete_patterns):
    try:
        for dir_path, pattern in delete_patterns:
            full_pattern = os.path.join(dir_path, pattern)
            for file_path in glob.glob(full_pattern):
                if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        raise Exception(e)
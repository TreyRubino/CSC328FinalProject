# Trey Rubino

import os

def normalize_path(path):
    """
    Normalize the given path to an absolute, canonical path
    """
    return os.path.normpath(os.path.abspath(path))

def is_within_root(root_path, target_path):
    """
    Check if the targe path is within the project root
    """
    root = normalize_path(root_path)
    target = normalize_path(target_path)
    return target.startswith(root + os.sep) or target == root

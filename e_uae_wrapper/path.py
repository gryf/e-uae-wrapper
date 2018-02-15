"""
Misc utilities
"""
import os


def which(executables):
    """
    Check if there selected archiver is available in the system and place it
    to the archiver attribute
    """

    if not isinstance(executables, list):
        executables = [executables]

    for fname in executables:
        for path in os.environ["PATH"].split(os.pathsep):
            path = os.path.join(path.strip('"'), fname)
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return fname

    return None

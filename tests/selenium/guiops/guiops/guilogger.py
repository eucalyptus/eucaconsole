import os
import sys
import logging
import time

class Guilogger(object):
    # Constructor for Guilogger
    def __init__(self,
                 parent_logger_name = 'guitester',
                 identifier="guilogger",
                 stdout_level="debug",
                 stdout_format = None,
                 logfile = "",
                 logfile_level="debug",
                 make_log_file_global=True,
                 use_global_log_files=True,
                 file_format = None,
                 clear_file = False):
        pass
#!/usr/bin/env python
# coding: utf-8

# ### diagnosis.py
# ```
# Created by: Ravi Kasarla
# Creation Date: 02-OCT-2019
# Purpose: Any utility functions 
# Input Parameters:
#     As required per function
# Output:
#     What ever function sends back
#
# Version History:
#     Version          Date            Change Reason
#     -------          ------------    -------------------------------------------------------------------
#     1.1              02-OCT-2019     Initial Creation
# ```

import os
import time

def mkdir_p(vDir):
    try:
        os.makedirs(vDir)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(vDir):
            pass
        else:
            raise



#!/usr/bin/python3.9

import shutil
import os
shutil.rmtree(os.path.join("static", "videos"))
os.mkdir(os.path.join("static", "videos"))
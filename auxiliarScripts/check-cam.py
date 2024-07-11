import json
import sys
import numpy as np
import matplotlib.pyplot as plt

from plot import plot_cams_3D

cam_file = sys.argv[1]

sys.path.append('src')
from vican.geometry import SE3
from vican.cam import Camera

cameras = []
with open(cam_file) as f:
    data = json.load(f)

    for i in data:
        if '_' not in i:
            s = SE3(R=np.array(data[i]['R']), t=np.array(data[i]['t']))
            c = Camera(i, np.eye(3), np.zeros(8), s, 1024, 1024)
            cameras.append(c)

plot_cams_3D(cameras)

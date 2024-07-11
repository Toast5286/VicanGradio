import os
import torch
import numpy as np
from shapely.geometry import Polygon
import scipy.io as sio
import json
import matplotlib.pyplot as plt

import sys
sys.path.append('src')

from vican.cam import estimate_pose_mp
from vican.bipgo import bipartite_se3sync, object_bipartite_se3sync
from vican.dataset import Dataset
from vican.parse_config import parse_config

DATASET_PATH = sys.argv[1]

aux = torch.load(DATASET_PATH)

obj_pose_est = object_bipartite_se3sync(aux,
                                        noise_model_r=lambda edge : 0.01 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1,
                                        noise_model_t=lambda edge : 0.01 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1,
                                        edge_filter=lambda edge : edge['reprojected_err'] < 0.5,
                                        maxiter=4,
                                        lsqr_solver="conjugate_gradient",
                                        dtype=np.float64)

print(obj_pose_est.keys())

xyz = np.stack([pose.inv().t() for pose in obj_pose_est.values()], axis=0)
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot(xyz[:,0], xyz[:,1], xyz[:,2], 'o')
plt.show()

import os
import torch
import numpy as np
from shapely.geometry import Polygon
import scipy.io as sio
import json

from vican.cam import estimate_pose_mp
from vican.bipgo import bipartite_se3sync, object_bipartite_se3sync
from vican.dataset import Dataset
from vican.parse_config import parse_config

def pose_est(DATASET_PATH='/dataset'):
    must_have_keys = ['object_calib', 'cameras_path', 'aruco', 'marker_size', 'marker_ids', 'brightness', 'contrast']
    config = parse_config(DATASET_PATH, must_have_keys)

    dataset = Dataset(root=os.path.join(DATASET_PATH, config['cameras_path']))

    aux = torch.load(os.path.join(DATASET_PATH, config['object_calib']))

    obj_pose_est = object_bipartite_se3sync(aux,
                                            noise_model_r=lambda edge : 0.01 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1,
                                            noise_model_t=lambda edge : 0.001 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1,
                                            edge_filter=lambda edge : edge['reprojected_err'] < 0.5,
                                            maxiter=4,
                                            lsqr_solver="conjugate_gradient",
                                            dtype=np.float64)
    
    cam_marker_edges = estimate_pose_mp(cams=dataset.im_data['cam'],
                                        im_filenames=dataset.im_data['filename'],
                                        aruco=config['aruco'],
                                        marker_size=config['marker_size'],
                                        corner_refine='CORNER_REFINE_SUBPIX',
                                        marker_ids=config['marker_ids'],
                                        flags='SOLVEPNP_IPPE_SQUARE',
                                        brightness=config['brightness'],
                                        contrast=config['contrast'])
    
    # torch.save(cam_marker_edges, os.path.join(DATASET_PATH, 'room_pose.pt'))

    # tmax = 2000
    # edges = {k : v for k, v in cam_marker_edges.items() if int(k[1].split('_')[0]) < tmax}

    pose_est = bipartite_se3sync(cam_marker_edges,
                                constraints=obj_pose_est,
                                noise_model_r=lambda edge : 0.001 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1.0,
                                noise_model_t=lambda edge : 0.001 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1.0,
                                edge_filter=lambda edge : edge['reprojected_err'] < 0.5,
                                maxiter=4,
                                lsqr_solver="conjugate_gradient",
                                dtype=np.float32)
    
    json_data = {}
    for i in pose_est:
        json_data[i] = {'R': pose_est[i].R().tolist(), 't': pose_est[i].t().tolist()}
    
    with open(os.path.join(DATASET_PATH, config['cameras_pose_est']), 'w') as f:
        json.dump(json_data, f)

if __name__ == "__main__":
    pose_est()
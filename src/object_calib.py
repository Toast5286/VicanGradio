import os
import json
from shapely.geometry import Polygon
import numpy as np

from vican.cam import estimate_pose_mp
from vican.dataset import Dataset
from vican.parse_config import parse_config
from vican.bipgo import object_bipartite_se3sync

def object_calib(DATASET_PATH='/dataset'):
    must_have_keys = ['object_path', 'object_calib', 'aruco', 'marker_size', 'marker_ids', 'brightness', 'contrast']
    config = parse_config(DATASET_PATH, must_have_keys)

    obj_dataset = Dataset(root=os.path.join(DATASET_PATH, config['object_path']))

    aux = estimate_pose_mp(cams=obj_dataset.im_data['cam'],
                        im_filenames=obj_dataset.im_data['filename'],
                        aruco=config['aruco'],
                        marker_size=config['marker_size'],
                        corner_refine='CORNER_REFINE_SUBPIX',
                        marker_ids=config['marker_ids'],
                        flags='SOLVEPNP_IPPE_SQUARE',
                        brightness=config['brightness'],
                        contrast=config['contrast'])
    
    obj_pose_est = object_bipartite_se3sync(aux,
                                            noise_model_r=lambda edge : 0.01 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1,
                                            noise_model_t=lambda edge : 0.001 * Polygon(zip(edge['corners'][:,0], edge['corners'][:,1])).area**1,
                                            edge_filter=lambda edge : edge['reprojected_err'] < 0.5,
                                            maxiter=4,
                                            lsqr_solver="conjugate_gradient",
                                            dtype=np.float64)

    json_data = {}
    for cam_id, pose in obj_pose_est.items():    
        #check if cam_id is a valid camera index
        if "_" in cam_id:
            continue
        json_data[int(cam_id)] = {'R': obj_pose_est[cam_id].R().tolist(), 't': obj_pose_est[cam_id].t().tolist()}

    with open(os.path.join(DATASET_PATH, config['object_calib']), 'w') as f:

        json.dump(json_data,f,indent=4)

if __name__ == "__main__":
    object_calib()
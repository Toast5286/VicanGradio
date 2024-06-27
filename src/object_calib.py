import os
import torch

from src.vican.cam import estimate_pose_mp
from src.vican.dataset import Dataset
from src.vican.parse_config import parse_config


def object_calib(DATASET_PATH):
    must_have_keys = ['object_path', 'object_calib', 'aruco', 'marker_size', 'marker_ids', 'brightness', 'contrast']
    config = parse_config(DATASET_PATH, must_have_keys)

    obj_dataset = Dataset(root=os.path.join(DATASET_PATH, config['object_path']))
    print(config)

    aux = estimate_pose_mp(cams=obj_dataset.im_data['cam'],
                        im_filenames=obj_dataset.im_data['filename'],
                        aruco=config['aruco'],
                        marker_size=config['marker_size'],
                        corner_refine='CORNER_REFINE_APRILTAG',
                        marker_ids=config['marker_ids'],
                        flags='SOLVEPNP_IPPE_SQUARE',
                        brightness=config['brightness'],
                        contrast=config['contrast'])

    torch.save(aux, os.path.join(DATASET_PATH, config['object_calib']))

import os

def parse_config(DATASET_PATH, must_have_keys):
    with open(os.path.join(DATASET_PATH, 'config.txt'), 'r') as f:
        lines = f.readlines()
        config = {}
        for line in lines:
            key, value = line.split(':')
            if key == 'marker_size':
                config[key] = float(value)
            elif key == 'marker_ids':
                config[key] = list(map(str, value.rstrip('\n').split(',')))
            elif key == 'brightness':
                config[key] = int(value)
            elif key == 'contrast':
                config[key] = int(value)
            else:
                config[key] = value.rstrip('\n')
        
        if 'cameras_pose_est' not in config:
            config['cameras_pose_est'] = 'pose_est.mat'
        
        for key in must_have_keys:
            if key not in config:
                raise ValueError(f"Key {key} not found in config file")

        return config
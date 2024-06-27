import gradio as gr
import os
import shutil
import zipfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat
import tempfile

import sys
sys.path.append('src')

from object_calib import object_calib
from pose_est import pose_est

# Example intrinsic and extrinsic matrices
K = np.array([
    [1000, 0, 320],
    [0, 1000, 240],
    [0, 0, 1]
])

R = np.array([
    [0, 0, 1],
    [0, 1, 0],
    [-1, 0, 0]
])

t = np.array([0, 0, -5])

M = [np.array([
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [-1, 0, 0, 5]
])]

#Aux. Functions-------------------------------------------------------------

def validate_zip_file(zip_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        # Check if directories "object-images" and "cameras-images" exist
        dir_obj = os.path.join(tmpdir, 'object-images')
        dir_cam = os.path.join(tmpdir, 'cameras-images')
        if not os.path.isdir(dir_obj) or not os.path.isdir(dir_cam):
            return "The uploaded file does not contain directories named 'object-images' or 'cameras-images'."

         # Iterate over all subdirectories in "object-images"
        for subdir in os.listdir(dir_obj):
            subdir_path = os.path.join(dir_obj, subdir)
            if os.path.isdir(subdir_path):
                # Check if the subdirectory contains .jpg files
                if not any(fname.endswith(('.jpg','.png')) for fname in os.listdir(subdir_path)):
                    return f"The subdirectory '{subdir}' in directory 'object-images' does not contain any .jpg files."

        if not os.path.isfile(os.path.join(dir_obj, 'cameras.json')):
            return "Directory 'cameras-images' does not contain the file 'cameras.json'."        
        
        
        # Iterate over all subdirectories in "cameras-images"
        for subdir in os.listdir(dir_cam):
            subdir_path = os.path.join(dir_cam, subdir)
            if os.path.isdir(subdir_path):
                # Check if the subdirectory contains .jpg files
                if not any(fname.endswith(('.jpg','.png')) for fname in os.listdir(subdir_path)):
                    return f"The subdirectory '{subdir}' in directory 'cameras-images' does not contain any .jpg files."
                
        if not os.path.isfile(os.path.join(dir_cam, 'cameras.json')):
            return "Directory 'cameras-images' does not contain the file 'cameras.json'."
                
        

        return "The uploaded file is valid."


# Function to create the text file with user inputs
def create_config_file(marker_size, marker_ids, brightness, contrast):
    config_content = f"""object_path:object-images
object_calib:cube-calib.pt
cameras_path:cameras-images
cameras_pose_est:pose_est.json
aruco:DICT_ARUCO_ORIGINAL
marker_size:{marker_size}
marker_ids:{marker_ids}
brightness:{brightness}
contrast:{contrast}
"""
    # Write to a text file
    with open("/CalibrationData/config.txt", "w") as file:
        file.write(config_content)

def camera_to_world(extrinsics):
    """
    Convert multiple camera coordinate systems to world coordinate systems.
    
    Parameters:
    extrinsics (list): List of extrinsic matrices, where each extrinsic matrix is [R|t] (3x4).
    
    Returns:
    list: List of tuples containing (R_world, t_world) for each camera.
    """
    camera_world_coords = []
    
    for extrinsic in extrinsics:
        R = extrinsic[:, :3]
        t = extrinsic[:, 3]
        
        R_inv = np.linalg.inv(R)
        t_inv = -R_inv @ t
        
        camera_world_coords.append((R_inv, t_inv))
    
    return camera_world_coords

def create_3d_plot(camera_world_coords):
    """
    Write camera positions and orientations to a plot.
    
    Parameters:
    camera_world_coords (list): List of tuples containing (R_world, t_world) for each camera.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for R_world, t_world in camera_world_coords:
        # Plot camera position
        ax.scatter(t_world[0], t_world[1], t_world[2], color='red', s=50)
        
        # Plot orientation line
        point_in_front = t_world + R_world[:, 2] * 0.1
        ax.plot([t_world[0], point_in_front[0]], 
                [t_world[1], point_in_front[1]], 
                [t_world[2], point_in_front[2]], color='blue')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Camera Visualization')
    
    return fig
 
 #Gradio's Function------------------------------------------------------

def process_file(fileobj,marker_size, marker_ids, brightness, contrast):

    validation_error = validate_zip_file(fileobj)

    if validation_error == "The uploaded file is valid.":

        #Create CalibrationData directory
        UploadDir = '/CalibrationData'
        path = UploadDir
        if not os.path.exists(UploadDir):
            os.mkdir(UploadDir)

        #copy and change directory
        shutil.copy(fileobj,UploadDir)
        path = os.path.join(UploadDir, os.path.basename(fileobj))
        print(path)
        #Unzips file
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(UploadDir)
            
        #creates config
        create_config_file(marker_size, marker_ids, brightness, contrast)

        #Correct the object-images/cameras.json file to have the correct structure
        #JSONCam("./CalibrationData/object-images/cameras.json")

        #TODO:Run Vican here
        object_calib(UploadDir)

        pose_est(UploadDir)
        
        '''
        #generates 3D visualization and outputs file
        camera_world_coords  = camera_to_world(M)
        matrices_dict = {f'matrix_{i+1}': M[i] for i in range(len(M))}
        savemat("pose_est.mat", matrices_dict)
        return "No Errors","pose_est.mat",create_3d_plot(camera_world_coords)
        '''
        return validation_error, savemat("pose_est.mat", {}), plt.figure()
    else:
        return validation_error, savemat("pose_est.mat", {}), plt.figure()

#Main---------------------------------------------------------------------

with open('src/description.html', 'r') as file:
    description_html = file.read()

appTab = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload Folder"),
        gr.Number(label="Marker Size", value=0.088),
        gr.Textbox(label="Marker IDs (comma-separated)", value="2,3,4,5,6,7,8,9,10,11,12,13"),
        gr.Number(label="Brightness", value=-50),
        gr.Number(label="Contrast", value=100)
    ],
    outputs=[gr.Text(label="Errors:"),
             gr.File(label="Camera calibration matrices File (.mat)"),
             gr.Plot(label="Camera calibration Visualization"),
             ]
)
def helpfunction():
    return "online"

helpTab = gr.Interface(
    fn=helpfunction,
    inputs=None,
    outputs=gr.Text(label="Status:"),
    description=description_html
)




if __name__ == "__main__":
    demo = gr.TabbedInterface([appTab, helpTab], ["VICAN interface", "How to use"])
    demo.launch()
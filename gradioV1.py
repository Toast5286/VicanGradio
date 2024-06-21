import gradio as gr
import cv2
import os
import shutil
import zipfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat

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


# Function to create the text file with user inputs
def create_config_file(marker_size, marker_ids, brightness, contrast):
    config_content = f"""object_path:./CalibrationData/object_path
                    object_calib:./CalibrationData/cube-calib.pt
                    cameras_path:./CalibrationData/cameras-images
                    cameras_pose_est:pose_est.mat
                    aruco:DICT_4X4_1000
                    marker_size:{marker_size}
                    marker_ids:{','.join(map(str, marker_ids))}
                    brightness:{brightness}
                    contrast:{contrast}
                    """
    # Write to a text file
    with open("./CalibrationData/config.txt", "w") as file:
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

    UploadDir = "./CalibrationData/"
    path = UploadDir
    if not os.path.exists(UploadDir):
        os.mkdir(UploadDir)

    #copy and change directory
    shutil.copy(fileobj,UploadDir)
    path += os.path.basename(fileobj)

    #Unzips file and creates config
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(UploadDir)
    create_config_file(marker_size, marker_ids, brightness, contrast)

    #TODO:Run Vican here
    #M = Vican(UploadDir)
    
    #generates 3D visualization and outputs file
    camera_world_coords  = camera_to_world(M)
    matrices_dict = {f'matrix_{i+1}': M[i] for i in range(len(M))}
    savemat("pose_est.mat", matrices_dict)
    return create_3d_plot(camera_world_coords),"pose_est.mat"

#Main---------------------------------------------------------------------


description_html = """
<div style="background-color: #d9d9d9; color: #000000; padding: 20px; border-radius: 10px; font-family: Arial, sans-serif;">
    <h2>Project Description</h2>
    <p>
    <p>1) Create a zip with the following structure:
    <pre style="background-color: #ffffff; padding: 10px; border-radius: 5px; overflow-x: auto;">
    &lt;uploaded-folder&gt.zip;
    │
    ├── &lt;object-images&gt;
    │   ├── 0
    │   │   └── 0.jpg
    │   ├── 1
    │   │   └── 1.jpg
    │   └── ...
    │
    └── &lt;cameras-images&gt;
        ├── 0
        │   └── 1.jpg
        │   └── 10.jpg
        │   └── 11.jpg
        │   └── 12.jpg
        ├── 1
        │   └── 1.jpg
        │   └── 10.jpg
        │   └── 11.jpg
        │   └── 15.jpg
        └── ...
    </pre>
    <p>Note: The &lt;object-images&gt; and &lt;cameras-images&gt; folders structure's is &lt;object-images or cameras-images&gt;/&lt;timestep&gt;/&lt;camera_id&gt;.jpg</p>
    <p>2) Fill the desired configurations </p>
    <p>3) Press Submit to start</p>
</div>
"""

demo = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload Folder"),
        gr.Number(label="Marker Size", value=0.276),
        gr.Textbox(label="Marker IDs (comma-separated)", value="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"),
        gr.Number(label="Brightness", value=-150),
        gr.Number(label="Contrast", value=120)
    ],
    outputs=[gr.Plot(label="Camera calibration Visualization"),gr.File(label="Camera calibration matrices File (.mat)"),],
    description=description_html
)


if __name__ == "__main__":
    
    demo.launch()
import os
import shutil
import zipfile
import numpy as np
import tempfile
import json

from object_calib import object_calib
from pose_est import pose_est

from vican.geometry import SE3
from vican.cam import Camera

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auxiliarScripts.plot import plot_cams_3D



def process_file(fileobj, arucos, marker_size, marker_ids, brightness, contrast):

    validation_error,NObjFrames = validate_zip_file(fileobj)

    if validation_error == "The uploaded file is valid.":

        #Unzips file and creates the config file
        UploadDir = '/CalibrationData'
        Unzip(UploadDir, fileobj, arucos, marker_size, marker_ids, brightness, contrast)

        #Correct the object-images/cameras.json file to have the correct structure
        objCalCameraJSON(NObjFrames,(UploadDir+"/object-images/cameras.json"))

        #Run Vican
        object_calib(UploadDir)
        pose_est(UploadDir)

        # Convert pose_est.json to string and displays the camera calibration in HTML
        Plot, pose_estData = PlotCamCalib((UploadDir+"/pose_est.json"))
        
        
        return "No Errors", UploadDir + '/pose_est.json',json.dumps(pose_estData,indent=4), Plot
    else:

        return validation_error, json.dumps({}),"", None
    

#Plots the camera calibration from a JSON file in to a HTML file and returns the JSON file's contents
def PlotCamCalib(JSONPath):
    cameras = []
    with open(JSONPath, 'r') as f:
        pose_estData = json.load(f)

        for i in pose_estData:
            if '_' not in i:
                s = SE3(R=np.array(pose_estData[i]['R']), t=np.array(pose_estData[i]['t']))
                c = Camera(i, np.eye(3), np.zeros(8), s, 1024, 1024)
                cameras.append(c)

    Plot = plot_cams_3D(cameras,renderer="png")

    return Plot, pose_estData


#Unzips file and creates the config file
def Unzip(outputDir, fileobj, arucos, marker_size, marker_ids, brightness, contrast):
        
    #Create CalibrationData directory
    UploadDir = outputDir
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
    create_config_file(arucos, marker_size, marker_ids, brightness, contrast)



# Function to create the text file with user inputs
def create_config_file(arucos, marker_size, marker_ids, brightness, contrast):
    config_content = f"""object_path:object-images
object_calib:cube-calib.pt
cameras_path:cameras-images
cameras_pose_est:pose_est.json
aruco:{arucos}
marker_size:{marker_size}
marker_ids:{marker_ids}
brightness:{brightness}
contrast:{contrast}
"""
    # Write to a text file
    with open("/CalibrationData/config.txt", "w") as file:
        file.write(config_content)




def objCalCameraJSON(NofFrames,JSONPath):

    with open(JSONPath, 'r') as f:
        data = json.load(f)
    cam0 = data['0']
    
    # Replicate the intrinsic parameters for the number of cams
    for i in range(1, NofFrames-1):
        data[str(i)] = cam0

    # Write the updated data back to the JSON file
    with open(JSONPath, 'w') as f:
        json.dump(data, f, indent=4)




def validate_zip_file(zip_file):

    NObjFrames = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        dir_obj = os.path.join(tmpdir, 'object-images')
        dir_cam = os.path.join(tmpdir, 'cameras-images')
        
        # Check if directories "object-images" and "cameras-images" exist
        if not os.path.isdir(dir_obj) or not os.path.isdir(dir_cam):
            return "The uploaded file does not contain directories named 'object-images' or 'cameras-images'.", NObjFrames


        #CHECK FOR PNG OR JPG
        # Iterate over all subdirectories in "object-images"
        for subdir in os.listdir(dir_obj):

            NObjFrames+=1
            subdir_path = os.path.join(dir_obj, subdir)

            # Check if the subdirectory contains .jpg files
            if os.path.isdir(subdir_path):
                if not any(fname.endswith(('.jpg','.png')) for fname in os.listdir(subdir_path)):
                    return f"The subdirectory '{subdir}' in directory 'object-images' does not contain any .jpg files.", NObjFrames
      
        # Iterate over all subdirectories in "cameras-images"
        for subdir in os.listdir(dir_cam):

            subdir_path = os.path.join(dir_cam, subdir)

            # Check if the subdirectory contains .jpg files
            if os.path.isdir(subdir_path):
                if not any(fname.endswith(('.jpg','.png')) for fname in os.listdir(subdir_path)):
                    return f"The subdirectory '{subdir}' in directory 'cameras-images' does not contain any .jpg files.", NObjFrames
                
        
        #CAMERA.JSON CHECK
        #Check if both "object-images" and "cameras-images" contain a "cameras.json"
        if not os.path.isfile(os.path.join(dir_obj, 'cameras.json')):
            return "Directory 'cameras-images' does not contain the file 'cameras.json'." , NObjFrames
                
        if not os.path.isfile(os.path.join(dir_cam, 'cameras.json')):
            return "Directory 'cameras-images' does not contain the file 'cameras.json'.", NObjFrames
                

        return "The uploaded file is valid.", NObjFrames
 
import os
import shutil
import zipfile
import numpy as np
import json
import gradio as gr
import time
import re

from vican.geometry import SE3
from vican.cam import Camera

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auxiliarScripts.plot import plot_cams_3D

#This function will check <NChecks> times if a directory has been deleted with a frequency of <checkFreq> in seconds
#if it hasnt been deleted at the end of <NChecks>, it will delete it
def cleanup(NChecks, checkFreq, req: gr.Request):

    dir = '/CalibrationData_' + req.session_hash

    #Check if the directory hasnt been deleted yet and if it has, kill this thread
    for i in range(NChecks):
        time.sleep(checkFreq)
        if not os.path.isdir(dir):
            return "All Cleared"
        
    # Delete the directory
    if os.path.isdir(dir):
        shutil.rmtree(dir)

    return "All Cleared"
    


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
def Unzip(outputDir, fileobj):
        
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
        



# Function to create the text file with user inputs
def create_config_file(UploadDir, arucos, marker_size, marker_ids, brightness, contrast):
    config_content = f"""object_path:object-images
object_calib:cube-calib.pkl
cameras_path:cameras-images
cameras_pose_est:pose_est.json
aruco:{arucos}
marker_size:{marker_size}
marker_ids:{marker_ids}
brightness:{brightness}
contrast:{contrast}
"""
    # Write to a text file
    with open(UploadDir + "/config.txt", "w") as file:
        file.write(config_content)


def ConfigValid(arucos, marker_size, marker_ids, brightness, contrast):
    if marker_size == None:
        return "Marker size can not be None."
    if brightness == None:
        return "Brightness can not be None."
    if contrast == None:
        return "Contrast can not be None."
    
    ValidArucoDic = ["DICT_4X4_50", "DICT_4X4_100", "DICT_4X4_250", "DICT_4X4_1000", "DICT_5X5_50", "DICT_5X5_100", "DICT_5X5_250", "DICT_5X5_1000", "DICT_6X6_50", "DICT_6X6_100", "DICT_6X6_250", "DICT_6X6_1000", "DICT_7X7_50", "DICT_7X7_100", "DICT_7X7_250", "DICT_7X7_1000", "DICT_ARUCO_ORIGINAL", "DICT_APRILTAG_16h5", "DICT_APRILTAG_25h9", "DICT_APRILTAG_36h10", "DICT_APRILTAG_36h11"]
    if (arucos==None) or (not any(arucos in x for x in ValidArucoDic)):
        return "The Aruco Dictionary was not found."
    
    if marker_ids == None:
        return "Marker_ids can not be None."
    
    pattern = r'^(\d+,)+'
    if not re.match(pattern, marker_ids):
        return "Marker_ids needs to folow a pattern\n Ex.:\"2,3,7,15,23,\n"
    
    return "The uploaded configs are valid."
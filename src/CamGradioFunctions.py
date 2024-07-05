import os
import zipfile
import tempfile
import json
import gradio as gr

from pose_est import pose_est
from pose_est import pose_est
from gradioFunctions import Unzip, create_config_file, PlotCamCalib,ConfigValid

def CamProcess_file(fileobj, arucos, marker_size, marker_ids, brightness, contrast, req: gr.Request):
    UploadDir = '/CalibrationData_' + req.session_hash

    if fileobj == None and os.path.exists(UploadDir):
        validation_error = "The uploaded file is valid."
    else:
        validation_error = CamValidate_zip_file(fileobj)
        config_error = ConfigValid(arucos, marker_size, marker_ids, brightness, contrast)

    if (validation_error == "The uploaded file is valid.") and (config_error == "The uploaded configs are valid."):

        if not os.path.exists(UploadDir+'/cameras-images'):
            #Unzips file and creates the config file
            Unzip(UploadDir, fileobj)

        #creates config
        create_config_file(UploadDir, arucos, marker_size, marker_ids, brightness, contrast)

        #Run Vican
        pose_est(UploadDir)

        # Convert pose_est.json to string and displays the camera calibration
        Plot, pose_estData = PlotCamCalib((UploadDir+"/pose_est.json"))
        
        return "No Errors", UploadDir + '/pose_est.json',json.dumps(pose_estData,indent=4), Plot
    
    elif validation_error != "The uploaded file is valid.":
        return validation_error, None,"", None
    else:
        return config_error, None,"", None



def CamValidate_zip_file(zip_file):

    if zip_file==None:
        return "No file was found in memory. Make sure your last upload was in the past 2h."

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        dir_cam = os.path.join(tmpdir, 'cameras-images')
        
        # Check if directories "object-images" and "cameras-images" exist
        if not os.path.isdir(dir_cam):
            return "The uploaded file does not contain directories named 'object-images' or 'cameras-images'."

        # Iterate over all subdirectories in "cameras-images"
        for subdir in os.listdir(dir_cam):

            subdir_path = os.path.join(dir_cam, subdir)

            # Check if the subdirectory contains .jpg files
            if os.path.isdir(subdir_path):
                if not any(fname.endswith(('.jpg','.png')) for fname in os.listdir(subdir_path)):
                    return f"The subdirectory '{subdir}' in directory 'cameras-images' does not contain any .jpg files."
                
        
        #CAMERA.JSON CHECK
        #Check if "cameras-images" contains a "cameras.json" and a "cube-calib.pkl"
        if not os.path.isfile(os.path.join(tmpdir,'cube-calib.pkl')):
            return "Zip file does not contain the file 'cube-calib.pkl' (the onject calibration file)." 
                
        if not os.path.isfile(os.path.join(dir_cam, 'cameras.json')):
            return "Directory 'cameras-images' does not contain the file 'cameras.json'."
                

        return "The uploaded file is valid."
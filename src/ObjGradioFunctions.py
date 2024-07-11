import os
import zipfile
import tempfile
import json
import gradio as gr

from object_calib import object_calib
from object_calib import object_calib
from gradioFunctions import Unzip, create_config_file,ConfigValid



def ObjProcess_file(fileobj, arucos, marker_size, marker_ids, brightness, contrast, req: gr.Request):
    UploadDir = '/CalibrationData_' + req.session_hash

    if fileobj == None and os.path.exists(UploadDir+'/object-images'):
        validation_error = "The uploaded file is valid."
    else:
        validation_error, NObjFrames = ObjValidate_zip_file(fileobj)
        config_error = ConfigValid(arucos, marker_size, marker_ids, brightness, contrast)

    if (validation_error == "The uploaded file is valid.") and (config_error == "The uploaded configs are valid."):

        if not os.path.exists(UploadDir+'/object-images'):
            #Unzips file and creates the config file
            Unzip(UploadDir, fileobj)
            #Correct the object-images/cameras.json file to have the correct structure
            objCalCameraJSON(NObjFrames,(UploadDir+"/object-images/cameras.json"))

        #creates config
        create_config_file(UploadDir, arucos, marker_size, marker_ids, brightness, contrast)

        #Run Vican
        object_calib(UploadDir)
        
        return "No Errors", UploadDir + '/cube-calib.pkl'
    elif validation_error != "The uploaded file is valid.":
        return validation_error, None
    else:
        return config_error, None
    



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




def ObjValidate_zip_file(zip_file):

    NObjFrames = 0

    if zip_file==None:
        return "No file was found in memory. Make sure your last upload was in the past 2h.", NObjFrames

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        dir_obj = os.path.join(tmpdir, 'object-images')
        
        # Check if directories "object-images" and "cameras-images" exist
        if not os.path.isdir(dir_obj):
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
                
        
        #CAMERA.JSON CHECK
        #Check if "object-images" contains a "cameras.json"
        if not os.path.isfile(os.path.join(dir_obj, 'cameras.json')):
            return "Directory 'cameras-images' does not contain the file 'cameras.json'." , NObjFrames
                

        return "The uploaded file is valid.", NObjFrames
import gradio as gr
import sys
sys.path.append('src')

from gradioFunctions import cleanup
from CamGradioFunctions import CamProcess_file
from ObjGradioFunctions import ObjProcess_file

#Define the "How to use" HTML description
with open('src/description.html', 'r') as file:
    description_html = file.read()

def CleanUpHelpfunction(req: gr.Request):
    return cleanup(0,0,req),None, "All Cleared", None,"",None


with gr.Blocks() as demo:

    #Define the "How to use" tab
    with gr.Tab("How to use"):
        gr.HTML(description_html)


    #Define the "Object Calibration interface" tab
    with gr.Tab("Object Calibration interface"):
        with gr.Row():
            #INPUTS
            with gr.Column(scale=1):
                ObjInputFile = gr.File(label="Upload Folder for Object Calibration")

                ObjArucoType = gr.Textbox(label="aruco", value="DICT_ARUCO_ORIGINAL")
                ObjMarkerSize = gr.Number(label="Marker Size", value=0.088)
                ObjMarkerID = gr.Textbox(label="Marker IDs (comma-separated)", value="2,3,4,5,6,7,8,9,10,11,12,13")
                ObjBrightness = gr.Number(label="Brightness", value=-50)
                ObjContrast = gr.Number(label="Contrast", value=100)

                ObjSubmitBtn = gr.Button("Submit File for Object Calibration")

            #OUTPUTS
            with gr.Column(scale=1):
                ObjErrors = gr.Text(label="Errors:")
                ObjOutputFile = gr.File(label="Download calibration matrices File (.JSON)")

                #BUTTON
                ClearBtn = gr.Button("Clear Memory")


    #Define the "Camera Pose Estimation interface" tab
    with gr.Tab("Camera Pose Estimation interface"):
        with gr.Row():
            #INPUTS
            with gr.Column(scale=1):
                CamInputFile = gr.File(label="Upload Folder for Camera Calibration")

                CamArucoType = gr.Textbox(label="aruco", value="DICT_ARUCO_ORIGINAL")
                CamMarkerSize = gr.Number(label="Marker Size", value=0.088)
                CamMarkerID = gr.Textbox(label="Marker IDs (comma-separated)", value="2,3,4,5,6,7,8,9,10,11,12,13")
                CamBrightness = gr.Number(label="Brightness", value=-50)
                CamContrast = gr.Number(label="Contrast", value=100)

                #BUTTON
                CamSubmitBtn = gr.Button("Submit File for Camera Calibration")

            with gr.Column(scale=1):
                CamErrors = gr.Text(label="Errors:")
                CamOutputFile = gr.File(label="Download calibration matrices File (.JSON)")
                CamOutputFileText = gr.Text(label="Calibration matrices File content")
                CamCameraPlot = gr.Plot(label="Camera calibration Visualization")

                #BUTTON
                ClearBtn = gr.Button("Clear Memory")

                
    #Action when ObjSubmit button is pressed
    ObjSubmitBtn.click(fn=ObjProcess_file,inputs=[ObjInputFile,ObjArucoType,ObjMarkerSize,ObjMarkerID,ObjBrightness,ObjContrast],outputs=[ObjErrors,ObjOutputFile])
    
    #Action when ObjSubmit button is pressed
    CamSubmitBtn.click(fn=CamProcess_file,inputs=[CamInputFile,CamArucoType,CamMarkerSize,CamMarkerID,CamBrightness,CamContrast],outputs=[CamErrors,CamOutputFile,CamOutputFileText,CamCameraPlot])
    
    #Action when ClearBtn button is pressed
    ClearBtn.click(fn=CleanUpHelpfunction,inputs=[],outputs=[ObjErrors,ObjOutputFile,CamErrors,CamOutputFile,CamOutputFileText,CamCameraPlot])

    #Clean Up when the user closes the tab
    demo.unload(CleanUpHelpfunction)


if __name__ == "__main__":
    demo.launch(share=True)
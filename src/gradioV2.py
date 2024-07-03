import gradio as gr
import sys
sys.path.append('src')

from gradioFunctions import process_file,cleanup

#Define the "How to use" HTML description
with open('src/description.html', 'r') as file:
    description_html = file.read()

def CleanUpHelpfunction(req: gr.Request):
    return cleanup(0,0,req)



with gr.Blocks() as demo:

    #Define the "How to use" tab
    with gr.Tab("How to use"):
        gr.HTML(description_html)


    #Define the "VICAN interface" tab
    with gr.Tab("VICAN interface"):
        with gr.Row():
            #INPUTS
            with gr.Column(scale=1):
                File = gr.File(label="Upload Folder")
                ArucoType = gr.Textbox(label="aruco", value="DICT_ARUCO_ORIGINAL")
                MarkerSize = gr.Number(label="Marker Size", value=0.088)
                MarkerID = gr.Textbox(label="Marker IDs (comma-separated)", value="2,3,4,5,6,7,8,9,10,11,12,13")
                Brightness = gr.Number(label="Brightness", value=-50)
                Contrast = gr.Number(label="Contrast", value=100)
                #BUTTON
                SubmitBtn = gr.Button("Submit")

            #OUTPUTS
            with gr.Column(scale=1):
                Errors = gr.Text(label="Errors:")
                OutputFile = gr.File(label="Download camera calibration matrices File (.JSON)")
                OutputFileText = gr.Text(label="Camera calibration matrices File content")
                CameraPlot = gr.Plot(label="Camera calibration Visualization")

                #BUTTONS
                ClearBtn = gr.Button("Clear Memory")

    SubmitBtn.click(fn=process_file,inputs=[File,ArucoType,MarkerSize,MarkerID,Brightness,Contrast],outputs=[Errors,OutputFile,OutputFileText,CameraPlot])
    ClearBtn.click(fn=CleanUpHelpfunction,inputs=[],outputs=Errors)
    demo.unload(CleanUpHelpfunction)


if __name__ == "__main__":
    demo.launch(share=True)
import gradio as gr
import sys
sys.path.append('src')

from gradioFunctions import process_file


#Define the "VICAN interface" tab
appTab = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload Folder"),
        gr.Textbox(label="aruco", value="DICT_ARUCO_ORIGINAL"),
        gr.Number(label="Marker Size", value=0.088),
        gr.Textbox(label="Marker IDs (comma-separated)", value="2,3,4,5,6,7,8,9,10,11,12,13"),
        gr.Number(label="Brightness", value=-50),
        gr.Number(label="Contrast", value=100)
    ],
    outputs=[gr.Text(label="Errors:"),
             gr.File(label="Download camera calibration matrices File (.JSON)"),
             gr.Text(label="Camera calibration matrices File content"),
             gr.HTML(label="Camera calibration Visualization"),
             ]
)


#Define the "How to use" tab
with open('src/description.html', 'r') as file:
    description_html = file.read()

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
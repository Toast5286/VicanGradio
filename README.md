
# VicanGradio

A simple Gradio WebUI to upload and configure the VICAN algorithm. 


## Run

Clone the project

```bash
  git clone https://github.com/Toast5286/VicanGradio.git
```

Go to the project directory and run 

```bash
    docker build -t gradio_v3 .
```

to create a Docker image with the necessery files. Dependecies will be automatically installed on the Docker image.

Run a Docker container

```bash
  docker run -p 7860:7860 -it --rm gradio_v3
```
The server will automatically start. The webUI can be accessed in localhost:7860 or the link written in the command line.


## Usage

The WebUI has instructions on how to use.

In this version, the Camera calibration only supports using a calibration object.


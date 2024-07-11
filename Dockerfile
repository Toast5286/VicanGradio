FROM python:3.9-slim-bullseye

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0

WORKDIR /vican

ADD src /vican/src
ADD auxiliarScripts /vican/auxiliarScripts
ADD requirements.txt /vican

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

# Expose the port Gradio will run on
EXPOSE 7860

ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "src/gradioV2.py"]

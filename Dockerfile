# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port Gradio will run on
EXPOSE 7860

ENV GRADIO_SERVER_NAME="0.0.0.0"
# Command to run the application
CMD ["python", "gradioV1.py"]
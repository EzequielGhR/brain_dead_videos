# Use the official Ubuntu 20.04 image
FROM ubuntu:20.04

# Set the working directory
WORKDIR /app

# Update the package list and install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y \
    python3-pyaudio \
    espeak \
    espeak-ng \
    mbrola \
    mbrola-* \
    imagemagick \
    python3-venv \
    git \
    nano

# Clone the pyttsx3 repository and install it from source
RUN git clone https://github.com/nateshmbhat/pyttsx3.git && \
    cd pyttsx3 && \
    python setup.py install && \
    cd ..

# Create a virtual environment and activate it
RUN python3 -m venv .venv
RUN /bin/bash -c "source .venv/bin/activate"

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python requirements inside the virtual environment
RUN /bin/bash -c "source .venv/bin/activate && pip install -r requirements.txt"

# Add execution permissions to the main shell script
COPY pipeline.sh .
RUN chmod +x pipeline.sh

# Source the commands in pipeline.sh
RUN echo "source /app/pipeline.sh" >> /root/.bashrc

# Set the entry point to /bin/bash
CMD ["/bin/bash"]

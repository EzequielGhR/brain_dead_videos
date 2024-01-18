# Use the official Ubuntu 20.04 image
FROM ubuntu:20.04

# Set the working directory
WORKDIR /app

SHELL ["/bin/bash", "-c"] 

# Update the package list and install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y \
    python3-pyaudio \
    espeak \
    espeak-ng \
    ffmpeg \
    libespeak1 \
    mbrola \
    mbrola-* \
    imagemagick \
    python3-venv \
    git \
    nano

# Create a virtual environment and activate it
RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy files to the working directory
COPY requirements.txt \
    etl.py \
    multimedia.py \
    publish.py \
    source.mkv \
    pipeline.sh \
    ./
COPY db/engine.py \
    db/models.py \
    ./db/
COPY editor/aita_editor.py editor/
COPY scrapper/aita_scrapper.py \
    scrapper/helper.py \
    ./scrapper/
COPY tts/aita_tts.py tts/

# Copy ImageMagick policy allowing resources that start with @*
COPY policy.xml /etc/ImageMagick-6/

# Install Python requirements inside the virtual environment
RUN /bin/bash -c "source .venv/bin/activate && pip install -r requirements.txt"

# Clone the pyttsx3 repository and install it from source (if 2.90 not installed before fails for some reason)
RUN git clone https://github.com/nateshmbhat/pyttsx3.git && \
    cd pyttsx3 && \
    python3 setup.py install && \
    cd ..

# Add execution permissions to the main shell script
RUN chmod +x pipeline.sh
# General
Brain Dead Videos (BDV) is a projects that's motivated from the deep hate I have for those videos you see all the time on youtube shorts, instagrams reels and tiktoks.
You know, the ones that's just a random video on the back while there is text and a text to speech voice over reading this text.
The text is usually a reddit post, so these kind of videos lack total originality but most of the time are successful.
This motivates the idea of automating the creation of videos like this using code, and so here we are.

# Requirements
You're gonna need to install a few lots of things:
- Python: I'm using Python 3.10.12 already included in my ubuntu distro.
- pyaudio: Used for text to speech libraries
- espeak: Necesary for text to speech
- espeak-ng: Necesary for pitch chnage to ve available on pyttsx3
- mbrola: "more human" voices for espeak (still far from human)
- mbrola voices: Variety of voices (mbrola-*)
- Python requirements: I recomend creating a virtualenv first (In my shell pipeline.sh I'm assuming it on .venv)

# How to
- Install all requirements except maybe for the python ones:
    - `sudo apt update`
    - `sudo apt install python3-pyaudio`
    - `sudo apt install espeak`
    - `sudo apt install espeak-ng`
    - `sudo apt-get install mbrola`
    - `sudo apt install mbrola-*`
    - `sudo apt install imagemagick`
- Create a venv using python and install it's requirements there:
    - `python -m venv .venv` to create the venv.
    - `source .venv/bin/activate` to activate the venv
    - `pip install -r rquirements.txt` to install python requirements
    - If you get issues with setProperty on pyttsx3 you should install form source:
        - clone the source repo: `git clone https://github.com/nateshmbhat/pyttsx3.git`
        - Execute setup.py: `python setup.py install`
- Add execution permissions to main sheel script. `chmod +x pipeline.sh`
- Source the commands: `source pipeline.sh`
- (Optional) Add the command to load the scripts to Run Control (`.profile` or `.bashrc`):
    - Open your rc file, in my case I'll use nano: `nano ~/.bashrc`
    - Add the line at the end to load your scripts. In my case: `source ~/Documents/Repos/brain_dead_videos/pipeline.sh`
    - You should be able to run the commands (functions inside `pipeline.sh`)

# Commands
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
- ffmpeg: Necesary for video processing
- libespeak1: Necesary for espeak to work properly
- mbrola: "more human" voices for espeak (still far from human)
- mbrola voices: Variety of voices (mbrola-*)
- Python requirements: I recomend creating a virtualenv first (In my shell pipeline.sh I'm assuming it on .venv)

# How to
Add to your project folder, your source video. Preset to "source.mkv" but modifieble on `multimedia.py`
## Using Docker
- Execute `docker build -t bdv-image .` to buil
- To run and connect to the container `docker run -it bdv-image`
- Once in the container you can use the commands like `bdv-run` to get latest post.
- After executing you'll see the video saved to `editor/output/{post_id}.mp4`
- Use `Ctrl+P` followed by `Ctrl+Q` to detach from the container
- Check container id: `docker ps`
- To copy the video to local use `docker cp {CONTAINER_ID}:/app/editor/output/{post_id}.mp4 {local/path/to/store}`
- To attach again to the container `docker attach {CONTAINER_ID}` then just type `exit` to exit the container
## If you want to do it on your local machine
- Install all requirements except maybe for the python ones:
    - `sudo apt update`
    - `sudo apt install python3-pyaudio`
    - `sudo apt install espeak`
    - `sudo apt install espeak-ng`
    - `sudo apt install ffmpeg`
    - `sudo apt install libespeak1`
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
- If you run `identify -list policy` you'll see the location of your ImageMagick policy on the first line
    - In my case the policy is in `/etc/ImageMagick-6/policy.xml`. Open it.
    - There is a line that reads "<policy domain="path" rights="none" pattern="@*" />", delete it or comment it with <!-- line -->
    - (Optional) You can copy the policy provided here in the repo to said location.

# Commands
- `dbv-fetch [OPTIONS]`:
If no option is provided it will fetch latest post
    - `-h| --help`: Shows a help message
    - `-p| --post-id {post_id}`: fetches a specific post.

- `dbv-edit [OPTIONS]`:
If no option is provided it will process latest data (acording to reddit timestamp) stored on db
    - `-h| --help`: Shows a help message
    - `-p| --post-id {post_id}`: processes a specific post from the db.

- `dbv-run [OPTIONS]`:
If no option is provided it will fetch and edit latest post
    - `-h| --help`: Shows a help message
    - `-p| --post-id {post_id}`: fetches and edits a specific post.
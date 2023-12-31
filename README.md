# AudioBookSlides

![Turbo_RealitiesEdgeXLLCM_A1111-SD](https://github.com/GotAudio/AudioBookSlides/assets/13667229/4f30b0c5-9ab6-4940-89ca-e5ddb2235e0b)


Create an AI generated video slideshow from an audiobook.

[**AudioBookSlides**](https://github.com/GotAudio/AudioBookSlides/)<br/>

I created a sample book to test this installation. Public domain Librivox [Alice in Wonderland](https://www.youtube.com/watch?v=27SwZZ8jiBc). You can find more free audiobooks [here](https://librivox.org/).

[Contact Sheet from Alice In Wonderland](https://github.com/GotAudio/AudioBookSlides/assets/13667229/acf17491-81be-42ee-a2de-230a19922d57)


This is a demo contact sheet showing the images generated. (Made with [VideoCS](https://sourceforge.net/projects/videocs) not this program.)

### Installation

AudioBookSlides requires 3 external packages;
- WhisperX: Windows users can install whisperx from [here](https://github.com/Purfview/whisper-standalone-win/releases/tag/faster-whisper)
Extract and save whisper-faster.exe and add it's path to [default_config.yaml](default_config.yaml)
- Unix users can install WhisperX with 'pip install faster-whisper'
- ffmpeg: ffmpeg can be installed from [here](https://github.com/BtbN/FFmpeg-Builds/releases)
- ComfyUI: ComfyUI stand-alone portable can be downloaded from [here](https://github.com/comfyanonymous/ComfyUI/releases)
You will not need to use the CompfyUI web interface. It is enough to simply launch the server.


####
To use the GPT API you will need to sign up for an API Key. You can register and get one [here](https://platform.openai.com).
Add your API key to the default_config.yaml file.  It will cost about $2 for a 12 hour audio book.  You might still get $20 free credit when you sign up.
You can also use the free [LM-Studio Local GPT server](https://lmstudio.ai/). It is about 3 times slower (1 hour vs 20 minutes) and it is not as accurate. I recommend using [this](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) model.
I have not tweaked all of the reqeusts for LMS. Results may be poor for some requests. (I used it myself but I have not verified it works with this installation.)


### To install AudioBookSlides;

You may create a [conda](https://conda.io/) environment.  There are only a few required packages and one version requirement; openai==0.28 (because it is compatible with LM-Studio).  I have used Python 3.9 and 3.10
```
conda create -n abs python=3.10
conda activate abs

git clone https://github.com/GotAudio/AudioBookSlides.git

cd AudioBookSlides

pip install .

python abs.py BookName \path_to_audiobook\bookname.mp3
```

## Overview of processing.

- The application keeps track of it's workflow and it can be stopped or restarted at any time. 
- If it stops or you interrupt it, you can launch it again and it will begin where it left off. (You may need to remove the most recent incomplete output file)
- The app will connect to ChatGPT API to generate the image prompts needed for Stable Diffusion
- It will connect to GPT again to extract the scene/setting information for the image prompts.
- It will stop to allow you to modify, or keep the default, file used to replace characters with actors.
- I have provided default lists of actors. By default the app picks the replacement actor starting at the top of the file.
- You can create custom actor lists in the <bookname> folder by chagging the books\bookname\bookname.yaml file. 
- You can add guidence to the actor description, such as "long blond hair", "20yo", NSFW etc.
- You must save the books/bookname/bookname_ts_p_actors_EDIT.txt as books/bookname/bookname_ts_p_actors.txt, then relaunch the app and it will continue.
- It will stop once the image generation requests have been submitted. You must wait for all images are created then rename the ComfyUI "output"folder to  bookname" before continuing.

The finished files will be in a folder under the installation directory books\bookname 

```
$abs/
├── books
│   ├── BookName1
│   ├──── Bookname.avi 
│   ├── ...
├── BookName2
├── ...
```

TODO: 
1) Test wildcard input folder with multiple mp3 files.
2) Test spaces in BookName and mp3 path
3) Test WSL
4) Test A1111 (some manual steps required)
5) Test .WAV, .ACC input.

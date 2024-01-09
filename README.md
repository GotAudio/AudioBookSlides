# AudioBookSlides

![Turbo_RealitiesEdgeXLLCM_A1111-SD](https://github.com/GotAudio/AudioBookSlides/assets/13667229/4f30b0c5-9ab6-4940-89ca-e5ddb2235e0b)

# Create an AI generated video slideshow from an audiobook. 
This app was written mostly by ChatGPT. I told it the tasks I wanted and it eventually made this.

I created a sample book to test this installation. 
Public domain Librivox [Alice in Wonderland](https://www.youtube.com/watch?v=27SwZZ8jiBc). You can find more free audiobooks [here](https://librivox.org/).

[Contact Sheet from Alice In Wonderland](https://github.com/GotAudio/AudioBookSlides/assets/13667229/acf17491-81be-42ee-a2de-230a19922d57)


This is a demo contact sheet showing the images generated. (Made with [VideoCS](https://sourceforge.net/projects/videocs) not this program.)


[Reduced sample from Alice In Wonderland](https://github.com/GotAudio/AudioBookSlides/assets/13667229/d663dfda-2c0c-4ee7-aec2-6fe368c70fbc)

This is a 38 second, 320x218 sample, reduced from 768x512. Your video dimensions are limited by your GPU VRAM.

### Installation of AudioBookSlides
- __You must change the paths to your Stable Diffusion (ComfyUI or A1111) output folder path in `default_config.yaml`__
- Consider creating a [conda (or mamba)](https://conda.io/) environment for the installation.
- The requirements are minimal with one specific version requirement: `openai==0.28` (compatible with LM-Studio).
- Python versions 3.9 and 3.10 have been used successfully.

**Windows**:
<details><summary>Windows Installation Steps (click to expand)</summary>
    
- **ffmpeg**:
  - ffmpeg can be installed from [here](https://github.com/BtbN/FFmpeg-Builds/releases).

- **ComfyUI** (See default_config.yaml to use A1111 in manual mode):
  - Download ComfyUI stand-alone portable from [here](https://github.com/comfyanonymous/ComfyUI/releases).

Ensure each package is correctly installed and configured before using AudioBookSlides.    
<pre><code>
conda create -n abs python=3.10 cudnn
conda activate abs
conda install -c conda-forge zlib-wapi
pip install faster-whisper
pip install -U whisper-ctranslate2

git clone https://github.com/GotAudio/AudioBookSlides.git
cd AudioBookSlides
pip install .

# If you have just installed ComfyUI you may need to install these components.
# Copy nodes_custom_sampler.py to your ComfyUI\comfy_extras folder. 
# Change the \ComfyUI\ path below as necessary for your install directory.

Browse to https://civitai.com/models/129666/realities-edge-xl-lcmsdxlturbo and click the download button 
to download the 6GB file "RealitiesEdgeXLLCM_TURBOXL.safetensors" and save it to 
\ComfyUi\models\checkpoints\RealitiesEdgeXLLCM_TURBOXL.safetensors If you already have A1111 installed, 
you can also modify \ComfyUI\extra_model_paths.yaml and point the base path to your A1111 SD folder if 
you prefer. ( base_path: E:\SD\stable-diffusion-webui\ )
    
copy nodes_custom_sampler.py \ComfyUI\comfy_extras\nodes_custom_sampler.py
git clone https://github.com/ltdrdata/ComfyUI-Manager.git \ComfyUI\custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git \ComfyUI\custom_nodes

# Start ComfyUI. (You will also need to start it when AudioBookSlides app tells you to launch it.)
\ComfyUI\run_nvidia_gpu.bat
#Click on "Manager" in the menu, then click "Update ComfyUI". When the update finishes, press CTRL-C in the CMD window to stop the Server


#Launch AudioBookSlides application. After the .mp3 file has been created in the first step, 
#the path to the mp3 file(s) can be omitted for subsequent reruns.

python abs.py BookName \path_to_audiobook\bookname.mp3

</code></pre>
</details>

**Linux**:
<details><summary>WSL Installation Steps (click to expand)</summary>
<pre><code>
#Change to the folder where you want to install AudioBookSlides
md /mnt/e/wsl
cd /mnt/e/wsl
git clone https://github.com/GotAudio/AudioBookSlides.git
cd AudioBookSlides/

#Save your openai API Key in ABS_API_KEY.txt
echo YOUR_API_KEY> ABS_API_KEY.txt

# Install Mambaforge, a minimal Conda
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
chmod +x Mambaforge-Linux-x86_64.sh
./Mambaforge-Linux-x86_64.sh
source ~/.bashrc
mamba create -n abs python=3.10 cudnn
mamba activate abs

wget https://github.com/Purfview/whisper-standalone-win/releases/download/libs/cuBLAS.and.cuDNN_linux_v2.7z
sudo apt install p7zip-full
7z x cuBLAS.and.cuDNN_linux_v2.7z
mamba install -c conda-forge zlib
pip install faster-whisper
pip install -U whisper-ctranslate2

# 2GB+ downoad. Tab to OK and press enter when asked. 
sudo apt install nvidia-cudnn

pip install .	
	
#Install ffmpeg
sudo apt install ffmpeg

#Clone and set up ComfyUI
cd ..
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI/
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

__2021-1-1: The Turbo API did not work because it was missing the latest version of SDTurboScheduler node.__ 
cp ../AudioBookSlides/nodes_custom_sampler.py ./comfy_extras/nodes_custom_sampler.py

#Install helper nodes
cd custom_nodes/
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ..

Browse to https://civitai.com/models/129666/realities-edge-xl-lcmsdxlturbo and click the download button 
to download the 6GB file "RealitiesEdgeXLLCM_TURBOXL.safetensors" and save it to 
ComfyUi/models/checkpoints/RealitiesEdgeXLLCM_TURBOXL.safetensors If you already have A1111 installed, 
you can also modify ComfyUI/extra_model_paths.yaml and point the base path to your A1111 SD folder if 
you prefer. ( base_path: /mnt/e/SD/stable-diffusion-webui/ )

To launch ComfyUI run this command from the ComfyUI folder in a seperate terminal when asked to start ComfyUI
python main.py 

You can also install firefox on WSL2 if you want to view the execution queue;
sudo apt install firefox
firefox
(Browse to http://127.0.0.1:8188)


#Start the application
python abs.py 06DeeplyOdd '/mnt/e/Media/Audiobooks/DNK-PLO (2013)/Dean Koontz - Deeply Odd (2013)/*.mp3'

![WSL_images](https://github.com/GotAudio/AudioBookSlides/assets/13667229/10753daa-faee-4d03-a34c-70e5f8b75c62)
Dean Koontz - Odd Thomas - Deeply Odd Book 6. Length: 9:37, 2500 images took 5.5 hours to generate. 
(Video creation only takes a few minutes)

</code></pre>
</details>


#### GPT API Setup*
- To use the GPT API, you need to sign up for an API Key. Register and get your key [here](https://platform.openai.com).
- Save your API key in a file named `ABS_API_KEY.txt` in the application folder.
- The cost is approximately $2 for a 12-hour audiobook. New sign-ups might receive $20 free credit.
- Alternatively, use the free [LM-Studio Local GPT server](https://lmstudio.ai/). It's about 3 times slower (1 hour vs 20 minutes) and less accurate. The recommended model is [here](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF).
- Note: Not all requests have been optimized for LM-Studio. Some results may be suboptimal. This feature was utilized during development but has not been fully verified with the current installation.
- *I also have a version that does not utilize GPT. In that version, image prompts are generated directly from the text, which can lead to often ridiculous or confusing scene transitions. Additionally, character names are generated programmatically, often resulting in inaccuracies. Instead of having around 50 nearly 100% accurate characters, you might encounter 200+ characters with frequent errors, necessitating increased effort in managing actor mappings. However, this might not be a concern for you. The process is significantly faster, taking only seconds versus 20 minutes, and avoids a $2 API fee. I can release this version if there is interest.
  
## Overview of Processing

- The application keeps track of its workflow and can be stopped or restarted at any time.
- If it stops or you interrupt it, you can relaunch it and it will resume from where it left off. (You may need to remove the most recent incomplete output file.)
- The app will connect to the ChatGPT API to identify characters and generate the image prompts needed for Stable Diffusion.
- It will connect to GPT again to extract the scene/setting information for the image prompts.
- The process will pause to allow you to modify, or keep the default, file used to replace characters with actors.
- Default lists of actors are provided. By default, the app picks the replacement actor starting at the top of the file.
- You can create custom actor lists in the <bookname> folder by changing the books\bookname\bookname.yaml file.
- You can add guidance to the actor description, such as "long blond hair", "20yo", NSFW, etc.
- You must save the books/bookname/bookname_ts_p_actors_EDIT.txt as books/bookname/bookname_ts_p_actors.txt, then relaunch the app and it will continue.
- The process will pause once the image generation requests have been submitted. Wait for all images to be created, then rename the ComfyUI "output" folder to "bookname" before continuing.

The finished files will be in a folder under the installation directory books\bookname:

```
$abs/
├── books
│   ├── BookName1
│   ├──── Bookname1.avi 
│   ├──── Bookname1.srt
├───├── BookName2
├── ...
```

## Tips on Managing Actors
- Replacing characters with actors is conducted to create consistent character appearances. This approach is simpler than trying to describe a particular character in detail.
- Character names will be replaced with actor names from .csv files configured in `default_config.yaml`. The file will be sorted from the highest to the lowest occurrence.
- Due to the audiobook being transcribed with speech-to-text, actor names may often be misheard or misspelled. They might also be spoken in various forms, such as "John Smith", "John", "Smith", or "Mr. Smith."
- You are responsible for identifying these cases and assigning a single actor to all variations.
- Well-known characters like "Vampire", "Santa Claus", "Peter Rabbit", or any other character the AI already knows how to render, can be omitted.
- The "depth" key in `default_config.yaml` controls the minimum number of times a name must appear to be included in the initial replacement list. The default value is 4.
- While you might not need to provide an actor name for a character mentioned only once, that single instance may actually be a misspelling of the main character. Therefore, you might prefer to set the depth to 1 and manually remove any unrecognized names.
- It is important to order the various actor names from the longest to the shortest character length. For example, if the names "John" and "John Smith" both occur, place "John Smith" before "John" to ensure "John Smith" is correctly replaced.
- Exercise caution when using actor names that are also names of characters in your book. If overlooked, you might end up replacing a part of an actor's name with a different actor.
- Actor replacements are case-sensitive because the names you see are written in the case they appear.
- Be careful when replacing very short names that may be part of other words. For instance, entering "Pat " (with a space after) will ensure that the letters in "Patterns danced..." are not replaced.
- The format of this file is: count&lt;tab&gt;character name, _solo [age] &lt;gender&gt; [actor | actress] actor name @. Do not remove or alter the "count&lt;tab&gt;character," portion of the text.
- The delimiters _...@ are included in case you want to make targeted replacements or corrections to the final prompt file, specifically for actors and not other spoken text.
- The file submitted to Stable Diffusion is named <bookname>_merged_names.txt. Before pressing return to start generating images, I often use a text editor to replace " I ", " me ", " my ", " protagonist ", " narrator " with the protagonists actor name to be sure they appear on-screen even if someone else is not saying their name.
- As a reference, I asked ChatGPT; List the character names and descriptions in the book "Lemony Snicket - Who Could That Be at This Hour"

### This is an example of a default vs. manually edited actor list. 

| [Default] books/01ThisHour/01ThisHour_ts_p_actors_EDIT.txt            | [Edited] books/01ThisHour/01ThisHour_ts_p_actors.txt
| --------------------------------------------------------------------- | ---------------------------------------------------------------------- | 
|                                                                       |                                                                        | 
|100   Theodora, _solo  female actress Anna Paquin @                    |10	**Lemony Snicket**, _solo 30yo male actor Patrick Warburton@	 |
|62    Moxie, _solo 25yo female actress Naomi Watts long blond hair @   |4	Mr. **Snicket**, _solo 30yo male actor Patrick Warburton@		 |
|50    Ellington, _solo 25yo female actress Florence Pugh @             |40	**Snicket**, _solo 30yo male actor Patrick Warburton@		 |
|40    Snicket, _solo 30yo male actor Al Pacino @                       |12	S. Theodora Markson, _solo 25yo female **Daenerys Targaryen**@	 |
|18    Ellington Faint, _solo 30yo female actress Meg Donnelly @        |100	Theodora, _solo 25yo green eyed female Daenerys Targaryen@	 |
|17    Pip, _solo 30yo male actor Matthew Lewis @                       |62	Moxie, _solo 25yo female actress Naomi Watts curly hair@	 |
|16    Hangfire, _solo  male actor George Clooney @                     |18	**Ellington Faint**, _solo 25yo sexy female actress Margot Robbie@	 |
|13    Qwerty, _solo 25yo male actor Keanu Reeves @                     |50	**Ellington**, _solo 25yo sexy female actress Margot Robbie@	 |
|12    S. Theodora Markson, _solo 40yo female actress Summer H. Howell @|7	Stu Mitchum, _solo 12yo male actor Brad Pitt@			 |
|12    Hector, _solo 12yo male actor Colin Farrell @                    |7	Stu , _solo 12yo male actor Brad Pitt@				 |
|11    Prosper Lost, _solo 12yo male actor Christopher Walken @         |7	**Harvey Mitchum**, _solo 35yo male actor Gene Hackman@		 |
|10    Lemony Snicket, _solo 45yo male actor John Barrowman @           |6	**Mitchum**, _solo 35yo male actor Gene Hackman@			 |
|7    Harvey Mitchum, _solo 40yo male actor Anthony Heald @             |6	**Harvey**, _solo 35yo male actor Gene Hackman@			 |
|7    Stu, _solo  male actor Dwayne Johnson @                           |6	Mimi Mitchum, _solo 30yo female actress Angelina Jolie@		 |
|7    Mrs. Sallis, _solo 50yo female actress Markella Kavenagh @        |13	**Qwerty**, _solo 25yo male actor Keanu Reeves@			 |
|7    Squeak, _solo 30yo male actor Michael Caine @                     |4	**Quirty**, _solo 25yo male actor Keanu Reeves@			 |
|6    Harvey, _solo 35yo male actor Cary Grant @                        |7	Murphy Sallis, _solo 55yo female actress Sharon Stone @		 |
|6    Mimi Mitchum, _solo 30yo female actress Madison Lintz @           |7	Sally Murphy, _solo 55yo female actress Sharon Stone @		 |
|6    Mitchum, _solo 40yo male actor Gene Hackman @                     |7	Mrs. Sallis, _solo 55yo female actress Sharon Stone @		 |
|5    Malahan, _solo 45yo male actor David Harbour @                    |4	Mrs. Salas, _solo 55yo female actress Sharon Stone@		 |
|5    Father, _solo 50yo male actor Henry Cavill @                      |17	**Pecuchet**, _solo 30yo male actor Jet Li@				 |
|4    Mother, _solo 30yo female actress Maia Mitchell @                 |17	**Pip** , _solo 30yo male actor Jet Li@				 |
|4    Mrs. Salas, _solo 60yo female actress Amelia Clarkson @           |7	Bouvard, _solo 30yo male actor Ken Watanabe@			 |
|4    Quirty, _solo  female actress Camila Morrone @                    |7	Squeak, _solo 30yo male actor Ken Watanabe@			 |
|4    Mr. Snicket, _solo 40yo male actor Javier Bardem @                |11	Prosper Lost, _solo 55yo male actor Christopher Walken@		 |
|                                                                       |16	Hangfire, _solo  male actor Rich Litle@                          |
|                                                                       |12	Hector, _solo 12yo male actor Colin Farrell@                     |
|                                                                       |5	Malahan, _solo 45yo male actor David Harbour@                    |
|                                                                       |5	Father, _solo 50yo male actor George Clooney@                    |
|                                                                       |4	Mother, _solo 40yo female actress Michael Pfeiffer@              |


## TODO List for AudioBookSlides

- [X] 1) Test wildcard input folder with multiple MP3 files.
   - Verified 3 files (chapters) concatenated: 
     ```
     python abs.py 01ThisHour "E:\Media\AudioBooks\Lemony Snicket\All the Wrong Questions 1 - Who Could That Be at This Hour\*.mp3"
     ```
- [X] 2) Test spaces in BookName and MP3 path.
- [X] 3) Test on Windows Subsystem for Linux (WSL).
- [ ] 4) Test on system A1111 (note: some manual steps required).
- [x] 5) Test input with different audio formats (.WAV, .AAC).



**Note: WhisperX transcription from audio to text (.srt) can be much (6X) faster.  A 13 hour book reduced from 3 hours to 30 minutes.  I may replace the current installation with it. If you want to try it;** 
<code>
conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia
git clone https://github.com/m-bain/whisperx.git
cd whisperx
#Modify the requirements.txt: Find the line in requirements.txt that specifies faster-whisper with a Git URL and comment it out or remove it. 
#Then run;
git clone https://github.com/SYSTRAN/faster-whisper.git
cd faster-whisper
git checkout 0.10.0
pip install .
cd ..
pip install .
#Then change default_config.yaml. Replace "whisper-ctranslate2..." with "whisperx --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --max_line_count 1 --verbose False --output_format srt --language en --output_dir "
#whisperX 28 minutes vs. 2:57:00 for whisper-c2translate
This new version starts the .srt timestamp where it detects audio.  The current version starts at 00:00:00,000.  It needs to be 00:00:00,000 or the images will not sync with the audio, so you will need to interrupt processing after whisperx finishes and change bookname.srt from eg.
1
**00:00:11,733** --> 00:00:17,317
to 
1
**00:00:00,000** --> 00:00:17,317

I will do that in the app when I switch to this version.

Delete any files created after creation of the .srt file and they will be rebuilt when you relaunch. (If you forget to fix it, you can simply rename the first .PNG file from 000011733.PNG to 000000000.PNG before renaming your ComfyUI "output" folder to "bookname")

</code>

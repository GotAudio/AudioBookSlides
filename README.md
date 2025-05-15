
# AudioBookSlides: Create an AI generated slide show and subtitles from an audio book.

![002333030](https://github.com/GotAudio/AudioBookSlides/assets/13667229/fce869e0-1523-4dfc-9b07-7082a1c7acdc)

This sample was created without GPT API.  You can find more free audiobooks [here](https://librivox.org/).

[Contact Sheet from Venom Lethal Protector](https://github.com/GotAudio/AudioBookSlides/assets/13667229/f3d4c70a-b4b5-414f-a140-cb08ce6e7fe9)

This is a demo contact sheet showing the images generated for "Venom Lethal Protector". (Made with [VideoCS](https://sourceforge.net/projects/videocs) not this program.)

[Sample from Venom Lethal Protector](https://github.com/GotAudio/AudioBookSlides/assets/13667229/789dfc42-fefa-402f-b838-6301dfd009cb)

Sample from "Venom Lethal Protector". Click the muted speaker icon to enable audio when playing.

### 2024-2-21 Version 1.1.0 Update
- __Removed GPT requirement. Characters and scenes can now be generated programatically.__
- Randomized default actor assignments 
- Changed default Stable Diffusion model to photon_v1.safetensors. It generates 10 images per minute on my NVIDIA 12GB 3060 GPU. [Released for $329, February 25, 2021. Amazon: $289](https://www.amazon.com/MSI-GeForce-RTX-3060-12G/dp/B08WPRMVWB) (Other sellers list for under $100. Maybe refurbished?) The 1,221 Images for the 5 hour Venom book took 2 hours to generate.
- SD LCM support requires existing installations update ComfyUI from the Manager menu
- default_config.yaml setting _"keep_actors: 1"_  allows you to set how many characters to allow in a scene
- default_config.yaml setting _"actor_priority: "creature, actress, female"_ to ensure creatures and women get priority over men
- default_config.yaml setting _"LUFS_target: -17"_ automatically increase volume of input files under -17 LUFS (Loudness Units Full Scale)


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

mamba create -n abs python=3.10 cudnn cuda-libraries cuda-runtime cuda-libraries-dev -c conda-forge -c nvidia
mamba activate abs
SET BASE=H:\win
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
mamba install zlib -c conda-forge
git clone https://github.com/GotAudio/AudioBookSlides.git "%BASE%/AudioBookSlides"
git clone https://github.com/m-bain/whisperx.git "%BASE%/AudioBookSlides/whisperx"

__Edit %BASE%\AudioBookSlides\whisperx\requirements.txt__
Comment this line (it may fail on my machine because TEMP is on another drive);
#faster-whisper @ git+https://github.com/SYSTRAN/faster-whisper.git@0.10.0

#Clone it manually;   
git clone https://github.com/SYSTRAN/faster-whisper.git --branch 0.10.0 "%BASE%/AudioBookSlides/whisperx/faster-whisper"
pip install "%BASE%/AudioBookSlides/whisperx/faster-whisper"
pip install "%BASE%/AudioBookSlides/whisperx"
pip install "%BASE%/AudioBookSlides"

echo "Test whisperx functionality;"
WARNING: DO NOT DO IT when whisperX displays: "To apply the upgrade to your files permanently, run `python -m pytorch_lightning.utilities.upgrade_checkpoint" 
whisperx --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --max_line_count 1 --verbose False --output_format srt --language en --output_dir "%BASE%\AudioBookSlides" "%BASE%\AudioBookSlides\OneStep.mp3"
type "%BASE%\AudioBookSlides\OneStep.srt"

#Usage: abs [bookname] [audio_file_wildcard_path]
#Example:
H:\win\AudioBookSlides>abs 06DeeplyOdd "E:\audiobooks\Dean Koontz - Deeply Odd (2013)\*.mp3"

__ComfyUI__
    
# If you have just installed ComfyUI you may need to install these components.
# Copy nodes_custom_sampler.py to your ComfyUI\comfy_extras folder. 
# Change the \ComfyUI\ path below as necessary for your install directory.

Browse to https://civitai.com/models/129666/realities-edge-xl-lcmsdxlturbo and click the download button 
to download the 6GB file "RealitiesEdgeXLLCM_TURBOXL.safetensors" and save it to 
\ComfyUi\models\checkpoints\RealitiesEdgeXLLCM_TURBOXL.safetensors If you already have A1111 installed, 
you can also modify \ComfyUI\extra_model_paths.yaml and point the base path to your A1111 SD folder if 
you prefer. ( base_path: E:\SD\stable-diffusion-webui\ )

2024-2-21 Update: Also download photon_v1.safetensors from here; https://civitai.com/models/84728/photon. 
I have changed the default model to this. It generates 10 quality images per minute on my NVIDIA 3060 GPU.
If your performance differs, it may be due to a few modifications I made to ComfyUI codebase. I can share them if requested.

copy nodes_custom_sampler.py \ComfyUI\comfy_extras\nodes_custom_sampler.py
git clone https://github.com/ltdrdata/ComfyUI-Manager.git \ComfyUI\custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git \ComfyUI\custom_nodes

# Start ComfyUI. (You will also need to start it when AudioBookSlides app tells you to launch it.)
\ComfyUI\run_nvidia_gpu.bat
#Click on "Manager" in the menu, then click "Update ComfyUI". When the update finishes, press CTRL-C in the CMD window to stop the Server

</code></pre>
</details>

**Linux**:
<details><summary>WSL Installation Steps (click to expand) [whisperX update]</summary>
<pre><code>

__ This can not run as a single bash script. A new mamba environment starts a new shell. __

#Enter the path of the folder you wish to install AudioBookSlides and ComfyUI to.
export BASE=/path_to_install_folder

#Install Mambaforge, a minimal Conda
#1. Navigate to the home directory
cd ~

#2. Download the Mambaforge installer script
#Run the following command to download the Mambaforge installer.
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh

#3. Make the installer script executable
chmod +x Mambaforge-Linux-x86_64.sh

#4. Run the installer script
echo "Now running the Mambaforge installer. Follow the on-screen instructions."
echo "During the installation process, you will need to:"
echo "  - Press 'Enter' to confirm the installation location."
echo "  - Type 'yes' and press 'Enter' to agree to the license terms."
echo "  - Press 'Enter' again to prepend the install location to PATH in your .bashrc file."
./Mambaforge-Linux-x86_64.sh

#5. Source the .bashrc file to update the environment (to be executed after the installation script completes)
echo "After the installation script completes, execute the following command to update your environment:"
source ~/.bashrc

#6. Create a new Conda environment named 'abs' with Python 3.10 and other dependencies
echo "Creating a new Conda environment named 'abs' with Python 3.10 and necessary packages."
mamba create -n abs python=3.10 cudnn cuda-libraries cuda-runtime cuda-libraries-dev -c conda-forge -c nvidia

__#  *** 7. INTERACTIVE ONLY Activate the newly created 'abs' environment ***__
echo "Activating the 'abs' environment."
mamba activate abs

#8. Install PyTorch, torchaudio, and CUDA support for PyTorch
echo "Installing PyTorch, torchaudio, and CUDA support for PyTorch."
mamba install pytorch torchaudio pytorch-cuda -c pytorch -c conda-forge -c nvidia

#9. Install ffmpeg using apt (requires sudo privileges)
echo "Installing ffmpeg. You might be prompted to enter your password."
sudo apt install ffmpeg

#10. Install zlib from the conda-forge channel
echo "Installing zlib."
mamba install zlib -c conda-forge

#11. Clone the AudioBookSlides repository
echo "Cloning the AudioBookSlides repository."
git clone https://github.com/GotAudio/AudioBookSlides.git "$BASE/AudioBookSlides"

#12. Save your OpenAI API Key
echo "Saving your OpenAI API Key."
echo "Replace YOUR_ACTUAL_API_KEY in the next command with your actual API key."
echo "YOUR_ACTUAL_API_KEY" > "$BASE/AudioBookSlides/ABS_API_KEY.txt"

#13. Clone the ComfyUI repository
echo "Cloning the ComfyUI repository."
git clone https://github.com/comfyanonymous/ComfyUI.git "$BASE/ComfyUI"

#14. Install requirements for ComfyUI
echo "Installing requirements for ComfyUI."
pip install -r "$BASE/ComfyUI/requirements.txt"

#15. Copy custom sampler node to ComfyUI
echo "Copying custom sampler node to ComfyUI."
cp "$BASE/AudioBookSlides/nodes_custom_sampler.py" "$BASE/ComfyUI/comfy_extras/nodes_custom_sampler.py"

#16. Install helper nodes for ComfyUI
echo "Installing helper nodes for ComfyUI."
git clone https://github.com/ltdrdata/ComfyUI-Manager.git "$BASE/ComfyUI/custom_nodes/ComfyUI-Manager"
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git "$BASE/ComfyUI/custom_nodes/ComfyUI-Impact-Pack"

#17. Manual Step: Download Model File
echo "Manual Step Required:"
echo "Visit https://civitai.com/models/129666/realities-edge-xl-lcmsdxlturbo"
echo "Click the download button to download the 'RealitiesEdgeXLLCM_TURBOXL.safetensors' file."
echo "Save it to '$BASE/ComfyUI/models/checkpoints/RealitiesEdgeXLLCM_TURBOXL.safetensors'"
echo If you already have A1111 installed, you may want to copy \ComfyUI\extra_model_paths.yaml.example to \ComfyUI\extra_model_paths.yaml
echo and point the base path to your A1111 SD folder if you prefer. ( base_path: /mnt/e/SD/stable-diffusion-webui/ )

echo 2024-2-21 Update: Also download photon_v1.safetensors from here; https://civitai.com/models/84728/photon. 
echo I have changed the default model to this. It generates 10 quality images per minute on my NVIDIA 3060 GPU.
echo If your performance differs, it may be due to a few modifications I made to ComfyUI codebase. I can share them if requested.

#18. Launch ComfyUI to download initial models and packages
echo "Launching ComfyUI to download initial models and packages. This may take a while."
python "$BASE/ComfyUI/main.py"

#19. Optional: Install Firefox on WSL2 for viewing the execution queue
echo "Optional: Installing Firefox on WSL2 for viewing the execution queue."
sudo apt install firefox
echo "You can launch Firefox and browse to http://127.0.0.1:8188 to view the execution queue."

#__Install Whisper__

#20. Clone the whisperx and faster-whisper repositories
echo "Cloning the whisperx and faster-whisper repositories."
git clone https://github.com/m-bain/whisperx.git "$BASE/AudioBookSlides/whisperx"
git clone https://github.com/SYSTRAN/faster-whisper.git "$BASE/AudioBookSlides/whisperx/faster-whisper"

#21. Install the whisperx and faster-whisper packages
echo "Installing the whisperx and faster-whisper packages."
pip install "$BASE/AudioBookSlides/whisperx/faster-whisper"
pip install "$BASE/AudioBookSlides/whisperx"

#22. Install the AudioBookSlides package
echo "Installing the AudioBookSlides package."
pip install -e "$BASE/AudioBookSlides"

#23. Clean up the build and egg-info directories
#idk if these are needed or not. I deleted them with no errors but later something caused an error. 
#Maybe the app has to be run at least once before they are no longer needed. Maybe I changed some code.
#"pip install ." will regenerate them
#echo "Cleaning up unnecessary files."
#rm -rf "$BASE/AudioBookSlides/build"
#rm -rf "$BASE/AudioBookSlides/AudioBookSlides.egg-info"

#24. Test whisperx functionality
echo "Testing the whisperx functionality."
WARNING: DO NOT DO IT when whisperX displays: "To apply the upgrade to your files permanently, run `python -m pytorch_lightning.utilities.upgrade_checkpoint" 
whisperx --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --max_line_count 1 --verbose False --output_format srt --language en --output_dir "$BASE/AudioBookSlides" "$BASE/AudioBookSlides/OneStep.mp3"
cat "$BASE/AudioBookSlides/OneStep.srt"

#25. How to start the AudioBookSlides application
#Usage: abs [bookname] [audio_file_wildcard_path]
#Example command (replace with actual book name and path to your audio files):
#abs 06DeeplyOdd '/path/to/your/audiobooks/Dean Koontz - Deeply Odd (2013)/*.mp3'

#26. End of Installation
echo "Installation complete. Please refer to the README for further instructions on using AudioBookSlides."

![WSL_images](https://github.com/GotAudio/AudioBookSlides/assets/13667229/10753daa-faee-4d03-a34c-70e5f8b75c62)
Dean Koontz - Odd Thomas - Deeply Odd Book 6. Length: 9:37, 2500 images took 5.5 hours to generate. 
(Video creation only takes a few minutes)

</code></pre>
</details>


#### Optional GPT API Setup
- 2024-2-21 Version 1.1.0 Update. GPT is no longer required. Scripts are now included to generate character and scene data locally. (GPT does a better job though.)
- To use the GPT API, you need to sign up for an API Key. Register and get your key [here](https://platform.openai.com).
- Save your API key in a file named `ABS_API_KEY.txt` in the application folder.
- The cost is approximately $1 for a 12-hour audiobook. New sign-ups might receive $20 free credit.
- Alternatively, use the free [LM-Studio Local GPT server](https://lmstudio.ai/). It's about 3 times slower (1 hour vs 20 minutes) and less accurate. The recommended model is [here](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF).
- Note: Not all requests have been optimized for LM-Studio. Some results may be suboptimal. This feature was utilized during development but has not been fully verified with the current installation.
  
## Overview of Processing

- The application keeps track of its workflow and can be stopped or restarted at any time.
- If it stops or you interrupt it, you can relaunch it and it will resume from where it left off. 
- The app will connect to the ChatGPT API to identify characters if you have configured an API key. 
- It may connect to GPT again to extract the scene/setting information for the image prompts.
- The process will pause to allow you to modify, or keep the default, file used to replace characters with actors.
- Default lists of actors are provided. By default, the app picks the replacement actor randomly.
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
- Adding actor entries only once, and allowing replacements to be consolidated into a single select name, reduces name collision issues. See edited example below.
- Replacing characters with actors is conducted to create consistent character appearances. This approach is simpler than trying to describe a particular character in detail.
- Character names will be replaced with actor names from .csv files configured in `default_config.yaml`. The file will be sorted with actors on top and actresses below.
- Due to the audiobook being transcribed with speech-to-text, actor names may often be misheard or misspelled. They might also be spoken in various forms, such as "John Smith", "John", "Smith", or "Mr. Smith."
- You are responsible for identifying these cases and assigning a single actor to all variations.
- Well-known characters like "Vampire", "Santa Claus", "Peter Rabbit", or any other character the AI already knows how to render, can be omitted.
- You are not required to enter actual actors.  You can enter any name from popular culture the AI may recognize, as I did below with 'Daenerys Targaryen'
- The "depth" key in `default_config.yaml` controls the minimum number of times a name must appear to be included in the initial replacement list. The default value is 4.
- While you might not need to provide an actor name for a character mentioned only once, that single instance may actually be a misspelling of the main character. Therefore, you might prefer to set the depth to 1 in the config file and manually remove any unrecognized names.
- It is important to order the various actor names from the longest to the shortest character length. For example, if the names "John" and "John Smith" both occur, place "John Smith" before "John" to ensure "John Smith" is correctly replaced.
- Exercise caution when using actor names that are also names of characters in your book. If overlooked, you might end up replacing a part of an actor's name with a different actor.
- Actor replacements are case-sensitive because the names you see are written in the case they appear.
- Be careful when replacing very short names that may be part of other words. For instance, entering "Pat " (with a space after) will ensure that the letters in "Patterns danced..." are not replaced.
- The format of this file is: count&lt;tab&gt;character name, _solo [age] &lt;gender&gt; [actor | actress] actor name @. Do not remove or alter the "count&lt;tab&gt;character," portion of the text.
- The delimiters _...@ are included in case you want to make targeted replacements or corrections to the final prompt file, specifically for actors and not other spoken text.
- For non-GPT processing, if you suspect a character's name is missing from your actor file, please follow these steps for possible correction:
   1. Open the file tokenizer_vocab_2.txt. This file acts as an English dictionary from which numerous names have been removed, including those scraped from U.S. baby names, census data, and extracted from 200,000 lines of eBooks. For instance, I recently had to remove the name "Holmes" from this file.
   2. If you believe there are still names missing after the initial edit, you can set 'use_dictionary: 0' in the config file. Proceed by deleting all files except for bookname.mp3 and bookname.srt, and re-run the generation script (for example, abs 01SherlockHolmes). This process ensures that no names from the dictionary are filtered out during name generation.
   3. If you're not satisfied with the results, you can set 'use_speech_verbs: 0' in the config file. This adjustment bypasses the validation check that requires proper names to be immediately followed by one of 500 different verbs, which indicate actions performed by a character. After this change, the sole criterion for a word to be considered a potential character name is capitalization, though this may result in some place names being included in your actor list. Ideally, you should review the list to identify and remove any such instances. (This match only needs to occur once, so for a prominent character, it is very likely to happen at least once.)
   4. I do not recommend setting both of these values to 0. If you do, you will probably get every word from the beginning of every sentence. Execution time will also increase.
   5. Or you can just type the missing character into the bookname_ts_p_actors_EDIT.txt file by copying and pasteing an existing line, then change the name in order to keep proper delimiters.

### This is an example of a default vs. manually edited actor list. 

| [Default] books/01ThisHour/01ThisHour_ts_p_actors_EDIT.txt            | [Edited] books/01ThisHour/01ThisHour_ts_p_actors.txt
| --------------------------------------------------------------------- | ---------------------------------------------------------------------- | 
|                                                                       |                                                                        | 
|100   Theodora, _solo  female actress Anna Paquin @                    |10	**Lemony Snicket**, Snicket                                 	 |
|62    Moxie, _solo 25yo female actress Naomi Watts long blond hair @   |4	Mr. **Snicket**, Snicket                                 		 |
|50    Ellington, _solo 25yo female actress Florence Pugh @             |40	**Snicket**, _solo 30yo male actor Patrick Warburton@		 |
|40    Snicket, _solo 30yo male actor Al Pacino @                       |12	S. Theodora Markson, Theodora                                 	 |
|18    Ellington Faint, _solo 30yo female actress Meg Donnelly @        |100	Theodora, _solo 25yo green eyed female **Daenerys Targaryen**@|
|17    Pip, _solo 30yo male actor Matthew Lewis @                       |62	Moxie, _solo 25yo female actress Naomi Watts curly hair@	 |
|16    Hangfire, _solo  male actor George Clooney @                     |18	**Ellington Faint**, Ellington                                    	 |
|13    Qwerty, _solo 25yo male actor Keanu Reeves @                     |50	**Ellington**, _solo 25yo sexy female actress Margot Robbie@	 |
|12    S. Theodora Markson, _solo 40yo female actress Summer H. Howell @|7	Stu Mitchum, _solo 12yo male actor Brad Pitt@			 |
|12    Hector, _solo 12yo male actor Colin Farrell @                    |7	Stu , _solo 12yo male actor Brad Pitt@				 |
|11    Prosper Lost, _solo 12yo male actor Christopher Walken @         |7	**Harvey Mitchum**, Harvey                             		 |
|10    Lemony Snicket, _solo 45yo male actor John Barrowman @           |6	**Harvey**, _solo 35yo male actor Gene Hackman@			 |
|7    Harvey Mitchum, _solo 40yo male actor Anthony Heald @             |6	Mimi Mitchum, _solo 30yo female actress Angelina Jolie@		 |
|7    Stu, _solo  male actor Dwayne Johnson @                           |6	**Quirty**, Qwerty                                  		 |
|7    Mrs. Sallis, _solo 50yo female actress Markella Kavenagh @        |13	**Qwerty**, _solo 25yo male actor Keanu Reeves@			 |
|7    Squeak, _solo 30yo male actor Michael Caine @                     |4	Murphy Sallis, Murphy                                  		 |
|6    Harvey, _solo 35yo male actor Cary Grant @                        |7	Sally Murphy, Murphy                                  		 |
|6    Mimi Mitchum, _solo 30yo female actress Madison Lintz @           |7	Mrs. Sallis, Murphy                                  		 |
|6    Mitchum, _solo 40yo male actor Gene Hackman @                     |7	Mrs. Salas, Murphy                                 		 |
|5    Malahan, _solo 45yo male actor David Harbour @                    |4	Murphy, _solo 55yo female actress Sharon Stone@		 |
|5    Father, _solo 50yo male actor Henry Cavill @                      |17	**Pip** , Peuchet                      				 |
|4    Mother, _solo 30yo female actress Maia Mitchell @                 |17	**Pecuchet**, _solo 30yo male actor Jet Li@				 |
|4    Mrs. Salas, _solo 60yo female actress Amelia Clarkson @           |7	Bouvard, Squeak                             			 |
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
- [X] 4) Test on system A1111 (note: some manual steps required).
- [X] 5) Test input with different audio formats (.WAV, .AAC). (ffmpeg does not support .m4b containing images so rename those to .aac and they will work)
- [X] 6) Finish Win/Whisper upgrade
- [ ] 7) Enable Tortoise-TTS text-to-speech to convert text eBooks to .mp3 with AI narrator. 
         Sample: Cave Johnson from "Portal" video game reads "Oil Slick" by Warren Murphy.

[Oil Slick, Cave Johnson](https://github.com/GotAudio/AudioBookSlides/assets/13667229/c9b740d3-feac-4213-b329-01aebc9732d7)

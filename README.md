# AudioBookSlides

![Turbo_RealitiesEdgeXLLCM_A1111-SD](https://github.com/GotAudio/AudioBookSlides/assets/13667229/4f30b0c5-9ab6-4940-89ca-e5ddb2235e0b)


Create an AI generated video slideshow from an audiobook.

[**AudioBookSlides**](https://github.com/GotAudio/AudioBookSlides/)<br/>

I created a sample book to test this installation. Public domain Librivox [Alice in Wonderland](https://www.youtube.com/watch?v=27SwZZ8jiBc). You can find more free audiobooks [here](https://librivox.org/).

[Contact Sheet from Alice In Wonderland](https://github.com/GotAudio/AudioBookSlides/assets/13667229/acf17491-81be-42ee-a2de-230a19922d57)


This is a demo contact sheet showing the images generated. (Made with [VideoCS](https://sourceforge.net/projects/videocs) not this program.)

## AudioBookSlides Installation Guide

AudioBookSlides requires the installation of three external packages:

- **WhisperX**:
  - **Windows Users**:
    - Install WhisperX from [here](https://github.com/Purfview/whisper-standalone-win/releases/tag/faster-whisper).
    - Extract `whisper-faster.exe` to the application directory.
    - Download `cuBLAS.and.cuDNN_win_v4.7z` from [here](https://github.com/Purfview/whisper-standalone-win/releases/tag/libs) and unzip it to the application folder.
  - **Unix Users**:
    - Install WhisperX using the command: `pip install faster-whisper`.

- **ffmpeg**:
  - ffmpeg can be installed from [here](https://github.com/BtbN/FFmpeg-Builds/releases).
  - This package is essential for handling multimedia files.

- **ComfyUI**:
  - Download ComfyUI stand-alone portable from [here](https://github.com/comfyanonymous/ComfyUI/releases).
  - Launching the server is sufficient; using the ComfyUI web interface is not necessary.

Ensure each package is correctly installed and configured before using AudioBookSlides.

#### GPT API Setup
- To use the GPT API, you need to sign up for an API Key. Register and get your key [here](https://platform.openai.com).
- Save your API key in a file named `ABS_API_KEY.txt` in the application folder.
- The cost is approximately $2 for a 12-hour audiobook. New sign-ups might receive $20 free credit.
- Alternatively, use the free [LM-Studio Local GPT server](https://lmstudio.ai/). It's about 3 times slower (1 hour vs 20 minutes) and less accurate. The recommended model is [here](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF).
- Note: Not all requests have been optimized for LM-Studio. Some results may be poor. (This was used in development but hasn't been fully verified with this installation.)

### Installation of AudioBookSlides
- Consider creating a [conda](https://conda.io/) environment for the installation.
- The requirements are minimal with one specific version requirement: `openai==0.28` (compatible with LM-Studio).
- Python versions 3.9 and 3.10 have been used successfully.

```
conda create -n abs python=3.10
conda activate abs

git clone https://github.com/GotAudio/AudioBookSlides.git

cd AudioBookSlides

pip install .

python abs.py BookName \path_to_audiobook\bookname.mp3

# Note:
# After the .mp3 file has been created in the first few steps, 
# the path to the mp3 file can be omitted for subsequent reruns.
```

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
│   ├──── Bookname.avi 
│   ├── ...
├── BookName2
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

1. Test wildcard input folder with multiple MP3 files.
   - Verified 3 files (chapters) concatenated: 
     ```
     python abs.py 01ThisHour "E:\Media\AudioBooks\Lemony Snicket\All the Wrong Questions 1 - Who Could That Be at This Hour\*.mp3"
     ```
2. Test spaces in BookName and MP3 path.
- [ ] 2) Test spaces in BookName and MP3 path.
- [ ] 3) Test on Windows Subsystem for Linux (WSL).
- [ ] 4) Test on system A1111 (note: some manual steps required).
- [ ] 5) Test input with different audio formats (.WAV, .ACC).

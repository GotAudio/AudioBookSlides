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
Extract and save whisper-faster.exe to the application directory. Download [cuBLAS.and.cuDNN_win_v4.7z from here](https://github.com/Purfview/whisper-standalone-win/releases/tag/libs) and unzip to application folder.
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
- The format of this file is: count<tab>character name, _solo [age] <gender> [actor | actress] actor name @. Do not remove or alter the "count<tab>character," portion of the text.
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


TODO: 
1) Test wildcard input folder with multiple mp3 files.
2) Test spaces in BookName and mp3 path
3) Test WSL
4) Test A1111 (some manual steps required)
5) Test .WAV, .ACC input.

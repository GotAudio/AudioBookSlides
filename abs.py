import argparse
import platform
import os
import shutil
import subprocess
import yaml
import glob
import logging
import sys
import re
from pathlib import Path, PureWindowsPath

# Define constants and initialize logging
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DEBUG = 1  # Set to 1 for debug mode, 0 to disable

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

def concatenate_files(filelist_path, output_file):
    ffmpeg_concat_cmd = f'ffmpeg -hide_banner -f concat -safe 0 -i "{filelist_path}" -c copy "{output_file}"'
    return run_command(ffmpeg_concat_cmd)

def convert_to_mp3(source_file, target_file):
    ffmpeg_convert_cmd = f'ffmpeg -hide_banner -i "{source_file}" -acodec libmp3lame "{target_file}"'
    return run_command(ffmpeg_convert_cmd)

def handle_single_file(file_path, target_file):
    if file_path.endswith('.mp3'):
        shutil.copyfile(file_path, target_file)
        return True
    else:
        return convert_to_mp3(file_path, target_file)

def is_file_nonempty(file_path):
    """Check if the file exists and is not empty."""
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            return sum(1 for _ in file)
    except IOError as e:
        logging.error("Error reading file %s: %s", filepath, e)
        return -1

def create_file_if_missing(source, target):
    try:
        if not os.path.exists(target):
            shutil.copy(source, target)
            logging.info("Creating: %s", target)
            return True
        else:
            logging.info("Already exists: %s", target)
            return True
    except IOError as e:
        logging.error("Error copying file: %s", e)
        return False

def run_command(command):
    logging.info("Executing command: %s", command)
    try:
        result = subprocess.run(command, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e)
        return False

def create_directory(path):
    if os.path.exists(path):
        logging.info("Already exists: %s", path)
        return True
    try:
        os.makedirs(path, exist_ok=True)
        logging.info("Creating directory: %s", path)
    except OSError as e:
        logging.error("Error creating directory %s: %s", path, e)
        return False
    return True

# Define a function to recursively replace placeholders
def replace_bookname_recursive(data, bookname):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_bookname_recursive(value, bookname)
        return data
    elif isinstance(data, list):
        return [replace_bookname_recursive(item, bookname) for item in data]
    elif isinstance(data, str):
        return data.replace('<bookname>', bookname)
    else:
        return data

def fix_path(old_path):
    if (os.name != "nt"):
        linux_path = old_path.replace('\\', '/')
        if ':' in linux_path:
            drive_letter, rest_of_path = linux_path.split(':', 1)
            linux_path = '/mnt/' + drive_letter.lower() + rest_of_path
        return linux_path
    else:
        return old_path

def main(bookname, wildcard_path=None):
    # Step 1: Create the folder books\<bookname> if it does not exist

    book_folder = os.path.join('books', bookname)
    if not create_directory(book_folder):
        return
    else:
        if DEBUG:
            logging.debug("Step 01/20: Audio book folder: %s",book_folder)

    api_key_file_path = os.path.join(SCRIPT_PATH, 'ABS_API_KEY.txt')

    # Read the default configuration
    default_config_path = os.path.join(SCRIPT_PATH, 'default_config.yaml')

    try:
        with open(default_config_path, 'r') as file:
            default_config = yaml.safe_load(file)
    except Exception as e:
        logging.error("Error reading default YAML file: %s", e)
        return

    # Step 2: Check for book-specific configuration
    if DEBUG:
        logging.debug("Step 02/20: Checking for book-specific configuration file %s", f"{bookname}.yaml")

    book_config_path = os.path.join(book_folder, f"{bookname}.yaml")

    # Initialize config with default settings
    config = default_config

    # If book-specific configuration exists, read and merge it
    if os.path.exists(book_config_path):
        try:
            with open(book_config_path, 'r') as file:
                book_config = yaml.safe_load(file)

            # Merge configurations, with book-specific settings taking precedence
            config.update(book_config)

        except Exception as e:
            logging.error("Error reading book-specific YAML file: %s", e)
            return

    # Replace placeholders in the config dictionary
    config = replace_bookname_recursive(config, bookname)

    # Normalize paths in the config dictionary
    keys_to_normalize = ['whisperx', 'actors', 'actresses', 'path_to_stablediffusion', 'path_to_comfyui', 'path_to_workflow','image_generator']

    for key in keys_to_normalize:
        if key in config:
            original_path = config[key]
            config[key] = fix_path(original_path)

    openai_api_key = None

    # Read the OpenAI API key from ABS_API_KEY.txt
    try:
        with open(api_key_file_path, 'r') as file:
            openai_api_key = file.read().strip()
        os.environ['ABS_API_KEY'] = openai_api_key
    except Exception as e:
        logging.info("ABS_API_KEY.txt does not contain an API key. GPT API will be unavailable.")

    # Step 3: Create the MP3 file if it does not exist
    mp3_file_path = os.path.join(book_folder, f"{bookname}.mp3")

    if not os.path.exists(mp3_file_path):
        if wildcard_path is None:
            logging.error("Missing required wildcard path for audio file creation.")
            return False

        # Initialize dir_path
        dir_path = None
        file_extension = None  # Initialize file_extension

        wildcard_path = wildcard_path.rstrip('"')  # Ensure no trailing quote

        # Normalize the wildcard path to eliminate any OS-specific characters
        normalized_path = os.path.normpath(wildcard_path)

        # Determine if the path is a directory, a specific file pattern, or a wildcard for any file
        if os.path.isdir(normalized_path) or normalized_path.endswith('*.*'):
            dir_path = normalized_path if os.path.isdir(normalized_path) else os.path.dirname(normalized_path)
        else:
            dir_path = os.path.dirname(normalized_path)
            file_extension = os.path.splitext(os.path.basename(normalized_path))[1] if '.' in os.path.basename(normalized_path) else None

        # Check if dir_path is set before logging
        if dir_path:
            logging.debug("Determined audio directory path: %s", dir_path)
        else:
            logging.error("The directory path could not be determined.")
            return False  # or handle the error as appropriate

        if DEBUG:
            logging.debug("Step 03/20: Audio file %s", wildcard_path)
            logging.debug("Determined audio directory path: %s", dir_path)

        filelist_path = os.path.join(book_folder, 'filelist.txt')

        # Search for files based on the determined extension or default to common audio file types
        if file_extension:
            files = [f for f in os.listdir(dir_path) if f.endswith(file_extension)]
        else:
            extensions = ['.mp3', '.aac', '.wav']
            files = [f for f in os.listdir(dir_path) for ext in extensions if f.endswith(ext)]

        if not files:
            logging.error(f"No matching files found in {dir_path} for the pattern {wildcard_path}")
            return False

        if DEBUG and files:
            logging.debug("Found %d files: %s...", len(files), files[0])

        # Process files
        if len(files) == 1:
            # Only one file, handle it directly
            single_file_path = os.path.join(dir_path, files[0])
            if not handle_single_file(single_file_path, mp3_file_path):
                logging.error(f"Failed to copy single file to book folder {single_file_path} , {mp3_file_path}")
                return False
        else:
            # Multiple files, concatenate and then convert
            with open(filelist_path, 'w') as filelist:
                for audio_file in sorted(files):
                    full_path = os.path.join(dir_path, audio_file)
                    # Inside the loop where you write to filelist.txt
                    escaped_path = full_path.replace('\\', '\\\\')  # Escape the backslashes
                    escaped_path = escaped_path.replace("'", "'\\''")  # Escape single quotes
                    filelist.write(f"file '{escaped_path}'\n")

            temp_output_file = os.path.splitext(filelist_path)[0] + os.path.splitext(files[0])[1]  # Use the extension of the first file
            if not concatenate_files(filelist_path, temp_output_file):
                return False
            if not handle_single_file(temp_output_file, mp3_file_path):
                return False
            os.remove(temp_output_file)
    else:
        logging.info("MP3 file already exists, skipping creation: %s", mp3_file_path)


    # Step 4: Create .srt file
    srt_file_path = os.path.join(book_folder, f"{bookname}.srt")
    if not os.path.exists(srt_file_path):

        logging.info("Creating ssubtitle: %s", srt_file_path)

        # Step 4.1: construct and optionally display the whisperx_cmd

        # Determine the appropriate key based on the operating system
        key = 'whisperx_win' if platform.system() == 'Windows' else 'whisperx_linux'

        # Extract directory from mp3_file_path
        output_dir = os.path.dirname(mp3_file_path)
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

        # Construct whisperx_cmd using the base command from config and appending the dynamic directory and file path
        whisperx_cmd = f"{config[key]} {output_dir} {mp3_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 04/20: WhisperX command: %s", whisperx_cmd)

        try:
            result = subprocess.run(whisperx_cmd, shell=True, check=True)
            # Verify if the srt file was created
            if result.returncode == 0 and os.path.exists(srt_file_path):
                logging.info("Created srt: %s", srt_file_path)
            else:
                logging.error("Failed to create SRT file: %s", srt_file_path)
                return
                # WhisperX creates this for some reason.
                temp_output_file = "temp_output.srt"
                if os.path.exists(temp_output_file):
                    try:
                        os.remove(temp_output_file)
                        print(f"Deleted file: {temp_output_file}")
                    except OSError as e:
                        print(f"Error deleting file {temp_output_file}: {e}")
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Subtitle already exists: %s", srt_file_path)

    # Step 5: Modify SRT file with fix_srt.py script
    modified_srt_file_path = os.path.join(book_folder, f"{bookname}_m300.srt")
    original_srt_file_path = os.path.join(book_folder, f"{bookname}.srt")

    if not os.path.exists(modified_srt_file_path):
        logging.info("Creating modified srt: %s", modified_srt_file_path)

        # Construct the fix_srt.py command
        fix_srt_cmd = f"python fix_srt.py -join 300 {original_srt_file_path} {modified_srt_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 05/20: Convert subtitle to 300 characters per line: %s", fix_srt_cmd)

        try:
            result = subprocess.run(fix_srt_cmd, shell=True, check=True)
            # Verify if the modified srt file was created
            if result.returncode == 0 and os.path.exists(modified_srt_file_path):
                logging.info("Created modified srt: %s", modified_srt_file_path)
            else:
                logging.error("Failed to create modified SRT file: %s", modified_srt_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Merged subtitle already exists: %s", modified_srt_file_path)

    # Step 6: Create time-synced SRT file with make_prompts.py script
    ts_srt_file_path = os.path.join(book_folder, f"{bookname}_ts.srt")
    modified_srt_file_path = os.path.join(book_folder, f"{bookname}_m300.srt")

    if not os.path.exists(ts_srt_file_path):
        logging.info("Creating time-stamped srt: %s", ts_srt_file_path)

        # Construct the make_prompts.py command
        make_prompts_cmd = f"python make_prompts.py {modified_srt_file_path} {ts_srt_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 06/20: Add timestamp tags to .srt file: %s", make_prompts_cmd)

        try:
            result = subprocess.run(make_prompts_cmd, shell=True, check=True)
            # Verify if the time-synced srt file was created
            if result.returncode == 0 and os.path.exists(ts_srt_file_path):
                logging.info("Created time-stamp srt: %s", ts_srt_file_path)
            else:
                logging.error("Failed to create time-stamp SRT file: %s", ts_srt_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Timestamped subtitle already exists: %s", ts_srt_file_path)


    ts_srt_file_path = os.path.join(book_folder, f"{bookname}_ts.srt")
    ts_p_srt_file_path = os.path.join(book_folder, f"{bookname}_ts_p.srt")

    if not openai_api_key:
        m300_srt_filepath = os.path.join(book_folder, f"{bookname}_m300.srt")

        if not os.path.exists(ts_p_srt_file_path):
            logging.info("Generating character names : %s", ts_p_srt_file_path)

            # tokenizer_vocab_2.txt is a dictionary of words that are probably not english names. If you regularly see
            # character names you do not think are characters, add them to this list to have them excluded.
            make_api_names_cmd = f"python combined_dictionary.py tokenizer_vocab_2.txt {m300_srt_filepath} {ts_srt_file_path} {ts_p_srt_file_path}"

            if DEBUG:
                logging.debug("Step 07/20: Generate a list of potential character names: %s", make_api_names_cmd)

            try:
                result = subprocess.run(make_api_names_cmd, shell=True, check=True)
                if result.returncode == 0:
                    logging.info("Created file with character names: %s", ts_p_srt_file_path)
                else:
                    logging.error("Failed to create file with character names: %s", ts_p_srt_file_path)
                    return
            except subprocess.CalledProcessError as e:
                logging.error("Command failed: %s", e)
                return
        else:
            logging.info("Timestamped characters already exists: %s", ts_p_srt_file_path)

    file_needs_creation = not is_file_nonempty(ts_p_srt_file_path)
    file_created_or_verified = False

    if openai_api_key:
        # Step 7: Create or verify prompt-enhanced SRT file with gen_prompts.py script

        # Function to execute gen_prompts.py command
        def execute_gen_prompts():
            gen_prompts_cmd = f"python gen_prompts.py {ts_srt_file_path} {ts_p_srt_file_path}"
            if DEBUG:
                logging.debug("Step 07/20: Use GPT API to create image prompts for StableDiffusion: %s", gen_prompts_cmd)
            try:
                result = subprocess.run(gen_prompts_cmd, shell=True, check=True)
                return result.returncode == 0
            except subprocess.CalledProcessError as e:
                logging.error("Command failed: %s", e)
                return False

        file_needs_creation = not is_file_nonempty(ts_p_srt_file_path)
        file_created_or_verified = False

        if file_needs_creation:
            logging.info("Creating prompt-enhanced srt: %s", ts_p_srt_file_path)
            file_created_or_verified = execute_gen_prompts()
        else:
            logging.info("Timestamped characters already exists: %s", ts_p_srt_file_path)

    # Verify line count and non-emptiness
    if file_created_or_verified or is_file_nonempty(ts_p_srt_file_path):
        input_lines = count_lines(ts_srt_file_path)
        output_lines = count_lines(ts_p_srt_file_path)
        if input_lines == output_lines:
            logging.info("Verified prompt-enhanced srt with correct line count: %s", ts_p_srt_file_path)
        else:
            logging.error("Line count mismatch or %s vs. %s", ts_srt_file_path, ts_p_srt_file_path)
            os.remove(ts_p_srt_file_path)  # Delete the empty or incorrect file
            if file_needs_creation and openai_api_key:
                logging.info("Attempting to recreate prompt-enhanced SRT file.")
                file_created_or_verified = execute_gen_prompts()
                if not file_created_or_verified:
                    return
            else:
                return
    else:
        logging.error("File creation failed or file is empty: %s", ts_p_srt_file_path)
        return


    # Step 11: Get characters with get_characters.py script
    ts_srt_p_file_path = os.path.join(book_folder, f"{bookname}_ts_p.srt")
    ts_srt_p_characters_file_path = os.path.join(book_folder, f"{bookname}_ts_p_characters.srt")

    if not os.path.exists(ts_srt_p_characters_file_path):
        logging.info("Getting characters list: %s", ts_srt_p_characters_file_path)

        # Construct the get_characters.py command
        get_characters_cmd = f"python get_characters.py {ts_srt_p_file_path} {ts_srt_p_characters_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 11/20: Extract named characters from .srt file: %s", get_characters_cmd)

        try:
            result = subprocess.run(get_characters_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Got characters to: %s", ts_srt_p_characters_file_path)
            else:
                logging.error("Failed to get characters: %s", ts_srt_p_characters_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Characters list already exists: %s", ts_srt_p_characters_file_path)

   # Step 12: Extract scenes with extract_scene.py script
    ts_srt_file_path = os.path.join(book_folder, f"{bookname}_ts.srt")
    ts_srt_p_ns_file_path = os.path.join(book_folder, f"{bookname}_ts_p_ns.srt")

    if not os.path.exists(ts_srt_p_ns_file_path):
        logging.info("Extracting scenes: %s", ts_srt_p_ns_file_path)

        # Construct the extract_scene.py command
        extract_scene_cmd = f"python extract_scene.py {ts_srt_file_path} {ts_srt_p_ns_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 12/20: Generate scene information: %s", extract_scene_cmd)

        try:
            result = subprocess.run(extract_scene_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Extracted scenes to: %s", ts_srt_p_ns_file_path)
            else:
                logging.error("Failed to extract scenes: %s", ts_srt_p_ns_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Scenes file already exists: %s", ts_srt_p_ns_file_path)

    # Verify line count
    input_lines = count_lines(ts_srt_file_path)
    output_lines = count_lines(ts_srt_p_ns_file_path)
    if input_lines == output_lines:
        logging.info("Verified scenes file with correct line count: %s", ts_srt_p_ns_file_path)
    else:
        logging.error("Line count mismatch in scenes file: %s", ts_srt_p_ns_file_path)
        return

    # Step 13: Merge two input files and create an output file
    input_file1 = f"books/{bookname}/{bookname}_ts_p_ns.srt"
    input_file2 = f"books/{bookname}/{bookname}_ts_p.srt"
    output_file = f"books/{bookname}/{bookname}_merged.txt"

    if not os.path.exists(output_file):
        logging.info("Step 12/20: Merging timestamp, character, and scenes: %s and %s to %s", input_file1, input_file2, output_file)

        try:
            # Open input files for reading
            with open(input_file1, 'r', encoding='utf-8') as file1, \
                 open(input_file2, 'r', encoding='utf-8') as file2:

                # Create a dictionary to store data from the first file
                data_dict = {}

                # Read and store data from the first file
                for line in file1:
                    fields = line.strip().split('\t')
                    if len(fields) >= 2:
                        key, value = fields[0], fields[1]
                        data_dict[key] = value

                # Merge data from the second file and write to the output file
                with open(output_file, 'w', encoding='utf-8') as merged_file:
                    for line in file2:
                        fields = line.strip().split('\t')
                        if len(fields) >= 2:
                            key, value = fields[0], fields[1]
                            if key in data_dict:
                                merged_line = f"{value}\t{data_dict[key]}\t{key}\n"
                                merged_file.write(merged_line)

            logging.info("Merged files to: %s", output_file)

        except Exception as e:
            logging.error("Error during merging: %s", e)
            return
    else:
        logging.info("Merged characters and scenes already exists: %s", output_file)

    # Step 14: Replace actors using the existing script
    male_actors_csv = config.get('actors')
    female_actors_csv = config.get('actresses')
    depth = config.get('depth')

    # Ensure platform-independent path separators
    input_file = os.path.join("books", bookname, f"{bookname}_ts_p_characters.srt")
    edit_file = os.path.join("books", bookname, f"{bookname}_ts_p_actors_EDIT.txt")

    if not os.path.exists(edit_file):
        logging.info("Step 14/20: Creating actor list from %s and saving to %s", input_file, edit_file)

        try:
            # Execute the existing replace_actors.py script with depth parameter
            replace_actors_cmd = f"python replace_actors.py {input_file} {male_actors_csv} {female_actors_csv} {edit_file} {depth}"

            # Log the command if debugging is enabled
            if DEBUG:
                logging.debug("Step 14/20: Combining characters with actors: %s", replace_actors_cmd)

            result = subprocess.run(replace_actors_cmd, shell=True, check=True)

            if result.returncode == 0:
                logging.info("* You must edit actors file %s, make any corrections, and save as %s", edit_file, os.path.join("books", bookname, f"{bookname}_ts_p_actors.txt"))
            else:
                logging.error("Failed to replace actors: %s", edit_file)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return

    # Step 15: Apply actors using the apply_actors.py script
    input_file = f"books/{bookname}/{bookname}_ts_p_actors.txt"
    merged_file = f"books/{bookname}/{bookname}_merged.txt"
    output_file = f"books/{bookname}/{bookname}_merged_names_dup.txt"

    # Check if input_file exists
    if not os.path.exists(input_file):
        logging.info("* You must edit actors file %s, make any corrections, and save as %s", edit_file, input_file)
        return  # Stop processing or skip to the next step

    if not os.path.exists(output_file):
        logging.info("Applying actors from %s and saving as %s.", input_file, output_file)

        try:
            # Execute the apply_actors.py script
            apply_actors_cmd = f"python apply_actors.py {input_file} {merged_file} {output_file}"

            # Log the command if debugging is enabled
            if DEBUG:
                logging.debug("Step 15/20: Making replacements of character names with actor names: %s", apply_actors_cmd)

            result = subprocess.run(apply_actors_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Actors applied and saved to: %s", output_file)
            else:
                logging.error("Failed to apply actors: %s", output_file)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Replaced actors already exists: %s", output_file)

    # Step 15.1: Apply actors using the apply_actors.py script
    input_file = f"books/{bookname}/{bookname}_merged_names_dup.txt"
    output_file = f"books/{bookname}/{bookname}_merged_names.txt"

    # Check if input_file exists
    if not os.path.exists(input_file):
        logging.error("Error pruning duplicate actors. Input file %s not found. Exiting.", input_file)
        return  # Stop processing or skip to the next step

    if not os.path.exists(output_file):
        logging.info("Pruning extra actors from %s and saving to %s.", input_file, output_file)

        try:
            # Execute the apply_actors.py script
            apply_actors_cmd = f"python remove_all_other_actors.py {input_file} {output_file} --bookname {bookname}"

            # Log the command if debugging is enabled
            if DEBUG:
                logging.debug("Step 15.1/20: Removing low priority actors per actor_priority in config file. Removals in removed.log: %s", apply_actors_cmd)

            result = subprocess.run(apply_actors_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Pruned actors file: %s", output_file)
            else:
                logging.error("Failed to prune actors: %s", output_file)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Pruned low priority actors already exists: %s", output_file)


    # Step 16: Verify the existence of <path_to_comfyui> from config YAML
    input_file = f"books/{bookname}/{bookname}_merged_names.txt"

    if not os.path.exists(input_file):
        logging.error("Error generating images. Input file %s not found. Exiting.", input_file)
        return  # Stop processing or skip to the next step

    image_generator = config.get('image_generator')
    if image_generator not in ['ComfyUI', 'A1111']:
        logging.error("image_generator tag in config file must be A1111 or ComfyUI. Found: %s", image_generator)
        exit(1)

    if image_generator == 'ComfyUI':
        path_to_comfyui = config['path_to_comfyui']
        if os.path.isdir(path_to_comfyui):
            logging.info("Output folder already exists: %s", path_to_comfyui)
        else:
            comfyui_model = config['comfyui_model']
            cfg = config['cfg']
            steps = config['steps']
            image_count = config['image_count']
            image_width = config['image_width']
            image_height = config['image_height']
            workflow_path = config['path_to_workflow']

            input_file = os.path.join("books", bookname, f"{bookname}_merged_names.txt")

            logging.info("Generating images using ComfyUI")
            run_comfy_cmd = (
                f"python run_comfy_wf_api.py --ckpt_name \"{comfyui_model}\" "
                f"--cfg {cfg} --steps {steps} --count {image_count} "
                f"--width {image_width} --height {image_height} "
                f"{input_file} {workflow_path} --bookname {bookname}"
            )

            if DEBUG:
                logging.debug("Step 16/20: Launch ComfyUI. Command: %s", run_comfy_cmd)

            try:
                result = subprocess.run(run_comfy_cmd, shell=True, check=True)
                if result.returncode == 0:
                    logging.info("Images generated successfully")
                else:
                    logging.error("Failed to generate images")
            except subprocess.CalledProcessError as e:
                logging.error("Command failed: %s", e)

    elif image_generator == 'A1111':
        path_to_stablediffusion = config['path_to_stablediffusion']  # This should be 'E:\SD\stable-diffusion-webui\outputs\txt2img-images\03BAllTheseWorlds'
        if os.path.isdir(path_to_stablediffusion):
            logging.info("Output folder already exists: %s", path_to_stablediffusion)
        else:
            input_file = os.path.join("books", bookname, f"{bookname}_merged_names.txt")

            if DEBUG:
                logging.debug("Step 16/20: Launch Stable Diffusion (A1111)")

            # Corrected user instruction using string replace
            path_for_renaming = path_to_stablediffusion.replace(bookname, 'YYYY-MM-DD')
            user_instruction = (
                "Ready for A1111 image generation.\n"
                "1. Change the 'Script' dropdown setting near the bottom of the txt2img tab to 'Prompts from file or textbox'.\n"
                "2. Drop '{input_file}' onto the file upload box.\n"
                "3. Select the model, and styles you want and click Generate.\n"
                "4. Rename '{path_for_renaming}' to '{path_to_stablediffusion}' when images are complete.\n"
                "5. You may need to merge multiple folders together if your image generation task crossed midnight.\n"
                "Press <enter> when ready:"
            ).format(input_file=input_file, path_for_renaming=path_for_renaming, path_to_stablediffusion=path_to_stablediffusion)

            input(user_instruction)

    # Step 17: Verify the existence of <path_to_comfyui> after image generation
    if config.get('image_generator') == 'ComfyUI':
        if not os.path.exists(path_to_comfyui):
            # Count the lines in the input file again to get the image count
            generated_image_count = count_lines(input_file)
            if generated_image_count >= 0:
                logging.debug(
                    "If there were no errors, you should see %d images appear in the ComfyUI\\output folder. When they are finished, delete any images you do not want,\n"
                    "then rename ComfyUI\\output to ComfyUI\\%s. Output folder does not exist: %s",
                    generated_image_count, bookname, path_to_comfyui)
            else:
                logging.error("Failed to count submitted image generation prompts.")
            return
    elif config.get('image_generator') == 'A1111':
        if not os.path.exists(path_to_stablediffusion):
            # Count the lines in the input file again to get the image count
            generated_image_count = count_lines(input_file)
            if generated_image_count >= 0:
                logging.debug("There should be %d images in the '%s' folder when complete.",generated_image_count, path_to_stablediffusion)
            else:
                logging.error("Failed to count image generation requirements")
            return
    else:
        logging.error("image_generator tag in config file must be A1111 or ComfyUI. Found: %s", config.get('image_generator'))
        return


    # Step 18: Run png_text.py and rename_png_files.py scripts
    path_to_images = ''
    if config.get('image_generator') == 'ComfyUI':
        path_to_images = config.get('path_to_comfyui', '')
    elif config.get('image_generator') == 'A1111':
        path_to_images = config.get('path_to_stablediffusion', '')

    if not path_to_images:
        logging.error("Missing path to images in the config YAML. Exiting.")
        return

    # Check if 'path_to_images' exists as a folder
    if not os.path.exists(path_to_images):
        logging.error("Folder '%s' does not exist. Exiting.", path_to_images)
        return

    file_path = os.path.join(path_to_images, '000000000.png')

    skip_renaming = "n"
    if os.path.exists(file_path):
        while True:
            skip_renaming = input("Step 18/20: Generated image file %s already exists. Do you want to skip file renaming step? [Y/n] (Default: Y): " % file_path).strip().lower()

            if not skip_renaming:  # Default to "Y" if the user presses Enter
                skip_renaming = "y"

            if skip_renaming in ["y", "n"]:
                break
            else:
                print("Invalid input. Please enter 'Y' or 'N'.")

    if skip_renaming == "n":
        # Define the command to run png_text.py
        # removed -o (overwrite) flag. Not sure why it was enabled. Allows for faster restarts
        make_text_cmd = f"python png_text.py {path_to_images}"

        # Define the command to run rename_png_files.py
        rename_png_cmd = f"python rename_png_files_int.py {path_to_images}"

        # Log the commands if debugging is enabled
        if DEBUG:
            logging.debug("Step 18/20: Extract metadata from PNG files and save as .tEXt.txt: %s", make_text_cmd)

        try:
            # Execute the png_text.py command
            result = subprocess.run(make_text_cmd, shell=True, check=True)

            if DEBUG:
                logging.debug("Step 18.1/20 Read .txt files and rename PNG files to the .srt timestamp: %s", rename_png_cmd)

            # Execute the rename_png_files.py command
            result = subprocess.run(rename_png_cmd, shell=True, check=True)

            path_to_images = path_to_images.replace("<bookname>", bookname)  # Replace placeholder
            txt_files = glob.glob(os.path.join(path_to_images, "*.tEXt.txt"))
            for file_path in txt_files:
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
    else:
        print("Skipping file renaming step as per user choice.")

    # Step 19: Create an output video if it doesn't exist
    output_video_path = os.path.join(book_folder, f"{bookname}_output.avi")

    if not os.path.exists(output_video_path):
        logging.info("Creating silent output video: %s", output_video_path)

        # Construct the jobvid.py command
        jobvid_cmd = f"python jobvid.py \"{os.path.join(path_to_images, '*.png')}\" \"{output_video_path}\""

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 19/20: Parallel ffmpeg processes generate and combine still image .AVIs %s", jobvid_cmd)

        try:
            subprocess.run(jobvid_cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            # Silently ignore the error
            pass

        # Check if the output file was created, after the try-except block
        if not os.path.exists(output_video_path):
            logging.error("Failed to create output video: %s", output_video_path)
            return  # Exit from the current function or script
        else:
            logging.info("Output video created: %s", output_video_path)

    else:
        logging.info("Output video already exists: %s", output_video_path)

    # Step 20: Create the final video if it doesn't already exist
    output_avi_path = os.path.join(book_folder, f"{bookname}.avi")

    if not os.path.exists(output_avi_path):
        logging.info("Creating the final video with audio: %s", output_avi_path)

        ffmpeg_cmd = (
            f'ffmpeg -hide_banner -i "books/{bookname}/{bookname}_output.avi" '
            f'-i "books/{bookname}/{bookname}.mp3" '
            f'-c:v copy -map 0:v:0 -map 1:a:0 "{output_avi_path}"'
        )

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 20/20: This combines the original mp3 audio book and the generated video. .srt is included in the same folder. You could embed it in the video if you wanted to: \n%s", ffmpeg_cmd)
        try:
            result = subprocess.run(ffmpeg_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info(f"{output_avi_path} and books/{bookname}/{bookname}.srt files created.")

                temp_output_file = f"books/{bookname}/{bookname}_output.avi"
                if os.path.exists(temp_output_file):
                    try:
                        os.remove(temp_output_file)
                    except OSError:
                        pass  # Do nothing if there's an error
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
    else:
        logging.info("Final video already exists: %s", output_avi_path)


def check_ffmpeg_availability():
    try:
        # Run the ffmpeg --version command and capture its output
        ffmpeg_version_output = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT, text=True)

        # Display the first line of the output
        first_line = ffmpeg_version_output.splitlines()[0]
        logging.info("ffmpeg found: %s", first_line)
        return True

    except subprocess.CalledProcessError as e:
        # ffmpeg command failed, so it's not available
        logging.error("ffmpeg not found. Error: %s", e.output)
        return False

def get_version_and_description_from_setup():
    setup_path = 'setup.py'  # Assuming setup.py is in the same directory
    info = {"version": "1.0", "description": "Default description"}  # Default values

    # Regular expressions to match version and description
    version_match = re.compile(r"^.*version=['\"]([^'\"]*)['\"].*$", re.M)
    description_match = re.compile(r"^.*description=['\"]([^'\"]*)['\"].*$", re.M)

    with open(setup_path, 'rt') as f:
        setup_contents = f.read()

    # Search for version
    version_search = version_match.search(setup_contents)
    if version_search:
        info["version"] = version_search.group(1)

    # Search for description
    description_search = description_match.search(setup_contents)
    if description_search:
        info["description"] = description_search.group(1)

    return info

def cli():
    setup_info = get_version_and_description_from_setup()
    print(f"Audiobookslides (abs) version: {setup_info['version']}, {setup_info['description']}")
    parser = argparse.ArgumentParser(description='AudioBookSlides Command Line Tool')
    parser.add_argument('bookname', type=str, help='Name of the book')
    parser.add_argument('wildcard_path', nargs='?', default=None, help='Wildcard path to audio files')

    args = parser.parse_args()
    # Check ffmpeg availability
    if not check_ffmpeg_availability():
        sys.exit(1)

    main(args.bookname, args.wildcard_path)

if __name__ == "__main__":
    cli()
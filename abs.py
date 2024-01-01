import os
import shutil
import subprocess
import yaml
import glob
import logging

# Define constants and initialize logging
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DEBUG = 1  # Set to 1 for debug mode, 0 to disable

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

def is_file_nonempty(file_path):
    """Check if the file exists and is not empty."""
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def count_lines(filepath):
    try:
        with open(filepath, 'r') as file:
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

def create_mp3(filelist_path, mp3_file_path):
    if not os.path.exists(mp3_file_path):
        ffmpeg_cmd = f"ffmpeg -f concat -safe 0 -i {filelist_path} -c copy {mp3_file_path}"
        if run_command(ffmpeg_cmd):
            logging.info("Created: %s", mp3_file_path)
            return True
        else:
            logging.error("Failed to create MP3 file.")
            return False
    else:
        logging.info("Already exists: %s", mp3_file_path)
        return True

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

def main(bookname, wildcard_path=None):
    # Step 1: Create the folder books\<bookname> if it does not exist

    book_folder = os.path.join('books', bookname)
    if not create_directory(book_folder):
        return
    else:
        if DEBUG:
            logging.debug("Step 01/20: Audio book folder: %s",book_folder)

    # Assuming SCRIPT_PATH is defined and points to your application folder
    default_config_path = os.path.join(SCRIPT_PATH, 'default_config.yaml')
    api_key_file_path = os.path.join(SCRIPT_PATH, 'ABS_API_KEY.txt')

    # Read the OpenAI API key from ABS_API_KEY.txt
    try:
        with open(api_key_file_path, 'r') as file:
            openai_api_key = file.read().strip()
        os.environ['ABS_API_KEY'] = openai_api_key
    except Exception as e:
        logging.error("Error reading OpenAI API key file: %s", e)
        return

    # Read the default configuration
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

    # Verify yaml file is complete
    required_keys = ['whisperx_cmd', 'path_to_stablediffusion', 'path_to_comfyui']
    if not all(key in config for key in required_keys):
        logging.error("YAML file is missing some required keys.")
        return

    # The OpenAI API key is now set in the environment variable 'ABS_API_KEY'




    # Step 3: Create the MP3 file if it does not exist
    mp3_file_path = os.path.join(book_folder, f"{bookname}.mp3")

    # Check if the MP3 file already exists
    if not os.path.exists(mp3_file_path):
        # Check if wildcard_path is provided
        if wildcard_path is None:
            logging.error("Missing required wildcard path for audio file creation.")
            return

        filelist_path = os.path.join(book_folder, 'filelist.txt')
        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 03/20: Audio file %s", mp3_file_path)

        try:
            with open(filelist_path, 'w') as filelist:
                for audio_file in sorted(glob.glob(wildcard_path)):
                    corrected_path = audio_file.replace('\\', '/')
                    filelist.write(f"file '{corrected_path}'\n")
        except IOError as e:
            logging.error("Error writing to filelist: %s", e)
            return

        if not create_mp3(filelist_path, mp3_file_path):
            return
    else:
        logging.info("MP3 file already exists, skipping creation: %s", mp3_file_path)


    # Step 4: Create .srt file
    srt_file_path = os.path.join(book_folder, f"{bookname}.srt")
    if not os.path.exists(srt_file_path):

        logging.info("Creating srt: %s", srt_file_path)

        # Step 4.1: construct and optionally display the whisperx_cmd
        whisperx_cmd = config['whisperx_cmd'] + f" {mp3_file_path}"

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
        logging.info("Already exists: %s", srt_file_path)

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
        logging.info("Already exists: %s", modified_srt_file_path)

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
        logging.info("Already exists: %s", ts_srt_file_path)

    # Step 7: Create or verify prompt-enhanced SRT file with gen_prompts.py script
    ts_p_srt_file_path = os.path.join(book_folder, f"{bookname}_ts_p.srt")
    ts_srt_file_path = os.path.join(book_folder, f"{bookname}_ts.srt")

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
        logging.info("Already exists: %s", ts_p_srt_file_path)

    # Verify line count and non-emptiness
    if file_created_or_verified or is_file_nonempty(ts_p_srt_file_path):
        input_lines = count_lines(ts_srt_file_path)
        output_lines = count_lines(ts_p_srt_file_path)
        if input_lines == output_lines:
            logging.info("Verified prompt-enhanced srt with correct line count: %s", ts_p_srt_file_path)
        else:
            logging.error("Line count mismatch or empty file in prompt-enhanced SRT file: %s", ts_p_srt_file_path)
            os.remove(ts_p_srt_file_path)  # Delete the empty or incorrect file
            if file_needs_creation:
                logging.info("Attempting to recreate prompt-enhanced SRT file.")
                file_created_or_verified = execute_gen_prompts()
                if not file_created_or_verified:
                    return
            else:
                return
    else:
        logging.error("File creation failed or file is empty: %s", ts_p_srt_file_path)
        return


    '''  This was not very effective.  Use a different GPT method.

    # Step 8: Match dictionary and create a new file with match_dictionary.py script.
    m300_nodict_file_path = os.path.join(book_folder, f"{bookname}_m300_nodict.txt")
    m300_srt_file_path = os.path.join(book_folder, f"{bookname}_m300.srt")
    tokenizer_vocab_file = "tokenizer_vocab_2.txt"  # Assuming this file is in the current directory

    if not os.path.exists(m300_nodict_file_path):
        logging.info("Creating file with matched dictionary: %s", m300_nodict_file_path)

        # Construct the match_dictionary.py command
        match_dictionary_cmd = f"python match_dictionary.py {tokenizer_vocab_file} {m300_srt_file_path} {m300_nodict_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("match_dictionary.py command: %s", match_dictionary_cmd)

        try:
            result = subprocess.run(match_dictionary_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Created file with matched dictionary: %s", m300_nodict_file_path)
            else:
                logging.error("Failed to create file with matched dictionary: %s", m300_nodict_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Already exists: %s", m300_nodict_file_path)

    '''
    # Step 9: Create a new file with make_API_Names.py script
    ts_srt_api_names_file_path = os.path.join(book_folder, f"{bookname}_ts_API_Names.srt")
    ts_srt_file_path = os.path.join(book_folder, f"{bookname}_ts.srt")

    if not os.path.exists(ts_srt_api_names_file_path):
        logging.info("Creating file with API Names: %s", ts_srt_api_names_file_path)


        # Construct the make_API_Names.py command
        make_api_names_cmd = f"python make_API_Names.py {ts_srt_file_path} {ts_srt_api_names_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 09/20: Format .srt file for use in GPT API calls: %s", make_api_names_cmd)

        try:
            result = subprocess.run(make_api_names_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Created file with API Names: %s", ts_srt_api_names_file_path)
            else:
                logging.error("Failed to create file with API Names: %s", ts_srt_api_names_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Already exists: %s", ts_srt_api_names_file_path)

    ''' Bad API name extractor. Skip it. Enable the one from Step 8

    # Step 10: GPT API calls. Extract names with extract_names.py script. This output file requires manual edit. Try to eliminate it.
    # There is a better version that assigns [name] {age} <gender>. Delete this after that one is integrated.
    # This also needs to pass api_base from yaml file to work with LM-Studio
    ts_srt_api_names_file_path = os.path.join(book_folder, f"{bookname}_ts_API_Names.srt")
    ts_srt_api_names_out_file_path = os.path.join(book_folder, f"{bookname}_ts_API_Names_out.srt")

    if not os.path.exists(ts_srt_api_names_out_file_path):
        logging.info("Extracting names: %s", ts_srt_api_names_out_file_path)

        # Construct the extract_names.py command
        extract_names_cmd = f"python extract_names.py {ts_srt_api_names_file_path} {ts_srt_api_names_out_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("extract_names.py command: %s", extract_names_cmd)

        try:
            result = subprocess.run(extract_names_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Extracted names to: %s", ts_srt_api_names_out_file_path)
            else:
                logging.error("Failed to extract names: %s", ts_srt_api_names_out_file_path)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("Already exists: %s", ts_srt_api_names_out_file_path)

    '''

    # Step 11: Get characters with get_characters.py script
    ts_srt_p_file_path = os.path.join(book_folder, f"{bookname}_ts_p.srt")
    ts_srt_p_characters_file_path = os.path.join(book_folder, f"{bookname}_ts_p_characters.srt")

    if not os.path.exists(ts_srt_p_characters_file_path):
        logging.info("Getting characters: %s", ts_srt_p_characters_file_path)

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
        logging.info("Already exists: %s", ts_srt_p_characters_file_path)

   # Step 12: Extract scenes with extract_scene.py script
    ts_srt_file_path = os.path.join(book_folder, f"{bookname}_ts.srt")
    ts_srt_p_ns_file_path = os.path.join(book_folder, f"{bookname}_ts_p_ns.srt")

    if not os.path.exists(ts_srt_p_ns_file_path):
        logging.info("Extracting scenes: %s", ts_srt_p_ns_file_path)

        # Construct the extract_scene.py command
        extract_scene_cmd = f"python extract_scene.py {ts_srt_file_path} {ts_srt_p_ns_file_path}"

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 12/20: Use GPT API to generate scene information: %s", extract_scene_cmd)

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
        logging.info("Already exists: %s", ts_srt_p_ns_file_path)

    # Verify line count
    input_lines = count_lines(ts_srt_file_path)
    output_lines = count_lines(ts_srt_p_ns_file_path)
    if input_lines == output_lines:
        logging.info("Verified output file with correct line count: %s", ts_srt_p_ns_file_path)
    else:
        logging.error("Line count mismatch in output file: %s", ts_srt_p_ns_file_path)
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
        logging.info("Already exists: %s", output_file)

    # Step 14: Replace actors using the existing script
    input_file = f"books/{bookname}/{bookname}_ts_p_characters.srt"
    output_file = f"books/{bookname}/{bookname}_ts_p_actors_EDIT.txt"
    male_actors_csv = config.get('actors', "actors\\male.csv")  # Default if not specified
    female_actors_csv = config.get('actresses', "actors\\female.csv")  # Default if not specified
    depth = config.get('depth', 4)  # Default depth to 4 if not specified in config

    if not os.path.exists(output_file):
        logging.info("Step 14/20: Generating editable character and actor list from %s and saving to %s", input_file, output_file)

        try:
            # Execute the existing replace_actors.py script with depth parameter
            replace_actors_cmd = f"python replace_actors.py {input_file} {male_actors_csv} {female_actors_csv} {output_file} {depth}"

            # Log the command if debugging is enabled
            if DEBUG:
                logging.debug("Step 14/20: Combining characters with actors: %s", replace_actors_cmd)

            result = subprocess.run(replace_actors_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("****** Actors replaced and saved to: %s You must review this file,make any corrections and save as %s", output_file, f"books/{bookname}/{bookname}_ts_p_actors.txt")
            else:
                logging.error("Failed to replace actors: %s", output_file)
                return
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
            return
    else:
        logging.info("****** Already exists: %s. You must review this file, make any corrections and save as %s", output_file, f"books/{bookname}/{bookname}_ts_p_actors.txt")

    # Step 15: Apply actors using the apply_actors.py script
    input_file = f"books/{bookname}/{bookname}_ts_p_actors.txt"
    merged_file = f"books/{bookname}/{bookname}_merged.txt"
    output_file = f"books/{bookname}/{bookname}_merged_names.txt"

    # Check if input_file exists
    if not os.path.exists(input_file):
        logging.error("You must optionally edit, then save %s as %s before proceeding.", f"books/{bookname}/{bookname}_ts_p_actors_EDIT.txt", input_file)
        return  # Stop processing or skip to the next step

    if not os.path.exists(output_file):
        logging.info("Applying actors to %s and saving to %s. Note: When choosing actors, you must take care their names are not the same as existing character names to avoid confusion.", input_file, output_file)

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
        logging.info("Already exists: %s", output_file)

    # Step 16: Verify the existence of <path_to_comfyui> from config YAML
    path_to_comfyui = config.get('path_to_comfyui')
    if os.path.exists(path_to_comfyui):
        logging.info("Output folder already exists: %s", path_to_comfyui)
    else:
        comfyui_model = config.get('comfyui_model')
        cfg = config.get('cfg')
        steps = config.get('steps')
        image_count = config.get('image_count')
        image_width = config.get('image_width')
        image_height = config.get('image_height')
        workflow_path = config.get('path_to_workflow')

        input_file = f"books/{bookname}/{bookname}_merged_names.txt"

        logging.info("Generating images using ComfyUI")
        try:
            run_comfy_cmd = (
                f"python run_comfy_wf_api.py "
                f"--ckpt_name \"{comfyui_model}\" "
                f"--cfg {cfg} "
                f"--steps {steps} "
                f"--count {image_count} "
                f"--width {image_width} "
                f"--height {image_height} "
                f"{input_file} "
                f"{workflow_path}"
            )

            # Log the command if debugging is enabled
            if DEBUG:
                logging.debug("Step 16/20: Launch ComfyUI. Support for A1111 exists but is not fully automated. See config .yaml file: %s", run_comfy_cmd)

            # Display the prompt before processing
            input("Ready for image generation. Start the ComfyUI application. Delete the contents of ComfyUI\output before proceeding.\nNo need to launch browser GUI, it just slows image generation down, but you can view the Queue progress with it.\nPress <enter> when ready:")

            result = subprocess.run(run_comfy_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Images generated successfully")
            else:
                logging.error("Failed to generate images")
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)

    # Step 17: Verify the existence of <path_to_comfyui> after image generation
    if not os.path.exists(path_to_comfyui):
        # Count the lines in the input file again to get the image count
        generated_image_count = count_lines(input_file)
        if generated_image_count >= 0:
            logging.error("If there were no errors, you should see %d images appear in the ComfyUI\\output folder. When they are finished, delete any images you do not want,\nthen rename ComfyUI\\output to ComfyUI\\%s. Output folder does not exist: %s", generated_image_count, bookname, path_to_comfyui)
        else:
            logging.error("Failed to count submitted image generation prompts.")
        return

    # Step 18: Run make_tEXt.py and rename_png_files.py scripts
    path_to_comfyui = config.get('path_to_comfyui', '')  # Assuming 'path_to_comfyui' is a key in the config YAML

    if not path_to_comfyui:
        logging.error("Missing 'path_to_comfyui' in the config YAML. Exiting.")
        return

    # Check if 'path_to_comfyui' exists as a folder
    if not os.path.exists(path_to_comfyui):
        logging.error("Folder '%s' does not exist. Exiting.", path_to_comfyui)
        return

    # Define the command to run make_tEXt.py
    # removed -o (overwrite) flag. Not sure why it was enabled.  Allows for faster restarts
    make_text_cmd = f"python make_tEXt.py {path_to_comfyui}"

    # Define the command to run rename_png_files.py
    rename_png_cmd = f"python rename_png_files.py {path_to_comfyui}"

    # Log the commands if debugging is enabled
    if DEBUG:
        logging.debug("Step 18/20: Extract metadata from PNG files and save as .txt: %s", make_text_cmd)
        logging.debug("rename_png_files.py command: %s", rename_png_cmd)

    try:
        # Execute the make_tEXt.py command
        result = subprocess.run(make_text_cmd, shell=True, check=True)
        logging.info("make_tEXt.py completed successfully.")

        if DEBUG:
            logging.debug("Step 18/20 Read .txt files and rename PNG files to the .srt timestamp enbeded in the prompt. {ts=001234125} = HH:MM:SS,mms or 00 Houurs, 12 minutes, 34.123 seconds: %s", rename_png_cmd)
        # Execute the rename_png_files.py command
        result = subprocess.run(rename_png_cmd, shell=True, check=True)
        logging.info("rename_png_files.py completed successfully.")

        path_to_comfyui = path_to_comfyui.replace("<bookname>", bookname)  # Replace placeholder
        txt_files = glob.glob(os.path.join(path_to_comfyui, "*.tEXt.txt"))
        for file_path in txt_files:
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e)

    # Step 19: Create an output video if it doesn't exist
    output_video_path = os.path.join(book_folder, f"{bookname}_output.avi")

    if not os.path.exists(output_video_path):
        logging.info("Creating output video: %s", output_video_path)

        # Construct the jobvid.py command
        jobvid_cmd = f"python jobvid.py \"{os.path.join(path_to_comfyui, '*.png')}\" \"{output_video_path}\""

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 19/20: This spawns 30 parallel ffmpeg processes to generate a ~30 second (time based on the file name) still image .AVI video from each image, then combines them: %s", jobvid_cmd)

        try:
            result = subprocess.run(jobvid_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info("Output video created: %s", output_video_path)
            else:
                logging.error("Failed to create output video: %s", output_video_path)
        except subprocess.CalledProcessError as e:
            logging.error("Command failed: %s", e)
    else:
        logging.info("Output video already exists: %s", output_video_path)

    # Step 20: Create the final video if it doesn't already exist
    output_avi_path = os.path.join(book_folder, f"{bookname}.avi")

    if not os.path.exists(output_avi_path):
        logging.info("Creating the final video: %s", output_avi_path)

        # Define the FFmpeg command
        ffmpeg_cmd = (
            f"ffmpeg -i books/{bookname}/{bookname}_output.avi "
            f"-i books/{bookname}/{bookname}.mp3 "
            f"-c:v copy -map 0:v:0 -map 1:a:0 {output_avi_path}"
        )

        # Log the command if debugging is enabled
        if DEBUG:
            logging.debug("Step 20/20: This combines the original mp3 audio book and the generated video. .srt is included in the same folder. You could embed it in the video if you wanted to: %s", ffmpeg_cmd)

        try:
            result = subprocess.run(ffmpeg_cmd, shell=True, check=True)
            if result.returncode == 0:
                logging.info(f"{output_avi_path} and books/{bookname}/{bookname}.srt files created. Process complete.")
            else:
                logging.error("Failed to create the final video.")
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logging.error("Usage: python script.py <bookname> [<wildcard_path_to_audio_files>]")
        sys.exit(1)

    bookname = sys.argv[1]
    wildcard_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Check ffmpeg availability
    if not check_ffmpeg_availability():
        sys.exit(1)

    main(bookname, wildcard_path)
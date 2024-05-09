import json
import argparse
import sys
import random
from urllib import request, parse
import re
import os
import yaml

DEBUG = True  # Set to False to disable debug print statements
DEBUG2 = True  # Set to False to disable debug print statements

def replace_tabs_with_space(text):
    return re.sub(r'\t+', ' ', text)

def load_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def get_style_and_key_from_config(config, target):
    for key, value in config.items():
        if value.get("class_type") == "CLIPTextEncode" and target in value["inputs"]["text"]:
            return value["inputs"]["text"], key
    return "", None

def update_empty_latent_image(config, width, height):
    for key, value in config.items():
        if value.get("class_type") == "EmptyLatentImage":
            value["inputs"]["width"] = width
            value["inputs"]["height"] = height

def update_config(config, args, pos_style, neg_style, line_number, pos_key, neg_key):
    for key, value in config.items():
        if isinstance(value, dict):
            inputs = value.get("inputs", {})
            for input_key in inputs.keys():
                if input_key == "filename_prefix":
                    base_name = args.filename_prefix if args.filename_prefix else args.ckpt_name.split('.')[0]
                    line_num_str = f"{line_number:04d}"
                    inputs[input_key] = f"{base_name}_{args.cfg}.{args.steps}.[{line_num_str}]"
                elif input_key in vars(args) and getattr(args, input_key) is not None:
                    inputs[input_key] = getattr(args, input_key)

def queue_prompt(prompt):
    wrapped_payload = {"prompt": prompt}
    json_data = json.dumps(wrapped_payload)
    encoded_data = json_data.encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = request.Request("http://127.0.0.1:8188/prompt", data=encoded_data, headers=headers)
    try:
        response = request.urlopen(req)
        print("Response:", response.read().decode())
    except Exception as e:
        print("Error:", e)

def get_lines(file, count):
    lines = file.readlines()
    if count is None or count == 0:
        for line in lines:
            yield line.strip()
    else:
        for i in range(count):
            yield lines[i % len(lines)].strip()

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

def load_and_process_config(SCRIPT_PATH, bookname):
    default_config_path = os.path.join(SCRIPT_PATH, 'default_config.yaml')
    config = {}

    try:
        with open(default_config_path, 'r') as file:
            default_config = yaml.safe_load(file)
        config = default_config
        if DEBUG:
            print("Loaded default config.")
    except Exception as e:
        if DEBUG:
            print("Warning: Error reading default YAML file. Proceeding with an empty configuration.")

    if DEBUG2:
        print("Default config Pos:", config.get("Pos"))

    if bookname:
        book_config_path = os.path.join(SCRIPT_PATH, 'books', bookname, f"{bookname}.yaml")

        if os.path.exists(book_config_path):
            try:
                with open(book_config_path, 'r') as file:
                    book_config = yaml.safe_load(file)
                config.update(book_config)
                if DEBUG2:
                    print(f"Loaded book-specific config from {book_config_path}.")
            except Exception as e:
                if DEBUG2:
                    print(f"Warning: Error reading book-specific YAML file: {e}. Proceeding with available configuration.")
        else:
            if DEBUG2:
                print(f"Book-specific config file not found at {book_config_path}. Using default config.")

    if DEBUG2:
        print("Merged config Pos:", config.get("Pos"))

    return replace_bookname_recursive(config, bookname) if bookname else config



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update workflow configuration.')
    parser.add_argument('--ckpt_name', type=str, help='Model checkpoint name')
    parser.add_argument('--cfg', type=float, default=1, help='CFG parameter value')
    parser.add_argument('--steps', type=int, default=4, help='Steps parameter value')
    parser.add_argument('--filename_prefix', type=str, help='Filename prefix for saving images')
    parser.add_argument('--sampler_name', type=str, default='euler', help='Sampler name')
    parser.add_argument('--count', type=int, help='Number of lines to process from the input file')
    parser.add_argument('--width', type=int, default=768, help='Width for EmptyLatentImage')
    parser.add_argument('--height', type=int, default=512, help='Height for EmptyLatentImage')
    parser.add_argument('prompts_file', type=str, help='File containing text prompts')
    parser.add_argument('config_file', type=str, help='Workflow configuration JSON file')
    parser.add_argument('--bookname', type=str, default="", help='BookName (optional)')
    args = parser.parse_args()

    SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
    config = load_and_process_config(SCRIPT_PATH, args.bookname)

    prompt_config = load_json_file(args.config_file)
    pos_style, pos_key = get_style_and_key_from_config(prompt_config, "Pos:")
    neg_style, neg_key = get_style_and_key_from_config(prompt_config, "Neg:")

    # Save default prompts from the workflow
    default_pos_prompt = prompt_config.get(pos_key, {}).get("inputs", {}).get("text", "")
    default_neg_prompt = prompt_config.get(neg_key, {}).get("inputs", {}).get("text", "")

    # Update the negative prompt once, using config value or default
    final_neg_prompt = config.get("Neg", default_neg_prompt)
    if neg_key:
        prompt_config[neg_key]["inputs"]["text"] = final_neg_prompt

    # Update EmptyLatentImage node
    update_empty_latent_image(prompt_config, args.width, args.height)

    # Process each line from the input file for the positive prompt
    line_number = 1
    with open(args.prompts_file, 'r', encoding='utf-8-sig') as file:
        for text_prompt in get_lines(file, args.count):
            if text_prompt:
                text_prompt = replace_tabs_with_space(text_prompt)

                # Determine the positive prompt to use (config or default)
                final_pos_prompt = config.get("Pos", default_pos_prompt)

                # Update positive prompt in workflow configuration
                if pos_key:
                    updated_text = text_prompt + " " + final_pos_prompt
                    prompt_config[pos_key]["inputs"]["text"] = updated_text

                update_config(prompt_config, args, final_pos_prompt, final_neg_prompt, line_number, pos_key, neg_key)

                for key, value in prompt_config.items():
                    if value.get("class_type") == "SamplerCustom":
                        value["inputs"]["noise_seed"] = random.randint(0, 1000000)
                    if value.get("class_type") == "KSampler":
                        value["inputs"]["seed"] = random.randint(0, 1000000)

                queue_prompt(prompt_config)
                line_number += 1
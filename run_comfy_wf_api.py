import json
import argparse
import sys
import random
from urllib import request, parse
import re

def replace_tabs_with_space(text):
    return re.sub(r'\t+', ' ', text)

def load_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def get_style_and_key_from_config(config):
    for key, value in config.items():
        if value.get("class_type") == "CLIPTextEncode" and "Pos:" in value["inputs"]["text"]:
            return value["inputs"]["text"], key
    return "", None  # Return an empty string and None if no style is found

def update_empty_latent_image(config, width, height):
    for key, value in config.items():
        if value.get("class_type") == "EmptyLatentImage":
            value["inputs"]["width"] = width
            value["inputs"]["height"] = height

def update_config(config, args, style, line_number, pos_key):
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

    # Only update the 'Pos:' prompt in the correct node
    if pos_key and pos_key in config:
        config[pos_key]["inputs"]["text"] = style

def queue_prompt(prompt):
    wrapped_payload = {"prompt": prompt}
    json_data = json.dumps(wrapped_payload)
    encoded_data = json_data.encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    #print(encoded_data)
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
    args = parser.parse_args()

    prompt_config = load_json_file(args.config_file)
    style, pos_key = get_style_and_key_from_config(prompt_config)

    # Update EmptyLatentImage node
    update_empty_latent_image(prompt_config, args.width, args.height)

    line_number = 1
    with open(args.prompts_file, 'r') as file:
        for text_prompt in get_lines(file, args.count):
            if text_prompt:
                text_prompt = replace_tabs_with_space(text_prompt)

                # Append style only to the specific 'Pos:' prompt node
                if pos_key and pos_key in prompt_config:
                    updated_style = text_prompt + " " + style
                    update_config(prompt_config, args, updated_style, line_number, pos_key)

                for key, value in prompt_config.items():
                    if value.get("class_type") == "SamplerCustom":
                        value["inputs"]["noise_seed"] = random.randint(0, 1000000)
                    if value.get("class_type") == "KSampler":
                        value["inputs"]["seed"] = random.randint(0, 1000000)

                queue_prompt(prompt_config)
                line_number += 1

import re
import glob
import sys
import os
import yaml
import argparse

DEBUG = True  # Ensure DEBUG is True to activate debug outputs
DEBUG2 = False # Ensure DEBUG is True to activate debug outputs

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
    if DEBUG2:
        print(f"Loading configuration for bookname: {bookname}")
    default_config_path = os.path.join(SCRIPT_PATH, 'default_config.yaml')
    config = {}

    try:
        with open(default_config_path, 'r') as file:
            default_config = yaml.safe_load(file)
        config = default_config
        if DEBUG2:
            print("Loaded default config.")
    except Exception as e:
        if DEBUG2:
            print(f"Warning: Error reading default YAML file. Proceeding with an empty configuration. Error: {e}")

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
                if DEBUG:
                    print(f"Warning: Error reading book-specific YAML file: {e}. Proceeding with available configuration.")

    if DEBUG2:
        print("Merged config pos_prompt:", config.get("pos_prompt"))

    return replace_bookname_recursive(config, bookname) if bookname else config

def process_files(file_pattern, output_file_path, log_file_path, config):  # Added config parameter
    if DEBUG2:
        print(f"Processing files with pattern {file_pattern}")
    try:
        with open(log_file_path, 'w') as log_file, open(output_file_path, 'w', encoding='cp1252') as output_file:
            for filename in glob.glob(file_pattern):
                if DEBUG2:
                    print(f"Opening file {filename} for processing")
                remove_duplicate_patterns(filename, log_file, output_file, config)  # Pass config to the function
    except Exception as e:
        print(f"Failed to process files: {e}")

def remove_duplicate_patterns(filename, log_file, output_file, config):
    import re
    pattern = re.compile(r'(_[^@]*@)')
    line_number = 0
    keep_actors = int(config.get('keep_actors', 0))  # Default to 0 if not specified
    actor_priority = config.get('actor_priority', '').split(', ') if config.get('actor_priority') else None

    with open(filename, 'r') as file:
        for line in file:
            line_number += 1
            found = pattern.findall(line)
            seen = set()
            found_unique = [x for x in found if not (x in seen or seen.add(x))]

            if actor_priority:
                sorted_found = sorted(found_unique, key=lambda x: next((actor_priority.index(actor) for actor in actor_priority if actor in x), float('inf')))
            else:
                sorted_found = found_unique

            if keep_actors > 0:
                matches_to_keep = sorted_found[:keep_actors]
            else:
                matches_to_keep = sorted_found

            removed_matches = set(found) - set(matches_to_keep)

            # Remove all matches to ensure a clean slate
            for match in found:
                line = line.replace(match, '')

            # Reinsert matches to keep with a space after the trailing @, in the correct priority order
            for match in reversed(matches_to_keep):
                line = match + " " + line

            # Log removed matches with the specified format
            match_count = 0
            for match in removed_matches:
                match_count += 1
                log_entry = f"[{line_number:05}.{match_count:02}] {match}\n"
                log_file.write(log_entry)

            output_file.write(line)


def main():
    if DEBUG2:
        print("Script started")  # Immediate feedback when the script runs
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument('file_pattern', type=str, help='The pattern for files to process')
    parser.add_argument('output_file', type=str, help='Path to the output file')
    parser.add_argument('--bookname', type=str, help='Optional book name for configuration', default='')
    args = parser.parse_args()

    if DEBUG2:
        print(f"Arguments parsed: File pattern={args.file_pattern}, Output file={args.output_file}, Bookname={args.bookname}")

    SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
    if DEBUG2:
        print(f"Script path: {SCRIPT_PATH}")

    config = load_and_process_config(SCRIPT_PATH, args.bookname)
    if DEBUG2:
        print(f"Configuration loaded: {config}")

    log_file_path = os.path.join(SCRIPT_PATH, 'books', args.bookname, 'remove.log')
    # Corrected call to process_files with the config argument
    process_files(args.file_pattern, args.output_file, log_file_path, config)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception: {e}")

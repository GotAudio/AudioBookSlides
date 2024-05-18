import sys
import openai
import csv
import re
import os
from joblib import Parallel, delayed
import time

def generate_response(prompt, api_key):
    openai.api_key = api_key
    max_retries = 5
    retry_delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct-0914",
                prompt=prompt,
                temperature=0,
                max_tokens=250
            )
            return response.choices[0].text.strip()
        except openai.error.RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                #retry_delay *= 2  # exponential backoff
            else:
                raise e

def generate_response(prompt, api_key):
    openai.api_key = api_key
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=prompt,
        temperature=0,
        max_tokens=250
    )
    return response.choices[0].text.strip()

def process_line(line, idx, total, api_key, default_scene):
    timestamp_match = re.search(r"({ts=\d+})", line)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
        user_query = line.replace(timestamp, "").strip().replace("\n", "\\n")

        if not api_key:
            # Simply return the original script line without extra formatting
            response = user_query
        else:
            system_message = (
                "You are a set designer. I will provide sentences from a film script. Your task is to create concise set designs for each line. Aim for succinct descriptions that capture the essence of the physical environment, focusing on key elements such as furniture, decor, and lighting. Align designs with the script context. Avoid Character Actions, emotions, and dialog. If the script line doesn't provide enough information for a new scene, use or modify the default scene.\n\n"
                + default_scene + "\n\n" + user_query
            )
            prompt = f"{system_message}"
            response = generate_response(prompt, api_key)

            # Update default scene if new scene is described.
            if "Default Scene=" not in response:
                default_scene = f"[Default Scene={response.split('.')[0]}]"

        result_line = [timestamp, response.replace('\n', ' ').replace('""', '"') if api_key else user_query]

        # Only update progress bar if api_key is provided
        if api_key:
            # Calculate the interval for updating the progress bar
            update_interval = max(1, total // 100)
            # Update progress bar only at specified intervals
            if idx % update_interval == 0 or idx == total - 1:
                sys.stdout.write('.')
                sys.stdout.flush()

        return result_line

    return None


def main(input_file, output_file, api_key):
    with open(input_file, "r", newline="", encoding="utf-8-sig") as infile:
        lines = infile.readlines()

    total_lines = len(lines)

    default_scene = "[((Default View=A warm intimate recording studio with state-of-the-art equipment, soundproofing panels, large clear windows, a cozy narrator's booth bathed in soft light.))]"
    results = []

    if api_key:
        # Use parallel processing when API key is available
        sys.stdout.write('[' + ' ' * 100 + ']\r[')  # Initialize progress bar for parallel processing
        results = Parallel(n_jobs=5)(delayed(process_line)(line, idx, total_lines, api_key, "") for idx, line in enumerate(lines))
        sys.stdout.write('\n')  # Move to the next line after progress bar completion
    else:
        # Process lines sequentially without API key
        for idx, line in enumerate(lines):
            result = process_line(line, idx, total_lines, api_key, "")
            if result:
                results.append(result)

    # Initialize default scene for the first image description
    if results:
        results[0] = (results[0][0], default_scene + results[0][1])

    # Write results to the output file
    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter="\t", quoting=csv.QUOTE_ALL)
        for result_line in results:
            if result_line:
                corrected_result_line = [element.replace('\t', '') for element in result_line]
                writer.writerow(corrected_result_line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_scene.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    api_key = os.environ.get('ABS_API_KEY')
    if not api_key:
        print("OpenAI API key not found in ABS_API_KEY environment variable. GPT will not be used for scene extraction.")
    else:
        print("OpenAI API key found in ABS_API_KEY environment variable. Using GPT for scene extraction.")

    main(input_file, output_file, api_key)

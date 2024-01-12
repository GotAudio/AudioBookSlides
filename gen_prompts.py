import sys
import openai
import csv
import re
import os
from joblib import Parallel, delayed

def generate_response(prompt, api_key):
    openai.api_key = api_key
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=prompt,
        temperature=0,
        max_tokens=250
    )
    return response.choices[0].text.strip()

def process_line(line, idx, total, api_key):
    timestamp_match = re.search(r"({ts=\d+})", line)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
        user_query = line.replace(timestamp, "").strip().replace("\n", "\\n")

        system_message = "You are a character and costume designer. Provide a response in this format [proper name], {gender}, (age), <clothing>, physical activity. Ignore any quoted dialog."
        prompt = f"{system_message}\n\n{user_query}"

        response = generate_response(prompt, api_key)
        result_line = [timestamp, response.replace('\n', ' ')]

        # Calculate the interval for updating the progress bar
        update_interval = max(1, total // 100)

        # Update progress bar only at specified intervals
        if idx % update_interval == 0 or idx == total - 1:
            sys.stdout.write('.')
            sys.stdout.flush()

        return result_line

    return None

def main(input_file, output_file, num_jobs, api_key):
    with open(input_file, "r", newline="", encoding="utf-8-sig") as infile:
        lines = infile.readlines()

    total_lines = len(lines)
    sys.stdout.write('[' + ' ' * 100 + ']\r[')
    sys.stdout.flush()

    results = Parallel(n_jobs=num_jobs)(delayed(process_line)(line, idx, total_lines, api_key) for idx, line in enumerate(lines))

    sys.stdout.write('\n')  # Move to the next line after progress bar completion

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter="\t", quoting=csv.QUOTE_ALL)
        for result_line in results:
            if result_line:
                writer.writerow(result_line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gen_prompts.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    num_jobs = 10  # Number of parallel jobs, adjust as needed

    api_key = os.environ.get('ABS_API_KEY')
    if not api_key:
        print("OpenAI API key not found in environment variables.")
        sys.exit(1)

    main(input_file, output_file, num_jobs, api_key)

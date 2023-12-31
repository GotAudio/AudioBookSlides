import sys
import openai
import csv
import re
from tqdm import tqdm

# Check if the correct number of arguments are passed; if not, print usage and exit
if len(sys.argv) != 3:
    print("Usage: python gen_prompts.py <input_file> <output_file>")
    sys.exit(1)

# Set your OpenAI API key
openai.api_key = "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"

# Assign command line arguments to input and output file variables
input_file = sys.argv[1]
output_file = sys.argv[2]

# Initialize default scene
default_scene = "[Default Scene=A warm, intimate recording studio with state-of-the-art equipment, soundproofing panels, and a cozy narrator's booth bathed in soft light.] "

# Set the number of rows to process (50 for testing, 0 for no limit)
COUNT = 0

# Function to generate a response using v1 completions endpoint
def generate_response(prompt):
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=prompt,
        temperature=0,
        max_tokens=250,
    )
    return response.choices[0].text.strip()

# Open input and output files
with open(input_file, "r", newline="", encoding="utf-8-sig") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    # Create CSV writer for output
    writer = csv.writer(outfile, delimiter="\t", quoting=csv.QUOTE_ALL)

    # Initialize progress bar and row counter
    total_lines = sum(1 for line in infile)
    infile.seek(0)  # Reset file pointer to beginning of file
    processed_lines = 0
    pbar = tqdm(total=min(total_lines, COUNT) if COUNT else total_lines, desc="Processing", unit="line")

    # Iterate through the queries in queries.csv
    for line in infile:
        if COUNT and processed_lines >= COUNT:
            break

        # Extract the timestamp using regular expression
        timestamp_match = re.search(r"({ts=\d+})", line)
        if timestamp_match:
            timestamp = timestamp_match.group(1)
            user_query = line.replace(timestamp_match.group(1), "").strip().replace("\n", "\\n")

            # Construct system message
            system_message = (
                "You are a set designer. I will provide sentences from a film script. Your task is to create concise set designs for each line. Aim for succinct descriptions that capture the essence of the physical environment, focusing on key elements such as furniture, decor, and lighting. Align designs with the script context. Avoid Character Actions, emotions, and dialog. If the script line doesn't provide enough information for a new scene, use or modify the default scene.\n\n"
                + default_scene + "\n\n" + user_query
            )
            prompt = f"{system_message}"

            # Get the response from the chatbot
            response = generate_response(prompt)

            # Update default scene if new scene is described
            if "Default Scene=" not in response:
                default_scene = f"[Default Scene={response.split('.')[0]}]"

            # Concatenate the timestamp and response into a single line
            result_line = [timestamp, response.replace('\n', ' ')]

            # Write the result line to results.csv
            writer.writerow(result_line)

            processed_lines += 1

        pbar.update(1)  # Update progress bar

    pbar.close()  # Close progress bar

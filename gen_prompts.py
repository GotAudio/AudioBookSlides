import sys
import openai
import csv
import re
import os
from tqdm import tqdm

# Check if the correct number of arguments are passed; if not, print usage and exit
if len(sys.argv) != 3:
    print("Usage: python gen_prompts.py <input_file> <output_file>")
    sys.exit(1)

# Retrieve the OpenAI API key from the environment variable
api_key = os.environ.get('ABS_API_KEY')
if not api_key:
    print("OpenAI API key not found in environment variables.")
    sys.exit(1)

openai.api_key = api_key

# Assign command line arguments to input and output file variables
input_file = sys.argv[1]
output_file = sys.argv[2]

# Set the number of lines to process (0 for all rows)
COUNT = 0

# Function to generate a response using v1 completions endpoint
def generate_response(prompt):
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",  # You can change this to your preferred model
        prompt=prompt,
        temperature=0,
        max_tokens=250,  # You can adjust this value according to your needs
    )
    return response.choices[0].text.strip()

# Open input and output files
with open(input_file, "r", newline="", encoding="utf-8-sig") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    # Create CSV writer for output
    writer = csv.writer(outfile, delimiter="\t", quoting=csv.QUOTE_ALL)

    # Initialize progress bar
    lines_processed = 0
    total_lines = sum(1 for line in infile)
    infile.seek(0)  # Reset file pointer to beginning of file
    pbar = tqdm(total=min(COUNT, total_lines) if COUNT else total_lines, desc="Processing", unit="line")

    # Iterate through the queries in queries.csv
    for line in infile:
        if COUNT and lines_processed >= COUNT:
            break

        # Extract the timestamp using regular expression
        timestamp_match = re.search(r"({ts=\d+})", line)
        if timestamp_match:
            timestamp = timestamp_match.group(1)
            user_query = line.replace(timestamp_match.group(1), "").strip().replace("\n", "\\n")

            system_message = "You are a character and costume designer. For each character in the following script, provide a response in this format [proper name], {gender}, (age), <clothing>, physical activity. Ignore any quoted dialog. ' "
            prompt = f"{system_message}\n\n{user_query}"

            # Get the response from the chatbot
            response = generate_response(prompt)

            # Concatenate the timestamp and response into a single line
            result_line = [timestamp, response.replace('\n', ' ')]

            # Write the result line to results.csv
            writer.writerow(result_line)

            lines_processed += 1

        pbar.update(1)  # Update progress bar

    pbar.close()  # Close progress bar

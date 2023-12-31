import sys
import openai
import csv
import re
import os
from tqdm import tqdm

# Function to generate a response using the gpt-3.5-turbo-instruct-0914 model
def generate_response(text, api_base, max_tokens=2000):
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=text,
        temperature=0,
        max_tokens=max_tokens
    )
    return response.choices[0].text.strip()

# Function to filter the output
def filter_output(raw_file, filtered_file):
    with open(raw_file, 'r', encoding='utf-8') as infile, open(filtered_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Check if line contains 'Male' or 'Female' and does not contain the placeholder pattern
            if ('Male' in line or 'Female' in line) and 'Male|Female' not in line:
                outfile.write(line)

# Check if the correct number of arguments are passed; if not, print usage and exit
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("Usage: python extract_names.py <input_file> <output_file> [api_base]")
    sys.exit(1)

# Set your OpenAI API key from environment variable
api_key = os.environ.get('ABS_API_KEY')
if not api_key:
    print("OpenAI API key not found in environment variables.")
    sys.exit(1)

openai.api_key = api_key

# Set the default value for api_base
api_base = ""

# Check if the optional api_base parameter is provided
if len(sys.argv) == 4:
    api_base = sys.argv[3]

# Set the api_base if it's provided and not blank
if api_base.strip() != "":
    openai.api_base = api_base

# Assign command-line arguments to input and output file variables
input_file = sys.argv[1]
output_file = sys.argv[2]
raw_output_file = output_file + "_raw"  # Name for the raw output file

with open(input_file, "r", newline="", encoding="utf-8-sig") as infile, open(raw_output_file, "w", newline="", encoding="utf-8") as raw_outfile:
    writer = csv.writer(raw_outfile, delimiter="\t", quoting=csv.QUOTE_ALL)

    # Get total number of lines in infile and initialize progress bar
    total_lines = sum(1 for line in infile)
    infile.seek(0)  # Reset file pointer to beginning of file
    pbar = tqdm(total=total_lines, desc="Processing", unit="line")

    max_sentences_per_request = 12
    sentences = []
    line_count = 0

    for line in infile:
        sentence = line.strip()
        sentences.append(sentence)
        line_count += 1

        if len(sentences) >= max_sentences_per_request or line_count % 100 == 0:
            text_block = ' '.join(sentences)
            max_tokens = 270 if api_base.strip() != "" else 2000
            prompt = "You are a Chatbot. I will provide sentences from a book. Your task is to return the names of every male or female character as they are written in the text. Return names in the format: [Name] (Male or Female) {Adult or Child or Unknown} \n\n" + text_block
            response = generate_response(prompt, api_base, max_tokens)
            writer.writerow([response])
            sentences = []
            pbar.update(min(max_sentences_per_request, line_count))

    if sentences:
        text_block = ' '.join(sentences)
        max_tokens = 270 if api_base.strip() != "" else 2000
        prompt = "You are a Chatbot. I will provide sentences from a book. Your task is to return the names of every male or female character as they are written in the text. Return names in the format: [Name] (Male or Female) {Adult or Child or Unknown} \n\n" + text_block
        response = generate_response(prompt, api_base, max_tokens)
        writer.writerow([response])

    pbar.close()

# Now filter the raw output and write to the final output file
filter_output(raw_output_file, output_file)

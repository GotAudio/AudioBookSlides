import sys
import csv
from collections import defaultdict

def process_input(input_file, output_file):
    # Initialize a dictionary to store counts and values
    counts = defaultdict(int)
    values = defaultdict(lambda: {"count": 0, "value2": "", "value3": ""})

    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')

            for row in reader:
                if len(row) == 2:
                    _, text = row  # Assuming the second column contains the text
                    # Remove double quotes and leading/trailing spaces
                    cleaned_text = text.replace('"', '').strip()
                    # Check if the cleaned text starts with an alphabetic character
                    if cleaned_text and cleaned_text[0].isalpha():
                        # Split by comma and take the first part
                        value_parts = cleaned_text.split(',')
                        if len(value_parts) >= 3:
                            value = value_parts[0].strip()
                            value2 = value_parts[1].strip()
                            value3 = value_parts[2].strip()
                            key = (value,)
                            counts[key] += 1
                            if counts[key] >= values[key]["count"]:
                                values[key] = {"count": counts[key], "value2": value2, "value3": value3}

            # Sort the counts in descending order and write the results
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            for key, count in sorted_counts:
                writer.writerow([count, key[0], values[key]["value2"], values[key]["value3"]])

        print("Processing completed. Output saved to", output_file)

    except FileNotFoundError:
        print("Input file not found.")
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_input(input_file, output_file)

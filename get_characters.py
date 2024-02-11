import sys
import csv
from collections import defaultdict
import re

def extract_data(text, delimiter):
    pattern = f"\\{delimiter[0]}(.*?)\\{delimiter[1]}"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""

def is_placeholder(value):
    placeholder_values = ["unknown", "gender", "age", "not mentioned", "n/a", "not unspecified", "unspecified", "",]
    return value.lower() if value.lower() not in placeholder_values else None

def process_input(input_file, output_file):
    counts = defaultdict(int)
    details = defaultdict(lambda: {"gender": None, "age": None})

    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')

            for row in reader:
                if len(row) == 2:
                    _, text = row
                    name = extract_data(text, "[]").title()
                    gender = is_placeholder(extract_data(text, "{}"))
                    age = is_placeholder(extract_data(text, "()"))

                    if not name or name.lower() == "proper name":
                        #print("Diagnostic: Empty or placeholder name found in row:", row)  # Diagnostic print
                        continue

                    key = name
                    counts[key] += 1
                    if gender:
                        details[key]["gender"] = gender
                    if age:
                        details[key]["age"] = age

            for key, count in counts.items():
                gender = details[key]["gender"] or "unknown"
                age = details[key]["age"] or "unknown"
                writer.writerow([count, key, gender, age])

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

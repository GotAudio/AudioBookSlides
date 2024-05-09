import re

def load_replacements(file_path):
    replacements = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                key_value = parts[1].split(',', 1)
                if len(key_value) == 2:
                    key = key_value[0]
                    value = key_value[1]+' '
                    replacements[key] = value
    return replacements

def replace_in_file(input_path, replacements, output_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_path, 'w') as file:
        for line in lines:
            # Perform replacements for exact case matches
            for key, value in replacements.items():
                if key in line:
                    line = line.replace(key, value)
            # Replace uppercase names with mixed case replacements
            for key, value in replacements.items():
                if key.upper() in line:
                    line = line.replace(key.upper(), value)
            line = process_line(line)
            file.write(line)

def process_line(line):
    # Replace tab with a space
    line = line.replace('\t', ' ')
    # Replace multiple spaces with a single space
    line = line.replace('{female}', 'female').replace('{male}', 'male')
    line = line.replace('{FEMALE}', 'female').replace('{MALE}', 'male')
    while '  ' in line:
        line = line.replace('  ', ' ')
    # Perform other replacements
    line = re.sub(r'\(\d+s?\)', '', line)
    for char in ['"', '[', ']']:
        line = line.replace(char, '')

    # Replace specific values with a single space
    replace_with_space = [
        "Not Specified", "NOT SPECIFIED", "Not mentioned", "physical activity", "plural",
        "N/A", "n/a", "GENDER", "gender", "(AGE)", "PROPER NAME", "Unnamed",
        "UNKNOWN", "unknown", "CLOTHING", "clothing", "unspecified", "<none>",
        "UNSPECIFIED", "not mentioned", "( )", "< >", "{ }", "()", "<>", "{}"
    ]
    for value in replace_with_space:
        line = line.replace(value, ' ')

    line = line.replace('Set Design:', ' BREAK Set Design:')

    # Replace ", ." and ". ," with "."
    line = re.sub(r',\s*\.', '.', line)
    line = re.sub(r'\.\s*,', '.', line)
    line = re.sub(r'^\.\s*', '', line)
    line = line.replace("\\", " ")

    # Normalize the spaces around commas
    line = re.sub(r'\s*,\s*', ', ', line)

    line = line.replace(' , ', ', ')
    line = line.replace(',  ,', ',')
    line = line.replace(',  ,', ',')
    line = line.replace(', ,', ',')
    line = line.replace(', ,', ',')
    line = line.replace(', ,', ',')
    line = line.replace(', ,', ',')
    line = line.replace(', ,', ',')
    line = line.replace(', ,', ',')
    line = line.replace(',,', ',')
    line = line.replace(',,', ',')
    line = line.replace(',,', ',')
    line = line.replace(',,', ',')
    line = line.replace("''", "'")

    # Remove comma at the beginning of a line
    line = re.sub(r'^,', '', line)
    # Remove "BREAK" at the beginning of a line
    line = re.sub(r'^BREAK', '', line)
    line = re.sub(r'^\.', '', line)
    line = re.sub(r'^\s+', '', line)

    return line

def main(replacements_file, input_file, output_file):
    replacements = load_replacements(replacements_file)
    replace_in_file(input_file, replacements, output_file)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: script.py _ts_p_actors.txt _merged.txt _merged_names_dup.txt ")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])

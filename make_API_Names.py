import sys

def is_printable(char):
    """ Check if a character is printable. """
    return char.isprintable() or char.isspace()

def process_line(line):
    # Delete the first 18 characters
    new_line = line[18:]

    # Perform the replacements
    new_line = new_line.replace("''", "'")
    new_line = new_line.replace("\\\"", "^")
    new_line = new_line.replace("\"", "")
    new_line = new_line.replace("^", "\"")

    # Replace non-printable and non-ASCII characters with Unicode escape
    new_line = ''.join(c if is_printable(c) else '\\u{:04x}'.format(ord(c)) for c in new_line)

    return new_line

def main(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='replace') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            processed_line = process_line(line)
            outfile.write(processed_line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Convert primary input .srt file to non-csv/escaped eBook text to pass to GPT  API to learn character names.")
        print("Usage: python make_API_Names.py <input_file> <output_file>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        main(input_file, output_file)

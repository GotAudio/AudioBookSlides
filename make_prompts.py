import sys
import re

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in:
        content = f_in.read()

    # Remove comment lines
    content = re.sub(r'^#.*\r?\n', '', content, flags=re.MULTILINE)

    # Merge lines between empty lines
    paragraphs = re.split(r'\r?\n\r?\n', content)

    # Process each paragraph
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for paragraph in paragraphs:
            if paragraph:  # check that paragraph is not empty
                index, timestamp, *text = paragraph.split('\n')
                index = index.zfill(5)
                text = ' '.join(text).strip()

                # Extract and format start timestamp
                start_timestamp = re.match(r'\d\d:\d\d:\d\d,\d\d\d', timestamp).group()
                start_timestamp = re.sub(r'[:,\s]', '', start_timestamp)
                start_timestamp = f'{{ts={start_timestamp}}}'

                # Format and escape text
                text = text.replace('"', '\\"').replace("'", "''")

                f_out.write(f'"{start_timestamp}"\t"{text}"\n')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python make_prompts.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_file(input_file, output_file)

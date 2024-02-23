import os
import sys
import re
import tempfile
import shutil

def preprocess_text(text):
    """ Appends a period to the end of text if it does not end with sentence-ending punctuation. """
    if text and not re.search(r"[.?!\"]\s*$", text):
        return text + '.'
    return text

def process_pass(input_file, output_file, char_limit):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Correct the first timestamp if needed
    # Search for the first occurrence of "-->" at position 14
    for i, line in enumerate(lines):
        if line.strip().find("-->") == 13:  # 13 because indexing starts at 0
            start_time, end_time = line.split(' --> ')
            if start_time != '00:00:00,000':
                lines[i] = '00:00:00,000 --> ' + end_time + '\n'
            break

    new_lines = []
    buffer_line = ""
    buffer_start_time = ""
    buffer_end_time = ""
    current_index = 1
    combined_any = False

    for i in range(0, len(lines) - 3, 4):
        index_line = lines[i].strip()
        time_line = lines[i + 1].strip()
        text_line = lines[i + 2].strip()

        # Apply preprocessing only to text lines
        preprocessed_text_line = preprocess_text(text_line)

        if not buffer_line:  # If buffer is empty, set the start time
            buffer_start_time = time_line.split('-->')[0].strip()

        if buffer_line and len(buffer_line + ' ' + preprocessed_text_line) <= char_limit:
            # Combine lines
            buffer_end_time = time_line.split('-->')[1].strip()
            combined_time = f"{buffer_start_time} --> {buffer_end_time}"
            new_lines.append(f"{current_index}\n{combined_time}\n{buffer_line} {preprocessed_text_line}\n\n")
            current_index += 1
            buffer_line = ""  # Clear the buffer after combining
            combined_any = True
        else:
            if buffer_line:
                # Add buffered line as is
                buffer_end_time = buffer_time.split('-->')[1].strip()
                combined_time = f"{buffer_start_time} --> {buffer_end_time}"
                new_lines.append(f"{current_index}\n{combined_time}\n{buffer_line}\n\n")
                current_index += 1

            buffer_line = preprocessed_text_line
            buffer_start_time = time_line.split('-->')[0].strip()
            buffer_end_time = time_line.split('-->')[1].strip()
            buffer_time = time_line

    # Add the last buffered line if it exists
    if buffer_line:
        combined_time = f"{buffer_start_time} --> {buffer_end_time}"
        new_lines.append(f"{current_index}\n{combined_time}\n{buffer_line}\n\n")

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

    return combined_any


def join_subtitles(input_file, output_file, char_limit):
	with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.srt', encoding='utf-8') as temp:
		temp_file = temp.name
		combined_any = process_pass(input_file, temp_file, char_limit)

		while combined_any:
			combined_any = process_pass(temp_file, temp_file, char_limit)

		# Rewind the temporary file to read its content
		temp.seek(0)
		final_content = temp.readlines()

	# Copy the final output to the desired output file
	with open(output_file, 'w', encoding='utf-8') as file:
		file.writelines(final_content)

	# Remove the temporary file
	try:
		os.remove(temp_file)
	except OSError as e:
		print(f"Error: {e.filename} - {e.strerror}.")

def main():
    if len(sys.argv) < 5 or sys.argv[1] != '-join':
        print("Usage: python fix_srt.py -join <char_limit> <input_file> <output_file>")
        sys.exit(1)

    char_limit = int(sys.argv[2])
    input_file = sys.argv[3]
    output_file = sys.argv[4]

    join_subtitles(input_file, output_file, char_limit)

if __name__ == "__main__":
    main()
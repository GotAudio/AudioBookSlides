import sys
import io
import struct
import os
from joblib import Parallel, delayed

def read_text_comment(png_file, part='both'):
    """Reads the tEXt comment block from a PNG file.

    Args:
        png_file: A file object containing the PNG file.
        part: A string indicating which part of the text to return.
            'book' for the book text, 'gen' for the generation text,
            or 'both' for both parts.

    Returns:
        A string containing the requested part of the tEXt comment block,
        or None if the file does not contain a tEXt comment block.
    """

    png_file.seek(0)
    header = png_file.read(8)
    if header != b'\x89PNG\r\n\x1a\n':
        return None

    while True:
        chunk_length = struct.unpack('>I', png_file.read(4))[0]
        chunk_type = png_file.read(4)
        if chunk_type == b'tEXt' or chunk_type == b"iTXt":
            chunk_data = png_file.read(chunk_length)
            text = chunk_data.decode('utf-8').replace('parameters\x00', '')  # Remove null characters
            book_text, sep, gen_text = text.partition('==================================================')
            if part == 'book':
                return book_text.strip()
            elif part == 'gen':
                return gen_text.strip()
            else:
                return text
        png_file.seek(chunk_length + 4, io.SEEK_CUR)
        if chunk_type == b'IEND':
            break

    return None

def write_text_comment(png_file, text):
    """Writes a tEXt comment block to a PNG file.

    Args:
        png_file: A file object containing the PNG file.
        text: The text to write to the tEXt comment block.
    """

    png_file.seek(0)
    header = png_file.read(8)
    if header != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a PNG file')

    chunk_length = len(text.encode('utf-8'))
    png_file.write(struct.pack('>I', chunk_length))
    png_file.write(b'tEXt')
    png_file.write(text.encode('utf-8'))
    png_file.write(b'\x00')

def process_file(input_filename, part, overwrite, idx, total):
    try:
        output_filename = input_filename[:-4] + '.tEXt.txt'
        if overwrite or not os.path.exists(output_filename):
            with open(input_filename, 'rb') as png_file:
                text = read_text_comment(png_file, part)
            if text is not None:
                with open(output_filename, 'w') as output_file:
                    output_file.write(text)

        # Progress update
        progress_update_interval = max(1, total // 100)
        if idx % progress_update_interval == 0 or idx == total - 1:
            completed = (idx + 1) // progress_update_interval
            sys.stdout.write('[' + '.' * completed + ' ' * (100 - completed) + ']\r')
            sys.stdout.flush()

    except Exception as e:
        print(f"Error processing file {input_filename}: {e}", file=sys.stderr)


def process_directory(directory, part, overwrite):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.png')]
    total = len(files)

    # Initialize progress bar
    print('[' + ' ' * 100 + ']', end='\r')  # Print initial progress bar

    Parallel(n_jobs=30)(delayed(process_file)(file, part, overwrite, idx, total) for idx, file in enumerate(files))

    print()  # Print newline after progress bar completion


def main():
    if len(sys.argv) < 2:
        print('Usage: {} <png_file or directory> [-r [book|gen|both]] [-o] or {} -w <png_file>'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    target = sys.argv[1]
    read_mode = '-r' in sys.argv
    write_mode = '-w' in sys.argv
    part = 'both'  # Default part is 'both'
    overwrite = '-o' in sys.argv

    if read_mode:
        if '-r' in sys.argv:
            part_index = sys.argv.index('-r') + 1
            if part_index < len(sys.argv) and sys.argv[part_index] in ['book', 'gen', 'both']:
                part = sys.argv[part_index]

        if os.path.isdir(target):
            process_directory(target, part, overwrite)
        elif os.path.isfile(target):
            with open(target, 'rb') as png_file:  # Read mode for single file
                try:
                    text = read_text_comment(png_file, part)
                    if text is not None:
                        print(text)
                except Exception as e:
                    print(f"Error processing file {target}: {e}", file=sys.stderr)
        else:
            print(f"Invalid PNG file or directory: {target}")
            sys.exit(1)

    elif write_mode:
        if os.path.isfile(target):
            with open(target, 'r+b') as png_file:  # Write mode for single file
                text = input('Enter text to write to tEXt comment block: ')
                write_text_comment(png_file, text)
                png_file.flush()
        else:
            print(f"Invalid PNG file for writing: {target}")
            sys.exit(1)

    else:
        # Default to read mode with 'both' part
        if os.path.isdir(target):
            process_directory(target, part, overwrite)
        elif os.path.isfile(target):
            with open(target, 'rb') as png_file:
                try:
                    text = read_text_comment(png_file, part)
                    if text is not None:
                        print(text)
                except Exception as e:
                    print(f"Error processing file {target}: {e}", file=sys.stderr)
        else:
            print(f"Invalid PNG file or directory: {target}")
            sys.exit(1)

if __name__ == '__main__':
    main()

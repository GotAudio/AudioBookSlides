import argparse
import os
import re

def generate_new_filename(folder, base_filename):
    counter = 1
    new_filename = f"{base_filename}_{str(counter).zfill(3)}.png"
    while os.path.exists(os.path.join(folder, new_filename)):
        counter += 1
        new_filename = f"{base_filename}_{str(counter).zfill(3)}.png"
    return new_filename

def is_numeric_filename(filename):
    try:
        number = int(os.path.splitext(filename)[0])
        return 1000000000 <= number <= 1999999999
    except ValueError:
        return False

def rename_png_files(folder):
    png_files = [entry.name for entry in os.scandir(folder) if entry.name.endswith('.png')]

    # Check if there are PNG files in the folder
    if not png_files:
        print("No PNG files found in the folder. Nothing to rename.")
        return

    for png_file in png_files:
        # Check if the PNG file name already has a 9-digit timestamp
        if is_numeric_filename(png_file):
            continue

        # Construct the corresponding .tEXt.txt file name
        txt_file = png_file.replace('.png', '.tEXt.txt')
        txt_path = os.path.join(folder, txt_file)

        # Check if the .tEXt.txt file exists
        if not os.path.exists(txt_path):
            continue

        # Read the .tEXt.txt file to find the timestamp
        with open(txt_path, 'r') as f:
            content = f.read()
            match = re.search(r"\{ts=(\d{9})\}", content)
            if match:
                timestamp = match.group(1)
                new_png_name = f"{timestamp}.png"
                new_png_path = os.path.join(folder, new_png_name)

                # Check if the new PNG name already exists
                if not os.path.exists(new_png_path):
                    os.rename(os.path.join(folder, png_file), new_png_path)
                else:
                    new_png_path = os.path.join(folder, generate_new_filename(folder, timestamp))
                    os.rename(os.path.join(folder, png_file), new_png_path)

def main():
    parser = argparse.ArgumentParser(description='Rename PNG files')
    parser.add_argument('folder', help='Folder containing .tEXt.txt and .png files')

    args = parser.parse_args()
    rename_png_files(args.folder)


if __name__ == '__main__':
    main()

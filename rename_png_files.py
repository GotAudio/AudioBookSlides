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

def is_correctly_named(file_name, timestamp):
    pattern = re.compile(rf"^{timestamp}(_\d{{3}})?\.png$")
    return pattern.match(file_name) is not None

def rename_png_files(folder):
    txt_files = [f for f in os.listdir(folder) if f.endswith('.tEXt.txt')]
    for txt_file in txt_files:
        txt_path = os.path.join(folder, txt_file)
        with open(txt_path, 'r') as f:
            content = f.read()
            match = re.search(r"\{ts=(\d{9})\}", content)
            if match:
                timestamp = match.group(1)
                png_file = txt_file.replace('.tEXt.txt', '.png')
                png_path = os.path.join(folder, png_file)
                new_png_path = os.path.join(folder, f"{timestamp}.png")

                if os.path.exists(png_path) and not is_correctly_named(png_file, timestamp):
                    if not os.path.exists(new_png_path):
                        os.rename(png_path, new_png_path)
                        print(f"Renamed {png_file} to {timestamp}.png")
                    else:
                        new_png_path = os.path.join(folder, generate_new_filename(folder, timestamp))
                        os.rename(png_path, new_png_path)
                        print(f"Renamed {png_file} to {os.path.basename(new_png_path)}")
                elif not os.path.exists(png_path):
                    print(f"PNG file {png_file} not found")
            else:
                print(f"No timestamp found in {txt_file}")

def main():
    parser = argparse.ArgumentParser(description='Rename PNG files')
    parser.add_argument('folder', help='Folder containing .tEXt.txt and .png files')

    args = parser.parse_args()
    rename_png_files(args.folder)

if __name__ == '__main__':
    main()

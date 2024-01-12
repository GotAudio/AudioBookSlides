import os
import cv2
from joblib import Parallel, delayed
import sys
import fnmatch
import time
import platform

def process_image(image_file, output_folder, frame_count, idx, total):
    img = cv2.imread(image_file)
    video_file = os.path.join(output_folder, os.path.basename(image_file).replace('png', 'avi'))
    height, width, layers = img.shape
    size = (width, height)

    out = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'XVID'), 30, size)

#    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
#    out = cv2.VideoWriter(video_file,fourcc, 20.0, (768,768))

    for _ in range(frame_count):
        out.write(img)

    out.release()

    # Update progress bar, ensuring the divisor is at least 1
    progress_update_interval = max(1, total // 100)
    if idx % progress_update_interval == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

def main(input_wildcard, output_video):


    start_time = time.time()
    if os.path.dirname(input_wildcard):
        image_folder = os.path.dirname(input_wildcard)
    else:
        image_folder = os.getcwd()
    images = sorted([f for f in os.listdir(image_folder) if f.endswith('.png') and fnmatch.fnmatch(f, os.path.basename(input_wildcard))])

    timestamps = set()
    processed_images = []
    duplicate_images = []

    for img in images:
        timestamp = os.path.splitext(img)[0][:9]
        if timestamp not in timestamps:
            timestamps.add(timestamp)
            processed_images.append(img)
        else:
            duplicate_images.append(img)


    output_folder = "temp_output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamps = set()
    processed_images = []
    duplicate_images = []

    for img in images:
        timestamp = os.path.splitext(img)[0][:9]
        if timestamp not in timestamps:
            timestamps.add(timestamp)
            processed_images.append(img)
        else:
            duplicate_images.append(img)

    total_images = len(images)
    step_size = total_images / 100

    frame_counts = []
    accumulated_fraction = 0.0
    for i in range(len(images) - 1):
        # Extract HHMMSSmmm from the filename
        current_time_str = os.path.splitext(images[i])[0]
        next_time_str = os.path.splitext(images[i + 1])[0]

        # print("current_time_str ", current_time_str)
        # Convert HHMMSSmmm to total milliseconds
        current_time = (int(current_time_str[:2]) * 60 * 60 * 1000 +
            int(current_time_str[2:4]) * 60 * 1000 +
            int(current_time_str[4:6]) * 1000 +
            int(current_time_str[6:]))

        next_time = (int(next_time_str[:2]) * 60 * 60 * 1000 +
             int(next_time_str[2:4]) * 60 * 1000 +
            int(next_time_str[4:6]) * 1000 +
            int(next_time_str[6:]))

        # Extract seconds and milliseconds from the timestamps
        current_seconds = current_time // 1000
        current_milliseconds = current_time % 1000

        next_seconds = next_time // 1000
        next_milliseconds = next_time % 1000

        # Calculate duration in seconds (and fractions of a second)
        duration_seconds = next_seconds - current_seconds
        duration_milliseconds = next_milliseconds - current_milliseconds
        if duration_milliseconds < 0:
            duration_seconds -= 1
            duration_milliseconds += 1000

        # Convert this duration to frames
        total_frames = duration_seconds * 30 + (duration_milliseconds / 1000 * 30)

        # Add the previously accumulated fraction to the total frame count
        total_frames += accumulated_fraction

        # Split the total frames into integer and fractional parts
        frame_count = int(total_frames)
        accumulated_fraction = total_frames - frame_count

        # If the accumulated fraction is >= 1, adjust frame count and reduce the fraction
        if accumulated_fraction >= 1.0:
            frame_count += int(accumulated_fraction)
            accumulated_fraction -= int(accumulated_fraction)

        frame_counts.append(frame_count)

    # Add frames for last image
    frame_counts.append(30)  # Default to 1 second for the last image

    sys.stdout.write('[' + ' ' * 100 + ']')
    sys.stdout.flush()
    sys.stdout.write('\b' * 101)

    Parallel(n_jobs=-1, backend="threading")(delayed(process_image)(os.path.join(image_folder, img), output_folder, frame_count, idx, total_images) for idx, (img, frame_count) in enumerate(zip(images, frame_counts)))

    sys.stdout.write('\n')  # Move to the next line after progress bar completion

    # Determine the operating system
    os_name = platform.system()

    # Create file list for ffmpeg. Full paths for Linux
    file_list = os.path.join(output_folder, 'file_list.txt')
    with open(file_list, 'w') as f:
        for img in images:
            video_file = os.path.basename(img).replace('png', 'avi')
            video_file_abs_path = os.path.abspath(os.path.join(output_folder, video_file))
            f.write(f"file '{video_file_abs_path}'\n")

    # Print duplicate filenames only if there are any
    if duplicate_images:
        print("\nDuplicate filenames:")
        for dup in duplicate_images:
            print(dup)
    # Print the elapsed time
    elapsed_time = time.time() - start_time
    elapsed_time_formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    # automatic ffmpeg invocation and cleanup
    print(f"\nffmpeg -hide_banner -f concat -safe 0 -i {file_list} -c copy {output_video}")
    os.system(f"ffmpeg  -hide_banner -f concat -safe 0 -i {file_list} -c copy {output_video}")

    # Check if the output_video file exists
    if os.path.exists(output_video):
        os.system(f"rm -r {output_folder}")
    else:
        print(f"Error: The output video file {output_video} does not exist.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_wildcard> <output_video>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

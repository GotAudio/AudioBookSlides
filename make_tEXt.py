import os
import sys
import subprocess

def execute_command(command, output_filename, dry_run, overwrite):
    """Executes a command, optionally overwriting the output file or displaying the command without executing it.

    Args:
      command: The command to execute.
      output_filename: The name of the output file.
      dry_run: Whether to print the command without executing it.
      overwrite: Whether to overwrite the output file.
    """

    if dry_run:
        print(command)
        return

    if not overwrite and os.path.exists(output_filename):
        print('Output file {} already exists, skipping.'.format(output_filename))
        return

    subprocess.run(command, shell=True)

def main(directory, dry_run, overwrite):
    """Processes all .png files in the specified directory."""

    # Process only files in the specified directory.
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            # Get the input and output file paths.
            input_filename = os.path.join(directory, filename)
            output_filename = os.path.join(directory, filename[:-4] + '.tEXt.txt')

            # Execute the command.
            command = r'python pngtextb.py -r "{}" > "{}"'.format(input_filename, output_filename)
            execute_command(command, output_filename, dry_run, overwrite)

if __name__ == '__main__':
    dry_run = '-l' in sys.argv
    overwrite = '-o' in sys.argv

    if len(sys.argv) < 2:
        print("Usage: python make_tEXt.py [-l] [-o] <directory>")
        sys.exit(1)

    directory = sys.argv[-1]
    main(directory, dry_run, overwrite)

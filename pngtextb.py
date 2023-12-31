import sys
import io
import struct

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
    if chunk_type == b'tEXt':
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

def main():
  if len(sys.argv) < 3:
    print('Usage: {} -r <png_file> [book|gen|both] or {} -w <png_file>'.format(sys.argv[0], sys.argv[0]))
    sys.exit(1)

  png_mode = 'r+b'
  if sys.argv[1] == '-r':
    png_mode = 'rb'

  with open(sys.argv[2], png_mode) as png_file:
    png_file.seek(0)

    if sys.argv[1] == '-r':
      part = 'both'
      if len(sys.argv) > 3:
        part = sys.argv[3]
      try:
        text = read_text_comment(png_file, part)
        if text is not None:
          print(text)
      except Exception as e:
        print(f"Error processing file {sys.argv[2]}: {e}", file=sys.stderr)
        pass
    elif sys.argv[1] == '-w':
      text = input('Enter text to write to tEXt comment block: ')
      write_text_comment(png_file, text)
      png_file.flush()
    else:
      print('Invalid option: {}'.format(sys.argv[1]))
      sys.exit(1)

if __name__ == '__main__':
  main()

import sys
import csv
import re

DEBUG = False  # Set to True to enable debug print statements

def process_input(characters_file, male_actors_file, female_actors_file, output_file, depth=4):
    try:
        with open(characters_file, 'r', newline='', encoding='utf-8') as char_file, \
             open(male_actors_file, 'r', newline='', encoding='utf-8') as male_file, \
             open(female_actors_file, 'r', newline='', encoding='utf-8') as female_file, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:

            char_reader = csv.reader(char_file, delimiter='\t')
            male_reader = csv.reader(male_file, delimiter='\t')
            female_reader = csv.reader(female_file, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')

            # Read male actors into a list
            male_actors = [row[1] for row in male_reader]

            # Read female actors into a list
            female_actors = [row[1] for row in female_reader]

            for row in char_reader:
                if len(row) == 4:
                    count, name, gender, age = row
                    count = int(count)

                    # Check if gender is male or {male}
                    if gender in ['male', '{male}'] and count >= depth:
                        if male_actors:
                            actor_name = male_actors.pop(0)
                            age = re.search(r'(\d+)', age)
                            age = f"{age.group()}yo" if age else ""
                            output_line = f"{count}\t{name}, _solo {age} male actor {actor_name} @"
                            writer.writerow([count, f"{name}, _solo {age} male actor {actor_name} @"])
                            if DEBUG:
                                print(output_line)  # Debugging print

                    # Check if gender is female or {female}
                    elif gender in ['female', '{female}'] and count >= depth:
                        if female_actors:
                            actor_name = female_actors.pop(0)
                            age = re.search(r'(\d+)', age)
                            age = f"{age.group()}yo" if age else ""
                            output_line = f"{count}\t{name}, _solo {age} female actress {actor_name} @"
                            writer.writerow([count, f"{name}, _solo {age} female actress {actor_name} @"])
                            if DEBUG:
                                print(output_line)  # Debugging print

        print("Processing completed. Output saved to", output_file)

    except FileNotFoundError as e:
        print("File not found:", str(e))
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python replace_actors.py <characters_file> <male_actors_file> <female_actors_file> <output_file>")
        sys.exit(1)

    characters_file = sys.argv[1]
    male_actors_file = sys.argv[2]
    female_actors_file = sys.argv[3]
    output_file = sys.argv[4]

    process_input(characters_file, male_actors_file, female_actors_file, output_file)

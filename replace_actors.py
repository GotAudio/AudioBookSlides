import sys
import csv
import re
import os

import random  # Import the random module

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

            # Read male actors into a list and shuffle
            male_actors = [row[1] for row in male_reader]
            random.shuffle(male_actors)  # Shuffle the list randomly

            # Read female actors into a list and shuffle
            female_actors = [row[1] for row in female_reader]
            random.shuffle(female_actors)  # Shuffle the list randomly

            # Create lists to store sorted male and female characters
            sorted_male_characters = []
            sorted_female_characters = []

            api_key = os.environ.get('ABS_API_KEY')

            for row in char_reader:
                if len(row) == 4:
                    count, name, gender, age = row
                    count = int(count)

                    # Check if gender is male or {male}
                    if gender.lower() in ['male', '{male}'] and count >= depth:
                        if male_actors:
                            actor_name = male_actors.pop(0)
                            age_match = re.search(r'(\d+)', age)
                            age_text = f"{age_match.group()}yo" if age_match else ""
                            output_line = f"{count}\t{name}, _solo {age_text} {gender} actor {actor_name} @"
                            sorted_male_characters.append(output_line)

                    # Check if gender is female or {female}
                    elif gender.lower() in ['female', '{female}'] and count >= depth:
                        if female_actors:
                            actor_name = female_actors.pop(0)
                            age_match = re.search(r'(\d+)', age)
                            age_text = f"{age_match.group()}yo" if age_match else ""
                            output_line = f"{count}\t{name}, _solo {age_text} {gender} actress {actor_name} @"
                            sorted_female_characters.append(output_line)

                    # Check if gender is unknown and we did not use GPT, accept unknown as Male
                    elif gender.lower() in ['unknown', '{unknown}'] and count >= depth and not api_key:
                        if male_actors:
                            actor_name = male_actors.pop(0)
                            age_match = re.search(r'(\d+)', age)
                            age_text = f"{age_match.group()}yo" if age_match else ""
                            # For unknown gender without API key, default to Male but maintain the original case for gender in the output
                            output_line = f"{count}\t{name}, _solo {age_text} {gender} actor {actor_name} @"
                            sorted_male_characters.append(output_line)

            # Sort male and female characters separately by name
            sorted_male_characters.sort(key=lambda x: x.split('\t')[1])
            sorted_female_characters.sort(key=lambda x: x.split('\t')[1])

            # Write sorted characters to the output file
            for character in sorted_male_characters:
                writer.writerow(character.split('\t'))

            for character in sorted_female_characters:
                writer.writerow(character.split('\t'))

    except FileNotFoundError as e:
        print("File not found:", str(e))
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print("Usage: python replace_actors.py <characters_file> <male_actors_file> <female_actors_file> <output_file> [depth]")
        sys.exit(1)

    characters_file = sys.argv[1]
    male_actors_file = sys.argv[2]
    female_actors_file = sys.argv[3]
    output_file = sys.argv[4]
    depth = int(sys.argv[5]) if len(sys.argv) == 6 else 4

    process_input(characters_file, male_actors_file, female_actors_file, output_file, depth)
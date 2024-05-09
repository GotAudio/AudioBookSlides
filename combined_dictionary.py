import sys
import re
import argparse
from tqdm import tqdm
import concurrent.futures
from collections import Counter
import string

# Function to preprocess words
def preprocess_word(word):
    return word.lower(), word

# Function to check if word or its parts are in dictionary
def is_part_in_dictionary(word, dictionary):
    if word.lower() in dictionary:
        return True
    parts = word.split('-')
    return all(part.lower() in dictionary for part in parts)

# Function to remove trailing punctuation
def remove_trailing_punctuation(word):
    while word and word[-1] in string.punctuation:
        word = word[:-1]
    return word


def process_file(csv_file, dictionary, speech_verbs, strict=1):
    unique_words = {}
    speech_verb_flags = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as infile:
        for line_number, line in enumerate(infile, 1):
            # Ignore lines that do not contain the expected tab separation (e.g., timestamps)
            if '\t' in line:
                _, text = line.split('\t', 1)
                text = text.strip('"')
            else:
                continue  # Skip lines without proper format

            words = text.split()
            buffer = []
            last_was_capitalized = False

            for i, word in enumerate(words):
                # Exclude words with apostrophes, digits, or internal punctuation
                if "'" in word or word[0].isdigit() or any(c in string.punctuation for c in word.strip(string.punctuation)):
                    buffer = []
                    last_was_capitalized = False
                    continue

                processed_word, original_word = preprocess_word(word)
                cleaned_word = remove_trailing_punctuation(processed_word)

                if word[0].isupper() and not is_part_in_dictionary(processed_word, dictionary) and not is_part_in_dictionary(cleaned_word, dictionary):
                    buffer.append(original_word)
                    last_was_capitalized = True
                else:
                    buffer = []
                    last_was_capitalized = False
                    continue  # Skip appending and reset for the next word

                # Commit the buffer if the end of a sentence is reached or if followed by a speech verb
                if buffer and (i == len(words) - 1 or words[i + 1].strip(",.?!") in speech_verbs):
                    phrase = ' '.join(buffer)
                    if phrase not in unique_words:
                        unique_words[phrase] = line_number
                        speech_verb_flags[phrase] = 0  # Keeping the speech_verb_flag logic, though it's not updated in this snippet
                    buffer = []  # Clear the buffer for new accumulation
                    last_was_capitalized = False

    return unique_words, speech_verb_flags

def preprocess_counts(csv_file, unique_words, strict=0):
    counts = Counter()
    male_counts = Counter()
    female_counts = Counter()

    male_pattern = re.compile(r'\b(?:he|him)\b')
    female_pattern = re.compile(r'\b(?:she|her)\b')

    with open(csv_file, "r", newline="", encoding='utf-8-sig') as infile:
        for line in infile:
            contains_male = bool(male_pattern.search(line))
            contains_female = bool(female_pattern.search(line))

            # Normalize line for non-strict comparison
            line_lower = line.lower()
            for term in unique_words:
                # Determine if term needs to be case-sensitive
                term_to_count = term if strict and term[0].isupper() else term.lower()

                if ' ' in term:  # Handle multi-word terms
                    term_count = line.count(term) if strict and term[0].isupper() else line_lower.count(term.lower())
                else:  # Handle single-word terms
                    # Use regex to match whole words, considering strict flag for capitalization
                    pattern = re.compile(r'\b{}\b'.format(re.escape(term)), re.IGNORECASE if not strict or not term[0].isupper() else 0)
                    term_count = len(pattern.findall(line if strict and term[0].isupper() else line_lower))

                counts[term] += term_count
                if contains_male:
                    male_counts[term] += term_count
                if contains_female:
                    female_counts[term] += term_count

    top_terms = {term: (counts[term], male_counts[term], female_counts[term]) for term in unique_words if counts[term] > 0}

    return top_terms


def find_matches(csv_file, unique_words, top_terms):
    """Finds matches for unique_words terms in the context of speech verbs and compiles associated counts.
    Only includes the term with the smallest count for each timestamp."""
    matches = {}
    try:
        with open(csv_file, "r", encoding='utf-8-sig') as infile:
            for line_number, line in enumerate(infile, 1):
                timestamp_match = re.search(r"({ts=\d+})", line)
                timestamp = timestamp_match.group(1) if timestamp_match else "unknown"
                lowest_count_term = None
                lowest_count = None
                for term in unique_words:
                    # Match terms based on their exact case
                    if re.search(r'\b' + re.escape(term) + r'\b', line):
                        count, male_count, female_count = top_terms.get(term, (0, 0, 0))
                        # Update the term with the lowest count if this is the first term checked or if its count is lower than the current lowest
                        if lowest_count is None or count < lowest_count:
                            lowest_count_term = f"{term}_{count}_{male_count}_{female_count}"
                            lowest_count = count
                if lowest_count_term:  # If there's a term with the lowest count for this timestamp
                    matches[timestamp] = [lowest_count_term]
                else:
                    matches[timestamp] = []
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    return matches


def write_output(output_file, matches, top_terms):
    with open(output_file, 'w', encoding='utf-8') as file:
        for keyname, term_tuple_list in matches.items():
            if not term_tuple_list:  # Check if there are no terms for this keyname
                # Output a row with placeholders if no terms
                output_line = f'"{keyname}"\t"[], {{}}, (), <>, "\n'
                file.write(output_line)
                continue  # Skip to the next iteration

            # Since term_tuple is a list, assume it contains only one element
            term_tuple = term_tuple_list[0]

            # Split term_tuple to extract the character name
            character_name = term_tuple.split('_')[0]

            count, male_count, female_count = top_terms[character_name]  # Look up counts using the character name

            # Determine gender label and associated age based on counts from top_terms
            if male_count > female_count:
                gender_label = "{male}"
                age = "(35yo)"
            elif female_count > male_count:
                gender_label = "{female}"
                age = "(24yo)"
            elif female_count == 0 and male_count == 0:
                gender_label = "{creature}"
                age = "(20yo)"
            else:
                # Handle the case where male_count == female_count
                gender_label = "{Male}"  # Indicate uncertainty in gender
                age = "(30yo)"

            # Check if name is empty and set the output format accordingly
            if character_name == "" or character_name.upper() == "PROPER NAME":
                # Use placeholders for all fields
                output_line = f'"{keyname}"\t"[], {{}}, (), <>, "\n'
            else:
                # Format the output line to match the required format, including actual description
                output_line = f'"{keyname}"\t"[{character_name}]", {gender_label}, {age}, <>, "\n'

            # Write the formatted line to the output file
            file.write(output_line)


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('dict_file', help='tokenizer_vocab_2.txt dictionary file')
    parser.add_argument('m300_file', help='_m300.srt input file')
    parser.add_argument('csv_file', help='_ts.srt m300 with timestamps input file')
    parser.add_argument('output_file', help='_ts_p.srt Output file')
    parser.add_argument('--strict', type=int, choices=[0, 1], default=1, help='Strict mode (default: 1)')

    args = parser.parse_args()

    # Attempt to read the dictionary file
    try:
        with open(args.dict_file, 'r') as file:
            dictionary = {line.strip().lower() for line in file}
    except FileNotFoundError:
        print(f"No dictionary found ({args.dict_file}), skipping dictionary check.")
        dictionary = set()  # Initialize dictionary as an empty set if file not found

    m300_file = args.m300_file
    csv_file = args.csv_file
    output_file = args.output_file
    strict = args.strict

    speech_verbs = [
        "acknowledged", "added", "admitted", "advised", "affirmed", "agreed", "announced", "appeared", "argued", "asked",
        "barely", "battling", "began", "begged", "believed", "boiled", "bounced", "bubbled", "burned", "buzzed",
        "calculated", "called", "captured", "chopped", "claimed", "closed", "collapsed", "combined", "commanded", "concluded",
        "confessed", "constricted", "continued", "countered", "covered", "crawled", "cried", "crossed", "crouched", "curled",
        "dealt", "declared", "denied", "described", "desired", "desperately", "did", "died", "disagreed", "discouraged",
        "dodged", "doubted", "dove", "drew", "dropped", "drove", "encouraged", "engulfed", "exclaimed", "explained",
        "faced", "feared", "fell", "felt", "finds", "flew", "flexed", "flipped", "flowed", "flung",
        "followed", "forgot", "formed", "fought", "found", "frowned", "furiously", "gave", "gestured", "glanced",
        "got", "grabbed", "granted", "guessed", "had", "hesitated", "hit", "hoped", "hopped", "hung",
        "indicated", "insisted", "intended", "interrupted", "invaded", "invited", "jerked", "jogged", "joined", "joked",
        "jumped", "just", "keeps", "kept", "kicked", "killed", "knelt", "knew", "knocked", "lapped",
        "lashed", "latched", "laughed", "lay", "leaned", "leapt", "left", "lifted", "liked", "looked",
        "lost", "lowered", "lunged", "made", "maintained", "marked", "mentioned", "might", "motioned", "moved",
        "murmured", "mused", "must", "narrated", "nodded", "noted", "noticed", "nudged", "objected", "offered",
        "ordered", "peeled", "pieced", "placed", "planned", "plastered", "pleaded", "pointed", "pounded", "poured",
        "promised", "protected", "protested", "pulled", "pushed", "put", "questioned", "raised", "ran", "rattled",
        "reached", "realized", "reared", "recalled", "refused", "released", "relented", "remained", "remarked", "remembered",
        "replied", "resisted", "responded", "retreated", "rippled", "rode", "rolled", "rose", "said", "sailed",
        "sat", "saw", "scanned", "screamed", "sent", "set", "shifted", "shook", "shot", "shouted",
        "simply", "slammed", "slapped", "slid", "slung", "smashed", "smiled", "sought", "spawned", "spilled",
        "spotted", "sprawled", "spun", "squeezed", "staggered", "stared", "stated", "stayed", "stepped", "still", "stood",
        "stopped", "strained", "stretched", "strode", "struggled", "studied", "stumbled", "suddenly", "suggested", "swirled",
        "swooped", "swung", "teased", "thought", "thrashed", "threatened", "tickled", "tilted", "took", "tore",
        "tossed", "trapped", "trickled", "tried", "trusted", "tugged", "tumbled", "turned", "twisted", "twitched",
        "unfurled", "unspooled", "urged", "used", "walked", "wanted", "warned", "was", "watched", "whispered",
        "widened", "wielded", "wished", "wondered", "wove", "wrapped", "wrenched", "writhed", "yanked", "here","is",
        "accepted", "accompanied", "accomplished", "accounted", "accustomed", "activities", "acts", "address", "addressed", "advertised", "affected", "aided", "aids", "aligned", "alleged", "allotted",
        "altered", "always", "answered", "anticipated", "appreciated", "appropriated", "approved", "armed", "assigned", "assisted", "assured", "attached", "attended", "attributed", "authorized",
        "backhanded", "baked", "banks", "barred", "batted", "betrothed", "bleached", "bleed", "blessed", "blotted", "bobbed", "bothered", "bowed", "bragged", "branded", "bred",
        "bridled", "bullshitted", "cantered", "capped", "challenged", "changed", "charged", "charted", "chipped", "chugged", "clapped", "clipped", "clubbed", "collected", "colored",
        "committed", "compelled", "compensated", "completed", "compounded", "compressed", "concealed", "concurred", "conferred", "confined", "confirmed", "connected", "considered",
        "consumed", "controlled", "convinced", "cooked", "corrected", "counted", "cropped", "crowded", "crowned", "cupped", "cured", "cursed", "dabbed", "damaged", "dated",
        "deadpanned", "decided", "defeated", "defended", "deferred", "delighted", "delivered", "departed", "deserved", "detected", "determined", "developed", "devoted", "differentiated",
        "digested", "dimmed", "dipped", "discharged", "disconnected", "discovered", "disguised", "dispelled", "disposed", "dissolved", "distracted", "disturbed", "divided",
        "documented", "does", "donned", "dragged", "dreamed", "dripped", "drummed", "drys", "dunned", "earned", "eavesdropped", "edited", "educated", "embedded", "emitted", "equipped",
        "excelled", "excess", "excused", "experiences", "explored", "exposed", "expressed", "fanned", "fed", "feed", "feigned", "fielded", "fields", "filings", "filled", "filtered",
        "finished", "fitted", "fixed", "flagged", "flapped", "flitted", "flopped", "fluxed", "focused", "forced", "formatted", "founded", "framed", "frequented", "fretted", "fulfilled",
        "furnished", "gagged", "glued", "goes", "graded", "grinned", "gritted", "grovelled", "guarded", "guided", "gunned", "gutted", "hammed", "handed", "hardened", "harmed",
        "harness", "harvested", "hatched", "healed", "heated", "heed", "heeded", "heralded", "hiss", "hugged", "hummed", "hurried", "identified", "implemented", "impressed",
        "improved", "incorporated", "influenced", "informed", "inhabited", "initiated", "injured", "inspired", "instructed", "interested", "interpreted", "involved", "jabbed", "jammed",
        "jared", "jotted", "kidnapped", "kiss", "knitted", "knotted", "labeled", "lagged", "laughs", "layered", "lettered", "licensed", "lied", "lighted", "limited", "lined", "listed",
        "lobbed", "logged", "loved", "lugged", "mapped", "marks", "married", "masters", "matched", "measured", "merited", "mimicked", "minded", "missed", "mixed", "modified",
        "moped", "mopped", "motivated", "mounted", "mourned", "mouths", "nagged", "named", "needed", "nipped", "numbered", "observed", "occupied", "opened", "opposed",
        "organized", "padded", "painted", "paired", "panicked", "paralleled", "parks", "patted", "paved", "payed", "pegged", "penned", "perceived", "performed", "permitted", "persuaded",
        "petted", "pinned", "plodded", "plopped", "plotted", "plugged", "popped", "populated", "positioned", "possess", "potted", "practiced", "precious", "preferred", "prepared", "prepped", "pressed",
        "prized", "proceed", "proceeds", "processed", "professed", "programmed", "prompted", "propelled", "propped", "proved", "provided", "punished", "purported", "qualified", "quested",
        "quipped", "quizzed", "ragged", "rammed", "rapped", "rated", "ratted", "recognized", "reconstructed", "recorded", "referred", "reformed", "regards", "registered", "regretted",
        "repeated", "reported", "represented", "reserved", "resigned", "resolved", "restrained", "restricted", "revealed", "revved", "rewarded", "rigged", "ripped", "rivaled",
        "robbed", "rotted", "rubbed", "ruffled", "sacred", "sagged", "salted", "sapped", "satisfied", "saved", "scammed", "scarred", "scented", "schooled", "scratched", "scripted",
        "scrubbed", "seasoned", "sectioned", "secured", "segmented", "shaped", "shed", "shields", "shipped", "shred", "shredded", "shrugged", "shucks", "sidestepped", "sifted",
        "sighs", "signed", "sipped", "skidded", "skimmed", "skipped", "sled", "slipped", "slotted", "slurred", "smooths", "snagged", "snapped", "snipped", "sobbed", "soiled",
        "solved", "sorted", "spanned", "sparred", "spears", "specified", "sped", "speed", "spirited", "splatted", "spoiled", "spurred", "squatted", "stabbed", "stained", "states", "stirred",
        "stomachs", "strapped", "stressed", "stripped", "strutted", "stunned", "submitted", "substantiated", "succeed", "summons", "supported", "supposed", "suppressed", "suspected",
        "swabbed", "swapped", "swatted", "swayed", "swigged", "tagged", "tamed", "tapped", "tarnished", "tarred", "tasted", "tended", "tested", "texted", "throbbed", "thudded",
        "tipped", "topped", "toss", "touched", "trafficked", "trained", "transferred", "translated", "transmitted", "traveled", "treated", "trekked", "trialed", "tripped", "triumphs", "trotted",
        "tutored", "tutted", "varnished", "verified", "versioned", "viced", "voiced", "wadded", "wagged", "warranted", "warred", "washed", "weighs", "weighted", "whipped",
        "whirred", "whizzed", "winded", "witness", "works", "worms", "worried", "wrinkled", "yaws", "yeahs", "zigzagged", "zipped"
    ]

    unique_words, speech_verb_flags = process_file(csv_file, dictionary, speech_verbs, strict)
    #print(unique_words)
    top_terms = preprocess_counts(csv_file, unique_words, strict)
    #print(top_terms)
    matches = find_matches(csv_file, unique_words, top_terms)
    #print(matches)
    write_output(output_file, matches, top_terms)




#!/usr/bin/env python3
import sys
import re

def is_valid_reference_line(line):
    # Strip whitespace and check if line is empty
    line = line.strip()
    if not line:
        return False

    # Define patterns for different components
    book_names = r'Mat|Mar|Luk|Jhn|Act|Rom|1Co|2Co|Gal|Eph|Phl|Col|1Th|2Th|1Ti|2Ti|Heb|Jas|1Pe|2Pe|1Jo|Jde|Rev|1Ch|1Ki|1Sa|2Ch|2Ki|2Sa|Amo|Dan|Deu|Ecc|Est|Exo|Eze|Gen|Hab|Hag|Hos|Isa|Jdg|Jer|Job|Joe|Jon|Jos|Lam|Lev|Mal|Mic|Nah|Neh|Num|Pro|Psa|Zec|Zep'

    # Pattern for verse range (integer-integer or integer)
    verse_range = r'\d+(?:-\d+)?'
    # Pattern for verse range list (comma-separated verse ranges)
    verse_range_list = fr'{verse_range}(?:,{verse_range})*'
    # Pattern for chapter range (integer:verseRangeList or integer-integer or integer)
    chapter_range = fr'(?:\d+:{verse_range_list}|\d+(?:-\d+)?)'

    # Pattern for reference list (bookName chapterRange)
    reference_list = fr'{book_names}\s+{chapter_range}'

    # Pattern for allusion markers
    allusion_marker = r'(?:\*|)'
    possible_allusion_marker = r'(?:†|)'

    # Complete pattern for reference line
    pattern = fr'^{reference_list};{reference_list};{allusion_marker};{possible_allusion_marker}$'

    return bool(re.match(pattern, line))

def validate_file(filename):
    try:
        with open(filename, 'r') as file:
            # Skip the header line
            next(file)
            for i, line in enumerate(file, 2):  # Start counting from line 2 since header is line 1
                if is_valid_reference_line(line):
                    print(f"Line {i}: VALID - {line.strip()}")
                else:
                    print(f"Line {i}: INVALID - {line.strip()}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

def run_tests():
    test_cases = [
        "Act 7:33-34;Exo 3:5,7-8,10;;",      # Valid: from provided examples
        "Act 7:35;Exo 2:14;;",                # Valid: from provided examples
        "Act 7:35;Exo 3:15-18;*;",            # Valid: from provided examples
        "Act 7:36;Exo 7:1-12:51;*;",          # Valid: from provided examples
        "Act 7:36;Exo 14:21;*;",              # Valid: from provided examples
        "Mat 1:1-5;Jhn 3:16;*;†",             # Valid: complete with markers
        "Gen 1-3;Exo 2;*;",                   # Valid: chapter range
        "Psa 23:1,2-3;Pro 1:1;;",             # Valid: verse range list
        "Mat 1;Jhn a:16;;",                   # Invalid: invalid chapter/verse format
        "Invalid 1;Mat 2;;",                  # Invalid: invalid book name
        "Mat 1;Jhn 2;**;",                    # Invalid: invalid allusion marker
        "Mat 1;Jhn 2;*;††",                   # Invalid: invalid possible allusion marker
        "Mat 1;Jhn 2",                        # Invalid: missing semicolons
        ""                                     # Invalid: empty line
    ]

    print("Running test cases:")
    for i, test in enumerate(test_cases, 1):
        result = is_valid_reference_line(test)
        print(f"Test {i}: {'VALID' if result else 'INVALID'} - {test}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        print("Running test cases instead...")
        run_tests()
    else:
        filename = sys.argv[1]
        print(f"Validating file: {filename}")
        validate_file(filename)

if __name__ == "__main__":
    main()


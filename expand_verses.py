#!/usr/bin/env python3
'''
Suppose a file of semicolon-delimited lines has lines of the form “'Mat
21:42';'Psa 118:22,29';'';''”. The first and second fields consist of one or more Bible verses
separated by commas. Expand lines with more than one verse into multiple lines,
one for each of the verses. So the above example would become two lines, “'Mat
21:42';'Psa 118:22';'';'’" and ‘“Mat 21:42”;'Psa 118:29';'';’'".

We need to define the format of fields one and two. They are a comma-separated
list of Bible verse references. A Bible verse reference begins with a book name,
space, chapter number, colon, verse or range of verses. The second and following verses
will omit the book name if it is the same as the first book name, and will omit
the chapter number and colon if it is the same as the first chapter number. 

Valid book names are: Mat, Mar, Luk, Jhn, Act, Rom, 1Co, 2Co, Gal, Eph, Phl,
Col, 1Th, 2Th, 1Ti, 2Ti, Heb, Jas, 1Pe, 2Pe, 1Jo, Jde, Rev, 1Ch, 1Ki, 1Sa, 2Ch,
2Ki, 2Sa, Amo, Dan, Deu, Ecc, Est, Exo, Eze, Gen, Hab, Hag, Hos, Isa, Jdg, Jer,
Job, Joe, Jon, Jos, Lam, Lev, Mal, Mic, Nah, Neh, Num, Pro, Psa, Zec, Zep.

The first line of the input file is a header and should be skipped. Also a verse
may be a range, expressed as two numbers separated by a hyphen. E.g., in “‘Rev
21:2’;‘Eze 40:1-49,48:1-35’;’’;’†’” the second field contains two verses,
“Eze 40:1-49” and “Eze 48:1-35”

Take the file names from the command line.

'''

#!/usr/bin/env python3
import csv
import re
import sys

VALID_BOOKS = {
    'Mat', 'Mar', 'Luk', 'Jhn', 'Act', 'Rom', '1Co', '2Co', 'Gal', 'Eph', 'Phl', 'Col',
    '1Th', '2Th', '1Ti', '2Ti', 'Tit', 'Phm', 'Heb', 'Jas', '1Pe', '2Pe', '1Jo', '2Jo',
    '3Jo', 'Jde', 'Rev', '1Ch', '1Ki', '1Sa', '2Ch', '2Ki', '2Sa', 'Amo', 'Dan', 'Deu',
    'Ecc', 'Est', 'Exo', 'Eze', 'Gen', 'Hab', 'Hag', 'Hos', 'Isa', 'Jdg', 'Jer', 'Job',
    'Joe', 'Jon', 'Jos', 'Lam', 'Lev', 'Mal', 'Mic', 'Nah', 'Neh', 'Num', 'Pro', 'Psa',
    'Zec', 'Zep'
}

def parse_reference(ref_str, prev_book=None, prev_chapter=None):
    """Parse a Bible reference with optional book/chapter inheritance."""
    ref_str = ref_str.strip()
    if not ref_str:
        return None, None, None

    # Check if reference starts with a book name
    book = None
    remaining = ref_str
    for book_name in sorted(VALID_BOOKS, key=len, reverse=True):
        if ref_str.startswith(book_name):
            if len(ref_str) > len(book_name) and ref_str[len(book_name)] in (' ', ':'):
                book = book_name
                remaining = ref_str[len(book_name):].strip()
                break

    # If no book found, use previous book if available
    if book is None:
        if prev_book is None:
            return None, None, None
        book = prev_book
    else:
        # New book resets chapter inheritance
        prev_chapter = None

    # Parse chapter and verse parts
    if ':' in remaining:
        chapter_part, verse_part = remaining.split(':', 1)
        chapter = int(chapter_part.strip())
        remaining = verse_part.strip()
    else:
        if prev_chapter is None:
            return None, None, None
        chapter = prev_chapter
        remaining = remaining.strip()

    # Parse verse or verse range
    if '-' in remaining:
        # Handle chapter-spanning ranges (e.g., "7:1-12:51")
        if ':' in remaining.split('-')[1]:
            start_verse = int(remaining.split('-')[0])
            end_chapter, end_verse = map(int, remaining.split('-')[1].split(':'))
            return book, chapter, (start_verse, end_verse, end_chapter)
        else:
            start_verse, end_verse = map(int, remaining.split('-'))
            return book, chapter, (start_verse, end_verse, chapter)
    else:
        verse = int(remaining)
        return book, chapter, (verse, verse, chapter)

def expand_verses(input_file, output_file):
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:

        reader = csv.reader(infile, delimiter=';', quotechar="'")
        # Use QUOTE_NONNUMERIC to quote all non-numeric fields (including empty strings)
        writer = csv.writer(outfile, delimiter=';', quotechar="'", quoting=csv.QUOTE_NONNUMERIC)

        # Skip header line
        next(reader, None)

        for row in reader:
            # Normalize to exactly 4 single-quoted fields
            row = (row + [''] * 4)[:4]
            ref1_str, ref2_str, field3, field4 = [field.strip("'") for field in row]

            # Process first field (semicolon-separated references)
            ref1_parts = []
            for ref_group in ref1_str.split(';'):
                prev_book = prev_chapter = None
                for ref_part in ref_group.split(','):
                    book, chapter, verses = parse_reference(ref_part, prev_book, prev_chapter)
                    if book is None:
                        continue

                    # For field 1, just take the first verse of any range
                    start_verse, _, _ = verses
                    ref1_parts.append(f"{book} {chapter}:{start_verse}")

                    prev_book, prev_chapter = book, chapter

            # Process second field (semicolon-separated references)
            ref2_parts = []
            for ref_group in ref2_str.split(';'):
                prev_book = prev_chapter = None
                for ref_part in ref_group.split(','):
                    book, chapter, verses = parse_reference(ref_part, prev_book, prev_chapter)
                    if book is None:
                        continue

                    # For field 2, just take the first verse of any range
                    start_verse, _, _ = verses
                    ref2_parts.append(f"{book} {chapter}:{start_verse}")

                    prev_book, prev_chapter = book, chapter

            # Cross product of all references from both fields
            for r1 in ref1_parts:
                for r2 in ref2_parts:
                    # Convert empty strings to None to ensure they get quoted as ''
                    writer.writerow([
                        r1,
                        r2,
                        field3 if field3 else None,
                        field4 if field4 else None
                    ])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output.csv>", file=sys.stderr)
        sys.exit(1)

    try:
        expand_verses(sys.argv[1], sys.argv[2])
    except FileNotFoundError:
        print(f"Error: Input file not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


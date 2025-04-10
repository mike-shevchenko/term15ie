from enum import Enum


koi7_n1: list = [
    'ю', 'а', 'б', 'ц', 'д', 'е', 'ф', 'г', 'х', 'и', 'й', 'к', 'л', 'м', 'н', 'о',
    'п', 'я', 'р', 'с', 'т', 'у', 'ж', 'в', 'ь', 'ы', 'з', 'ш', 'э', 'щ', 'ч', 'ъ',
    'Ю', 'А', 'Б', 'Ц', 'Д', 'Е', 'Ф', 'Г', 'Х', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О',
    'П', 'Я', 'Р', 'С', 'Т', 'У', 'Ж', 'В', 'Ь', 'Ы', 'З', 'Ш', 'Э', 'Щ', 'Ч', 'Ъ',
]

def koi7_to_rus(b: int) -> str:
    assert 0x40 <= b <= 0x7F
    return koi7_n1[b - 0x40]


# Returns 0 if not a Russian letter.
def rus_to_koi7(c: str) -> int:
    try:
        index = koi7_n1.index(c)
    except ValueError:
       return 0
    return index + 0x40


class Mode(Enum):
    LAT = 0
    RUS = 1


# The values are 15IE character codes.
CODE_RUS = '0x0E'
#CODE_RUS = 'R'  # Uncomment for testing.
CODE_LAT = '0x0F'
#CODE_LAT = 'L'  # Uncomment for testing.

# Current mode of the terminal guessed by the program. It must be global because both input decoding and printing needs
# to access the same current value.
mode: Mode = Mode.LAT


def print_to_term_with_hex_dump(s: str):
    global mode
    for c in s:
        print_to_term(f"0x{ord(c):02x}")
        if ord(c) >= 32 and ord(c) != 127:  # Not an ASCII control code.
            print_to_term(" '" + c + "', ")
    print()


def main():
    global mode

    print('''Test program for the terminal Elektronika 15IE.
    
Connect with the terminal and run this program. Enter a line of text,
using RUS and LAT keys along the way, and press VK (aka Enter). The
program will print the line back, and then the Unicode code points of
the decoded line along with the characters if they are printable.
Cyrillic letters are printed via issuing the RUS/LAT codes.

All input characters with codes >= 128 are replaced with question marks.

Enter an empty line to quit.
''')
    while True:
        input_line: str = input()
        if not input_line:
            print("Exiting the program.")
            break
        output_line: str = convert_from_term(input_line)
        print_to_term_with_hex_dump(output_line)


def convert_from_term(term: str) -> str:
    global mode
    s: str = ''
    for c in term:
        if c == CODE_RUS:
            mode = Mode.RUS
        elif c == CODE_LAT:
            mode = Mode.LAT
        elif ord(c) >= 0x80:  # Should not happen because the terminal sends 7-bit codes only.
            s += '?'
        elif mode == Mode.RUS and 0x40 <= ord(c) <= 0x7F:
            s += koi7_to_rus(ord(c))
        else:
            s += c
    return s


# Prints a Unicode string to the terminal. Non-ASCII non-Cyrillic characters are printed as '?', while ASCII control
# codes are printed as-is. Does not append a newline.
def print_to_term(s: str):
    global mode
    for c in s:
        if ord(c) <= 0x40:
            print(c, end="")
            continue
        rus: int = rus_to_koi7(c)
        if rus != 0:  # Cyrillic letter - print it, temporarily switching to RUS if needed.
            if mode == Mode.LAT:
                mode = Mode.RUS
                print(CODE_RUS, end="")
            print(chr(rus), end="")
        else:
            if ord(c) >= 128:  # Non-ASCII non-Cyrillic - substitute such characters.
                print('?', end="")
            else:  # ASCII character.
                if mode == Mode.RUS:
                    mode = Mode.LAT
                    print(CODE_LAT, end="")
                print(c, end="")

if __name__ == '__main__':
    main()

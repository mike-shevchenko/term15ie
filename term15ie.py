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
CODE_RUS = 0x0E
CODE_LAT = 0x0F

# Current mode of the terminal guessed by the program.
mode: Mode = Mode.LAT


def print_hex_dump(s: str):
    global mode
    for c in s:
        print(f"#{ord(c)} ", end="")
        rus: int = rus_to_koi7(c)
        if rus != 0:  # Cyrillic letter - print it, temporarily switching to RUS if needed.
            if mode == Mode.LAT:
                print(chr(CODE_RUS), end="")
                print("'" + chr(rus) + "', ", end="")
                print(chr(CODE_LAT), end="")
            else:
                print(chr(rus), end="")
        elif 0 <= ord(c) <= 32 or ord(c) >= 127:
            print(",", end="")  # Non-printable - do not print the character.
        else:
            print("'" + c + "', ", end="")  # Printable non-Cyrillic character.
    print()


def main():
    global mode

    print('''Test program for the terminal Elektronika 15IE.
    
Connect with the terminal and run this program. Enter a line of text,
using RUS and LAT keys along the way, and press VK (aka Enter). The
program will print the Unicode code points of the decoded line along
with the characters if they are printable. Cyrillic letters are
printed via issuing the RUS/LAT codes.

All input characters with codes >= 128 are replaced with underscores.

Enter an empty line to quit.
''')
    while True:
        input_line: str = input()
        if not input_line:
            print("Exiting the program.")
            break
        output_line: str = process_line(input_line)
        print_hex_dump(output_line)


def process_line(input_line: str) -> str:
    global mode
    output_line: str = ''
    for c in input_line:
        if ord(c) == CODE_RUS:
            mode = Mode.RUS
        elif ord(c) == CODE_LAT:
            mode = Mode.LAT
        elif ord(c) >= 0x80:
            output_line += '_'
        elif mode == Mode.RUS and 0x40 <= ord(c) <= 0x7F:
            output_line += koi7_to_rus(ord(c))
        else:
            output_line += c
    return output_line


if __name__ == '__main__':
    main()

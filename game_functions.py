import time
import random
import requests
from wordfreq import zipf_frequency

# -------------------- Constants --------------------

# ASCII logo displayed at the top of the game
HUGE_STR = """
                        .___.__                           ㅤ⠀⠀⢀⣤⣄  
__  _  _____________  __| _/|  |   ____       _ __  _   _    ⢰⣿⣿⣿⣿⡆ ⣠⣶⣿⣶⡀
\ \/ \/ /  _ \_  __ \/ __ | |  | _/ __ \     | '_ \| | | |   ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
 \     (  <_> )  | \/ /_/ | |  |_\  ___/     | |_) | |_| |    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏
  \/\_/ \____/|__|  \____ | |____/\___  > (_) .__/ \__,  |     ⣿⣿⣿⣿⣿⣿⣿⠋
                         \/           \/     |_|    |___/       ⠻⣿⣿⠿⠉"""

# Word lists grouped by word length (3–9)
WORDLIST = {
    3: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/3-letter-words.json').json(),
    4: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/4-letter-words.json').json(),
    5: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/5-letter-words.json').json(),
    6: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/6-letter-words.json').json(),
    7: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/7-letter-words.json').json(),
    8: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/8-letter-words.json').json(),
    9: requests.get('https://raw.githubusercontent.com/jonathanwelton/word-lists/main/9-letter-words.json').json(),
}

# Difficulty settings: (name, max guesses, display color)
DIFFICULTIES = {
    1: ("Easy", 8, ('LIGHT_GREEN','BOLD')),
    2: ("Moderate", 7, ('LIGHT_CYAN','BOLD')),
    3: ("Normal", 6, ('BLUE','BOLD')),
    4: ("Hard", 5, ('YELLOW','BOLD')),
    5: ("Extreme", 4, ('LIGHT_RED','BOLD')),
    6: ("Impossible", 3, ('RED','BOLD')),
}

# ANSI escape codes for colors and styles
ANSI_EFFECTS = {
    "RED": "\033[38;5;196m", "LIGHT_RED": "\033[38;5;203m",
    "YELLOW" : "\033[38;5;220m", "LIGHT_YELLOW": "\033[38;5;227m",
    "GREEN": "\033[38;5;46m", "LIGHT_GREEN": "\033[38;5;82m",
    "CYAN": "\033[38;5;51m", "LIGHT_CYAN": "\033[38;5;87m",
    "BLUE": "\033[38;5;21m", "LIGHT_BLUE": "\033[38;5;75m",
    "MAGENTA": "\033[38;5;201m", "LIGHT_MAGENTA": "\033[38;5;213m",
    "DARK_GRAY": "\033[38;5;236m", "GRAY": "\033[38;5;245m", "WHITE": "\033[38;5;255m",
    "BOLD": "\033[1m","RESET": "\033[0m",
}

# Color gradients for animated logo
GRADIENTS = {
    "NORMAL" : {"colors" : ["WHITE"], "speed" : 0.08},
    "RAINBOW": {"colors": ["RED", "YELLOW", "GREEN", "CYAN", "BLUE", "MAGENTA", "LIGHT_RED"], "speed": 0.09},
    "PASTEL_RAINBOW": {"colors": ["LIGHT_RED", "LIGHT_YELLOW", "LIGHT_GREEN", "LIGHT_CYAN", "LIGHT_BLUE", "LIGHT_MAGENTA"], "speed": 0.05},
    "FIRE": {"colors": ["DARK_GRAY", "RED", "LIGHT_RED", "YELLOW", "LIGHT_YELLOW", "WHITE"], "speed": 0.06},
    "ICE": {"colors": ["DARK_GRAY", "BLUE", "CYAN", "LIGHT_CYAN", "LIGHT_BLUE", "WHITE"], "speed": 0.14},
    "MATRIX": {"colors": ["DARK_GRAY", "GREEN", "LIGHT_GREEN", "WHITE", "LIGHT_GREEN", "GREEN"], "speed": 0.05},
    "SYNTH": {"colors": ["MAGENTA", "LIGHT_MAGENTA", "LIGHT_BLUE", "CYAN", "LIGHT_CYAN", "WHITE"], "speed": 0.09},
    "GRAYSCALE": {"colors": ["DARK_GRAY", "GRAY", "WHITE"], "speed": 0.18},
    "SUNSET": {"colors": ["LIGHT_MAGENTA", "MAGENTA", "RED", "LIGHT_RED", "YELLOW", "LIGHT_YELLOW"], "speed": 0.10},
    "OCEAN": {"colors": ["GRAY", "BLUE", "LIGHT_BLUE", "CYAN", "LIGHT_CYAN", "WHITE"], "speed": 0.13},
}

# Stores runtime settings such as the current gradient
GAME_VARS = {
    'gradient_name' : None,
    'gradient' : GRADIENTS[random.choice(list(GRADIENTS.keys()))]
}

# Filters each word list to include only common English words
common_words = {}
for length, words in WORDLIST.items():
    common_list = []
    for word in words:
        # zipf score measures how common a word is
        if zipf_frequency(word, "en") >= 4.5:
            common_list.append(word)
    common_words[length] = common_list

# -------------------- Functions --------------------

# Prints text character by character for a typing animation
def write(text: str, speed: float, de=False):
    for i, char in enumerate(text):
        print(char, end="", flush=True)
        if de and i == len(text) - 1:
            return
        time.sleep(speed)
    print()

# Clears the terminal and optionally animates the logo
def clear(animate=False, dontuseLogo=False):
    if dontuseLogo:
        print("\033c", end="")
        return
    
    gradient = GAME_VARS['gradient']["colors"]
    sleep_time = GAME_VARS['gradient']["speed"]
    lines = HUGE_STR.splitlines()

    print("\033c", end="")

    def printTitle(offset=0):
        gr = gradient
        if offset != 0 and GAME_VARS["gradient_name"] == "NORMAL":
            gr = GRADIENTS['GRAYSCALE']["colors"]

        for i, line in enumerate(lines):
            color = gr[(i + offset) % len(gr)]
            print(applyANSI(line, True, color))

    if animate:
        try:
            tick = time.time()
            offset = 0
            while time.time() - tick < 3.5:
                print("\033[H", end="")
                printTitle(offset)
                offset += 1
                time.sleep(sleep_time)
        finally:
            print('Loading...')
            time.sleep(2)
            print("\033c", end="")
            printTitle()
    else:
        printTitle()

# Debug helper to manually configure a game
def debugSettings():
    while True:
        v1 = input('Enter a word [R for random]: ').lower()
        if v1 == 'r':
            word_pool = common_words[random.randint(3,9)]
            v1 = random.choice(word_pool)

        v2 = len(v1)
        v3 = int(input('Enter guess amount: '))
        v4 = int(input('Enter difficulty: '))
        break

    return newGame({
        'debug': True,
        'word': v1,
        'word_length': v2,
        'max_guesses': v3,
        'difficulty': v4
    })

# Displays difficulty menu and returns selected difficulty
def selectDiff():
    n = 0
    while True:
        print("Select a Difficulty:\n")
        for i, (name, guesses, ansi) in enumerate(DIFFICULTIES.values()):
            print(f" {i+1}. {applyANSI(name.upper(), True, *ansi)} ({guesses} guesses)")

        try:
            diff = int(input("> "))
            if 1 <= diff <= 6:
                return diff, DIFFICULTIES[diff][1]
        except ValueError:
            pass

        n += 1
        print("Enter a valid number between 1 and 6.")
        time.sleep(0.3)
        clear()

# Prompts the user for a valid word length
def selectWordLength():
    while True:
        clear()
        write('Enter how long you want the word to be (3-9 letters): ', 0.03, True)
        try:
            word_len = int(input())
            if 3 <= word_len <= 9:
                return word_len
        except ValueError:
            pass

        print(applyANSI('Enter a number from 3 to 9!', True, 'BOLD'))
        time.sleep(0.4)

# Applies ANSI color/style codes to text
def applyANSI(text, reset, *effects):
    codes = ""
    for e in effects:
        codes += ANSI_EFFECTS[e]

    return codes + text + (ANSI_EFFECTS["RESET"] if reset else "")

# Creates a new game state dict.
def newGame(u1):
    word_pool = common_words[u1['word_length']]
    word = random.choice(word_pool)

    return {
        "word": u1['debug'] and u1['word'] or word,
        "guesses": [],
        "debug": u1['debug'],
        "difficulty": u1['difficulty'],
        "loaded": False,
        "max_guesses": u1['max_guesses'],
        "keyboard": {},
        "won": None,
    }

# Renders the game screen and guess history
def refresh(state, u_2=False):
    diff, _, effs = DIFFICULTIES[state['difficulty']]
    print(applyANSI(diff, True, *effs))
    print(f"{len(state['word'])} letters\n")

    guesses_left = state["max_guesses"] - len(state["guesses"])

    for i, guess in enumerate(state["guesses"]):
        rendered = renderGuess(guess, state["word"])
        if i == len(state["guesses"]) - 1 and not u_2:
            write(rendered, 0.005)
        else:
            print(rendered)

    if state["won"]:
        print(f"\nWon in {len(state['guesses'])} guesses!")
    else:
        print(f"\nYou have {guesses_left} guesses.")

# Evaluates a guess and returns colored output
def renderGuess(guess: str, word: str):
    result = [None] * len(word)   # Stores final colored letters
    used = [False] * len(word)    # Tracks matched letters in word

    for i in range(len(word)):
        if guess[i] == word[i]:
            result[i] = applyANSI(guess[i].upper(), True, 'GREEN', 'BOLD')
            used[i] = True

    for i in range(len(word)):
        if result[i] is not None:
            continue

        if guess[i] in word:
            for j in range(len(word)):
                if not used[j] and guess[i] == word[j]:
                    result[i] = applyANSI(guess[i].upper(), True, 'YELLOW', 'BOLD')
                    used[j] = True
                    break
            else:
                result[i] = applyANSI(guess[i].upper(), True, 'WHITE')
        else:
            result[i] = applyANSI(guess[i].upper(), True, 'WHITE')

    return " ".join(result)

# Runs doctests if present
if __name__ == "__main__":
    import doctest
    doctest.testmod()
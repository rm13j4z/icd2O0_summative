```
                        .___.__                           ㅤ⠀⠀⢀⣤⣄  
__  _  _____________  __| _/|  |   ____       _ __  _   _    ⢰⣿⣿⣿⣿⡆ ⣠⣶⣿⣶⡀
\ \/ \/ /  _ \_  __ \/ __ | |  | _/ __ \     | '_ \| | | |   ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
 \     (  <_> )  | \/ /_/ | |  |_\  ___/     | |_) | |_| |    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏
  \/\_/ \____/|__|  \____ | |____/\___  > (_) .__/ \__,  |     ⣿⣿⣿⣿⣿⣿⣿⠋
                         \/           \/     |_|    |___/       ⠻⣿⣿⠿⠉
```
wordle.py
============
A terminal based word guessing game inspired by Wordle.  
![Python](https://img.shields.io/badge/-Python-3572A5?style=for-the-badge)
====
## The game supports:
- [x] **multiple difficulties**
- [x] **custom word lengths (3-9)**
- [x] **ANSI color gradients**
- [x] **common word filtering** 

# Requirements
- Python 3.x
- `wordfreq` library:

## Install dependencies with:
```bash
pip install wordfreq
```

# game_functions.py:

## Data Structures

### WORDLIST : dict[int, list[str]]
Maps word length to available words:

```py
{
  3: [...],
  4: [...],
  ...
  9: [...]
}
```
Words are scraped from [this repo](https://github.com/jonathanwelton/word-lists)


### common_words : dict[int, list[str]]

Filtered version of WORDLIST containing only common English words.
-  Uses  `wordfreq.zipf_frequency()`
-  Filters out rare words
-  Improves fairness and playability

### DIFFICULTIES : dict[int, tuple]
```py
{
  difficulty_number: (name, max_guesses, ansi_effects)
}
```
Example
```py
1: ("Easy", 8, ("LIGHT_GREEN", "BOLD"))
```
Controls:
-  Difficulty name
-  Allowed guesses
-  Display color

### ANSI_EFFECTS : dict[str, str]

Maps readable names to ANSI escape codes used for terminal formatting.
Used to color text & apply effects such as bolding.

### GRADIENTS : dict[str, dict]

Defines animated gradients for the ASCII logo.

Each gradient contains:
-  `colors`: list of ANSI color names
-  `speed`: animation delay

GAME_VARS : dict

Stores global runtime state:
```py
{
  "gradient_name": str | None,
  "gradient": dict
}
```

## Functions
### write(text: str, speed: float, de: bool = False)

Displays text character-by-character in the terminal.
-  `text`: string to display
-  `speed`: delay between characters
-  `de`: disables `newline` if True

---
### clear(animate: bool = False, dontuseLogo: bool = False)

Clears the terminal screen.
-  Displays ASCII logo unless disabled
-  Animates logo if `animate` is True
-  Uses selected gradient colors


---
### debugSettings()

Debug settngs that allow:
-  Manual word selection
-  Custom guesses and difficulty

Returns a new game state dictionary
---
### selectDiff() -> (int,int)

Displays the difficulty selection menu

Returns:
```py
(difficulty_number, max_guesses)
```
---
### selectWordLength() -> int

Prompts the user for a word length
-  Accepts values from 3 to 9
-  Repeats until valid input is entered
---
### applyANSI(text: str, reset: bool, *effects: str) -> str

Applies ANSI effect from `ANSI_EFFECTS` and style formatting to text.

Example:
```py
applyANSI("HELLO", True, "GREEN", "BOLD")
```
Output (literal)
```
\033[38;5;46m\033[1mHELLO\033[0m 
```

---
### refresh(state: dict, u_2: bool = False)

Redraws the game screen.

Displays:
-  Difficulty
-  Word length
-  Guess history
-  Remaining guesses
-  Win message (if applicable)
---
### renderGuess(guess: str, word: str) -> str

Compares a user’s guess `guess` against string `word` and returns a colored, formatted string showing the correctness of each letter, similar to Wordle

Function follows Wordle's color matching rules, including correct handling of duplicate letters

#### Return Value

The function returns a single formatted string where:
- Letters are uppercase
- Letters are seperated by spaces
- Each letter is color coded using ANSI escape codes:
  - **Green** -> correct letter, correct position
  - **Yellow** -> correct letter, wrong positioon
  - **White** -> letter not present in the word

Example output (visual)
```
H U M O U R
```
Literal (if word is humour)
`"GREEN": \033[38;5;46m` in `ANSI_EFFECTS` dictonary.
```
\033[38;5;46mH\033[0m \033[38;5;46mU\033[0m \033[38;5;46mM\033[0m \033[38;5;46mO\033[0m \033[38;5;46mU\033[0m \033[38;5;46mR\033[0m
```

#### Data Structures

result : list[str | None]
```py
result = [None] * len(word)
```
- Stores the final rendered input for each letter position
- <mark>Each index corresponds directly to a character position in the guess</mark>
- Initially set to None to indicate that letter has not yet been evaluated
- Each index contains a formatted ANSI string after processing


used : list[bool]
```py
used = [False] * len(word)
```
- Tracks which letters in `word` have already been matched
- Prevents letters from being counted multiple times

Each index in used corresponds to the same index in the target word:
`used[i] == False` -> that letter has not been matched yet
`used[i] == true` -> that letter has already been matched with green or yellow
```
Word:  APPLE
Guess: ALLEY
```
The word contains a singular A along with an L, and the guess contains 2 L
If the program only checked `if guess[i] in word`, both L’s would incorrectly be marked yellow, even though the word only has one L

#### Algorithm

##### I. Green Letters (correct position)
```py
for i in range(len(word)):
    if guess[i] == word[i]:
        result[i] = applyANSI(guess[i].upper(), True, 'GREEN', 'BOLD')
        used[i] = True
```
Compares each guessed letter with the same index in `word`
If they match letter marked green, and corresponding pos in `used` is set to `True`

##### II. Yellow Letters (incorrect position)
```py
for i in range(len(word)):
    if result[i] is not None:
        continue
```
Loop iterates over each character pos in the guess again
Skips letters marked green / ensures green letters are not recolored
```py
if guess[i] in word:
    for j in range(len(word)):
        if not used[j] and guess[i] == word[j]:
            result[i] = applyANSI(guess[i].upper(), True, 'YELLOW', 'BOLD')
            used[j] = True
            break
```
Searches for a matching unused letter in the word
  -> Marks it as yellow only if an unused match exists

##### III. Default: White Letters
Letter is marked white if not green or has no unused match in the word
```py
result[i] = applyANSI(guess[i].upper(), True, 'WHITE')
```

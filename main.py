from game_functions import *

# Starts a new game and handles optional debug mode
def startGame(debugPrompted: bool):
    # Ask the user whether to enter debug mode (if prompte)
    if debugPrompted:
        if input(f'Enter debug mode? {applyANSI("[Y/N]", True, "BOLD")}: ').lower() == "y":
            return debugSettings()

    # Normal game setup
    clear()
    diff = selectDiff()                # Select difficulty
    word_length = selectWordLength()   # Select word length

    # Create and return a new game state
    return newGame({
        "debug": False,
        "word_length": word_length,
        "difficulty": diff[0],
        "max_guesses": diff[1]
    })


# Prompts the user until a valid guess is entered
def get_valid_guess(state, word_length):
    while True:
        guess = input().lower().strip()

        # Validate guess length
        if len(guess) != word_length:
            msg = f"Word must be {word_length} letters!"

        # Prevent duplicate guesses
        elif guess in state["guesses"]:
            msg = "Word already entered!"

        # Ensure guess is a valid dictionary word (UNLESS in debug mode)
        elif not state["debug"] and guess not in WORDLIST[word_length]:
            msg = "Not a valid word!"

        # Guess is valid
        else:
            return guess

        # Show error message and redraw game screen
        print(msg)
        time.sleep(0.6)
        clear()
        refresh(state, True)


# Initial prompt for entering debug mode
start = input(f'{applyANSI("[S for debug mode]", True, "BOLD")}\n''Press any key to continue...\n> ').lower()

# -------------------- Theme Selector --------------------

n = 0
while True:
    l_gradients = list(GRADIENTS.keys())

    clear(False, True)
    print(HUGE_STR)
    print("Select a Theme:\n")

    # Display each available gradient with animated colors
    for i, name in enumerate(l_gradients):
        grad = GRADIENTS[name]["colors"]
        f_str = ""

        for le, ch in enumerate(name.replace("_", " ")):
            color = grad[le % len(grad)]
            f_str += applyANSI(ch, True, color, "BOLD")

        if n >= 1:
            print(f" {i+1}. {f_str}")
        else:
            write(f" {i+1}. {f_str}", 0.003)

    # Get user selection
    theme = input("> ")
    if theme.isdigit() and int(theme) <= len(l_gradients):
        selected_name = l_gradients[int(theme) - 1]
        GAME_VARS["gradient"] = GRADIENTS[selected_name]
        GAME_VARS["gradient_name"] = selected_name
        break

    print(applyANSI('Enter a number in the range!', True, 'BOLD'))
    n += 1


# -------------------- Main Game --------------------

while True:
    clear(True, False)

    # Start a new game
    state = startGame(start == 's')
    word = state["word"]
    word_length = len(word)

    clear()
    refresh(state)

    # Show word in debug mode
    if state["debug"]:
        print(word)

    # Guessing loop
    while len(state["guesses"]) < state["max_guesses"]:
        guess = get_valid_guess(state, word_length)
        state["guesses"].append(guess)

        clear()
        if guess == word:
            state["won"] = True
            refresh(state)
            break

        refresh(state)

    # Loss condition
    if not state["won"]:
        print(f'You lost! Word was {applyANSI(word, True, "BOLD")}')

    # Ask to play again
    while True:
        play_again = input(
            f"\nPlay Again {applyANSI('[Y/N]', True, 'BOLD')}?: "
        ).lower()
        if play_again in ("y", "n"):
            break
        print("Enter Y or N!")

    if play_again == "n":
        break
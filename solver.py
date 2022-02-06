'''wordle solver
    for each word1
    try assuming that the word1 is the next guess
    loop through 

    for each word2 
    try assuming that the word2 is the correct solution

    for each word3
    assuming that word2 is correct and u guess word1, check if word3 is a valid guess
'''

from enum import Enum, auto
from copy import deepcopy


DICTIONARY_FILE = "dictionary.txt"
WORD_LENGTH = 5
LETTERS_IN_ALPHABET = 26


class GuessOutcome(Enum):
    '''enum of different types of guess outcomes'''
    CORRECT_POSITION = auto()
    CORRECT_LETTER = auto()
    INCORRECT = auto()
    UNKNOWN = auto()


class GuessState:
    '''guess state for wordle'''

    def __init__(self):
        self.correct_letters = []
        self.incorrect_letters = []
        self.correct_placement = ['' for _ in range(WORD_LENGTH)]

    def is_valid_guess(self, word):
        ''' returns if word is a valid guess given the guess state'''
        correct_letters = []
        for i, letter in enumerate(word):
            if letter in self.correct_letters and letter not in correct_letters:
                correct_letters.append(letter)
            # if letter is known to be incorrect
            if letter in self.incorrect_letters:
                return False
            # if letter is known to be correct but in wrong place
            elif letter in self.correct_letters and self.correct_placement[i] != letter and self.correct_placement[i] != "":
                return False
            # [a,b,c,d] in correct_letters and guess abcaf
            elif len(correct_letters) + WORD_LENGTH - 1 - i < len(self.correct_letters):
                return False

    def update(self, word, outcomes):
        ''' updates the guess state based on the outcome of the guess'''
        for i, letter in enumerate(word):
            outcome = outcomes[i]
            if outcome == GuessOutcome.CORRECT_POSITION:
                self.correct_placement[i] = letter
                if letter not in self.correct_letters:
                    self.correct_letters.append(letter)
            elif outcome == GuessOutcome.CORRECT_LETTER:
                if letter not in self.correct_letters:
                    self.correct_letters.append(letter)
            elif outcome == GuessOutcome.INCORRECT:
                if letter not in self.incorrect_letters:
                    self.incorrect_letters.append(letter)
    
    def is_done(self):
        ''' returns if the guess state is done'''
        return all(letter != '' for letter in self.correct_placement)


def _read_dictionary(filename):
    '''Reads the dictionary file and returns a set of words.'''
    with open(filename, "r") as f:
        words = list(f.read().split())
    print(f"Read {len(words)} words from {filename}")
    return words

def get_outcome(answer, guess):
    '''returns the outcome of the guess knowing the answer'''
    res = []
    for i, letter in enumerate(guess):
        if letter not in answer:
            res.append(GuessOutcome.INCORRECT)
        elif letter == answer[i]:
            res.append(GuessOutcome.CORRECT_POSITION)
        else:
            res.append(GuessOutcome.CORRECT_LETTER)
    return res

def get_outcome_from_str(outcome_str):
    '''returns the outcome from user input outcome str'''
    # check length
    if len(outcome_str) != WORD_LENGTH:
        raise ValueError(f"Outcome string must be of length {WORD_LENGTH}")
    res = []
    for letter in outcome_str:
        if letter == 'c':
            res.append(GuessOutcome.CORRECT_POSITION)
        elif letter == 'i':
            res.append(GuessOutcome.INCORRECT)
        elif letter == 'l':
            res.append(GuessOutcome.CORRECT_LETTER)
        else:
            raise ValueError(f"Invalid outcome character {letter}")
    return res

class Solver:
    '''worder solver'''

    def __init__(self):
        self.words = _read_dictionary(DICTIONARY_FILE)
        self.active_words = []
        self.guesses = []
        self.state = None
        self.best_guess = ""
        self.reset()

    def get_best_guess(self):
        '''returns the best guess'''
        res = ""
        res_evs = None
        count = 0
        for word in self.active_words:
            print(count)
            ev = self._get_word_ev(word)
            if res_evs is None or ev < res_evs:
                res = word
                res_evs = ev
            count += 1
        return res

    def guess(self, word, outcome_str):
        '''guesses a word and updates the state'''
        self.guesses.append(word)
        self.state.update(word, get_outcome_from_str(outcome_str))
        self.best_guess = self.get_best_guess()

    def _get_word_ev(self, guess):
        '''returns the total number of possible guesses after a possible guess'''
        ev = 0
        for word in self.active_words:
            ev += self._get_active_words_after_guess(word, guess)
        return ev

    def _get_active_words_after_guess(self, answer, guess):
        # copy the state
        state_after_guess = deepcopy(self.state)
        state_after_guess.update(guess, get_outcome(answer, guess))
        res = 0
        for word in self.active_words:
            if state_after_guess.is_valid_guess(word):
                res += 1
        return res

    def is_game_done(self):
        '''returns if the game is done'''
        return self.state.is_done()

    def reset(self):
        '''reset the solver'''
        self.active_words = self.words.copy()
        self.guesses = []
        self.state = GuessState()
        self.best_guess = self.get_best_guess()


def main():
    '''main function'''
    solver = Solver()
    while not solver.is_game_done():
        print(f'Optimal guess: {solver.best_guess}')
        word = input("Enter a word: ")
        ok = False
        while not ok:
            try:
                ok = True
                outcome_str = input("Enter outcome: ")
                outcome = get_outcome_from_str(outcome_str)

            except ValueError:
                ok = False
        solver.guess(word, outcome)


if __name__ == "__main__":
    main()

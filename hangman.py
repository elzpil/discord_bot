import random

class Hangman:
    words = ['python', 'discord', 'bot', 'programming', 'hangman']
    
    def __init__(self):
        self.word = random.choice(Hangman.words)
        self.guessed_letters = set()
        self.lives = 6

    def display_word(self):
        display = ' '.join([f'`{letter}`' if letter in self.guessed_letters else '`_`' for letter in self.word])        
        print(f'Displaying word: {display}')
        print(f'Guessed letters: {self.guessed_letters}')
        return display
    def guess(self, letter):
        if letter in self.guessed_letters:
            return 'You already guessed that letter.'
        
        self.guessed_letters.add(letter)
        
        if letter in self.word:
            if set(self.word) <= self.guessed_letters:
                return f'Congratulations! You won! The word was {self.word}'
            return f'Good guess! {self.display_word()}'
        else:
            self.lives -= 1
            if self.lives == 0:
                return f'Sorry, you lost. The word was {self.word}'
            return f'Wrong guess. You have {self.lives} lives left. {self.display_word()}'

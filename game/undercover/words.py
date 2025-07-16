import random

def get_word():
    return "Sun"
    with open('game/undercover/words.txt', 'r') as f:
        words = f.read().splitlines()
    return random.choice(words)
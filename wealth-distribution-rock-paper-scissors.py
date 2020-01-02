from time import sleep
# 64 € jaanile 100 €
import random

from enum import Enum
from dataclasses import dataclass

from asciimatics.screen import Screen
from more_itertools import pairwise
import numpy as np


class CONF:
    initial_wealth = 5 # smaller numbers give more dramatic results
    debt_treshold = 0  # should be <= 0; or None for unlimited debt
    revolt_if_gini_too_large = False  # TODO: revolution unimplemented


class CHOICE(Enum):
    paper = 'smothers'
    rock = 'smashes'
    scissors = 'slices'


CHOICES = list(CHOICE)

BEATS = {
    CHOICE.paper: CHOICE.scissors,
    CHOICE.rock: CHOICE.paper,
    CHOICE.scissors: CHOICE.rock,
}


class MOOD(Enum):
    happy = '😃'
    neutral = '😐'
    worried = '😟'
    sad = '😞'
    angry = '😠'  # TODO: revolution unimplemented
    fearful = '😨'
    shocked = '🤯'
    exploding = '💥'


@dataclass
class Player:
    name: str
    wealth: int
    mood: MOOD
    choice: CHOICE
    result: str

    def __str__(self):
        wealth_bar = ('$' * self.wealth if self.wealth > 0
                      else '-' * abs(self.wealth))
        return f'{self.name:7} | {self.mood.value} | {self.wealth:3} | {self.result:31} | {wealth_bar}'


PLAYERS = [Player(name, CONF.initial_wealth, MOOD.neutral, None, 'Waiting to start...')
           for name in ('Alice', 'Bob', 'Cecil', 'Dave', 'Emma', 'Fred', 'George',
                        'Helen', 'Ian', 'Jane', 'Kevin', 'Lisa', 'Michael',
                        'Nina', 'Oliver')]


def play_game(screen):
    calculate_stats_and_update_screen(screen)
    screen.wait_for_input(3)
    while True:
        play_round(PLAYERS)
        calculate_stats_and_update_screen(screen)
        if q_key_pressed(screen):
            return
        sleep(1)


def calculate_stats_and_update_screen(screen):
    gini = calculate_gini(PLAYERS)
    total = sum(player.wealth for player in PLAYERS)
    abstotal = sum(abs(player.wealth) for player in PLAYERS)
    update_screen(screen, PLAYERS, gini, total, abstotal)


def play_round(players):
    players = players if CONF.debt_treshold is None else [
        player for player in players if player.wealth > CONF.debt_treshold
    ]
    for a, b in pairwise(players):
        rock_paper_scissors(a, b)


def rock_paper_scissors(a, b):
    if CONF.debt_treshold is not None and (a.wealth == CONF.debt_treshold
                                           or b.wealth == CONF.debt_treshold):
        return
    a.choice = random.choice(CHOICES)
    b.choice = random.choice(CHOICES)
    if a.choice == BEATS[b.choice]:
        result = win_lose(a, b)
    elif b.choice == BEATS[a.choice]:
        result = win_lose(b, a)
    else:
        a.mood = b.mood = MOOD.neutral
        result = f'{a.name[0]} ties {b.name[0]}: {a.choice.name} and {b.choice.name}'
    a.result = b.result = result


def win_lose(a, b):
    a.wealth += 1
    a.mood = MOOD.happy
    b.wealth -= 1
    b.mood = (MOOD.worried if b.wealth > 0
              or CONF.debt_treshold is not None and b.wealth > CONF.debt_treshold
              else MOOD.sad)
    return f'{a.name[0]} wins {b.name[0]}: {a.choice.name} {a.choice.value} {b.choice.name}'


def update_screen(screen, players, gini, total, abstotal):
    screen.clear()
    for i, player in enumerate(players):
        screen.print_at(str(player), 0, i, Screen.COLOUR_RED, Screen.A_BOLD)
    screen.print_at('-' * 70, 0, i + 1)
    screen.print_at(f'Gini index: {gini}', 0, i + 2)
    screen.print_at(f'Total wealth: {total}', 0, i + 3)
    screen.print_at(f'Total absolute wealth: {abstotal}', 0, i + 4)
    screen.refresh()


def q_key_pressed(screen):
    evt = screen.get_key()
    return evt in (ord('Q'), ord('q'))


def calculate_gini(players):
    '''
    Gini coefficient calculation by Warren Weckesser,
    https://stackoverflow.com/a/39513799/258772.
    Concise implementation, but O(n**2) in time and memory, where n = len(xs).
    '''
    xs = rebase_to_minimum([p.wealth for p in players])
    # Mean absolute difference
    mad = np.abs(np.subtract.outer(xs, xs)).mean()
    # Relative mean absolute difference
    rmad = mad / np.mean(xs)
    # Gini coefficient
    g = 0.5 * rmad
    return g


def rebase_to_minimum(xs):
    m = min(xs)
    if m >= 0:
        return xs
    rebased = [abs(m) + x for x in xs]
    return rebased


if __name__ == '__main__':
    Screen.wrapper(play_game)

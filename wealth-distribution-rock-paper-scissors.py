import sys
from time import sleep
import random

from enum import Enum
from dataclasses import dataclass

from asciimatics.screen import Screen
from more_itertools import pairwise
import numpy as np


class CONF:
    initial_wealth = 5  # should be >= 1; smaller numbers give more dramatic results
    debt_treshold = 0  # should be <= 0; or None for unlimited debt
    gini_revolution_treshold = 0.7  # should be > 0 and < 1; None for no revolution


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
    angry = '😠'
    fearful = '😨'
    exploding = '💥'
    shocked = '🤯'
    relieved = '😌'


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

    def __hash__(self):
        return hash(self.name)


PLAYERS = [Player(name, CONF.initial_wealth, MOOD.neutral, None, 'Waiting to start...')
           for name in ('Alice', 'Bob', 'Cecil', 'Dave', 'Emma', 'Fred', 'George',
                        'Helen', 'Ian', 'Jane', 'Kevin', 'Lisa', 'Michael',
                        'Nina', 'Oliver')]


def play_game(screen):
    calculate_stats_and_update_screen(screen)
    screen.wait_for_input(3)  # 3 second delay before start
    while True:
        play_round(PLAYERS)
        gini = calculate_stats_and_update_screen(screen)
        if revolution_required(gini):
            revolt(PLAYERS, screen)
        sleep(1)


def calculate_stats_and_update_screen(screen):
    if q_key_pressed(screen):  # exit when Q pressed
        sys.exit(0)
    gini = calculate_gini(PLAYERS)
    total = sum(player.wealth for player in PLAYERS)
    abstotal = sum(abs(player.wealth) for player in PLAYERS)
    update_screen(screen, PLAYERS, gini, total, abstotal)
    return gini


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


def revolt(players, screen):
    # 1. before_revolt
    for player in players:
        if player.wealth > CONF.initial_wealth:
            player.mood = MOOD.fearful
            player.result = 'Tense times, build castles...'
        elif player.wealth > 0:
            player.mood = MOOD.worried
            player.result = 'Change is coming...'
        else:
            player.mood = MOOD.angry
            player.result = 'Give back our share!'

    calculate_stats_and_update_screen(screen)
    sleep(3)  # let observer see that revolution is coming

    # 2. revolt
    for player in players:
        player.mood = MOOD.exploding
        player.result = '...'

    calculate_stats_and_update_screen(screen)
    sleep(2)

    # 3. after revolt
    the_haves = {player for player in players if player.wealth >
                 CONF.initial_wealth}
    the_have_nots = {player for player in players if player.wealth <= 0}
    the_rest = set(players) - the_haves - the_have_nots

    redistributed_wealth = sum(player.wealth for player in the_haves)

    # assume "the haves" keep half of initial wealth
    for player in the_haves:
        player.wealth = CONF.initial_wealth // 2
        player.mood = MOOD.shocked
        player.result = 'Gosh!'

    redistributed_wealth -= sum(player.wealth for player in the_haves)

    have_nots_count = len(the_have_nots)
    share = redistributed_wealth // have_nots_count
    for player in the_have_nots:
        player.wealth = share
        player.mood = MOOD.happy
        player.result = 'Yay!'
    # someone random gets a little extra if the share should be fractional
    player.wealth += redistributed_wealth - have_nots_count * share

    for player in the_rest:
        player.mood = MOOD.relieved
        player.result = "Whew!"

    calculate_stats_and_update_screen(screen)
    sleep(3)


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


def revolution_required(gini):
    return CONF.gini_revolution_treshold is not None and gini >= CONF.gini_revolution_treshold


if __name__ == '__main__':
    Screen.wrapper(play_game)

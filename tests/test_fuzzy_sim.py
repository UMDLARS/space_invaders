import random

import pytest
import sys

from littlepython import Compiler

from CYLGame import GameLanguage, GameRunner
from CYLGame.Player import Room

from ..game import SpaceInvaders as Game


def get_fuzzing_seeds(new_seed_count=10):
    previous_bad_seeds = [3000701892487371629, 8579693467990630982, 1544972200648834169]
    return previous_bad_seeds + [random.randint(0, sys.maxsize) for _ in range(new_seed_count)]


@pytest.mark.parametrize("seed", get_fuzzing_seeds())
def test_run_for_playback(seed):
    # Make default player bot
    compiler = Compiler()
    bot = Game.default_prog_for_bot(GameLanguage.LITTLEPY)
    prog = compiler.compile(bot)
    room = Room([prog])

    runner = GameRunner(Game, room)
    runner.run_for_playback(seed=seed)


@pytest.mark.parametrize("seed", get_fuzzing_seeds())
def test_run_for_score(seed):
    # Make default player bot
    compiler = Compiler()
    bot = Game.default_prog_for_bot(GameLanguage.LITTLEPY)
    prog = compiler.compile(bot)
    room = Room([prog])

    runner = GameRunner(Game, room)
    runner.run_for_avg_score(1, seed=seed, func=sum)

# Winning Connections

This is a small python module to check if a player at a given point in a game
of [Connections](https://www.nytimes.com/games/connections) has a winning
strategy, even if they didn't know anything about the words written on the slots (squares).
A winning strategy here is one that leads to a win, even if you have the worst of luck.

It uses Phillip M. Feldman's [combinatorics.py](https://pypi.org/project/Combinatorics/) to generate
the possible solutions at a given state of the game.

## Why?

I was playing a game one day and found myself stumped on the last 8 words, after having found the
first two groups without a mistake. I asked myself if there is a way I could at least save myself from losing,
given the 4 remaining attempts. Turns out, there isn't. You'd need at least 6 if you're unlucky.

## How to use it

### As a script
```bash
$ python3 connections.py -t 4
There is no winning strategy. 🫤
$ python3 connections.py -t 5
There is no winning strategy. 🫤
$ python3 connections.py -t 6
There is a winning strategy! 🥳
```

### As a library
```python
from connections import Slot, GameParams, State, has_winning_strat

slots = Slot.create_n(8)
params = GameParams(slots, GROUP_SIZE=4)
start_state = State(params, moves=[])
print(has_winning_strat(start_state, n_tries=4))
```

## Performance
It scales quite well with the number of attempts/tries, because `Solution.get_possible_selections` removes a lot of redundant
selections you can make. For example for the first move in a game, it returns only one possible move (selecting arbitrary slots), because at this point the player has the same amount of information for each of them.

It currently doesn't scale very well with the number of slots. That's because to find the possible results for a selection, it enumerates all possible solutions (group assignments) to a game.

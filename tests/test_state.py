from typing import List
from connections import State, Move, Result, GameParams, Slot
from combinatorics import n_choose_m

def test_basis() -> None:
    slots = list(Slot.create_n(8))
    params = GameParams(slots)
    moves: List[Move] = []
    state = State(params, moves)

    sets = {frozenset(slots[0:4]), frozenset(slots)}
    basis = state._smallest_basis(sets)

    assert all(len(b0 & b1) == 0 for b0 in basis for b1 in basis if b0 != b1), f"Not all elements in {basis} are disjoint"
    

def test_possible_selections_helper() -> None:
    slots = list(Slot.create_n(8))
    params = GameParams(slots)
    s0 = State(params, [])
    sets = [frozenset(slots[0:2]), frozenset(slots[2:4]), frozenset(slots[4:6])]
    selects = list(s0._get_possible_selections(sets, 3))

    assert all(len(s) == 3 for s in selects), "Not all sets have the correct length"

    # You can either pick 2 from one set and 1 from another, or pick 3 from
    # different sets each.
    assert len(selects) == len(sets) * (len(sets)-1) + n_choose_m(len(sets), 3) # type: ignore

def test_possible_selections() -> None:
    slots = list(Slot.create_n(8))
    params = GameParams(slots)
    moves: List[Move] = []
    state = State(params, moves)
    selects = list(state.get_possible_selections())
    assert len(selects) == 1
    assert all(len(s) == 4 for s in selects), "Not all sets have the correct length"

    moves += [Move(frozenset(slots[0:4]), Result.OFF_BY_MORE)]
    state = State(params, moves)
    selects = list(state.get_possible_selections())

    # There are 5 ways to pick 4 elements from two groups of 4.
    # One of them has been selected already however, so it is excluded.
    assert len(selects) == 4
    assert all(len(s) == 4 for s in selects), "Not all sets have the correct length"

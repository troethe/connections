from typing import List, Tuple, Iterator, FrozenSet, Set
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum
from itertools import islice
import argparse

from combinatorics import labeled_balls_in_unlabeled_boxes


class Slot(int):
    @classmethod
    def from_int(cls, i: int) -> "Slot":
        return cls(i)

    @classmethod
    def create_n(cls, n: int) -> List["Slot"]:
        return [cls.from_int(i) for i in range(n)]


class Result(Enum):
    OFF_BY_MORE = 0
    OFF_BY_ONE = 1
    CORRECT = 3


@dataclass
class Move:
    selection: FrozenSet[Slot]
    result: Result


@dataclass
class GameParams:
    slots: List[Slot]
    GROUP_SIZE: int = 4


@dataclass
class Solution:
    groupings: Tuple[Tuple[Slot]]
    params: GameParams

    def result_for_move(self, selection: FrozenSet[Slot]) -> Result:
        group_counts = [
            sum(1 for s in group if s in selection) for group in self.groupings
        ]

        if self.params.GROUP_SIZE in group_counts:
            return Result.CORRECT
        elif self.params.GROUP_SIZE - 1 in group_counts:
            return Result.OFF_BY_ONE
        else:
            return Result.OFF_BY_MORE


@dataclass
class State:
    params: GameParams
    moves: List[Move]

    def smallest_basis(self, sets: Set[FrozenSet[Slot]]) -> Set[FrozenSet[Slot]]:
        participates_in: defaultdict[Slot, FrozenSet[FrozenSet[Slot]]] = defaultdict(
            lambda: frozenset()
        )
        for subset in sets:
            for item in subset:
                participates_in[item] |= {subset}
        inv_participates_in: defaultdict[
            FrozenSet[FrozenSet[Slot]], FrozenSet[Slot]
        ] = defaultdict(lambda: frozenset())
        for slot in participates_in:
            inv_participates_in[participates_in[slot]] |= {slot}

        return set(inv_participates_in.values())

    @staticmethod
    def _get_possible_selections(
        sets: List[FrozenSet[Slot]], n_items: int = 0
    ) -> Iterator[FrozenSet[Slot]]:
        if n_items == 0:
            yield frozenset()
            return
        if len(sets) == 0:
            return

        curent_set = sets[0]
        for i in range(min(n_items, len(curent_set)) + 1):
            selection = frozenset(islice(curent_set, i))
            for further_selection in State._get_possible_selections(
                sets[1:], n_items - i
            ):
                yield selection | further_selection

    def get_possible_selections(self) -> Iterator[FrozenSet[Slot]]:
        prev_selections = {m.selection for m in self.moves} | {
            frozenset(self.params.slots)
        }
        basis = self.smallest_basis(prev_selections)
        return self._get_possible_selections(list(basis), self.params.GROUP_SIZE)

    def possible_solutions(self) -> Iterator[Solution]:
        n_slots = len(self.params.slots)
        n_groups = n_slots // self.params.GROUP_SIZE
        group_sizes = [self.params.GROUP_SIZE] * n_groups
        for combi in labeled_balls_in_unlabeled_boxes(n_slots, group_sizes):  # type: ignore
            solution = Solution(combi, self.params)

            # Check if the result of a prior move rules out this solution, else `yield` it
            for move in self.moves:
                if solution.result_for_move(move.selection) != move.result:
                    break
            else:
                yield solution

    def get_possible_results(self, selection: FrozenSet[Slot]) -> List[Result]:
        result_counts: defaultdict[Result, int] = defaultdict(lambda: 0)
        for solution in self.possible_solutions():
            result_counts[solution.result_for_move(selection)] += 1

        return [result for result, count in result_counts.items() if count > 0]


def has_winning_strat(state: State, n_tries: int = 4) -> bool:
    if any(s.result == Result.CORRECT for s in state.moves):
        return True
    if n_tries == 0:
        return False

    for selection in state.get_possible_selections():
        for result in state.get_possible_results(selection):
            move = Move(selection, result)
            next_state = State(state.params, state.moves + [move])

            if not has_winning_strat(next_state, n_tries - 1):
                break
        else:
            return True

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Checks wether there is a winning strategy given a certain state of a game of "Connections"'
    )
    parser.add_argument("-s", "--slots", type=int, default=8)
    parser.add_argument("-t", "--tries", type=int, default=4)
    args = parser.parse_args()

    slots = Slot.create_n(args.slots)
    params = GameParams(slots, GROUP_SIZE=4)
    start_state = State(params, moves=[])
    if has_winning_strat(start_state, n_tries=args.tries):
        print("There is a winning strategy! 🥳")
    else:
        print("There is no winning strategy. 🫤")

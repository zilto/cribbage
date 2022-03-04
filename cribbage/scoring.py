from itertools import combinations
from collections import Counter
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Union

from card_objects import Card, Deck


# TODO could refactoring scoring through ScoringCheck subclasses
class ScoringCheck(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def check(self, hand: list[Card], cut: Card):
        pass


class SameRank(ScoringCheck):
    def check(self, hand, cut) -> tuple[int, int, int]:
        full_hand = hand + [cut]
        full_hand_rank = [c.rank for c in full_hand]

        pair, triplet, four = 0, 0, 0
        for rank, count in Counter(full_hand_rank).items():
            if count == 2:
                pair += 1
            elif count == 3:
                triplet += 1
            elif count == 4:
                four += 1

        return pair, triplet, four


class SameSuit(ScoringCheck):
    def check(self, hand, cut) -> tuple[bool, bool]:
        player_hand_suit = [c.suit for c in hand]
        most_common_suit = Counter(player_hand_suit).most_common(1)

        suit4, suit5 = False, False
        if most_common_suit[0][1] == 4:  # [1] is the count
            suit4 = True
            if most_common_suit[0][0] == cut.suit:  # [0] is the suit
                suit5 = True

        return suit4, suit5


class JackSuit(ScoringCheck):
    def check(self, hand, cut) -> bool:
        jack_suit = False
        for card in hand:
            if (card.rank == 11) and (card.suit == cut.suit):
                jack_suit = True

        return jack_suit


class RankSeries(ScoringCheck):
    def check(self, hand, cut) -> tuple[int, int, int]:
        full_hand = hand + [cut]
        full_hand_rank = [c.rank for c in full_hand]

        series3, series4, series5 = 0, 0, 0

        counter = Counter(full_hand_rank)
        prev_rank = -1
        consecutive = 1
        series_multiplier = 1

        for rank in sorted(counter.keys()):
            if (rank-1) == prev_rank:
                consecutive += 1
                series_multiplier *= counter[rank]
            else:
                if consecutive == 3:
                    series3 += 1 * series_multiplier
                elif consecutive == 4:
                    series4 += 1 * series_multiplier
                elif consecutive == 5:
                    series5 += 1 * series_multiplier

                consecutive = 1
                series_multiplier = 1
            prev_rank = rank

        return series3, series4, series5


class Fifteen(ScoringCheck):
    def check(self, hand, cut) -> int:
        full_hand = hand + [cut]
        full_hand_value = [c.value for c in full_hand]

        fifteen = 0
        # TODO search can be optimized
        for n_cards in range(2, 5):
            for c in combinations(full_hand_value, n_cards):
                if sum(c) == 15:
                    fifteen += 1

        return fifteen


@dataclass_json
@dataclass
class Scoresheet:
    hand: list[Card]
    cut: Card

    score: int = 0

    fifteen: int = 0

    pair: int = 0
    triplet: int = 0
    four: int = 0

    series3: int = 0
    series4: int = 0
    series5: int = 0

    suit4: bool = False
    suit5: bool = False

    jack_suit: bool = False

    @property
    def full_hand(self) -> list[Card]:
        return self.hand.copy() + [self.cut]

    def check_same_rank(self) -> tuple[int, int, int]:
        pair, triplet, four = 0, 0, 0

        full_hand_rank = [c.rank for c in self.full_hand]
        for rank, count in Counter(full_hand_rank).items():
            if count == 2:
                pair += 1
            elif count == 3:
                triplet += 1
            elif count == 4:
                four += 1

        return pair, triplet, four

    def check_same_suit(self) -> tuple[bool, bool]:
        suit4, suit5 = False, False

        player_hand_suit = [c.suit for c in self.hand]
        most_common_suit = Counter(player_hand_suit).most_common(1)

        if most_common_suit[0][1] == 4:  # [1] is the count
            suit4 = True
            if most_common_suit[0][0] == self.cut.suit:  # [0] is the suit
                suit5 = True

        return suit4, suit5

    def check_jack_suit(self) -> bool:
        jack_suit = False

        for card in self.hand:
            if (card.rank == 11) and (card.suit == self.cut.suit):
                jack_suit = True

        return jack_suit

    def check_series(self) -> tuple[int, int, int]:
        series3, series4, series5 = 0, 0, 0

        full_hand_rank = [c.rank for c in self.full_hand]
        counter = Counter(full_hand_rank)

        prev_rank = -1
        consecutive = 1
        series_multiplier = 1
        for rank in sorted(counter.keys()):
            if (rank-1) == prev_rank:
                consecutive += 1
                series_multiplier *= counter[rank]
            else:
                if consecutive == 3:
                    series3 += 1 * series_multiplier
                elif consecutive == 4:
                    series4 += 1 * series_multiplier
                elif consecutive == 5:
                    series5 += 1 * series_multiplier

                consecutive = 1
                series_multiplier = 1
            prev_rank = rank

        return series3, series4, series5

    def check_fifteen(self) -> int:
        fifteen = 0

        full_hand_value = [c.value for c in self.full_hand]
        # TODO search can be optimized
        for n_cards in range(2, 5):
            for c in combinations(full_hand_value, n_cards):
                if sum(c) == 15:
                    fifteen += 1

        return fifteen

    def compute_score(self) -> int:
        point_value = {
            "fifteen": 2,
            "pair": 2,
            "triplet": 6,
            "four": 12,
            "series3": 3,
            "series4": 4,
            "series5": 5,
            "suit4": 4,
            "suit5": 5,
            "jack_suit": 1
        }

        score = 0

        score += self.fifteen * point_value["fifteen"]
        score += self.pair * point_value["pair"]
        score += self.triplet * point_value["triplet"]
        score += self.four * point_value["four"]
        score += self.series3 * point_value["series3"]
        score += self.series4 * point_value["series4"]
        score += self.series5 * point_value["series5"]

        if self.suit5:
            score += point_value["suit5"]
        elif self.suit4:
            score += point_value["suit4"]

        if self.jack_suit:
            score += point_value["jack_suit"]

        return score

    def __post_init__(self) -> None:
        self.fifteen = self.check_fifteen()
        self.pair, self.triplet, self.four = self.check_same_rank()
        self.series3, self.series4, self.series5 = self.check_series()
        self.suit4, self.suit5 = self.check_same_suit()
        self.jack_suit = self.check_jack_suit()

        self.score = self.compute_score()


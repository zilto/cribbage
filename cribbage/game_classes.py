import random
from collections import Counter
from itertools import combinations
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass
class Card:
    rank: int
    suit: int

    def __repr__(self):
        rank_conversion = {
            1: "A",
            11: "J",
            12: "Q",
            13: "K"
        }

        suit_conversion = {
            0: "♠",
            1: "♣",
            2: "♥",
            3: "♦"
        }
        return f"<Card {rank_conversion.get(self.rank, self.rank)}{suit_conversion.get(self.suit)}>"

    def __eq__(self, other):
        return self.rank == other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __ge__(self, other):
        return self.rank >= other.rank


@dataclass
class Player:
    name: str
    score: int
    player_hand: list[Card] = field(default_factory=list)


class Deck:
    def __init__(self):
        self.cards = [Card(rank=r, suit=s) for r in range(1, 14) for s in range(4)]
        random.shuffle(self.cards)

    def deal_cards(self, n_cards: int):
        return [self.cards.pop() for i in range(n_cards)]


@dataclass_json
@dataclass
class Hand:
    player_hand: list[Card]
    cut_card: Card

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

    def get_fullhand(self) -> list[Card]:
        return self.player_hand.copy() + [self.cut_card]

    def check_same_rank(self) -> tuple[int, int, int]:
        pair, triplet, four = 0, 0, 0

        full_hand_rank = [c.rank for c in self.get_fullhand()]
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

        player_hand_suit = [c.suit for c in self.player_hand]
        most_common_suit = Counter(player_hand_suit).most_common(1)

        if most_common_suit[0][1] == 4:  # [1] is the count
            suit4 = True
            if most_common_suit[0][0] == self.cut_card.suit:  # [0] is the suit
                suit5 = True

        return suit4, suit5

    def check_jack_suit(self) -> bool:
        jack_suit = False

        for card in self.player_hand:
            if (card.rank == 11) and (card.suit == self.cut_card.suit):
                jack_suit = True

        return jack_suit

    def check_series(self) -> tuple[int, int, int]:
        series3, series4, series5 = 0, 0, 0

        full_hand_rank = [c.rank for c in self.get_fullhand()]
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

        rounded_figures = [c.rank if c.rank < 11 else 10 for c in self.get_fullhand()]
        for size in range(2, 5):
            for c in combinations(rounded_figures, size):
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


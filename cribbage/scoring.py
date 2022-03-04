from itertools import combinations
from collections import Counter
from abc import ABC, abstractmethod
from dataclasses import dataclass


from card_objects import Card, Deck


class ScoringCheck(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def check(self, hand: list[Card], cut: Card):
        raise NotImplementedError


class SameRank(ScoringCheck):
    def check(self, hand: list[Card], cut: Card) -> tuple[int, int, int]:
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
    def check(self, hand: list[Card], cut: Card) -> tuple[bool, bool]:
        player_hand_suit = [c.suit for c in hand]
        most_common_suit = Counter(player_hand_suit).most_common(1)

        suit4, suit5 = False, False
        if most_common_suit[0][1] == 4:  # [1] is the count
            suit4 = True
            if most_common_suit[0][0] == cut.suit:  # [0] is the suit
                suit5 = True

        return suit4, suit5


class JackSuit(ScoringCheck):
    def check(self, hand: list[Card], cut: Card) -> bool:
        jack_suit = False
        for card in hand:
            if (card.rank == 11) and (card.suit == cut.suit):
                jack_suit = True

        return jack_suit


class Series(ScoringCheck):
    def check(self, hand: list[Card], cut: Card) -> tuple[int, int, int]:
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
    def check(self, hand: list[Card], cut: Card) -> int:
        full_hand = hand + [cut]
        full_hand_value = [c.value for c in full_hand]

        fifteen = 0
        # TODO search can be optimized
        for n_cards in range(2, 5):
            for c in combinations(full_hand_value, n_cards):
                if sum(c) == 15:
                    fifteen += 1

        return fifteen


@dataclass
class Scoresheet:
    fifteen: int
    pair: int
    triplet: int
    four: int
    series3: int
    series4: int
    series5: int
    suit4: bool
    suit5: bool
    jack_suit: bool

    score = 0
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

    def __post_init__(self) -> None:
        self.score += self.fifteen * self.point_value["fifteen"]
        self.score += self.pair * self.point_value["pair"]
        self.score += self.triplet * self.point_value["triplet"]
        self.score += self.four * self.point_value["four"]
        self.score += self.series3 * self.point_value["series3"]
        self.score += self.series4 * self.point_value["series4"]
        self.score += self.series5 * self.point_value["series5"]

        if self.suit5:
            self.score += self.point_value["suit5"]
        elif self.suit4:
            self.score += self.point_value["suit4"]

        if self.jack_suit:
            self.score += self.point_value["jack_suit"]


def get_scoresheet(hand: list[Card], cut: Card) -> Scoresheet:
    fifteen = Fifteen.check(hand, cut)
    pair, triplet, four = SameRank.check(hand, cut)
    series3, series4, series5 = Series.check(hand, cut)
    suit4, suit5 = SameSuit.check(hand, cut)
    jack_suit = JackSuit.check(hand, cut)

    return Scoresheet(
        fifteen=fifteen,
        pair=pair,
        triplet=triplet,
        four=four,
        series3=series3,
        series4=series4,
        series5=series5,
        suit4=suit4,
        suit5=suit5,
        jack_suit=jack_suit
    )


def get_score(hand: list[Card], cut: Card) -> int:
    scoresheet = get_scoresheet(hand, cut)
    return scoresheet.score


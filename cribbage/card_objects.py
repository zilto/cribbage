import random
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass
class Card:
    rank: int
    suit: int

    @property
    def value(self):
        """
        Figures have a value of 10 when scoring fifteens
        """
        if self.rank > 10:
            return 10
        else:
            return self.rank

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


class Deck:
    def __init__(self):
        self.cards = [Card(rank=r, suit=s) for r in range(1, 14) for s in range(4)]
        random.shuffle(self.cards)

    def deal_cards(self, n_cards: int):
        return [self.cards.pop() for i in range(n_cards)]

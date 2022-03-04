from itertools import cycle, combinations
from dataclasses import dataclass, field

import numpy as np

from card_objects import Card, Deck, Scoresheet
from estimator import MatrixDeck


@dataclass
class Player:
    player_id: int
    history: list[int] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)

    @property
    def score(self) -> int:
        return sum(self.history)

    def discard_crib(self, n_cards: int) -> list[Card]:
        idx_to_discard = [0, 1]
        return [self.hand.pop(idx) for idx in idx_to_discard]

    def play_race(self):
        return



@dataclass
class Crib:
    crib_hand: list[Card] = field(default_directory=list)



class Game:
    def __init__(self, n_players: int) -> None:
        self.n_players: int = n_players
        self.round_idx: int = 0
        self.players: tuple[Player] = tuple(Player(player_id=i) for i in range(n_players))

    def play_round(self):
        round = Round(players=self.players, dealer_id=self.round_idx)


class Round:
    def __init__(self, players: tuple[Player], dealer_id: int) -> None:
        self.players: tuple[Player] = players
        self.n_players: int = len(players)
        self.dealer_id: int = dealer_id
        self.deck = Deck()
        self.cut = None
        self.crib = None

    def deal_cards(self) -> None:
        # assuming only 2 players for now
        if self.n_players == 2:
            for player in self.players:
                player.hand = self.deck.deal_cards(6)

    def set_crib(self) -> None:
        crib_cards: list[Card] = []
        if self.n_players == 2:
            for player in self.players:
                crib_cards.extend(player.discard_cribe(n_cards=2))
        # for 3 players, need to set one card from the deck
        elif self.n_players == 3:
            self.deck.deal_cards(1)

        self.crib = Cribe(cribe_hand=crib_cards)

    def set_cut(self) -> None:
        self.cut = self.deck.deal_cards(n_cards=1)






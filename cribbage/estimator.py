from itertools import combinations
from dataclasses import dataclass
from typing import Union, Callable

import numpy as np

from card_objects import Card, Deck, Scoresheet


@dataclass
class MatrixDeck:
    state: np.array = np.ones((13, 4))

    @property
    def shape(self):
        return self.state.shape

    @property
    def rank_vector(self):
        return self.state.sum(axis=1)

    @property
    def suit_vector(self):
        return self.state.sum(axis=0)

    def add_card(self, card: Card) -> np.array:
        self.state[card.rank, card.suit] = 1
        return self.state

    def remove_card(self, card: Card) -> np.array:
        self.state[card.rank, card.suit] = 0
        return self.state

    def get_rank_proba(self, rank: int):
        rank_proba_vector = self.rank_vector / self.state.sum()
        return rank_proba_vector[rank - 1]

    def get_suit_proba(self, suit: int):
        suit_proba_vector = self.suit_vector / self.state.sum()
        return suit_proba_vector[suit]

    def get_card_proba(self, card: Card):
        if self.state[card.rank, card.suit] == 1:
            return 1 / self.state.sum()
        else:
            return 0


def naive_rank_search(mdeck: MatrixDeck) -> Card:
    """
    Generate valid cards
    """
    rank_vector = mdeck.rank_vector
    for rank in range(mdeck.shape[0]):
        if rank_vector[rank] != 0:
            suit = np.nonzero(mdeck.state[rank, :])[0]
            yield Card(rank=rank, suit=suit)


def update_hand_knowledge(mdeck: MatrixDeck, hand: tuple[Card]) -> None:
    for card in hand:
         mdeck.remove_card(card)


def expected_four_card_payoff(search_func: Callable, mdeck: MatrixDeck, shorthand: tuple[Card, Card, Card, Card]) -> np.array:
    payoff_vector = np.zeros((13, 1))
    for idx, hypothesis in enumerate(search_func(mdeck)):
        scorer = Scoresheet(hand=shorthand, cut=hypothesis)
        payoff_vector[idx] = scorer.score
    return payoff_vector


def permute_hand(hand: list[Card]):
    mdeck = MatrixDeck()
    update_hand_knowledge(mdeck, hand)

    payoff_matrix = np.zeros((13, 15))
    for col_idx, shorthand in enumerate(combinations(hand, 4)):
        payoff_matrix[:, col_idx] = expected_four_card_payoff(
            search_func=naive_rank_search,
            mdeck=mdeck,
            shorthand=shorthand,
        )

    return payoff_matrix
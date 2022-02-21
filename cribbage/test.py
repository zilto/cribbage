import unittest

from game_classes import Card, Deck, Hand, Player


PHAND1: list[Card] = [Card(1, 0), Card(9, 2), Card(3, 0), Card(3, 1)]
CUT1: Card = Card(6, 3)

PHAND2: list[Card] = [Card(11, 0), Card(9, 0), Card(8, 0), Card(8, 1)]
CUT2: Card = Card(7, 0)


class TestHandScoring(unittest.TestCase):
    def setUp(self):
        self.testhand1 = Hand(PHAND1, CUT1)
        self.testhand2 = Hand(PHAND2, CUT2)

    def test_scoring(self):
        # self.assertEqual(self.testhand1.get_score(), 6, self.testhand1)
        self.assertEqual(self.testhand2.get_score(), 12, self.testhand2)


if __name__ == "__main__":
    unittest.main()

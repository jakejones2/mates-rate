from basicgame.utils import points_generator
from django.test import TestCase


class TestPointsGenerator(TestCase):
    """
    Points generator takes a number of players as its argument,
    and returns a generator that can be used to allocate points.
    """

    def test_num_of_players_greater_than_nine(self):
        gen = points_generator(10)
        self.assertEqual(next(gen), 7)
        self.assertEqual(next(gen), 4)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 1)
        TestCase.assertRaises(lambda _: next(gen), StopIteration)

    def test_num_of_players_greater_than_seven(self):
        gen = points_generator(8)
        self.assertEqual(next(gen), 5)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 1)
        TestCase.assertRaises(lambda _: next(gen), StopIteration)

    def test_num_of_players_greater_than_five(self):
        gen = points_generator(6)
        self.assertEqual(next(gen), 5)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 1)
        TestCase.assertRaises(lambda _: next(gen), StopIteration)

    def test_num_of_players_greater_than_three(self):
        gen = points_generator(4)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 1)
        TestCase.assertRaises(lambda _: next(gen), StopIteration)

    def test_num_of_players_greater_than_two(self):
        gen = points_generator(3)
        self.assertEqual(next(gen), 1)
        TestCase.assertRaises(lambda _: next(gen), StopIteration)

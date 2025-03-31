# pylint: skip-file
import unittest

from linalgo.annotate.utils import SoftDeleteSet


class TestUtils(unittest.TestCase):

    def test_soft_delete_set(self):

        s = SoftDeleteSet(['apple', 'banana', 'cherry'])
        self.assertEqual(len(s), 3)
        self.assertTrue('banana' in s)

        s.remove('banana')
        self.assertEqual(len(s), 2)
        self.assertFalse('banana' in s)

        self.assertEqual([f for f in s], ['apple', 'cherry'])

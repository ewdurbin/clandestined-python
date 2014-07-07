
import doctest
import unittest


class DocTestCase(unittest.TestCase):
    def test_readme(self):
        failure_count, test_count \
            = doctest.testfile('../../README.md', optionflags=doctest.ELLIPSIS)
        assert failure_count == 0


if __name__ == '__main__':
    unittest.main()

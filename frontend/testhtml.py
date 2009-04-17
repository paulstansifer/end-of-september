from html import *
import unittest


class TestHTML(unittest.TestCase):
    def test_simple_structures(self):
        t = div()('echo')
        self.assertEqual(t.emit(), "<div>echo</div>")

        t = div()(div()('sierra'))
        self.assertEqual(t.emit(), "<div><div>sierra</div></div>")

        t = div()('victor', div()('november'))
        self.assertEqual(t.emit(), "<div>victor<div>november</div></div>")

        t = div(role='handler')('boyd')
        self.assertEqual(t.emit(), "<div role='handler'>boyd</div>")

if __name__ == "__main__":
    unittest.main()

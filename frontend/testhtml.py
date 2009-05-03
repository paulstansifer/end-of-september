from html import *
import unittest


class TestHTML(unittest.TestCase):
  def test_simple_structures(self):
    with div() as t: txt('echo')
    self.assertEqual(t.emit(), "<div>echo</div>")

    with div() as t:
      with div(): txt('sierra')
    self.assertEqual(t.emit(), "<div><div>sierra</div></div>")

    with div() as t:
      txt('victor')
      with div(): txt('november')
    self.assertEqual(t.emit(), "<div>victor<div>november</div></div>")

    with div(role='handler') as t: txt('boyd')
    self.assertEqual(t.emit(), "<div role='handler'>boyd</div>")

  def test_encoding(self):
    with div(at='''<'">''') as t:
      txt('''<'">''')
    self.assertEqual(t.emit(), '''<div at='&lt;&#39;&quot;&gt;'>&lt;&#39;&quot;&gt;</div>''')

if __name__ == "__main__":
  unittest.main()

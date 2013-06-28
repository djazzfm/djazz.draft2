from django.utils import unittest


class PostTestCase(unittest.TestCase):
    
    def test_vdef(self):
        from djazz import vdef
        
        formatters = vdef.defaults['DJAZZ_FORMATTERS']
        self.assertEqual(vdef.get('DJAZZ_FORMATTERS'), formatters)
        self.assertEqual(vdef.get('UNDEF_VALUE', 'vdef'), 'vdef')
        self.assertEqual(vdef.get('UNDEF_VALUE'), None)


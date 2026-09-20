import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from audit import uncertainty

class AuditTests(unittest.TestCase):
    def test_constant_known_alpha(self):
        r=uncertainty(np.full(100,.001),np.zeros(100),1,samples=200)
        self.assertAlmostEqual(r['simultaneous_lower_alpha_annual'],.36525)
    def test_beta_is_not_alpha(self):
        x=np.tile([.01,-.005,.003,-.009],30)
        r=uncertainty(2*x,x,1,samples=200)
        np.testing.assert_allclose(r['arithmetic_alpha_annual_ci95'],[0,0],atol=1e-12)
    def test_seed_reproducible(self):
        x=np.linspace(-.01,.01,100)
        a=uncertainty(x,np.zeros(100),77,samples=200)
        b=uncertainty(x,np.zeros(100),77,samples=200)
        self.assertEqual(a,b)

if __name__=='__main__': unittest.main()

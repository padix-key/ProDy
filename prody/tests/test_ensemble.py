#!/usr/bin/python
# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2011 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module contains unit tests for :mod:`~prody.ensemble` module."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2011 Ahmet Bakan'

import unittest
import numpy as np
from numpy.testing import *

from prody import *
from test_datafiles import *

prody.changeVerbosity('none')

ATOMS = parseDatafile('multi_model_truncated', subset='ca')

ENSEMBLE = Ensemble(ATOMS)
CONF = ENSEMBLE[0]
ENSEMBLE_RMSD = parseDatafile('pdb2k39_truncated_RMSDca.dat')
ENSEMBLE_SUPERPOSE = parseDatafile('pdb2k39_truncated_alignRMSDca.dat')

ENSEMBLEW = Ensemble(ATOMS)
ENSEMBLEW.setWeights(np.ones(len(ATOMS), dtype=float))
CONFW = ENSEMBLEW[0]

PDBENSEMBLE = PDBEnsemble('PDBEnsemble')
PDBENSEMBLE.setCoordinates(ATOMS.getCoordinates())
WEIGHTS = []
for i, xyz in enumerate(ATOMS.iterCoordsets()):
    weights = np.ones((len(ATOMS), 1), dtype=float)
    if i > 0:
        weights[i] = 0
        weights[-i] = 0 
        PDBENSEMBLE.addCoordset(xyz, weights=weights)
    else:
        PDBENSEMBLE.addCoordset(xyz)
    WEIGHTS.append(weights)
PDBCONF = PDBENSEMBLE[0]
WEIGHTS = np.array(WEIGHTS)
WEIGHTS_BOOL = np.tile(WEIGHTS.astype(bool), (1,1,3))  
WEIGHTS_BOOL_INVERSE = np.invert(WEIGHTS_BOOL)


class TestEnsemble(unittest.TestCase):
    
    def testGetCoordinates(self):
        """Test correctness of reference coordinates."""
        
        assert_equal(ATOMS.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'failed to get correct coordinates')
    
    
    def testGetCoordsets(self):
        """Test correctness of all coordinates."""

        assert_equal(ATOMS.getCoordsets(), ENSEMBLE.getCoordsets(),
                     'failed to add coordinate sets for Ensemble')
    
    
    def testGetWeights(self):
        """Test correctness of all weights."""

        assert_equal(ENSEMBLEW.getWeights().ndim, 2,
                     'failed to get correct weights ndim')
        assert_equal(ENSEMBLEW.getWeights().shape, 
                     (ENSEMBLEW.getNumOfAtoms(), 1),
                    'failed to get correct weights shape')
        assert_equal(ENSEMBLEW.getWeights(),
                     np.ones((ENSEMBLEW.getNumOfAtoms(), 1), float),
                     'failed to get expected weights')

    def testSlicingCopy(self):
        """Test making a copy by slicing operation."""
        
        SLICE = ENSEMBLE[:]
        assert_equal(SLICE.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'slicing copy failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), ENSEMBLE.getCoordsets(),
                     'slicing copy failed to add coordinate sets')

    def testSlicing(self):
        """Test slicing operation."""
        
        SLICE = ENSEMBLE[:2]
        assert_equal(SLICE.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'slicing failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), ENSEMBLE.getCoordsets([0,1]),
                     'slicing failed to add coordinate sets')

    def testSlicingList(self):
        """Test slicing with a list."""
        
        SLICE = ENSEMBLE[[0,2]]
        assert_equal(SLICE.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'slicing failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), ENSEMBLE.getCoordsets([0,2]),
                     'slicing failed to add coordinate sets for Ensemble')


    def testSlicingWeights(self):
        """Test slicing operation with weights."""
        
        SLICE = ENSEMBLEW[:2]
        assert_equal(SLICE.getWeights(), ENSEMBLEW.getWeights(),
                     'slicing failed to set weights')

    def testIterCoordsets(self):
        """Test coordinate iteration."""
        
        for i, xyz in enumerate(ENSEMBLE.iterCoordsets()):
            assert_equal(xyz, ATOMS.getCoordsets(i),
                         'failed yield correct coordinates')
            
    def testGetNumOfAtoms(self):

        self.assertEqual(ENSEMBLE.getNumOfAtoms(), ATOMS.getNumOfAtoms(),
                         'failed to get correct number of atoms')  
            
    def testGetNumOfCoordsets(self):

        self.assertEqual(ENSEMBLE.getNumOfCoordsets(), 
                         ATOMS.getNumOfCoordsets(),
                         'failed to get correct number of coordinate sets')  

    def testGetRMSDs(self):
        
        assert_equal(ENSEMBLE.getRMSDs().round(3), ENSEMBLE_RMSD,
                     'failed to calculate RMSDs sets')

    def testSuperpose(self):
        
        ensemble = ENSEMBLE[:]
        ensemble.superpose()
        assert_equal(ensemble.getRMSDs().round(3), ENSEMBLE_SUPERPOSE,
                     'failed to superpose coordinate sets')

    def testGetRMSDsWeights(self):
        
        self.assertTrue(np.all(ENSEMBLE_RMSD == ENSEMBLEW.getRMSDs().round(3)),
                        'failed to calculate RMSDs sets for Ensemble')

    def testSuperposeWeights(self):
        
        ensemble = ENSEMBLEW[:]
        ensemble.superpose()
        self.assertTrue(np.all(ENSEMBLE_SUPERPOSE == 
                               ensemble.getRMSDs().round(3)),
                        'failed to superpose coordinate sets for Ensemble')

    def testDelCoordsetMiddle(self):
        
        ensemble = ENSEMBLE[:]
        ensemble.delCoordset(1)
        self.assertTrue(np.all(ATOMS.getCoordsets([0,2]) == 
                               ensemble.getCoordsets()),
                        'failed to delete middle coordinate set for Ensemble')
        
    def testDelCoordsetAll(self):
        
        ensemble = ENSEMBLE[:]
        ensemble.delCoordset(range(len(ENSEMBLE)))
        self.assertIsNone(ensemble.getCoordsets(),
                        'failed to delete all coordinate sets for Ensemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed to delete all coordinate sets for Ensemble')


    def testConcatenation(self):
        
        ensemble = ENSEMBLE + ENSEMBLE
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3,6))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed at concatenation for Ensemble')

    def testConcatenationWeights(self):
        
        ensemble = ENSEMBLEW + ENSEMBLEW
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3,6))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ensemble.getWeights() ==
                               ENSEMBLEW.getWeights()),
                        'failed at concatenation for Ensemble')

    def testConcatenationNoweightsWeights(self):
        
        ensemble = ENSEMBLE + ENSEMBLEW
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3,6))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed at concatenation for Ensemble')
        self.assertIsNone(ensemble.getWeights(),
                        'failed at concatenation for Ensemble')

    def testConcatenationWeightsNoweights(self):
        
        ensemble = ENSEMBLEW + ENSEMBLE 
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ATOMS.getCoordsets() == 
                               ensemble.getCoordsets(range(3,6))),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed at concatenation for Ensemble')
        self.assertTrue(np.all(ensemble.getWeights() ==
                               ENSEMBLEW.getWeights()),
                        'failed at concatenation for Ensemble')


class TestConformation(unittest.TestCase): 
    
    
    def testCoordinates(self):
        
        self.assertTrue(np.all(ATOMS.getCoordinates() == 
                               CONF.getCoordinates()),
                        'failed to get coordinates for conformation')
                        
    def testWeights(self):
        
        self.assertEqual(CONFW.getWeights().ndim, 2,
                        'wrong ndim for weights of Conformation')
        self.assertTupleEqual(CONFW.getWeights().shape, 
                              (CONFW.getNumOfAtoms(), 1),
                               'wrong shape for weights of Conformation')
        self.assertTrue(np.all(CONFW.getWeights() == 
                               np.ones(ATOMS.getNumOfAtoms(), float)),
                        'failed to set weights for Conformation')
                                                
    def testCoordinatesForAll(self):
        
        for i, conf in enumerate(ENSEMBLE):
            self.assertTrue(np.all(ATOMS.getCoordsets(i) == 
                                   conf.getCoordinates()),
                            'failed to get coordinates for Conformation')
    def testGetIndex(self):

        for i, conf in enumerate(ENSEMBLE):
            self.assertEqual(conf.getIndex(), i,
                             'failed to get correct index for Conformation')        
                        
    def testGetNumOfAtoms(self):

        for i, conf in enumerate(ENSEMBLE):
            self.assertEqual(conf.getNumOfAtoms(), ATOMS.getNumOfAtoms(),
                             'failed to get correct number of atoms for ' 
                             'Conformation')        

class TestPDBEnsemble(unittest.TestCase):
    
    def testGetCoordinates(self):
        
        self.assertTrue(np.all(ATOMS.getCoordinates() == 
                               PDBENSEMBLE.getCoordinates()),
                        'failed to set reference coordinates for PDBEnsemble')
    
    def testGetCoordsets(self):

        self.assertTrue(np.all((ATOMS.getCoordsets() == 
                               PDBENSEMBLE.getCoordsets())[WEIGHTS_BOOL]),
                        'failed to add coordinate sets for PDBEnsemble')
    
    def testGetWeights(self):

        self.assertEqual(PDBENSEMBLE.getWeights().ndim, 3,
                        'wrong ndim for weights of PDBEnsemble')
        self.assertTupleEqual(PDBENSEMBLE.getWeights().shape, 
                              (PDBENSEMBLE.getNumOfCoordsets(),
                               PDBENSEMBLE.getNumOfAtoms(), 1),
                               'wrong shape for weights of PDBEnsemble')
        self.assertTrue(np.all(PDBENSEMBLE.getWeights() == WEIGHTS),
                        'failed to set weights for PDBEnsemble')


    def testSlicingCopy(self):
        
        SLICE = PDBENSEMBLE[:]
        self.assertTrue(np.all(SLICE.getCoordinates() == 
                               PDBENSEMBLE.getCoordinates()),
                        'slicing copy failed to set reference coordinates for '
                        'PDBEnsemble')
        self.assertTrue(np.all(SLICE.getCoordsets() == 
                               PDBENSEMBLE.getCoordsets()),
                        'slicing copy failed to add coordinate sets for '
                        'Ensemble')

    def testSlicing(self):
        
        SLICE = PDBENSEMBLE[:2]
        self.assertTrue(np.all(SLICE.getCoordinates() == 
                               PDBENSEMBLE.getCoordinates()),
                        'slicing failed to set reference coordinates for '
                        'PDBEnsemble')
        self.assertTrue(np.all(SLICE.getCoordsets() == 
                               PDBENSEMBLE.getCoordsets([0,1])),
                       'slicing failed to add coordinate sets for PDBEnsemble')

    def testSlicingList(self):
        
        SLICE = PDBENSEMBLE[[0,2]]
        self.assertTrue(np.all(SLICE.getCoordinates() == 
                               PDBENSEMBLE.getCoordinates()),
                        'slicing failed to set reference coordinates for '
                        'PDBEnsemble')
        self.assertTrue(np.all(SLICE.getCoordsets() == 
                               PDBENSEMBLE.getCoordsets([0,2])),
                       'slicing failed to add coordinate sets for PDBEnsemble')


    def testSlicingWeights(self):
        
        SLICE = PDBENSEMBLE[:2]
        self.assertTrue(np.all(SLICE.getWeights() == 
                               PDBENSEMBLE.getWeights()[:2]),
                        'slicing failed to set weights for PDBEnsemble')

    def testIterCoordsets(self):
        
        for i, xyz in enumerate(ENSEMBLE.iterCoordsets()):
            self.assertTrue(np.all((xyz == ATOMS.getCoordsets(i))
                                    [WEIGHTS_BOOL[i]]),
                            'failed iterate coordinate sets for PDBEnsemble')
            
    def testGetNumOfAtoms(self):

        self.assertEqual(PDBENSEMBLE.getNumOfAtoms(), ATOMS.getNumOfAtoms(),
                       'failed to get correct number of atoms for PDBEnsemble')  
            
    def testGetNumOfCoordsets(self):

        self.assertEqual(PDBENSEMBLE.getNumOfCoordsets(), 
                         ATOMS.getNumOfCoordsets(),
                         'failed to get correct number of coordinate sets for ' 
                         'PDBEnsemble')  

    def testDelCoordsetMiddle(self):
        
        ensemble = PDBENSEMBLE[:]
        ensemble.delCoordset(1)
        self.assertTrue(np.all((ATOMS.getCoordsets([0,2]) == 
                               ensemble.getCoordsets())[WEIGHTS_BOOL[[0,2]]]),
                      'failed to delete middle coordinate set for PDBEnsemble')
        
    def testDelCoordsetAll(self):
        
        ensemble = PDBENSEMBLE[:]
        ensemble.delCoordset(range(len(PDBENSEMBLE)))
        self.assertIsNone(ensemble.getCoordsets(),
                        'failed to delete all coordinate sets for PDBEnsemble')
        self.assertIsNone(ensemble.getWeights(), 'failed to delete weights '
                          'with all coordinate sets for PDBEnsemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed to delete all coordinate sets for PDBEnsemble')


    def testConcatenation(self):
        
        ensemble = PDBENSEMBLE + PDBENSEMBLE
        self.assertTrue(np.all(PDBENSEMBLE.getCoordsets() == 
                               ensemble.getCoordsets(range(3))),
                        'failed at concatenation for PDBEnsemble')
        self.assertTrue(np.all(PDBENSEMBLE.getCoordsets() == 
                               ensemble.getCoordsets(range(3,6))),
                        'failed at concatenation for PDBEnsemble')
        self.assertTrue(np.all(ensemble.getCoordinates() ==
                               ATOMS.getCoordinates()),
                        'failed at concatenation for PDBEnsemble')

    def testConcatenationWeights(self):
        
        ensemble = PDBENSEMBLE + PDBENSEMBLE
        self.assertTrue(np.all(ensemble.getWeights()[range(3)] ==
                               PDBENSEMBLE.getWeights()),
                        'failed at concatenation for PDBEnsemble')
        self.assertTrue(np.all(ensemble.getWeights()[range(3,6)] ==
                               PDBENSEMBLE.getWeights()),
                        'failed at concatenation for PDBEnsemble')

class TestPDBConformation(unittest.TestCase): 
    
    
    def testCoordinates(self):
        
        self.assertTrue(np.all(ATOMS.getCoordinates() == 
                               PDBCONF.getCoordinates()),
                        'failed to get coordinates for PDBConformation')
                        
    def testWeights(self):
        
        self.assertEqual(PDBCONF.getWeights().ndim, 2,
                        'wrong ndim for weights of PDBConformation')
        self.assertTupleEqual(PDBCONF.getWeights().shape, 
                              (PDBCONF.getNumOfAtoms(), 1),
                               'wrong shape for weights of PDBConformation')
        self.assertTrue(np.all(PDBCONF.getWeights() == WEIGHTS[0]),
                        'failed to set weights for PDBConformation')

    def testWeightsForAll(self):

        for i, conf in enumerate(PDBENSEMBLE):
            self.assertTrue(np.all(conf.getWeights() == WEIGHTS[i]),
                            'failed to set weights for PDBConformation')

                                                
    def testCoordinatesForAll(self):
        
        for i, conf in enumerate(PDBENSEMBLE):
            self.assertTrue(np.all((ATOMS.getCoordsets(i) == 
                                   conf.getCoordinates())[WEIGHTS_BOOL[i]]),
                            'failed to get coordinates for PDBConformation')
    def testGetIndex(self):

        for i, conf in enumerate(PDBENSEMBLE):
            self.assertEqual(conf.getIndex(), i,
                             'failed to get correct index for PDBConformation')        
                        
    def testGetNumOfAtoms(self):

        for i, conf in enumerate(PDBENSEMBLE):
            self.assertEqual(conf.getNumOfAtoms(), ATOMS.getNumOfAtoms(),
                             'failed to get correct number of atoms for ' 
                             'PDBConformation')

class TestCalcSumOfWeights(unittest.TestCase):

    def testResults(self):
        self.assertTrue(np.all(WEIGHTS.sum(0).flatten() == 
                                calcSumOfWeights(PDBENSEMBLE)),
                        'calcSumOfWeights failed')

    def testInvalidType(self):
        
        self.assertRaises(TypeError, calcSumOfWeights, ENSEMBLE)
        
    def testWeightsNone(self):
        
        self.assertIsNone(calcSumOfWeights(PDBEnsemble()),
                          'calcSumOfWeights failed')


if __name__ == '__main__':
    prody.changeVerbosity('none')
    unittest.main()
    prody.changeVerbosity('debug')

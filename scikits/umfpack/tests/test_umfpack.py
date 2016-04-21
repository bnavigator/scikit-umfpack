""" Test functions for UMFPACK wrappers

"""

from __future__ import division, print_function, absolute_import

import warnings
import random

from numpy.testing import assert_array_almost_equal, run_module_suite
from numpy.testing.utils import WarningManager

from scipy import rand, matrix, diag, eye
from scipy.sparse import csc_matrix, spdiags, SparseEfficiencyWarning
from scipy.sparse.linalg import linsolve

import numpy as np
import scikits.umfpack as um


class _DeprecationAccept:
    def setUp(self):
        self.mgr = WarningManager()
        self.mgr.__enter__()
        warnings.simplefilter("ignore", DeprecationWarning)
        warnings.simplefilter('ignore', SparseEfficiencyWarning)

    def tearDown(self):
        self.mgr.__exit__()


class TestScipySolvers(_DeprecationAccept):
    """Tests inverting a sparse linear system"""

    def test_solve_complex_umfpack(self):
        # Solve with UMFPACK: double precision complex
        linsolve.use_solver(useUmfpack=True)
        a = self.a.astype('D')
        b = self.b
        x = linsolve.spsolve(a, b)
        assert_array_almost_equal(a*x, b)

    def test_solve_umfpack(self):
        # Solve with UMFPACK: double precision
        linsolve.use_solver(useUmfpack=True)
        a = self.a.astype('d')
        b = self.b
        x = linsolve.spsolve(a, b)
        assert_array_almost_equal(a*x, b)

    def test_solve_sparse_rhs(self):
        # Solve with UMFPACK: double precision, sparse rhs
        linsolve.use_solver(useUmfpack=True)
        a = self.a.astype('d')
        b = csc_matrix(self.b).T
        x = linsolve.spsolve(a, b)
        assert_array_almost_equal(a*x, self.b)

    def test_factorized_umfpack(self):
        # Prefactorize (with UMFPACK) matrix for solving with multiple rhs
        linsolve.use_solver(useUmfpack=True)
        a = self.a.astype('d')
        solve = linsolve.factorized(a)

        x1 = solve(self.b)
        assert_array_almost_equal(a*x1, self.b)
        x2 = solve(self.b2)
        assert_array_almost_equal(a*x2, self.b2)

    def test_factorized_without_umfpack(self):
        # Prefactorize matrix for solving with multiple rhs
        linsolve.use_solver(useUmfpack=False)
        a = self.a.astype('d')
        solve = linsolve.factorized(a)

        x1 = solve(self.b)
        assert_array_almost_equal(a*x1, self.b)
        x2 = solve(self.b2)
        assert_array_almost_equal(a*x2, self.b2)

    def setUp(self):
        self.a = spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]], [0, 1], 5, 5)
        self.b = np.array([1, 2, 3, 4, 5], dtype=np.float64)
        self.b2 = np.array([5, 4, 3, 2, 1], dtype=np.float64)

        _DeprecationAccept.setUp(self)


class TestFactorization(_DeprecationAccept):
    """Tests factorizing a sparse linear system"""

    def test_complex_lu(self):
        # Getting factors of complex matrix
        umfpack = um.UmfpackContext("zi")

        for A in self.complex_matrices:
            umfpack.numeric(A)

            (L,U,P,Q,R,do_recip) = umfpack.lu(A)

            L = L.todense()
            U = U.todense()
            A = A.todense()
            if not do_recip:
                R = 1.0/R
            R = matrix(diag(R))
            P = eye(A.shape[0])[P,:]
            Q = eye(A.shape[1])[:,Q]

            assert_array_almost_equal(P*R*A*Q,L*U)

    def test_real_lu(self):
        # Getting factors of real matrix
        umfpack = um.UmfpackContext("di")

        for A in self.real_matrices:
            umfpack.numeric(A)

            (L,U,P,Q,R,do_recip) = umfpack.lu(A)

            L = L.todense()
            U = U.todense()
            A = A.todense()
            if not do_recip:
                R = 1.0/R
            R = matrix(diag(R))
            P = eye(A.shape[0])[P,:]
            Q = eye(A.shape[1])[:,Q]

            assert_array_almost_equal(P*R*A*Q,L*U)

    def setUp(self):
        random.seed(0)  # make tests repeatable
        self.real_matrices = []
        self.real_matrices.append(spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]],
                                          [0, 1], 5, 5))
        self.real_matrices.append(spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]],
                                          [0, 1], 4, 5))
        self.real_matrices.append(spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]],
                                          [0, 2], 5, 5))
        self.real_matrices.append(rand(3,3))
        self.real_matrices.append(rand(5,4))
        self.real_matrices.append(rand(4,5))

        self.real_matrices = [csc_matrix(x).astype('d') for x
                in self.real_matrices]
        self.complex_matrices = [x.astype(np.complex128)
                                 for x in self.real_matrices]

        _DeprecationAccept.setUp(self)


if __name__ == "__main__":
    run_module_suite()

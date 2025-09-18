"""
Conjugate Gradient solver POC
Tries SciPy's sparse CG; falls back to a pure-numpy implementation for dense SPD matrices.
"""
from typing import Optional, Union, Tuple
import numpy as np


def cg_solve(A, b, tol: float = 1e-8, maxiter: Optional[int] = None):
    """Solve A x = b using Conjugate Gradient.

    A may be:
      - scipy.sparse matrix (preferred if scipy available)
      - numpy.ndarray (dense)

    Returns x as numpy.ndarray.
    """
    # Try SciPy sparse path
    try:
        import scipy.sparse.linalg as spla  # type: ignore
        import scipy.sparse as sp

        # Check if A is already sparse or can be converted
        if hasattr(A, 'tocsr') or sp.issparse(A):
            x, info = spla.cg(A, b, tol=tol, maxiter=maxiter)
            if info != 0:
                raise RuntimeError(f"CG failed (info={info})")
            return x

        # For dense matrices, check if it's worth converting to sparse
        A_array = np.array(A)
        sparsity = np.count_nonzero(A_array) / A_array.size
        if sparsity < 0.1:  # If less than 10% non-zero, use sparse
            A_sparse = sp.csr_matrix(A_array)
            x, info = spla.cg(A_sparse, b, tol=tol, maxiter=maxiter)
            if info != 0:
                raise RuntimeError(f"CG failed (info={info})")
            return x
    except ImportError:
        pass
    except Exception as e:
        # Log but continue to fallback
        pass

    # Fallback: numpy implementation for symmetric positive-definite dense matrix
    A = np.asarray(A)
    b = np.asarray(b)

    # Validate dimensions
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(f"A must be square matrix, got shape {A.shape}")
    if b.ndim != 1 or b.shape[0] != A.shape[0]:
        raise ValueError(f"b must be vector of length {A.shape[0]}, got shape {b.shape}")

    n = A.shape[0]
    x = np.zeros_like(b, dtype=np.float64)
    r = b - A.dot(x)
    p = r.copy()
    rsold = r.dot(r)

    it = 0
    maxiter = maxiter or min(n * 10, 10000)

    for it in range(maxiter):
        Ap = A.dot(p)
        pAp = p.dot(Ap)

        if abs(pAp) < 1e-30:
            # Breakdown - p is in null space of A
            break

        alpha = rsold / pAp
        x = x + alpha * p
        r = r - alpha * Ap
        rsnew = r.dot(r)

        if np.sqrt(rsnew) < tol:
            break

        beta = rsnew / (rsold + 1e-30)
        p = r + beta * p
        rsold = rsnew

    return x


def pcg_solve(A, b, M=None, tol: float = 1e-8, maxiter: Optional[int] = None):
    """Preconditioned Conjugate Gradient solver.

    M is the preconditioner (should approximate A^{-1}).
    If M is None, uses diagonal (Jacobi) preconditioning.
    """
    A = np.asarray(A)
    b = np.asarray(b)
    n = A.shape[0]

    # Default preconditioner: Jacobi (diagonal)
    if M is None:
        diag = np.diag(A)
        diag[diag == 0] = 1.0  # Avoid division by zero
        M_inv = lambda x: x / diag
    elif callable(M):
        M_inv = M
    else:
        M = np.asarray(M)
        M_inv = lambda x: np.linalg.solve(M, x)

    x = np.zeros_like(b, dtype=np.float64)
    r = b - A.dot(x)
    z = M_inv(r)
    p = z.copy()
    rzold = r.dot(z)

    maxiter = maxiter or min(n * 10, 10000)

    for it in range(maxiter):
        Ap = A.dot(p)
        alpha = rzold / (p.dot(Ap) + 1e-30)
        x = x + alpha * p
        r = r - alpha * Ap

        if np.linalg.norm(r) < tol:
            break

        z = M_inv(r)
        rznew = r.dot(z)
        beta = rznew / (rzold + 1e-30)
        p = z + beta * p
        rzold = rznew

    return x


def bicgstab_solve(A, b, tol: float = 1e-8, maxiter: Optional[int] = None):
    """BiConjugate Gradient Stabilized method for non-symmetric systems."""
    A = np.asarray(A)
    b = np.asarray(b)
    n = A.shape[0]

    x = np.zeros_like(b, dtype=np.float64)
    r = b - A.dot(x)
    r_hat = r.copy()
    rho = alpha = omega = 1.0
    v = p = np.zeros_like(b)

    maxiter = maxiter or min(n * 10, 10000)

    for it in range(maxiter):
        rho_new = r_hat.dot(r)

        if abs(rho_new) < 1e-30:
            break

        beta = (rho_new / rho) * (alpha / omega)
        p = r + beta * (p - omega * v)
        v = A.dot(p)
        alpha = rho_new / (r_hat.dot(v) + 1e-30)
        s = r - alpha * v

        if np.linalg.norm(s) < tol:
            x = x + alpha * p
            break

        t = A.dot(s)
        omega = t.dot(s) / (t.dot(t) + 1e-30)
        x = x + alpha * p + omega * s
        r = s - omega * t

        if np.linalg.norm(r) < tol:
            break

        rho = rho_new

    return x
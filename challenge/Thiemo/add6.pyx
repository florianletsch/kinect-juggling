import numpy as np
cimport numpy as np

DTYPE = np.uint8
ctypedef np.uint8_t DTYPE_t

def my_add(np.ndarray[DTYPE_t, ndim=2] a, np.ndarray[DTYPE_t, ndim=2] b):
    if a.shape[0] != b.shape[0] or a.shape[1] != b.shape[1]:
        raise ValueError("Arrays must have identical dimensions")
    if a.dtype != DTYPE or b.dtype != DTYPE:
        raise ValueError("Arrays must have type %s" % DTYPE)

    return a + b


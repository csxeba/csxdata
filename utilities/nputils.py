"""Utility functions that use the NumPy library"""

import numpy as np


floatX = "float32"


def featscale(X: np.ndarray, axis=0, ufctr=(0, 1), dfctr=None, return_factors=False):
    """Rescales the input by first downscaling between dfctr[0] and dfctr[1], then
    upscaling it between ufctr[0] and ufctr[1]."""
    assert X.ndim == 2, ""
    if dfctr is None:
        dfctr = (X.min(axis=axis), X.max(axis=axis))
    frm, to = ufctr
    output = X - dfctr[0]
    output /= dfctr[1] - dfctr[0]
    output *= (to - frm)
    output += frm

    if not return_factors:
        return output
    else:
        return output, dfctr, ufctr


def standardize(X: np.ndarray,
                mean: np.ndarray=None, std: np.ndarray=None,
                return_factors: bool=False):
    if (mean is None and std is None) or (mean is not None and std is not None):
        err = ("Please either supply the array of means AND the standard deviations for scaling,\n" +
               "or don't supply any of them. In the latter case they will be calculated.")
        raise RuntimeError(err)

    # TODO: assert shapes are OK! Maybe allow float mean and float std?
    if mean is None:
        mean = X.mean(axis=0)
    if std is None:
        std = X.std(axis=0) + 1e-8

    scaled = (X - mean) / std

    if return_factors:
        return scaled, mean, std
    else:
        return scaled


def pca_transform(X: np.ndarray, factors: int=None, whiten: bool=False,
                  return_features: bool=False):
    from sklearn.decomposition import PCA

    print("Fitting PCA...")
    if X.ndim > 2:
        print("PCA: Warning! X is multidimensional, flattening it to matrix!")
        X = ravel_to_matrix(X)
    if factors is None:
        factors = X.shape[-1]
        print("PCA: Factor amount not specified, assuming full ({})!".format(factors))
    pca = PCA(n_components=factors, whiten=whiten)
    data = pca.fit_transform(ravel_to_matrix(X))
    if data.shape[1] != factors and data.shape[1] == data.shape[0]:
        print("PCA: Warning! Couldn't calculate covariance matrix, used generalized inverse instead!")
    if return_features:
        return data, pca.components_
    else:
        return data


def euclidean(itr: np.ndarray, target: np.ndarray):
    """Distance of points in euclidean space"""
    # TODO: numpy.linalg.norm -> test for higher dimensions tho
    # return np.linalg.norm(itr - target)
    return np.sqrt(np.sum(np.square(itr - target), axis=0))


def haversine(coords1: np.ndarray, coords2: np.ndarray):
    """The distance of points on the surface of Earth given their GPS (WGS) coordinates"""
    err = "Please supply two arrays of coordinate-pairs!"
    assert coords1.ndim == coords2.ndim == 2, err
    assert all([dim1 == dim2 for dim1, dim2 in zip(coords1.shape, coords2.shape)]), err

    R = 6367  # Approximate radius of Mother Earth in kms
    np.radians(coords1, out=coords1)
    np.radians(coords2, out=coords2)
    lon1, lat1 = coords1[..., 0], coords1[..., 1]
    lon2, lat2 = coords2[..., 0], coords2[..., 1]
    dlon = lon1 - lon2
    dlat = lat1 - lat2
    d = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    e = 2 * np.arcsin(np.sqrt(d))
    return e * R


def ravel_to_matrix(A):
    """Converts an ndarray to a 2d array (matrix) by keeping the first dimension as the rows
    and flattening all the other dimensions to columns"""
    if A.ndim == 2:
        return A
    A = np.atleast_2d(A)
    return A.reshape(A.shape[0], np.prod(A.shape[1:]))


def logit(Z: np.ndarray):
    """The primitive function of the sigmoid function"""
    return np.log(Z / (1 - Z))


def combination(A, W, b, scale, actfn):
    """Calculates a linear combination, then applies an activation function."""
    return actfn(A.dot(W) + b) * scale


def avg2pool(matrix):
    """Does average-pooling with stride and filter size = 2"""
    if ((matrix.shape[1] - 2) % 2) != 0:
        raise RuntimeError("Non-integer output shape!")
    osh = matrix.shape[0], (matrix.shape[1] - 2) // 2

    avg = matrix[:, ::2][:osh[1]] + \
        matrix[:, 1::2][:osh[1]]
    avg /= 2
    return avg


def avgpool(array, e, stride=None):
    """
    Pool absorbance values to reduce dimensionality.
    e := int, the size of the pooling filter
    """

    if not stride:
        stride = e
    output = np.array([])
    outsize = int(((len(array) - e) / stride) - 1)
    for n in range(outsize):
        start = n*stride
        end = start + e
        avg = np.average(array[start:end])
        output = np.append(output, avg)

    return output


def subsample(array, step):
    return array[..., ::step]


def export_to_file(path: str, data: np.ndarray, labels=None, headers=None):
    outchain = ""
    if headers is not None:
        outchain = "MA\t"
        outchain += "\t".join(headers) + "\n"
    for i in range(data.shape[0]):
        if labels is not None:
            outchain += str(labels[i]) + "\t"
        outchain += "\t".join(data[i].astype("<U11")) + "\n"
    with open(path, "w", encoding="utf8") as outfl:
        outfl.write(outchain.replace(".", ","))
        outfl.close()


def frobenius(mat, filt):
    """Calculate the Frobenius product of <filt> and <mat>.
    Meaning: compute elementwise product, then sum the resulting tensor.
    nD Array goes in, scalar comes out."""
    assert mat.shape == filt.shape, "Shapes differ! Can't multiply..."
    return np.sum(mat * filt)


def maxpool(mat):
    return np.amax(mat, axis=(0, 1))


def shuffle(learning_table: tuple):
    """Shuffles and recreates the learning table"""
    indices = np.arange(learning_table[0].shape[0])
    np.random.shuffle(indices)
    return learning_table[0][indices], learning_table[1][indices]


class Test:
    def __init__(self):
        print("\n<<< <<< TESTING |nputils.py| >>> >>>")
        self.featscale()
        self.euclidean()
        self.ravel_to_matrix()
        self.combination()
        print("<<< <<< ALL TEST PASSED @ |nputils.py| >>> >>>\n")

    @staticmethod
    def featscale():
        x = np.arange(3 * 4).reshape((3, 4)).astype(float)
        y = np.array([[0.0, 0.0, 0.0, 0.0],
                      [1.0, 1.0, 1.0, 1.0],
                      [2.0, 2.0, 2.0, 2.0]])
        output = featscale(x, ufctr=(0, 2))
        assert np.all(np.equal(y, output)), "Feature scale test failed!"
        print("<<< Test @ featscale passed! >>>")

    @staticmethod
    def euclidean():
        def vector():
            x1 = np.zeros((2,)).astype(float)
            x2 = np.ones((2,)).astype(float)
            y = np.sqrt(2)
            output = euclidean(x1, x2)
            assert output == y, "Test failed @ euclidean of vectors!"

        def vector2():
            x1 = np.array([15.1, 0.5, 13.45, 0.0, 187.0, 27.0, 18.0, 254.0, 0.8, 7.2])
            x2 = np.array([11.6258517, 4.04255166, 3.51548475, 1.66430278, 266.139903, 146.10648500000002,
                           111.96102, 18.085486500000002, 15.335202500000001, 5.7048872])
            y = 292
            output = int(euclidean(x1, x2))
            assert output == y, "Test fauiled @ euclideon of vectors #2!"

        def matrix():
            x1 = np.zeros((2, 2)).astype(float)
            x2 = np.ones((2, 2)).astype(float)
            y = np.sqrt(2) * 2
            output = euclidean(x1, x2).sum()
            assert output == y, "Test failed @ euclidean of matrices!"

        vector()
        vector2()
        matrix()
        print("<<< Test @ euclidean passed! >>>")

    @staticmethod
    def ravel_to_matrix():
        x = np.arange(2*3*4*5*6).reshape((2, 3, 4, 5, 6))
        yshape = (2, 3*4*5*6)
        output = ravel_to_matrix(x).shape
        assert np.all(np.equal(yshape, output)), "Test failed @ ravel_to_matrix!"
        print("<<< Test @ ravel_to_matrix passed! >>>")

    @staticmethod
    def combination():
        def vector_times_scalar():
            x = np.arange(10)
            w = 2
            y = np.arange(0, 20, 2)
            output = combination(x, w, 0.0, 1.0, lambda z: z)
            assert np.all(np.equal(y, output)), "Test failed @ combination of vector with scalar!"

        def vector_times_vector():
            x = np.ones((10,)) * 2
            w = np.arange(10)
            y = float(np.arange(0, 20, 2).sum())
            output = combination(x, w, 0.0, 1.0, lambda z: z)
            assert output == y, "Test failed @ combination of vector with vector!"

        def matrix_times_matrix():
            x = np.arange(12).reshape(3, 4)
            w = np.arange(16).reshape(4, 4)
            y = np.dot(x, w)
            output = combination(x, w, 0.0, 1.0, lambda z: z)
            assert np.all(np.equal(y, output)), "Test failed @ combination of matrix with matrix!"

        vector_times_scalar()
        vector_times_vector()
        matrix_times_matrix()
        print("<<< Test @ combination passed! >>>")

    @staticmethod
    def avgpool():
        pass


if __name__ == '__main__':
    Test()


"""
Dear Sequence Dataframe,

I would like you to:
- hold sequential data for me
- ON DIMENSIONS:
-- the raw data can either have 1 dimension: N
-- or 2 dimensions: (N, timestep) where timestep might not be constant!
-- learning and testing should have 3 dimensions: (n, timestep, embeddim)
!! NOPE !! the returned table should be dimshuffled so: (timestep, n, embeddim)
This must be so because batch shuffling should be done on n, but RNNs require
the timestep to be the first dim to be able to "batch" them efficiently.

- timestep (aka the length of a sequence element) can vary!
- embeddim should be constant and should only be returned by <neurons_required>
- implement embedding on the independent variables (X)!
? maybe implement transformations on embedded X?

- a parser is also needed for text data and for DNA sequence data.

"""

import unittest
from csxdata import Sequence, roots


class TestSeq(unittest.TestCase):

    def setUp(self):
        self.path = roots["txt"] + "petofi.txt"

    def test_init(self):
        petofi = Sequence(self.path, embeddim=20, n_gram=1)
        self.assertEqual(petofi.crossval, 0.2)

    def test_compatibility_with_keras_lstm(self):
        from keras.models import Sequential
        from keras.layers import LSTM, Dense

        petofi = Sequence(self.path, embeddim=20, n_gram=1)
        inshape, outputs = petofi.neurons_required

        network = Sequential(layers=[
            LSTM(60, input_shape=inshape),
            Dense(outputs, activation="tanh")
        ])

        X, y = petofi.table("learning")
        vX, vy = petofi.table("testing")
        network.fit(X, y, validation_data=(vX, vy), nb_epoch=10)

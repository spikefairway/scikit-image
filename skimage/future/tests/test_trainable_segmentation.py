from functools import partial

import numpy as np
import pytest
from scipy import spatial

from skimage._shared._warnings import expected_warnings
from skimage.future import fit_segmenter, predict_segmenter, TrainableSegmenter
from skimage.feature import multiscale_basic_features


class DummyNNClassifier(object):
    def fit(self, X, labels):
        self.X = X
        self.labels = labels
        self.tree = spatial.cKDTree(self.X)

    def predict(self, X):
        nearest_neighbors = self.tree.query(X)[1]
        return self.labels[nearest_neighbors]


def test_trainable_segmentation_singlechannel():
    img = np.zeros((20, 20))
    img[:10] = 1
    img += 0.05 * np.random.randn(*img.shape)
    labels = np.zeros_like(img, dtype=np.uint8)
    labels[:2] = 1
    labels[-2:] = 2
    clf = DummyNNClassifier()
    features_func = partial(
        multiscale_basic_features,
        edges=False,
        texture=False,
        sigma_min=0.5,
        sigma_max=2,
    )
    features = features_func(img)
    clf = fit_segmenter(labels, features, clf)
    out = predict_segmenter(features, clf)
    assert np.all(out[:10] == 1)
    assert np.all(out[10:] == 2)


def test_trainable_segmentation_multichannel():
    img = np.zeros((20, 20, 3))
    img[:10] = 1
    img += 0.05 * np.random.randn(*img.shape)
    labels = np.zeros_like(img[..., 0], dtype=np.uint8)
    labels[:2] = 1
    labels[-2:] = 2
    clf = DummyNNClassifier()
    features = multiscale_basic_features(
        img,
        edges=False,
        texture=False,
        sigma_min=0.5,
        sigma_max=2,
        channel_axis=-1,
    )
    clf = fit_segmenter(labels, features, clf)
    out = predict_segmenter(features, clf)
    assert np.all(out[:10] == 1)
    assert np.all(out[10:] == 2)


def test_trainable_segmentation_predict():
    img = np.zeros((20, 20))
    img[:10] = 1
    img += 0.05 * np.random.randn(*img.shape)
    labels = np.zeros_like(img, dtype=np.uint8)
    labels[:2] = 1
    labels[-2:] = 2
    clf = DummyNNClassifier()
    features_func = partial(
        multiscale_basic_features,
        edges=False,
        texture=False,
        sigma_min=0.5,
        sigma_max=2,
    )
    features = features_func(img)
    clf = fit_segmenter(labels, features, clf)

    test_features = np.random.random((5, 20, 20))
    with pytest.raises(ValueError) as err:
        _ = predict_segmenter(test_features, clf)
        assert 'type of features' in str(err.value)


def test_trainable_segmentation_oo():
    img = np.zeros((20, 20))
    img[:10] = 1
    img += 0.05 * np.random.randn(*img.shape)
    labels = np.zeros_like(img, dtype=np.uint8)
    labels[:2] = 1
    labels[-2:] = 2
    clf = DummyNNClassifier()
    features_func = partial(
        multiscale_basic_features,
        edges=False,
        texture=False,
        sigma_min=0.5,
        sigma_max=2,
    )
    segmenter = TrainableSegmenter(clf=clf, features_func=features_func)
    segmenter.fit(img, labels)
    out = segmenter.predict(img)
    assert np.all(out[:10] == 1)
    assert np.all(out[10:] == 2)

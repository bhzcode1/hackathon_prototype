"""
Preprocessing utilities for fire risk prediction.
Currently, no preprocessing is required for RandomForestClassifier,
but this module can be extended if needed (e.g., for scaling, encoding).
"""

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FireRiskPreprocessor(BaseEstimator, TransformerMixin):
    """
    A placeholder preprocessor that does nothing.
    Can be replaced with actual preprocessing steps if needed.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

    def fit_transform(self, X, y=None):
        return self.transform(X)
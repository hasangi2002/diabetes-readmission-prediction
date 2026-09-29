"""Custom estimators. Kept in their own light module so the backend can import them when loading the model."""
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier


class BalancedXGB(XGBClassifier):
    """XGBoost has no class_weight option for multiclass, so balanced sample weights are computed inside fit()."""
    def fit(self, X, y, **kwargs):
        kwargs["sample_weight"] = compute_sample_weight("balanced", y)
        return super().fit(X, y, **kwargs)

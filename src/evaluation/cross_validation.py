import numpy as np
from sklearn.model_selection import KFold

def run_cross_validation(df, engine, k_folds=5):
    """Runs k-fold cross-validation on the queries to test metric stability."""
    subset = df[df["Engine"] == engine]
    if len(subset) < k_folds: return "Not enough data"

    kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)
    map_scores = []

    for train_index, test_index in kf.split(subset):
        fold_data = subset.iloc[test_index]
        map_scores.append(fold_data["MAP"].mean())

    return f"Mean MAP: {np.mean(map_scores):.3f} (Std: {np.std(map_scores):.3f})"

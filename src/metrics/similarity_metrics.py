import pandas as pd
from src.utils.normalization import normalize_url

def calculate_jaccard(list_a, list_b):
    set_a = set(normalize_url(u) for u in list_a)
    set_b = set(normalize_url(u) for u in list_b)
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0

def robust_spearman(list_a, list_b):
    norm_a = [normalize_url(u) for u in list_a]
    norm_b = [normalize_url(u) for u in list_b]
    universe = list(set(norm_a) | set(norm_b))
    if len(universe) <= 1: return 0.0

    rank_map_a = {url: i + 1 for i, url in enumerate(norm_a)}
    rank_map_b = {url: i + 1 for i, url in enumerate(norm_b)}

    vec_a = [rank_map_a.get(u, 11) for u in universe]
    vec_b = [rank_map_b.get(u, 11) for u in universe]

    return pd.Series(vec_a).corr(pd.Series(vec_b), method='spearman')

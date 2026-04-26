import math
from src.utils.normalization import normalize_url

def precision_at_k(baseline_urls, target_urls, k=10):
    norm_base = set(normalize_url(u) for u in baseline_urls)
    norm_target = [normalize_url(u) for u in target_urls][:k]
    if not norm_target: return 0.0
    hits = sum(1 for url in norm_target if url in norm_base)
    return hits / k

def recall_at_k(baseline_urls, target_urls, k=10):
    """Calculates Recall@k: (Relevant Retrieved) / (Total Relevant)"""
    norm_base = set(normalize_url(u) for u in baseline_urls)
    norm_target = [normalize_url(u) for u in target_urls][:k]

    total_relevant = len(norm_base)
    if total_relevant == 0: return 0.0

    hits = sum(1 for url in norm_target if url in norm_base)
    return hits / total_relevant

def average_precision(baseline_urls, target_urls, k=10):
    norm_base = set(normalize_url(u) for u in baseline_urls)
    norm_target = [normalize_url(u) for u in target_urls][:k]
    hits = 0
    sum_precisions = 0.0
    for i, url in enumerate(norm_target):
        if url in norm_base:
            hits += 1
            sum_precisions += (hits / (i + 1))
    possible_hits = min(len(norm_base), k)
    return sum_precisions / possible_hits if possible_hits > 0 else 0.0

def ndcg_at_k(baseline_urls, target_urls, k=10):
    relevance_map = {}
    norm_base = [normalize_url(u) for u in baseline_urls]
    for rank, url in enumerate(norm_base):
        if rank >= k: break
        relevance_map[url] = k - rank

    dcg = 0.0
    norm_target = [normalize_url(u) for u in target_urls][:k]
    for i, url in enumerate(norm_target):
        rel = relevance_map.get(url, 0)
        dcg += rel / math.log2(i + 2)

    idcg = 0.0
    ideal_rels = sorted(relevance_map.values(), reverse=True)
    for i, rel in enumerate(ideal_rels):
        idcg += rel / math.log2(i + 2)

    return dcg / idcg if idcg > 0 else 0.0

from scipy import stats

def run_t_test(list_a, list_b):
    """
    Runs a Paired T-Test between two lists of scores.
    Returns (t_statistic, p_value, significance_label)
    """
    if len(list_a) > 5 and len(list_b) > 5:
        min_len = min(len(list_a), len(list_b))
        t, p = stats.ttest_rel(list_a[:min_len], list_b[:min_len])
        sig = "SIGNIFICANT" if p < 0.05 else "NOT SIGNIFICANT"
        return t, p, sig
    return 0.0, 1.0, "INSUFFICIENT DATA"

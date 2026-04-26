import numpy as np

def bootstrap_ci(data, n_bootstraps=1000, ci=95):
    if len(data) < 2: return 0.0, 0.0, 0.0
    boot_means = []
    data_array = np.array(data)
    for _ in range(n_bootstraps):
        sample = np.random.choice(data_array, size=len(data_array), replace=True)
        boot_means.append(np.mean(sample))
    lower = np.percentile(boot_means, (100 - ci) / 2)
    upper = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return float(lower), float(np.mean(boot_means)), float(upper)

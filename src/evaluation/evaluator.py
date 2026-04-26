import pandas as pd
import logging
from src.utils.io_utils import load_results, get_latest_results_dir
from src.metrics.ranking_metrics import precision_at_k, recall_at_k, average_precision, ndcg_at_k
from src.metrics.similarity_metrics import calculate_jaccard, robust_spearman
from src.evaluation.cross_validation import run_cross_validation
from src.evaluation.bootstrap import bootstrap_ci
from src.visualization.plots import generate_plots
from src.metrics.statistical_tests import run_t_test

class Evaluator:
    def __init__(self, task1_output_dir, output_dir):
        self.task1_output_dir = task1_output_dir
        self.output_dir = output_dir

    def run(self):
        latest_dir = get_latest_results_dir(self.task1_output_dir)
        if not latest_dir:
            logging.error(f"No task1 results found in {self.task1_output_dir}")
            return

        logging.info(f"Evaluating results from: {latest_dir}")
        google_data = load_results(latest_dir, "Google")
        if not google_data:
            logging.error("Google baseline data not found.")
            return

        all_rows = []
        engines = ["Bing", "Yahoo!"]

        # Store P@k and R@k data for plotting curves
        pr_data = {eng: {'P@k': {k: [] for k in range(1, 11)},
                         'R@k': {k: [] for k in range(1, 11)}} for eng in engines}

        for engine in engines:
            engine_data = load_results(latest_dir, engine)
            if not engine_data:
                logging.warning(f"No data for {engine}, skipping...")
                continue

            for query, base_urls in google_data.items():
                target_urls = engine_data.get(query, [])

                # Metrics
                jaccard = calculate_jaccard(base_urls, target_urls)
                spearman = robust_spearman(base_urls, target_urls)
                ndcg = ndcg_at_k(base_urls, target_urls)
                map_score = average_precision(base_urls, target_urls)
                p10 = precision_at_k(base_urls, target_urls, k=10)

                # Collect Curve Data
                for k in range(1, 11):
                    pr_data[engine]['P@k'][k].append(precision_at_k(base_urls, target_urls, k=k))
                    pr_data[engine]['R@k'][k].append(recall_at_k(base_urls, target_urls, k=k))

                all_rows.append({
                    "Engine": engine,
                    "Query": query,
                    "Overlap %": jaccard * 100,
                    "Precision@10": p10,
                    "MAP": map_score,
                    "NDCG@10": ndcg,
                    "Spearman Rho": spearman,
                    "Jaccard": jaccard
                })

        if not all_rows:
            logging.error("No assessment data generated.")
            return

        df = pd.DataFrame(all_rows)
        output_file = f"{self.output_dir}/evaluation_final.csv"
        df.to_csv(output_file, index=False)
        logging.info(f"Saved CSV: {output_file}")

        # --- CROSS VALIDATION ---
        logging.info("5-FOLD CROSS VALIDATION")
        for engine in engines:
            cv_result = run_cross_validation(df, engine, k_folds=5)
            logging.info(f"[{engine}] {cv_result}")

        # --- BOOTSTRAP ---
        logging.info("BOOTSTRAP CONFIDENCE INTERVALS (95%)")
        bootstrap_results = {}
        for engine in engines:
            subset = df[df["Engine"] == engine]
            if subset.empty: continue

            bs_res = {}
            for metric in ["Spearman Rho", "MAP"]:
                lo, mean, hi = bootstrap_ci(subset[metric].tolist())
                bs_res[metric.split()[0]] = (lo, mean, hi)
                logging.info(f"[{engine}] {metric}: {mean:.3f} (CI: {lo:.3f}-{hi:.3f})")
            bootstrap_results[engine] = bs_res

        # --- T-TEST ---
        bing_scores = df[df["Engine"] == "Bing"]["Spearman Rho"].tolist()
        yahoo_scores = df[df["Engine"] == "Yahoo!"]["Spearman Rho"].tolist()
        t, p, sig = run_t_test(bing_scores, yahoo_scores)
        logging.info(f"[T-TEST] Bing vs Yahoo: p={p:.5f} -> {sig}")

        # --- PLOTS ---
        generate_plots(df, pr_data, bootstrap_results, self.output_dir)

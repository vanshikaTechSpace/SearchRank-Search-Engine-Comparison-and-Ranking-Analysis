import os
import logging
import statistics
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def generate_plots(df, pr_data, bootstrap_results, output_dir):
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    logging.info("--- Generating Visualizations ---")
    sns.set_theme(style="whitegrid", context="talk")

    # 1. Spearman Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Engine", y="Spearman Rho", hue="Engine", data=df, palette="Set2", legend=False)
    sns.stripplot(x="Engine", y="Spearman Rho", data=df, color='black', alpha=0.3, jitter=True)
    plt.title("Ranking Correlation Distribution (Spearman Rho)")
    plt.savefig(os.path.join(plots_dir, "spearman_boxplot.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Overlap Histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x="Overlap %", hue="Engine", kde=True, bins=10, palette="viridis", element="step")
    plt.title("Distribution of URL Overlap %")
    plt.savefig(os.path.join(plots_dir, "overlap_histogram.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. NDCG Violin Plot
    plt.figure(figsize=(10, 6))
    sns.violinplot(x="Engine", y="NDCG@10", hue="Engine", data=df, palette="muted", inner="quartile", legend=False)
    plt.title("NDCG@10 Density Distribution")
    plt.savefig(os.path.join(plots_dir, "ndcg_violin.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Precision at K Curve (Ranking Decay)
    plt.figure(figsize=(12, 7))
    for engine in pr_data.keys():
        ks = sorted(pr_data[engine]['P@k'].keys())
        p_means = [statistics.mean(pr_data[engine]['P@k'][k]) for k in ks]
        plt.plot(ks, p_means, marker='o', linewidth=2, label=f"{engine}")

    plt.title("Precision at Rank K")
    plt.xlabel("Rank (k)")
    plt.ylabel("Precision")
    plt.legend()
    plt.grid(True, linestyle="--")
    plt.savefig(os.path.join(plots_dir, "p_at_k_curve.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 5. TRUE Precision-Recall Curve
    plt.figure(figsize=(12, 7))
    for engine in pr_data.keys():
        # Calculate mean P and R for each k=1..10
        ks = range(1, 11)
        avg_precisions = [statistics.mean(pr_data[engine]['P@k'][k]) for k in ks]
        avg_recalls = [statistics.mean(pr_data[engine]['R@k'][k]) for k in ks]

        plt.plot(avg_recalls, avg_precisions, marker='o', linewidth=2, label=f"{engine}")

    plt.title("Precision-Recall Curve (Avg over all queries)")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend()
    plt.grid(True, linestyle="--")
    plt.savefig(os.path.join(plots_dir, "precision_recall_curve.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Bootstrap CI Visualization
    ci_data = []
    for eng, metrics in bootstrap_results.items():
        for metric, (lo, mean, hi) in metrics.items():
            ci_data.append(
                {"Engine": eng, "Metric": metric, "Mean": mean, "Lower": lo, "Upper": hi, "Error": (hi - lo) / 2})

    if ci_data:
        ci_df = pd.DataFrame(ci_data)
        plt.figure(figsize=(10, 6))
        subset = ci_df[ci_df["Metric"] == "Spearman"]
        if not subset.empty:
             plt.errorbar(x=subset["Engine"], y=subset["Mean"], yerr=subset["Error"], fmt='o', capsize=10, linewidth=3,
                     markersize=10, color='darkred')
             plt.title("95% Confidence Intervals (Spearman Rho)")
             plt.savefig(os.path.join(plots_dir, "bootstrap_ci.png"), dpi=300, bbox_inches='tight')
        plt.close()

    # 7. Metrics Heatmap
    numeric_cols = ["Overlap %", "Precision@10", "MAP", "NDCG@10", "Spearman Rho", "Jaccard"]
    # Filter columns that exist in df
    existing_cols = [col for col in numeric_cols if col in df.columns]
    if existing_cols:
        summary = df.groupby("Engine")[existing_cols].mean()
        plt.figure(figsize=(12, 6))
        sns.heatmap(summary, annot=True, cmap="RdYlGn", fmt=".3f", linewidths=1)
        plt.title("Average Performance Metrics Summary")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "metrics_heatmap.png"), dpi=300, bbox_inches='tight')
        plt.close()

    logging.info(f"All plots saved to {plots_dir}")

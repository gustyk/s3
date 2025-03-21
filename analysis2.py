import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Read the simulation results
df = pd.read_csv('simulation_results.csv')

# Filter for specific trigger methods
trigger_methods = ['DVNS', 'MaxPicker', 'UrgentPicker']
df_filtered = df[df['trigger_method'].isin(trigger_methods)]

# Detailed statistical analysis
def compare_trigger_methods(df, methods):
    # Prepare results dictionary
    results = {
        'method': [],
        'mean_late_orders': [],
        'median_late_orders': [],
        'std_late_orders': [],
        '25th_percentile': [],
        '75th_percentile': []
    }
    
    # Perform Kruskal-Wallis H-test
    trigger_groups = [df[df['trigger_method'] == method]['total_late_orders'] for method in methods]
    h_statistic, p_value = stats.kruskal(*trigger_groups)
    
    # Collect detailed statistics
    for method in methods:
        method_data = df[df['trigger_method'] == method]['total_late_orders']
        results['method'].append(method)
        results['mean_late_orders'].append(method_data.mean())
        results['median_late_orders'].append(method_data.median())
        results['std_late_orders'].append(method_data.std())
        results['25th_percentile'].append(method_data.quantile(0.25))
        results['75th_percentile'].append(method_data.quantile(0.75))
    
    # Create DataFrame of results
    results_df = pd.DataFrame(results)
    
    # Post-hoc pairwise comparisons using Mann-Whitney U test
    pairwise_comparisons = {}
    for i in range(len(methods)):
        for j in range(i+1, len(methods)):
            stat, p = stats.mannwhitneyu(
                df[df['trigger_method'] == methods[i]]['total_late_orders'],
                df[df['trigger_method'] == methods[j]]['total_late_orders']
            )
            pairwise_comparisons[f'{methods[i]} vs {methods[j]}'] = p
    
    return {
        'kruskal_test': {
            'h_statistic': h_statistic,
            'p_value': p_value
        },
        'detailed_stats': results_df,
        'pairwise_comparisons': pairwise_comparisons
    }

# Perform comparison
comparison_results = compare_trigger_methods(df_filtered, trigger_methods)

# Visualize the distribution
plt.figure(figsize=(12, 6))
sns.boxplot(x='trigger_method', y='total_late_orders', data=df_filtered)
plt.title('Distribution of Late Orders by Trigger Method')
plt.xlabel('Trigger Method')
plt.ylabel('Total Late Orders')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('trigger_method_boxplot.png')

# Violin plot for more detailed distribution
plt.figure(figsize=(12, 6))
sns.violinplot(x='trigger_method', y='total_late_orders', data=df_filtered)
plt.title('Distribution of Late Orders by Trigger Method')
plt.xlabel('Trigger Method')
plt.ylabel('Total Late Orders')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('trigger_method_violinplot.png')

# Print results
print("Kruskal-Wallis H-test Results:")
print(f"H-statistic: {comparison_results['kruskal_test']['h_statistic']}")
print(f"p-value: {comparison_results['kruskal_test']['p_value']}")

print("\nDetailed Statistics:")
print(comparison_results['detailed_stats'])

print("\nPairwise Comparisons (p-values):")
for comparison, p_value in comparison_results['pairwise_comparisons'].items():
    print(f"{comparison}: {p_value}")

# Additional analysis by incoming rate
def analyze_by_incoming_rate(df, methods):
    results = []
    for rate in df['incoming_rate'].unique():
        rate_df = df[(df['incoming_rate'] == rate) & (df['trigger_method'].isin(methods))]
        rate_results = compare_trigger_methods(rate_df, methods)
        results.append({
            'incoming_rate': rate,
            'detailed_stats': rate_results['detailed_stats'],
            'pairwise_comparisons': rate_results['pairwise_comparisons']
        })
    return results

rate_analysis = analyze_by_incoming_rate(df_filtered, trigger_methods)

# Save detailed results
with open('trigger_method_analysis.txt', 'w') as f:
    f.write("Trigger Method Comparative Analysis\n")
    f.write("==================================\n\n")
    f.write("Overall Analysis:\n")
    f.write("Kruskal-Wallis H-test Results:\n")
    f.write(f"H-statistic: {comparison_results['kruskal_test']['h_statistic']}\n")
    f.write(f"p-value: {comparison_results['kruskal_test']['p_value']}\n\n")
    
    f.write("Detailed Statistics:\n")
    f.write(comparison_results['detailed_stats'].to_string())
    f.write("\n\nPairwise Comparisons (p-values):\n")
    for comparison, p_value in comparison_results['pairwise_comparisons'].items():
        f.write(f"{comparison}: {p_value}\n")
    
    f.write("\n\nRate-specific Analysis:\n")
    for rate_result in rate_analysis:
        f.write(f"\nIncoming Rate: {rate_result['incoming_rate']}\n")
        f.write("Detailed Statistics:\n")
        f.write(rate_result['detailed_stats'].to_string())
        f.write("\nPairwise Comparisons:\n")
        for comparison, p_value in rate_result['pairwise_comparisons'].items():
            f.write(f"{comparison}: {p_value}\n")

print("\nAnalysis complete. Check trigger_method_boxplot.png, trigger_method_violinplot.png, and trigger_method_analysis.txt for detailed results.")
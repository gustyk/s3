import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Read the simulation results
df = pd.read_csv('simulation_results.csv')

# Function to perform ANOVA and print results
def perform_anova(df, factor_column):
    """
    Perform one-way ANOVA to check the significance of a factor on late orders
    
    Args:
        df (pd.DataFrame): DataFrame with simulation results
        factor_column (str): Column name to analyze
    
    Returns:
        dict: ANOVA results
    """
    # Group the data
    groups = [group['total_late_orders'].values for name, group in df.groupby(factor_column)]
    
    # Perform one-way ANOVA
    f_value, p_value = stats.f_oneway(*groups)
    
    return {
        'factor': factor_column,
        'f_value': f_value,
        'p_value': p_value
    }

# Analyze factors influencing late orders
factors_to_analyze = [
    'incoming_rate', 
    'cart_capacity', 
    'trigger_method', 
    'batching_method', 
    'routing_policy', 
    'num_pickers'
]

# Perform ANOVA for each factor
anova_results = []
for factor in factors_to_analyze:
    anova_result = perform_anova(df, factor)
    anova_results.append(anova_result)

# Create a DataFrame of ANOVA results for easy viewing
anova_df = pd.DataFrame(anova_results)
print("ANOVA Results for Factors Influencing Late Orders:")
print(anova_df)

# Visualize the impact of key factors
plt.figure(figsize=(15, 10))

# 1. Incoming Rate vs Late Orders
plt.subplot(2, 3, 1)
df.groupby('incoming_rate')['total_late_orders'].mean().plot(kind='bar')
plt.title('Avg Late Orders by Incoming Rate')
plt.xlabel('Incoming Rate (orders/min)')
plt.ylabel('Avg Late Orders')
plt.xticks(rotation=45)

# 2. Number of Pickers vs Late Orders
plt.subplot(2, 3, 2)
df.groupby('num_pickers')['total_late_orders'].mean().plot(kind='bar')
plt.title('Avg Late Orders by Number of Pickers')
plt.xlabel('Number of Pickers')
plt.ylabel('Avg Late Orders')
plt.xticks(rotation=45)

# 3. Trigger Method vs Late Orders
plt.subplot(2, 3, 3)
df.groupby('trigger_method')['total_late_orders'].mean().plot(kind='bar')
plt.title('Avg Late Orders by Trigger Method')
plt.xlabel('Trigger Method')
plt.ylabel('Avg Late Orders')
plt.xticks(rotation=45)

# 4. Cart Capacity vs Late Orders
plt.subplot(2, 3, 4)
df.groupby('cart_capacity')['total_late_orders'].mean().plot(kind='bar')
plt.title('Avg Late Orders by Cart Capacity')
plt.xlabel('Cart Capacity')
plt.ylabel('Avg Late Orders')
plt.xticks(rotation=45)

# 5. Batching Method vs Late Orders
plt.subplot(2, 3, 5)
df.groupby('batching_method')['total_late_orders'].mean().plot(kind='bar')
plt.title('Avg Late Orders by Batching Method')
plt.xlabel('Batching Method')
plt.ylabel('Avg Late Orders')
plt.xticks(rotation=45)

# 6. Routing Policy vs Late Orders
plt.subplot(2, 3, 6)
df.groupby('routing_policy')['total_late_orders'].mean().plot(kind='bar')
plt.title('Avg Late Orders by Routing Policy')
plt.xlabel('Routing Policy')
plt.ylabel('Avg Late Orders')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('late_orders_analysis.png')

# Correlation analysis
correlation_features = ['incoming_rate', 'cart_capacity', 'num_pickers', 'total_orders', 'total_late_orders']
correlation_matrix = df[correlation_features].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix of Key Features')
plt.tight_layout()
plt.savefig('correlation_matrix.png')

# Detailed insights
print("\nDetailed Insights:")
print("1. Incoming Rate Impact:")
print(df.groupby('incoming_rate')['total_late_orders'].agg(['mean', 'median', 'max']))

print("\n2. Number of Pickers Impact:")
print(df.groupby('num_pickers')['total_late_orders'].agg(['mean', 'median', 'max']))

print("\n3. Trigger Method Performance:")
print(df.groupby('trigger_method')['total_late_orders'].agg(['mean', 'median', 'max']))

# Save key findings to a text file
with open('late_orders_findings.txt', 'w') as f:
    f.write("Factors Influencing Late Orders - Key Findings\n")
    f.write("===========================================\n\n")
    f.write("ANOVA Results:\n")
    f.write(anova_df.to_string())
    f.write("\n\nDetailed Insights:\n")
    f.write("1. Incoming Rate Impact:\n")
    f.write(df.groupby('incoming_rate')['total_late_orders'].agg(['mean', 'median', 'max']).to_string())
    f.write("\n\n2. Number of Pickers Impact:\n")
    f.write(df.groupby('num_pickers')['total_late_orders'].agg(['mean', 'median', 'max']).to_string())
    f.write("\n\n3. Trigger Method Performance:\n")
    f.write(df.groupby('trigger_method')['total_late_orders'].agg(['mean', 'median', 'max']).to_string())

print("\nAnalysis complete. Check late_orders_analysis.png, correlation_matrix.png, and late_orders_findings.txt for detailed results.")
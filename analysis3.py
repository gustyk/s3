import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Baca data simulasi
df = pd.read_csv('simulation_results.csv')

# Fungsi normalisasi untuk multi-objective
def normalize_column(series):
    """
    Normalisasi min-max scaling
    Untuk late orders: semakin rendah semakin baik
    Untuk total orders dan picker utility: semakin tinggi semakin baik
    """
    min_val = series.min()
    max_val = series.max()
    return (series - min_val) / (max_val - min_val)

# Kelompokkan berdasarkan trigger method
grouped = df.groupby('trigger_method').agg({
    'total_late_orders': ['mean', 'median', 'std'],
    'total_orders': ['mean', 'median', 'std'],
    'picker_utility': ['mean', 'median', 'std']
})

# Persiapan multi-objective scoring
multi_obj_scores = []

for trigger_method in df['trigger_method'].unique():
    method_data = df[df['trigger_method'] == trigger_method]
    
    # Normalisasi metrik
    norm_late_orders = 1 - normalize_column(method_data['total_late_orders'])  # Dibalik karena semakin rendah semakin baik
    norm_total_orders = normalize_column(method_data['total_orders'])
    norm_picker_utility = normalize_column(method_data['picker_utility'])
    
    # Hitung skor multi-objektif (contoh: rata-rata tertimbang)
    multi_obj_score = (
        0.4 * norm_late_orders.mean() +  # Bobot terbesar pada order terlambat
        0.3 * norm_total_orders.mean() + 
        0.3 * norm_picker_utility.mean()
    )
    
    multi_obj_scores.append({
        'trigger_method': trigger_method,
        'late_orders_mean': method_data['total_late_orders'].mean(),
        'total_orders_mean': method_data['total_orders'].mean(),
        'picker_utility_mean': method_data['picker_utility'].mean(),
        'multi_obj_score': multi_obj_score
    })

# Konversi ke DataFrame
multi_obj_df = pd.DataFrame(multi_obj_scores)
multi_obj_df = multi_obj_df.sort_values('multi_obj_score', ascending=False)

# Visualisasi perbandingan
plt.figure(figsize=(15, 5))

# Subplot 1: Order Terlambat
plt.subplot(1, 3, 1)
sns.barplot(x='trigger_method', y='late_orders_mean', data=multi_obj_df)
plt.title('Rata-rata Order Terlambat')
plt.xticks(rotation=45)
plt.ylabel('Jumlah Order Terlambat')

# Subplot 2: Total Order
plt.subplot(1, 3, 2)
sns.barplot(x='trigger_method', y='total_orders_mean', data=multi_obj_df)
plt.title('Rata-rata Total Order')
plt.xticks(rotation=45)
plt.ylabel('Jumlah Order')

# Subplot 3: Utilisasi Picker
plt.subplot(1, 3, 3)
sns.barplot(x='trigger_method', y='picker_utility_mean', data=multi_obj_df)
plt.title('Rata-rata Utilisasi Picker')
plt.xticks(rotation=45)
plt.ylabel('Utilisasi Picker')

plt.tight_layout()
plt.savefig('trigger_method_comparison.png')

# Tampilkan hasil
print("Perbandingan Multi-Objektif Trigger Method:")
print(multi_obj_df.to_string(index=False))

# Simpan ke file
with open('multi_objective_analysis.txt', 'w') as f:
    f.write("Analisis Multi-Objektif Trigger Method\n")
    f.write("====================================\n\n")
    f.write(multi_obj_df.to_string())
    f.write("\n\nKeterangan Bobot:\n")
    f.write("- 40% Order Terlambat (semakin rendah semakin baik)\n")
    f.write("- 30% Total Order Diselesaikan (semakin tinggi semakin baik)\n")
    f.write("- 30% Utilisasi Picker (semakin tinggi semakin baik)\n")

print("\nAnalisis selesai. Cek trigger_method_comparison.png dan multi_objective_analysis.txt untuk detail lengkap.")
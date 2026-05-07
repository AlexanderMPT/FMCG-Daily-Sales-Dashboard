import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import warnings
import os

warnings.filterwarnings('ignore')
os.makedirs('images', exist_ok=True)

# ===================== НАСТРОЙКА СТИЛЯ =====================
plt.rcParams.update({
    'figure.facecolor': '#0F1F3D',
    'axes.facecolor': '#0F1F3D',
    'axes.edgecolor': '#4A6080',
    'text.color': '#FFFFFF',
    'xtick.color': '#CCCCCC',
    'ytick.color': '#CCCCCC',
    'axes.labelcolor': '#CCCCCC',
    'axes.titlecolor': '#FFFFFF',
    'grid.color': '#1E3A5F',
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
})
ACCENT = '#0A7EA4'
ACCENT2 = '#F4A233'

# ===================== ЗАГРУЗКА ДАННЫХ =====================
FILE = 'data/fmcg_sales.csv'
df = pd.read_csv(FILE)
df['date'] = pd.to_datetime(df['date'])
df['revenue'] = df['units_sold'] * df['price_unit']

print("Данные загружены")

# ===================== БЛОК РАСЧЁТОВ =====================
total_units = df['units_sold'].sum()
total_revenue = df['revenue'].sum()
avg_price = df['price_unit'].mean()
promo_share = (df[df['promotion_flag'] == 1]['units_sold'].sum() / total_units * 100) if total_units > 0 else 0
top_brand = df.groupby('brand')['units_sold'].sum().idxmax()
top_sku = df.groupby('sku')['units_sold'].sum().idxmax()

daily = df.groupby('date').agg(
    units_sold=('units_sold', 'sum'),
    revenue=('revenue', 'sum')
).reset_index()

brand_sales = df.groupby('brand')['units_sold'].sum().sort_values(ascending=False)
channel_sales = df.groupby('channel')['units_sold'].sum()
region_sales = df.groupby('region')['units_sold'].sum()
segment_sales = df.groupby('segment')['units_sold'].sum()
promo_effect = df.groupby('promotion_flag')['units_sold'].sum()
top_skus = df.groupby('sku')['units_sold'].sum().nlargest(10)

df['weekday'] = df['date'].dt.day_name()
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
pivot = df.pivot_table(values='price_unit', index='weekday', columns='channel', aggfunc='mean')
pivot = pivot.reindex(weekday_order)

print(f"Всего продано единиц: {total_units}")
print(f"Общая выручка: {total_revenue:.2f}")
print(f"Средняя цена: {avg_price:.2f}")
print(f"Доля промо-продаж: {promo_share:.1f}%")
print(f"Топ-бренд: {top_brand}")
print(f"Топ-SKU: {top_sku}")

# ===================== ГРАФИК 1: Динамика продаж и выручки (увеличенный масштаб) =====================
fig, ax1 = plt.subplots(figsize=(18, 6))
ax1.plot(daily['date'], daily['units_sold'], color=ACCENT, marker='o', markersize=4, label='Продано единиц')
ax1.set_ylabel('Продано единиц', color=ACCENT)
ax1.tick_params(axis='y', labelcolor=ACCENT)
ax1.yaxis.grid(True)

ax2 = ax1.twinx()
ax2.plot(daily['date'], daily['revenue'], color=ACCENT2, linestyle='--', marker='s', markersize=5, label='Выручка')
ax2.set_ylabel('Выручка', color=ACCENT2)
ax2.tick_params(axis='y', labelcolor=ACCENT2)
# СТАЛО:
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))  # раз в неделю, по понедельникам
fig.autofmt_xdate(rotation=45)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', facecolor='#1a2f4e', edgecolor='#4A6080')
ax1.set_title('Динамика продаж и выручки по дням (детальный масштаб)')
fig.tight_layout()
plt.savefig('images/01_sales_revenue_dynamics.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 2: Продажи по брендам =====================
fig, ax = plt.subplots(figsize=(12, 6))   # чуть шире, чтобы подписи не сжимались
bars = ax.bar(brand_sales.index, brand_sales.values, color=ACCENT)
max_val = brand_sales.max()
offset = max_val * 0.03
for bar, val in zip(bars, brand_sales.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + offset, str(val), ha='center', color='white', fontsize=9)
ax.set_ylim(top=ax.get_ylim()[1] * 1.12)
ax.set_title('Продажи по брендам (единиц)')
ax.grid(axis='y', alpha=0.4)

# Поворачиваем подписи на 45 градусов, выравниваем по правому краю и уменьшаем шрифт
ax.set_xticklabels(brand_sales.index, rotation=45, ha='right', fontsize=8)

fig.tight_layout()
plt.savefig('images/02_brand_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 3: Каналы продаж (Donut) =====================
fig, ax = plt.subplots(figsize=(9, 7))
colors_pie = ['#0A7EA4', '#F4A233', '#7BC8A4'][:len(channel_sales)]
wedges, texts, autotexts = ax.pie(channel_sales.values, labels=channel_sales.index,
                                  autopct='%1.1f%%', colors=colors_pie,
                                  startangle=90, pctdistance=0.78,
                                  wedgeprops=dict(width=0.55, edgecolor='#0F1F3D', linewidth=2))
for t in texts: t.set(color='white', fontsize=10)
for a in autotexts: a.set(color='white', fontsize=9, fontweight='bold')
ax.text(0, 0, f'{channel_sales.sum()}\nединиц', ha='center', va='center', fontsize=13, fontweight='bold', color='white')
ax.set_title('Продажи по каналам')
fig.tight_layout()
plt.savefig('images/03_channel_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 4: Продажи по регионам =====================
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(region_sales.index, region_sales.values, color=ACCENT2)
max_val = region_sales.max()
offset = max_val * 0.03
for bar, val in zip(bars, region_sales.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + offset, str(val), ha='center', color='white', fontsize=9)
ax.set_ylim(top=ax.get_ylim()[1] * 1.12)
ax.set_title('Продажи по регионам')
ax.grid(axis='y', alpha=0.4)
fig.tight_layout()
plt.savefig('images/04_region_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 5: Эффект промо =====================
promo_labels = ['Без промо', 'С промо']
promo_values = [promo_effect.get(0, 0), promo_effect.get(1, 0)]
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(promo_labels, promo_values, color=[ACCENT, ACCENT2])
max_val = max(promo_values) if max(promo_values) > 0 else 1
offset = max_val * 0.03
for bar, val in zip(bars, promo_values):
    ax.text(bar.get_x() + bar.get_width()/2, val + offset, str(val), ha='center', color='white', fontsize=9)
ax.set_ylim(top=ax.get_ylim()[1] * 1.15)
ax.set_title('Продажи с промо и без')
ax.grid(axis='y', alpha=0.4)
fig.tight_layout()
plt.savefig('images/05_promo_effect.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 6: Топ-10 SKU =====================
top_skus_plot = top_skus.sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(11, 6))
colors_bars = [ACCENT2 if i == len(top_skus_plot)-1 else ACCENT for i in range(len(top_skus_plot))]
bars = ax.barh(top_skus_plot.index, top_skus_plot.values, color=colors_bars)
max_val = top_skus_plot.max()
offset = max_val * 0.03
for bar, val in zip(bars, top_skus_plot.values):
    ax.text(val + offset, bar.get_y() + bar.get_height()/2, str(int(val)), va='center', color='white', fontsize=9)
ax.set_xlim(right=ax.get_xlim()[1] * 1.12)
ax.set_title('Топ-10 SKU по продажам')
ax.grid(axis='x', alpha=0.4)
fig.tight_layout()
plt.savefig('images/06_top_skus.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 7: KPI-карточки =====================
metrics = [
    ('Продано единиц', f'{total_units:,}'.replace(',', ' '), ACCENT),
    ('Выручка', f'{total_revenue:,.0f} ₽'.replace(',', ' '), ACCENT2),
    ('Средняя цена', f'{avg_price:.2f} ₽', '#7BC8A4'),
    ('Доля промо', f'{promo_share:.1f}%', '#F472B6'),
    ('Топ-бренд', str(top_brand), '#A78BFA'),
]
fig, axes = plt.subplots(1, 5, figsize=(16, 3))
for ax, (label, value, color) in zip(axes, metrics):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.add_patch(plt.Rectangle((0.05, 0.1), 0.9, 0.8, facecolor='#1a2f4e', edgecolor=color, linewidth=2))
    ax.text(0.5, 0.63, value, ha='center', va='center', fontsize=16, fontweight='bold', color=color)
    ax.text(0.5, 0.28, label, ha='center', va='center', fontsize=9, color='#AAAAAA')
fig.suptitle('Сводные показатели FMCG', fontsize=14, y=1.05)
fig.tight_layout()
plt.savefig('images/07_kpi_summary.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 8: Продажи по сегментам =====================
seg_sorted = segment_sales.sort_values(ascending=True)
total_seg = seg_sorted.sum()
fig, ax = plt.subplots(figsize=(12, 7))
colors_seg = [ACCENT if i % 2 == 0 else '#1A5276' for i in range(len(seg_sorted))]
bars = ax.barh(seg_sorted.index, seg_sorted.values, color=colors_seg)
for bar, val in zip(bars, seg_sorted.values):
    pct = val / total_seg * 100
    ax.text(val + total_seg * 0.005, bar.get_y() + bar.get_height()/2,
            f'{int(val):,} ({pct:.1f}%)'.replace(',', ' '),
            va='center', color='white', fontsize=8)
ax.set_xlim(right=ax.get_xlim()[1] * 1.18)
ax.set_title('Распределение продаж по сегментам')
ax.grid(axis='x', alpha=0.4)
fig.tight_layout()
plt.savefig('images/08_segment_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# ===================== ГРАФИК 9: Тепловая карта средней цены =====================
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(pivot.values, cmap='coolwarm', aspect='auto')
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_title('Средняя цена по дням недели и каналам')
fig.colorbar(im, ax=ax, label='Средняя цена')
fig.tight_layout()
plt.savefig('images/09_weekday_channel_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()

print("Все графики сохранены в папку images/")

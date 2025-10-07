from collections import defaultdict, Counter

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas as pd
import numpy as np


def make_simle_stats(data):
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")

    df_list = []
    for split, entities in data.items():
        for entity, count in entities.items():
            df_list.append({'Split': split, 'Entity': entity, 'Count': count})

    df = pd.DataFrame(df_list)

    plt.figure(figsize=(16, 8))
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle('Статистика', fontsize=16, fontweight='bold')

    pivot_df = df.pivot(index='Entity', columns='Split', values='Count')
    pivot_df.plot(kind='bar', ax=ax1, edgecolor='black', alpha=0.8)
    ax1.set_title('Распределение сущностей по датасетам', fontweight='bold')
    ax1.set_ylabel('Количество')
    ax1.set_xlabel('Тип сущности')
    ax1.legend(title='Dataset')
    ax1.grid(axis='y', alpha=0.3)

    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    for i, split in enumerate(['test']): # 'train', 'validation', 
        split_data = df[df['Split'] == split]
        wedges, texts, autotexts = ax2.pie(
            split_data['Count'], 
            labels=split_data['Entity'],
            autopct='%.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops=dict(edgecolor='w', linewidth=1)
        )
        ax2.set_title(f'Распределение {split} dataset', fontweight='bold')

    plt.tight_layout()
    plt.show()


def __plot_entity_histogram(ax, data, entity_type, color):
    words = data['words']
    counts = data['counts']
    
    bars = ax.barh(words, counts, color=color, alpha=0.8, edgecolor='black')
    ax.set_title(f'{entity_type} - Top {len(words)} Words\n'
                f'Total: {data["total_words"]:,} words, '
                f'Unique: {data["total_unique"]:,}', 
                fontweight='bold', fontsize=12)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Words')
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + max(counts)*0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:,}', ha='left', va='center', fontsize=9)
    
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()


def __plot_comparison_stats(ax, stats, colors):
    entities = list(stats.keys())
    total_words = [stats[entity]['total_words'] for entity in entities]
    unique_words = [stats[entity]['total_unique'] for entity in entities]
    
    x = np.arange(len(entities))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, total_words, width, label='Total Words', 
                   color=[colors[ent] for ent in entities], alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, unique_words, width, label='Unique Words', 
                   color=[colors[ent] for ent in entities], alpha=0.6, edgecolor='black')
    
    ax.set_title('Сравнительная статистика по типам сущностей', fontweight='bold')
    ax.set_xlabel('Entity Type')
    ax.set_ylabel('Number of Words')
    ax.set_xticks(x)
    ax.set_xticklabels(entities)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(total_words)*0.01,
                   f'{height:,}', ha='center', va='bottom', fontsize=10)


def __print_detailed_statistics(stats):
    print("=" * 80)
    print("ДЕТАЛЬНАЯ СТАТИСТИКА СЛОВ ПО ТИПАМ NER СУЩНОСТЕЙ")
    print("=" * 80)
    
    for entity_type, data in stats.items():
        print(f"\n{entity_type}:")
        print(f"  Всего слов: {data['total_words']:,}")
        print(f"  Уникальных слов: {data['total_unique']:,}")
        print(f"  Коэффициент уникальности: {data['total_unique']/data['total_words']:.3f}")
        print(f"  Топ-5 слов: {', '.join(data['words'][:5])}")


def plot_ner_word_statistics(word_lists, top_n=20, figsize=(20, 15)):
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")

    fig = plt.figure(figsize=figsize)
    fig.suptitle('Статистика слов по типам NER сущностей (TRAIN)', 
                 fontsize=20, fontweight='bold', y=0.95)

    gs = gridspec.GridSpec(2, 3, figure=fig)

    colors = {'PER': '#e74c3c', 'LOC': '#3498db', 'ORG': '#2ecc71', 'O': '#f39c12'}
    
    stats = {}
    for entity_type, words in word_lists.items():
        word_counts = Counter(words)
        top_words = word_counts.most_common(top_n)
        stats[entity_type] = {
            'words': [word for word, count in top_words],
            'counts': [count for word, count in top_words],
            'total_unique': len(word_counts),
            'total_words': len(words)
        }

    ax1 = fig.add_subplot(gs[0, 0])
    __plot_entity_histogram(ax1, stats['PER'], 'PER', colors['PER'])

    ax2 = fig.add_subplot(gs[0, 1])
    __plot_entity_histogram(ax2, stats['LOC'], 'LOC', colors['LOC'])

    ax3 = fig.add_subplot(gs[0, 2])
    __plot_entity_histogram(ax3, stats['ORG'], 'ORG', colors['ORG'])
    
    ax4 = fig.add_subplot(gs[1, 0])
    __plot_entity_histogram(ax4, stats['O'], 'O (Non-entity)', colors['O'])
    
    ax5 = fig.add_subplot(gs[1, 1:])
    __plot_comparison_stats(ax5, stats, colors)
    
    plt.show()
    
    __print_detailed_statistics(stats)

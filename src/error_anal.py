import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from sklearn.metrics import classification_report, confusion_matrix
import itertools


def __prepare_ner_analysis_data(results):
    """Подготовка данных для анализа NER"""
    
    analysis_data = []
    error_analysis = []
    
    for result in results:
        text_id = result['id']
        text = result['text']
        
        true_ents_by_pos = {(ent['start'], ent['end']): ent for ent in result['true_entities']}
        pred_ents_by_pos = {(ent['start'], ent['end']): ent for ent in result['predicted_entities']}
        
        all_positions = set(true_ents_by_pos.keys()) | set(pred_ents_by_pos.keys())
        
        for pos in all_positions:
            true_ent = true_ents_by_pos.get(pos)
            pred_ent = pred_ents_by_pos.get(pos)
            
            if true_ent and pred_ent:
                if true_ent['type'] == pred_ent['type']:
                    status = 'CORRECT'
                else:
                    status = 'TYPE_ERROR'
            elif true_ent and not pred_ent:
                status = 'MISSED'
            elif not true_ent and pred_ent:
                status = 'FALSE_POSITIVE'
            else:
                continue
                
            analysis_data.append({
                'text_id': text_id,
                'start': pos[0],
                'end': pos[1],
                'true_type': true_ent['type'] if true_ent else None,
                'pred_type': pred_ent['type'] if pred_ent else None,
                'status': status,
                'text': true_ent['text'] if true_ent else pred_ent['text']
            })
            
            if status != 'CORRECT':
                error_analysis.append({
                    'text_id': text_id,
                    'text': text,
                    'entity_text': true_ent['text'] if true_ent else pred_ent['text'],
                    'true_type': true_ent['type'] if true_ent else None,
                    'pred_type': pred_ent['type'] if pred_ent else None,
                    'error_type': status,
                    'start': pos[0],
                    'end': pos[1]
                })
    
    return pd.DataFrame(analysis_data), pd.DataFrame(error_analysis)


def __plot_ner_performance_summary(analysis_df):
    """График общего summary производительности"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('NER Model Performance Analysis', fontsize=16, fontweight='bold')
    
    error_counts = analysis_df['status'].value_counts()
    axes[0, 0].pie(error_counts.values, labels=error_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 0].set_title('Distribution of Prediction Types')

    true_types = analysis_df[analysis_df['true_type'].notna()]['true_type'].value_counts()
    pred_types = analysis_df[analysis_df['pred_type'].notna()]['pred_type'].value_counts()
    
    types_df = pd.DataFrame({'True': true_types, 'Predicted': pred_types}).fillna(0)
    types_df.plot(kind='bar', ax=axes[0, 1], color=['skyblue', 'lightcoral'])
    axes[0, 1].set_title('Entity Types: True vs Predicted')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    type_accuracy = {}
    for entity_type in analysis_df['true_type'].dropna().unique():
        type_data = analysis_df[analysis_df['true_type'] == entity_type]
        accuracy = len(type_data[type_data['status'] == 'CORRECT']) / len(type_data)
        type_accuracy[entity_type] = accuracy
    
    pd.Series(type_accuracy).plot(kind='bar', ax=axes[1, 0], color='lightgreen')
    axes[1, 0].set_title('Accuracy by Entity Type')
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    analysis_df['entity_length'] = analysis_df['end'] - analysis_df['start']
    length_accuracy = analysis_df[analysis_df['true_type'].notna()].groupby(
        pd.cut(analysis_df['entity_length'], bins=10)
    )['status'].apply(lambda x: (x == 'CORRECT').mean())
    
    length_accuracy.plot(kind='bar', ax=axes[1, 1], color='purple', alpha=0.7)
    axes[1, 1].set_title('Accuracy by Entity Length')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].set_xlabel('Entity Length')
    axes[1, 1].set_ylabel('Accuracy')
    
    plt.tight_layout()
    return fig

def __plot_confusion_matrix(analysis_df):
    """Матрица ошибок для типов сущностей"""
    
    true_types = []
    pred_types = []
    
    for _, row in analysis_df.iterrows():
        if row['true_type'] and row['pred_type']:
            true_types.append(row['true_type'])
            pred_types.append(row['pred_type'])
    
    if not true_types:
        print("No data for confusion matrix")
        return None
    
    unique_types = sorted(set(true_types + pred_types))
    cm = confusion_matrix(true_types, pred_types, labels=unique_types)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=unique_types, 
           yticklabels=unique_types,
           title='Confusion Matrix',
           ylabel='True Type',
           xlabel='Predicted Type')
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")
    
    fig.tight_layout()
    return fig

def __plot_error_analysis(error_df):
    """Анализ ошибок"""
    
    if error_df.empty:
        print("No errors to analyze")
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Error Analysis', fontsize=16, fontweight='bold')
    
    error_type_counts = error_df['error_type'].value_counts()
    error_type_counts.plot(kind='bar', ax=axes[0, 0], color=['red', 'orange', 'yellow'])
    axes[0, 0].set_title('Error Types Distribution')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    error_by_type = error_df[error_df['true_type'].notna()].groupby('true_type')['error_type'].value_counts().unstack().fillna(0)
    if not error_by_type.empty:
        error_by_type.plot(kind='bar', ax=axes[0, 1], stacked=True)
        axes[0, 1].set_title('Errors by Entity Type')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].legend(title='Error Type')

    error_df['entity_length'] = error_df['end'] - error_df['start']
    error_df['entity_length'].hist(bins=20, ax=axes[1, 0], color='lightcoral', alpha=0.7)
    axes[1, 0].set_title('Entity Length Distribution in Errors')
    axes[1, 0].set_xlabel('Entity Length')
    axes[1, 0].set_ylabel('Count')

    top_error_entities = error_df['entity_text'].value_counts().head(10)
    top_error_entities.plot(kind='barh', ax=axes[1, 1], color='salmon')
    axes[1, 1].set_title('Top 10 Most Frequently Erroneous Entities')
    
    plt.tight_layout()
    return fig

def __plot_position_analysis(analysis_df):
    """Анализ позиционных ошибок"""
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Positional Analysis', fontsize=16, fontweight='bold')
    
    analysis_df['position_ratio'] = analysis_df['start'] / analysis_df['start'].max()
    position_bins = pd.cut(analysis_df['position_ratio'], bins=10)
    position_accuracy = analysis_df.groupby(position_bins)['status'].apply(
        lambda x: (x == 'CORRECT').mean() if len(x) > 0 else 0
    )
    
    position_accuracy.plot(kind='line', ax=axes[0], marker='o', color='blue')
    axes[0].set_title('Accuracy by Position in Text')
    axes[0].set_xlabel('Normalized Position')
    axes[0].set_ylabel('Accuracy')
    axes[0].grid(True, alpha=0.3)
    
    sns.boxplot(data=analysis_df, x='status', y='entity_length', ax=axes[1])
    axes[1].set_title('Entity Length by Prediction Status')
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig


def generate_ner_report(results):
    """Генерация полного отчета с графиками"""
    
    print("Preparing NER analysis data...")
    analysis_df, error_df = __prepare_ner_analysis_data(results)
    
    print("Generating plots...")
    
    plots = {}
    
    plots['performance_summary'] = __plot_ner_performance_summary(analysis_df)
    # plots['confusion_matrix'] = __plot_confusion_matrix(analysis_df)
    plots['error_analysis'] = __plot_error_analysis(error_df)
    # plots['position_analysis'] = __plot_position_analysis(analysis_df)
    
    print("\n=== NER PERFORMANCE SUMMARY ===")
    total_entities = len(analysis_df[analysis_df['true_type'].notna()])
    correct_predictions = len(analysis_df[analysis_df['status'] == 'CORRECT'])
    accuracy = correct_predictions / total_entities if total_entities > 0 else 0
    
    print(f"Total entities: {total_entities}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Missed entities: {len(analysis_df[analysis_df['status'] == 'MISSED'])}")
    print(f"False positives: {len(analysis_df[analysis_df['status'] == 'FALSE_POSITIVE'])}")
    print(f"Type errors: {len(analysis_df[analysis_df['status'] == 'TYPE_ERROR'])}")
    
    return plots, analysis_df, error_df


from collections import Counter

def show_top_errors(results, top_n=5):
    """Показать топ ошибок по каждой категории сущностей"""
    
    error_categories = {}
    
    for result in results:
        true_ents = {(e['start'], e['end'], e['type']): e for e in result['true_entities']}
        pred_ents = {(e['start'], e['end'], e['type']): e for e in result['predicted_entities']}
        
        # Ложные срабатывания (False Positives)
        for pred in pred_ents.values():
            if (pred['start'], pred['end']) not in {(e['start'], e['end']) for e in true_ents.values()}:
                error_type = f"FP_{pred['type']}"
                if error_type not in error_categories:
                    error_categories[error_type] = Counter()
                error_categories[error_type][pred['text']] += 1
        
        # Пропущенные сущности (False Negatives)
        for true in true_ents.values():
            if (true['start'], true['end']) not in {(e['start'], e['end']) for e in pred_ents.values()}:
                error_type = f"FN_{true['type']}"
                if error_type not in error_categories:
                    error_categories[error_type] = Counter()
                error_categories[error_type][true['text']] += 1
        
        # Ошибки типа (Type Errors)
        for true in true_ents.values():
            for pred in pred_ents.values():
                if (true['start'], true['end']) == (pred['start'], pred['end']) and true['type'] != pred['type']:
                    error_type = f"TYPE_{true['type']}_as_{pred['type']}"
                    if error_type not in error_categories:
                        error_categories[error_type] = Counter()
                    error_categories[error_type][true['text']] += 1
    
    # Выводим топ ошибок для каждой категории
    for error_type, counter in sorted(error_categories.items()):
        print(f"\n{error_type}:")
        for text, count in counter.most_common(top_n):
            print(f"  {text}: {count}")
    
    return error_categories
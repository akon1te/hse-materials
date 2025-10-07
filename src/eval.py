from typing import Dict, List, Any
from collections import defaultdict



def evaluate(results: List[Dict], eval_by_types: bool=True) -> None:
    
    all_true = 0
    all_predicted = 0
    matches = 0
    
    type_breakdown = defaultdict(lambda: {'true': 0, 'predicted': 0, 'matches': 0})
    
    for example in results:
        true_entities = example['true_entities']
        predicted_entities = example['predicted_entities']
        
        all_true += len(true_entities)
        all_predicted += len(predicted_entities)
      
        for true_ent in true_entities:
            type_breakdown[true_ent['type']]['true'] += 1
            
            for pred_ent in predicted_entities:
                if (true_ent['start'] == pred_ent['start'] and 
                    true_ent['end'] == pred_ent['end'] and 
                    true_ent['type'] == pred_ent['type']):
                    
                    matches += 1
                    type_breakdown[true_ent['type']]['matches'] += 1
                    
                    break
        
        for pred_ent in predicted_entities:
            type_breakdown[pred_ent['type']]['predicted'] += 1
    
    
    precision = matches / all_predicted if all_predicted > 0 else 0
    recall = matches / all_true if all_true > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"Общие метрики:")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1:        {f1:.3f}")
    print(f"  True entities: {all_true}")
    print(f"  Predicted entities: {all_predicted}")
    print(f"  Matches: {matches}")
    
    if eval_by_types:
        
        print(f"\nДетализация по типам:")
        for ent_type in ['PER', 'LOC', 'ORG']:
            if ent_type in type_breakdown:
                stats = type_breakdown[ent_type]
                type_precision = stats['matches'] / stats['predicted'] if stats['predicted'] > 0 else 0
                type_recall = stats['matches'] / stats['true'] if stats['true'] > 0 else 0
                type_f1 = 2 * type_precision * type_recall / (type_precision + type_recall) if (type_precision + type_recall) > 0 else 0
                
                print(f"  {ent_type}:")
                print(f"    Precision: {type_precision:.3f}")
                print(f"    Recall:    {type_recall:.3f}")
                print(f"    F1:        {type_f1:.3f}")
                print(f"    True: {stats['true']}, Predicted: {stats['predicted']}, Matches: {stats['matches']}")


def get_error_pairs(results: List[Dict]) -> List[Dict]:
    
    error_examples = []
    
    for example in results:
        true_set = {(ent['start'], ent['end'], ent['type']) for ent in example['true_entities']}
        pred_set = {(ent['start'], ent['end'], ent['type']) for ent in example['predicted_entities']}
        
        false_negatives = [ent for ent in example['true_entities'] 
                            if (ent['start'], ent['end'], ent['type']) not in pred_set]
        false_positives = [ent for ent in example['predicted_entities'] 
                            if (ent['start'], ent['end'], ent['type']) not in true_set]
        
        if false_negatives or false_positives:
            error_examples.append({
                'id': example['id'],
                'text': example['text'],
                'false_negatives': false_negatives,
                'false_positives': false_positives,
                'true_entities': example['true_entities'],
                'predicted_entities': example['predicted_entities']
            })
        
    return error_examples

import os
import json
from typing import Dict, List
from datasets import DatasetDict



def load_natasha_data(data_dir: str = "./natasha_data") -> Dict[str, List[Dict]]:

    natasha_data = {}
    
    for split in ['train', 'validation', 'test']:
        file_path = os.path.join(data_dir, f"{split}.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                natasha_data[split] = json.load(f)
        #    print(f"Загружено {len(natasha_data[split])} примеров из {split}")
        else:
        #    print(f"Файл {file_path} не найден")
            natasha_data[split] = []
    
    return natasha_data


def get_stats(dataset: DatasetDict) -> Dict:
    entity_counts = {'train': {'PER': 0, 'LOC': 0, 'ORG': 0, 'O': 0},
              'validation': {'PER': 0, 'LOC': 0, 'ORG': 0, 'O': 0},
              'test': {'PER': 0, 'LOC': 0, 'ORG': 0, 'O': 0}}  

    for split in ['train', 'validation', 'test']:
        for example in dataset[split][0]['data']:
            for entity in example['ner_tags_str']:
                entity = entity.split('-')[-1]
                entity_counts[split][entity] += 1
                
    return entity_counts
            

def analyze_entity_patterns(entity_counts: Dict):

    for split in ['train', 'validation', 'test']:
        print(f"\n--- {split.upper()} ---")
        
        for entity_type in ['PER', 'LOC', 'ORG', 'O']:
            entities = entity_counts[split][entity_type]
            unique_entities = set(entities)
            
            print(f"{entity_type}:")
            print(f"  Всего: {len(entities)}")
            print(f"  Уникальных: {len(unique_entities)}")
            
            if entities and entity_type != 'O':

                from collections import Counter
                counter = Counter(entities)
                top_10 = counter.most_common(10)
                print(f"  Топ-10: {top_10}")
            
            if entity_type == 'O' and entities:
     
                from collections import Counter
                counter = Counter(entities)
                top_10_o = counter.most_common(10)
            
    
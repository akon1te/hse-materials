from typing import Dict, List, Any    

import json
import os
import re
from pathlib import Path

from datasets import load_dataset, DatasetDict

    
    
def parse_entities_from_example(example: Dict[str, Any]) -> tuple:

    tokens = example['tokens']
    ner_tags_str = example['ner_tags_str']
    
    text = reconstruct_text_from_tokens(tokens)
    token_positions = calculate_token_positions(tokens, text)
    
    entities = extract_entities_from_bio(tokens, ner_tags_str, token_positions)
    
    return text, entities


def reconstruct_text_from_tokens(tokens: List[str]) -> str:

    text = ""
    for i, token in enumerate(tokens):
        if i == 0:
            text += token
        else:
            prev_token = tokens[i-1]
            if should_add_space(prev_token, token):
                text += " " + token
            else:
                text += token
    return text


def should_add_space(prev_token: str, current_token: str) -> bool:

    no_space_after = {',', '.', '!', '?', ':', ';', '"', "'", '»', '”', ')', ']', '}'}
    no_space_before = {'«', '“', '(', '[', '{'}
    
    if prev_token in no_space_after:
        return False
    if current_token in no_space_before:
        return False
    
    return True


def calculate_token_positions(tokens: List[str], text: str) -> List[Dict[str, int]]:

    positions = []
    current_pos = 0
    
    for i, token in enumerate(tokens):
        if i == 0:
            start = 0
            end = len(token)
        else:
            prev_token = tokens[i-1]
            if should_add_space(prev_token, token):
                current_pos += 1
            start = current_pos
            end = current_pos + len(token)
        
        positions.append({'start': start, 'end': end, 'token': token})
        current_pos = end
    
    return positions


def extract_entities_from_bio(tokens: List[str], ner_tags_str: List[str], 
                            token_positions: List[Dict]) -> List[Dict[str, Any]]:

    entities = []
    current_entity = None
    
    for i, (token, tag) in enumerate(zip(tokens, ner_tags_str)):
        if tag == 'O':
            if current_entity is not None:
                entities.append(current_entity)
                current_entity = None
            continue
        
        bio, entity_type = tag.split('-')
        
        if bio == 'B':
            if current_entity is not None:
                entities.append(current_entity)
            
            current_entity = {
                'text': token,
                'type': entity_type,
                'start': token_positions[i]['start'],
                'end': token_positions[i]['end'],
                'tokens': [token]
            }
        
        elif bio == 'I':
            if current_entity is not None and current_entity['type'] == entity_type:
                current_entity['text'] += ' ' + token if should_add_space(
                    current_entity['tokens'][-1], token
                ) else token
                current_entity['end'] = token_positions[i]['end']
                current_entity['tokens'].append(token)
            else:
                if current_entity is not None:
                    entities.append(current_entity)
                current_entity = {
                    'text': token,
                    'type': entity_type,
                    'start': token_positions[i]['start'],
                    'end': token_positions[i]['end'],
                    'tokens': [token]
                }
    
    if current_entity is not None:
        entities.append(current_entity)
    
    for entity in entities:
        if 'tokens' in entity:
            del entity['tokens']
    
    return entities



def save_natasha_data(natasha_data: Dict, output_dir: str = "./natasha_data"):
    
    output_dir_path = Path(output_dir)
    
    if not output_dir_path.is_dir():
        os.makedirs(output_dir)
    
    for split in ['train', 'validation', 'test']:
        filename = os.path.join(output_dir, f"{split}.json")
        
        data_to_save = []
        for item in natasha_data[split]:
            data_to_save.append({
                'id': item['id'],
                'text': item['text'],
                'entities': item['entities']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)


def process_dataset(dataset_name: str) -> tuple:

    dataset = load_dataset(dataset_name, cache_dir='data')
    
    entity_counts = {
        'train': {'PER': [], 'LOC': [], 'ORG': [], 'O': []},
        'validation': {'PER': [], 'LOC': [], 'ORG': [], 'O': []},
        'test': {'PER': [], 'LOC': [], 'ORG': [], 'O': []}
    }
    
    natasha_data = {
        'train': [],
        'validation': [], 
        'test': []
    }
    
    for split in ['train', 'validation', 'test']:
        
        split_data = dataset[split][0]['data']
        
        for example in split_data:
            text, entities = parse_entities_from_example(example)
            
            for entity in entities:
                entity_type = entity['type']
                if entity_type in entity_counts[split]:
                    entity_counts[split][entity_type].append(entity['text'])
            
            for token, tag in zip(example['tokens'], example['ner_tags_str']):
                if tag == 'O':
                    entity_counts[split]['O'].append(token)
            
            natasha_data[split].append({
                'text': text,
                'entities': entities,
                'id': example['id']
            })
            
    save_natasha_data(natasha_data)
    
    return entity_counts, natasha_data


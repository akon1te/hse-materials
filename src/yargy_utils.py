from typing import List, Dict, Any

from yargy import Parser



def extract_entities_yargy(
    text: str, 
    per_parser: Parser, 
    loc_parser: Parser, 
    org_parser: Parser
) -> List[Dict[str, Any]]:

    entities = []

    for match in per_parser.findall(text):
        span = match.span
        entities.append({
            'text': text[span.start:span.stop],
            'type': 'PER',
            'start': span.start,
            'end': span.stop
        })

    for match in loc_parser.findall(text):
        span = match.span
        entities.append({
            'text': text[span.start:span.stop],
            'type': 'LOC',
            'start': span.start,
            'end': span.stop
        })

    for match in org_parser.findall(text):
        span = match.span
        entities.append({
            'text': text[span.start:span.stop],
            'type': 'ORG',
            'start': span.start,
            'end': span.stop
        })

    entities = resolve_overlapping_entities(entities)
    
    return entities


def resolve_overlapping_entities(entities: List[Dict]) -> List[Dict]:

    if not entities:
        return []
    
    entities.sort(key=lambda x: x['start'])
    
    result = []
    current = entities[0]
    
    for i in range(1, len(entities)):
        next_entity = entities[i]
        
        if current['end'] <= next_entity['start']:
            result.append(current)
            current = next_entity
        else:
            priorities = {'PER': 3, 'LOC': 2, 'ORG': 1}
            current_priority = priorities.get(current['type'], 0)
            next_priority = priorities.get(next_entity['type'], 0)
            
            if current_priority >= next_priority:
                pass
            else:
                current = next_entity
    
    result.append(current)
    return result


import json
import yaml
import random
import time

import pandas as pd

from confluent_kafka import Producer


class DataExtraction:
    def __init__(self, data_path: str, raw_data_config: dict, topic_configs: dict):
        self.data_path = data_path
        self.config = raw_data_config
        self.topic_configs = topic_configs
        
        self.producers = [Producer(self.config['producer_config']) for _ in range(self.config['n_producers'] + 1)]
        print(f'Producer number {len(self.producers)}')
        
        
    def extract(self):
        data = pd.read_csv(self.data_path)
        
        while True:
            #simulating transfer the sample to a random producer
            producer_idx = random.randint(0, self.config['n_producers'])
            
            input_idx = random.randint(0, data.shape[0] - 1)
            input_sample = data.iloc[input_idx].to_dict()
            input_sample['idx'] = input_idx
            
            self.producers[producer_idx].produce(self.topic_configs['raw_data_topic_name'], key='1', value=json.dumps(input_sample))
            self.producers[producer_idx].flush()
            
            print(f'Produced sample {input_idx} from producer {producer_idx}')
            time.sleep(2 + random.uniform(0, 5.0))


def main():
    
    with open('src/config.yaml') as cfg: 
        config = yaml.load(cfg, Loader=yaml.Loader)
    
    pipe = DataExtraction(
        data_path='data/train_augmented.csv',
        raw_data_config=config['stages_configs']['raw_data_configs'],
        topic_configs=config['topics']
    )        
    
    pipe.extract()
            
            
if __name__ == '__main__':
    main()
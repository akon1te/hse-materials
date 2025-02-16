import json
import yaml
import time

from confluent_kafka import Consumer, Producer

import torch
from transformers import AutoModelForSequenceClassification


class DataAnalysis:
    def __init__(self, ml_configs, topic_configs, model_name):

        self.config = ml_configs
        self.topic_configs = topic_configs
        
        print(f'Init tokenizer model with name {model_name}')
        if torch.cuda.is_available():
            self.device = 'cuda'
        else:
            self.device = 'cpu'
        print(f'Divice is {self.device}')
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
        
        self.consumer = Consumer(self.config['consumer_config'])
        self.consumer.subscribe([self.topic_configs['processing_topic_name']])
        
        self.producer = Producer(self.config['producer_config'])
    
    def inference(self):
        while True:
            msg = self.consumer.poll(1)
            
            if msg is not None:
            
                prepared_data = json.loads(msg.value())
                print(f'Msg index {prepared_data["idx"]}')
                
                s_time = time.time()    
                predicted_cls = self.model(torch.tensor([prepared_data['tokenized_text']]).to(self.device)).logits.argmax().item()
                infer_time = time.time() - s_time
                
                prepared_data = {
                    'idx': prepared_data["idx"], 
                    'need_ban': prepared_data['need_ban'],
                    'predicted_cls': predicted_cls,
                    'infer_time': infer_time
                }

                print(f'For {prepared_data["idx"]} predicted class: {predicted_cls}')
                
                self.producer.produce(topic=self.topic_configs['ml_topic_name'], key='1', value=json.dumps(prepared_data))
                self.producer.flush()
                

def main():
    
    with open('src/config.yaml') as cfg: 
        config = yaml.load(cfg, Loader=yaml.Loader)
    
    pipe = DataAnalysis(
        ml_configs=config['stages_configs']['ml_configs'],
        topic_configs=config['topics'],
        model_name="s-nlp/roberta_toxicity_classifier"
    )        
    
    pipe.inference()
            
            
if __name__ == '__main__':
    main()


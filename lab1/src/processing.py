import json
import yaml
from confluent_kafka import Consumer, Producer

from transformers import AutoTokenizer


class DataProcessing:
    def __init__(self, processing_configs, topic_configs, tokenizer_name):
        self.config = processing_configs
        self.topic_configs = topic_configs
        
        print(f'Init tokenizer model with name {tokenizer_name}')
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        
        self.consumer = Consumer(self.config['consumer_config'])
        self.consumer.subscribe([self.topic_configs['raw_data_topic_name']])
        
        self.producer = Producer(self.config['producer_config'])
    
    def process(self):
        while True:
            msg = self.consumer.poll(1)
            
            if msg is not None:
                
                data_dict = json.loads(msg.value())
                print(f'Msg index {data_dict["idx"]}')
                            
                text = data_dict['comment_text']
                tokenized_text = self.tokenizer.encode(text, truncation=True, max_length=512)
                prepared_data = {'idx': data_dict["idx"], 'need_ban': data_dict['need_ban'], 'tokenized_text': tokenized_text}
                
                print(f'Tonekized text shape {len(tokenized_text)}')
                
                self.producer.produce(topic=self.topic_configs['processing_topic_name'], key='1', value=json.dumps(prepared_data))
                self.producer.flush()
                

def main():
    
    with open('src/config.yaml') as cfg: 
        config = yaml.load(cfg, Loader=yaml.Loader)
    
    pipe = DataProcessing(
        processing_configs=config['stages_configs']['processing_configs'],
        topic_configs=config['topics'],
        tokenizer_name="s-nlp/roberta_toxicity_classifier"
    )        
    
    pipe.process()
            
            
if __name__ == '__main__':
    main()
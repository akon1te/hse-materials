import json
import yaml

import streamlit as st
import plotly.express as px

from confluent_kafka import Consumer

from sklearn.metrics import f1_score, balanced_accuracy_score

st.set_page_config(page_title='Raw data processing', layout='wide')


class DataVisualizer:
    def __init__(self, config, topic):
        
        self.age_data = {}
        self.device_data = {}
        self.toxicity_data = {}
        
        self.raw_data_consumer = Consumer(config['consumer_config'])
        self.raw_data_consumer.subscribe([topic['raw_data_topic_name']])
        
        st.session_state.ages = {}
        st.session_state.devices = {}
        st.session_state.toxic_types = {}
        
        self.chart_holder_age = st.empty()
        self.chart_holder_device = st.empty()
        self.chart_holder_toxicity = st.empty() 
        
        self.ml_predictions_consumer = Consumer(config['consumer_config'])
        self.ml_predictions_consumer.subscribe([topic['ml_topic_name']])
        
        st.session_state.infer_time = []
        
        self.gt_labels = []
        self.pred_labels = []

        st.session_state.f1 = []
        st.session_state.balanced_acc = []
        
        self.chart_holder_infer_time = st.empty()
        self.chart_holder_f1 = st.empty() 
        self.chart_holder_balanced_acc = st.empty() 

        
    def get_data(self):
        while True:
            msg = self.raw_data_consumer.poll(1)

            if msg is not None:
                raw_data = json.loads(msg.value())
                print(f'Raw data idx: {raw_data["idx"]}')
            
                if raw_data['age'] not in st.session_state.ages:
                    st.session_state.ages[raw_data['age']] = 1
                else:
                    st.session_state.ages[raw_data['age']] += 1
                
                if raw_data['device'] not in st.session_state.devices:
                    st.session_state.devices[raw_data['device']] = 1
                else:
                    st.session_state.devices[raw_data['device']] += 1
                
                for toxic_type in ['toxic', 'severe_toxic', 'obscene', 'threat','insult', 'identity_hate']:
                    if raw_data[toxic_type] not in st.session_state.toxic_types:
                        st.session_state.toxic_types[raw_data[toxic_type]] = 1
                    else:
                        st.session_state.toxic_types[raw_data[toxic_type]] += 1
                    
                self.visualize_raw()
                
                
            msg = self.ml_predictions_consumer.poll(1)

            if msg is not None:
                ml_data = json.loads(msg.value())
                print(f'Data idx from model: {ml_data["idx"]}')
                
                st.session_state.infer_time.append(ml_data['infer_time'])
                
                self.gt_labels.append(ml_data['need_ban'])
                self.pred_labels.append(ml_data['predicted_cls'])

                st.session_state.balanced_acc.append(balanced_accuracy_score(self.gt_labels, self.pred_labels))
                st.session_state.f1.append(f1_score(self.gt_labels, self.pred_labels))
                
                self.chart_holder_infer_time.line_chart(
                    st.session_state.infer_time,
                    x_label='Время инфернеса'
                )
                self.chart_holder_f1.metric(
                    label='f1', 
                    value=st.session_state.f1[-1],
                ) 
                self.chart_holder_balanced_acc.metric(
                    label='balanced_acc',
                    value=st.session_state.balanced_acc[-1], 
                )

            
    def show_age_distribution(self):

        fig = px.bar(
            {'Age Group': list(st.session_state.ages.keys()), 'Count': list(st.session_state.ages.values())},
            x='Age Group',
            y='Count',
            title='Распределение по возрастам',
            color='Age Group',
            labels={'Count': 'Количество людей'}
        )
        self.chart_holder_age.plotly_chart(fig, use_container_width=True)

    def show_device_pie(self):

        fig = px.pie(
            {'Device': list(st.session_state.devices.keys()), 'Count': list(st.session_state.devices.values())},
            names='Device',
            values='Count',
            title='Распределение устройств',
            hole=0.3
        )
        self.chart_holder_device.plotly_chart(fig, use_container_width=True)

    def show_toxicity_flags(self):

        fig = px.bar(
            {'Toxic types': list(st.session_state.toxic_types.keys()), 'Count': list(st.session_state.toxic_types.values())},
            x='Toxic types',
            y='Count',
            title='Распределение флагов токсичности',
            color='Toxic types',
            labels={'Count': 'Количество случаев'}
        )
        self.chart_holder_toxicity.plotly_chart(fig, use_container_width=True)

    def visualize_raw(self):
        
        self.show_age_distribution()
        self.show_device_pie()
        self.show_toxicity_flags()
        
    
    
def main():
    
    with open('src/config.yaml') as cfg: 
        config = yaml.load(cfg, Loader=yaml.Loader)
    
    st.header("Аналитика по сообщениям в соцсети")
    
    raw_data_visualizer = DataVisualizer(config['stages_configs']['visualization_configs'], config['topics'])
    raw_data_visualizer.get_data()
    
    
    
if __name__ == '__main__':
    main()
    
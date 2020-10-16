import streamlit as st
from Objects import website_objects as web

def micro_app():
    
    st.title('Data Collector')
    
    st.write('Get to know the status of tweets collected today')
    st.write('---')
    
    data_collector=web.data_collection()
    
    data_collector.status()
    
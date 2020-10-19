import streamlit as st
from Objects import website_objects as web

def micro_app():
    
    st.title('Pre Processing')
    st.write('In order to cluster the Community, we have to pre process the data')
    st.write('Please do this step **before Clustring**')
    st.write('---')
    
    
    pp=web.preprocess()
    
    pp.get_details()
    
    pp.process_data()
    
    pp.show_status()
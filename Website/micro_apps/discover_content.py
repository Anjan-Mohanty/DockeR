import streamlit as st
from Objects import website_objects as web

def micro_app():
    
    st.title('Discover Content')
    st.write('Get to **know** what are **people talking** in a **Cluster**')
    st.write('---')
    
    dc=web.discover_content()
    
    dc.extract_trends()
    
    dc.get_details()
    
    dc.show_content()
import streamlit as st
from Objects import website_objects as web

def micro_app():
    
    st.title('Discover Users')
    st.write('To Discover New Users go ahed 🚴‍♀️')
    st.write('---')
    
    du=web.discover_users()
    
    du.start_discovering()
    
    du.get_users()
    
    du.take_actions()
    
    du.show_preview()
    
    du.finilize()
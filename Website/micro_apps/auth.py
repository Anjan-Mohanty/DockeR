import streamlit as st
from Objects import website_objects as web

def micro_app():
    
    st.title('Twitter API Auth Keys')
    
    st.write('In order to collect data from twitter **ethically** we use **Twitter API Auth Keys**')
    st.write('To get your API Keys go to [apps.twitter](https://developer.twitter.com/en/apps)')
    st.write('To collect more data you need more Twitter API Keys')
    st.write('---')
    
    auth_key=web.auth_keys()
    
    auth_key.get_keys()
    
    auth_key.is_auth_added()
    
    auth_key.delete()
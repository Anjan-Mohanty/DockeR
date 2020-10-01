import streamlit as st
import website_objects as web

def micro_app():
    
    st.title('Twitter API Auth Keys')
    st.write('In order to collect data from twitter **ethically** we use **Twitter API Auth Keys**')
    st.write('To get your API Keys go to [apps.twitter](https://developer.twitter.com/en/apps)')
    st.write('To collect more data you need more Twitter API Keys')
    st.write('---')
    
    keys=web.auth_keys()
    
    keys.get_keys()
    
    keys.is_auth_added()
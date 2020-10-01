import streamlit as st
import website_objects as web

def micro_app():
    
    st.title('Add User')
    st.write('To add single user please fill the details')
    st.write('---')
    
    au=web.add_user()
    
    au.get_screen_name()
    au.is_core_user()
    au.get_user_status()
    au.assign_date()
    
    au.is_user_added()
    
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
    
    st.write('---')
    st.write('## Make Users')
    st.write('All the users added manually today sofar will be made or finalized.')
    st.write('To make them press the button below.')
    au.make_added_users()
    
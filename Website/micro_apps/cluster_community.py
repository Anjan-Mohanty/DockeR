import streamlit as st
from Objects import website_objects as web

def micro_app():
    
    st.title('Cluster Community')
    st.write('This is the place you can cluster your community ð')
    st.write('Here we do Machine Learning ððĪŠðĪ')
    st.write('---')
    
    cc=web.cluster_community()
    
    cc.do_clustering()
    
    cc.show_report()
    
    cc.show_clusters()
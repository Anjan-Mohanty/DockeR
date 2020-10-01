import streamlit as st

class app(object):
    
    def __init__(self):
        
        self.micro_apps=[]
    
    def add_micro_app(self,title,function):
        
        micro_app={'title':title,'function':function}
        self.micro_apps.append(micro_app)
    
    def run(self):
        
        micro_app=st.sidebar.radio('Go To',self.micro_apps,format_func=lambda micro_app: micro_app['title'])
        micro_app['function']()
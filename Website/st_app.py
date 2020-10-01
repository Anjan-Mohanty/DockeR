import streamlit as st
import website as wb
from micro_apps import home,auth,add_user

def main():
    
    website=wb.app()
    
    website.add_micro_app('Home',home.micro_app)
    website.add_micro_app('Twitter API Auth-Keys',auth.micro_app)
    website.add_micro_app('Add User',add_user.micro_app)
    
    website.run()
                
if __name__=='__main__':
    main()
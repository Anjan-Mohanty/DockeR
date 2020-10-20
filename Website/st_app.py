import streamlit as st
import website as wb
from micro_apps import home,auth,add_user,data_collector,discover_users,preprocessing,cluster_community

def main():
    
    website=wb.app()
    
    website.add_micro_app('Home',home.micro_app)
    website.add_micro_app('Data Collector',data_collector.micro_app)
    website.add_micro_app('Twitter API Auth-Keys',auth.micro_app)
    website.add_micro_app('Add User',add_user.micro_app)
    website.add_micro_app('Discover Users',discover_users.micro_app)
    website.add_micro_app('Pre Processing',preprocessing.micro_app)
    website.add_micro_app('Cluster Community',cluster_community.micro_app)
    
    website.run()
                
if __name__=='__main__':
    main()
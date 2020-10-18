import streamlit as st
import time
import pandas as pd
import pymongo

#connecting to dB
client=pymongo.MongoClient()
db=client.twitter

def main():
    
    st.title('Hello World')
    st.write('---')
    
    #did_now=False
    if(st.button('Get Data')):
        #did_now=True
        with st.spinner('Discovering..'):
            time.sleep(10)
        st.success('Done!')
    

    done=st.multiselect('Users',[i['name'] for i in db.emp.find({})])
    
    
    try:
        user=done[-1]
        url=f'[{user}](https://twitter.com/{user})'
        st.write('@'+url+' is the selected user, Please fill the details below')
        
        options=[None,'Discover','Mute','Block']
        label='What action do you wan to take on @'+user
        action=st.radio(label,options,index=0)
        
        options=[None,'Yes','No']
        label='Do you want @'+user+' to be Core user ?'
        core_user=st.radio(label,options,index=0)
        
        if st.button('Done'):
            
            if((action==None) or (core_user==None)):
                st.write('Enter above details properly')
                st.stop()
            else:
                
                with st.spinner('Working'):
                    time.sleep(1)
                    
                    db.emp.update({'name':user},{'$set':{'action':action,'core_user':core_user}})
                    
                    member=[]
                    for i in db.emp.find({'name':user}):
                        member.append(i)
                    
                    label=member[0]['name']+', '+member[0]['action']+', '+member[0]['core_user']
                    st.success(label)
        
        if st.button('Show preview'):
            member=[]
            for i in db.emp.find({}):
                member.append(i)
            df=pd.DataFrame(member,columns=['name','action','core_user'])
            st.dataframe(df)
                
        
    except IndexError:
        st.write('start selecting users if u have pressed above button')











if __name__=='__main__':
    main()
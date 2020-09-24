import streamlit as st

def main():
    #starting head of the front end
    st.title('Discover Weekly Twitter')
    st.write('''
             ---
             
             **Quickly** get **insights** of your **Twitter Community!**
             
             To *add services* as you need, go to [Discover Weekly Twitter](https://github.com/sameerpixelbot/discover_weekly_twitter_deployed)
             
             Now go ahed and discover new opinions in your Twitter Community
             
             ---
             ''')
    
    if(st.button('Data Collection')):
        st.write('''
                This feature is on its way 😅🤓
                ''')
                
    if(st.button('User Management')):
        st.write('''
                This might take even more time
                Sorry..😭😢
                ''')
                
    if(st.button('Get Insights')):
        st.write('''
                ..It\n
                will\n
                take\n
                more\n
                time..\n
                
                **..Dont go away 😬**\n
                **Please 😶..**
                ''')
                
if __name__=='__main__':
    main()
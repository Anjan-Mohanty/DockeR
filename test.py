from flask import Flask
import time

app=Flask(__name__)


@app.route('/')
def index():
    
    return('-_-'+" '_'"+" ^<>^")


if __name__=='__main__':
    app.run(debug=True)
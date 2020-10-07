from app import app
from flask import Flask

import time

@app.route('/')
def index():
    
    return(time.localtime())


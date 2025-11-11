from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "le bot perco vae est en ligne !"

def run():
  app.run(host='0.0.0.0', port=8180)
  
def keep_alive():
 t = Thread(target=run)
 t.start()

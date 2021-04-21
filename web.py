from flask import Flask,render_template
from threading import Thread
from os import path
from tickets_variables import bot_name,discord_embed

app = Flask('')


@app.route('/')
def home():
    return render_template('home.html',name=bot_name,discord_embed=discord_embed)

@app.route("/transcripts/<channel>")
def transcripts(channel):
  print(channel)
  if path.exists(f"templates/{channel}"):
    return render_template(channel)
  else:
    return render_template('not_found.html',name=bot_name,discord_embed=discord_embed)

@app.route("/arc-sw.js")
def arc():
   return render_template('arc-sw.js',mimetype="application/javascript")



def run():
    app.run(host='0.0.0.0', port=8080,debug=False)

def start():
    t = Thread(target=run)
    t.start()



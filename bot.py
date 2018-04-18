# -*- coding: utf-8 -*-
import sys
import time
import telepot
import telepot.namedtuple
from telepot.loop import MessageLoop

from datetime import datetime
import codecs
import os
import urllib2


def log(msg):
    with codecs.open(os.path.join(os.path.dirname(__file__), 'log.log'), "a", "utf-8") as f:
        f.write(msg+'\n')

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    global counter
    
    # group message
    if chat_id < 0:
        log('Received a %s from %s, by %s' % (content_type, m.chat, m.from_))
    
    # private message
    else:
        log("Received %s from %s at %s" %(msg['text'], msg['from']['username'], datetime.fromtimestamp(msg['date']).strftime("%Y-%m-%d %H:%M:%S")))
    
    #Mensajes
    if content_type == 'text':
        reply = ''
        command = msg['text'].strip().lower()
        
        #Commands
        if command[0] == "/":
            command=command[1:]
            
            if command == "ip":
                reply=urllib2.urlopen('http://ipinfo.io/ip').read()
            elif command == "newest":
                date=newest("/var/www/html/other/twitter").split("/")[-1].split("(")[0].lstrip("tweets_").replace("_"," ").strip()
                diff=datetime.now()-datetime.strptime(date, "%Y-%m-%d %H:%M")
                if diff.days==0:
                    reply="Hace %d horas" %(diff.seconds/3600)
                elif diff.days==1:
                    reply="Hace un día y %d horas" %(diff.seconds/3600)
                else:
                    reply="Hace %d días y %d horas" %(diff.days, diff.seconds/3600)
                    reply+="\n"+date
                    
            else:
                reply="Comando desconocido"
        else:
            reply="Nah, de momento no sé hablar contigo"
        
        bot.sendMessage(chat_id, reply)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
log('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)

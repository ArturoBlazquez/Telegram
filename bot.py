# -*- coding: utf-8 -*-
import sys
import time
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, per_callback_query_origin, create_open, pave_event_space

from datetime import datetime
import codecs
import os
import urllib2
import random
from getConfigs import getConfigs


def log(msg):
    with codecs.open(os.path.join(os.path.dirname(__file__), 'log.log'), "a", "utf-8") as f:
        f.write(msg+'\n')
        

def msgGlance(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type=='text':
            date=datetime.fromtimestamp(msg['date']).strftime("%Y-%m-%d %H:%M:%S")
            name=msg["from"]["first_name"]
            name_id=msg["from"]["id"]
            text=msg["text"]
        else:
            date,name,name_id,text=["no","no","no","no"]
        return [content_type, chat_id, date, name, name_id, text]

def isUrl(msg):
    if msg.find("http://")>=0 or msg.find("https://")>=0:
        return True
    else:
        return False

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

def getNewest():
    date=newest("/var/www/html/other/twitter").split("/")[-1].split("(")[0].lstrip("tweets_").replace("_"," ").strip()
    diff=datetime.now()-datetime.strptime(date, "%Y-%m-%d %H:%M")
    if diff.days==0:
        return "Hace %d horas" %(diff.seconds/3600)
    elif diff.days==1:
        return "Hace un día y %d horas" %(diff.seconds/3600)
    else:
        return "Hace %d días y %d horas\n%s" %(diff.days, diff.seconds/3600, date)

def getTumblrVideo(command, chat_id):
    global bot

    html=urllib2.urlopen(command).read()
    position=html.find("_frame1")
    if position<0:
        position=html.find("_smart1")

    if position>0:
        id=html[position-17:position]

        video="https://vt.media.tumblr.com/tumblr_"+id+"_480.mp4"
        
        try:
            urllib2.urlopen(video)
            with open(id+".mp4",'wb') as f:
                f.write(urllib2.urlopen(video).read())
            with open(id+".mp4",'r') as f:
                bot.sendVideo(chat_id, f)
            os.remove(id+".mp4")
            return ''
        except:
            return "Video bloqueado"
    else:
        return "No se ha encontrado :("


class MessageHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        content_type, chat_id, date, name, name_id, text = msgGlance(msg)
        
        if content_type == 'text':
            # group message
            if chat_id < 0:
                reply=''
                log("[%s] Received \"%s\" from %s(%s) at group %s" % (date, text, name, name_id, chat_id))
            # private message
            else:
                reply=''
                log("[%s] Received \"%s\" from %s(%s)" %(date, text, name, name_id))
            
            reply = ''
            keyboard = ''
            command = msg['text'].strip().lower()
            
            #Commands
            if command[0] == "/":
                command=command[1:]
                
                if command == "ip":
                    reply=urllib2.urlopen('http://ipinfo.io/ip').read()
                elif command == "newest":
                    reply=getNewest()
                elif command == "mariokart":
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Copa', callback_data='copa')],
                        [InlineKeyboardButton(text='Mapas', callback_data='mapas')]
                    ])
                elif command == "start":
                    reply="Hola 😊"
                elif command == "help":
                    reply="Simplemente habla conmigo y te iré contestando.\nSi escribes \"\\\" te saldrá la lista de comandos posibles"
                else:
                    reply="Comando desconocido"
            #Messages
            else:
                if isUrl(command):
                    reply=getTumblrVideo(command, chat_id)
                else:
                    reply="Nah, de momento no sé hablar contigo"
            
            if reply!="":
                bot.sendMessage(chat_id, reply)
            elif keyboard!="":
                bot.sendMessage(chat_id, "Elige una opción", reply_markup=keyboard)


class QueryHandler(telepot.helper.CallbackQueryOriginHandler):
    def __init__(self, *args, **kwargs):
        super(QueryHandler, self).__init__(*args, **kwargs)
    
    def on_callback_query(self, msg):
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        log("Callback Query: \"%s\" from %s(%s)" %(query_data, chat_id, query_id))
        
        reply = ''
        
        if query_data == "copa":
            reply = str(random.randint(1,8))
        elif query_data == "mapas":
            maps = [str(i)+'-'+str(j) for i in range(1,9) for j in range(1,5)]
            chosen = random.sample(maps, 4)
            reply = '\n'.join(chosen)
        
        if reply!="":
            self._editor.editMessageText(reply, reply_markup=None)





TOKEN = getConfigs()

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageHandler, timeout=10),
    pave_event_space()(
        per_callback_query_origin(), create_open, QueryHandler, timeout=10),
])
MessageLoop(bot).run_as_thread()
log('Listening '+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

while 1:
    time.sleep(10)

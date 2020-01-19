# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from humanfriendly import format_timespan, format_size, format_number, format_length
from argparse import ArgumentParser
from flask import Flask, request
import errno, os, sys, tempfile, json, requests, random, time, telegram, logging
from telegram.error import NetworkError, Unauthorized
from time import sleep

TOKEN = "1022420760:AAHN2E-GAebyMjixGg9kaOoi-9JXwhjAjVI"
URL = "https://family-100-telegram.herokuapp.com/"
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

tebak = {
    "games": {},
    "room":{},
    "score": {}
}

with open("quest.txt", "r") as file:
     blist = file.readlines()
     quest = [x.strip() for x in blist]
file.close()
			
def gamesJoin(msg_id):
	tebak['games'][msg_id]={'point':{}}
	tebak['games'][msg_id]['saklar']=False
	tebak['games'][msg_id]['quest']=''
	tebak['games'][msg_id]['asw']=[]
	tebak['games'][msg_id]['tmp']=[]
	
def getQuest(msg_id):
	tebak['games'][msg_id]['quest'] = ''
	tebak['games'][msg_id]['asw'] = []
	tebak['games'][msg_id]['tmp'] = []
	a = random.choice(quest)
	a = a.split('*')
	tebak['games'][msg_id]['quest'] = a[0]
	for i in range(len(a)):
		tebak['games'][msg_id]['asw'] += [a[i]]
	tebak['games'][msg_id]['asw'].remove(a[0])
	for j in range(len(tebak['games'][msg_id]['asw'])):
		tebak['games'][msg_id]['tmp'] += [str(j+1)+'. _________']
		
def bots(users, chatid, msgid, texts):
	user = users
	chat_id = chatid
	msg_id = msgid
	text = texts
	if msg_id in tebak['games']:
		if tebak['games'][msg_id]['saklar'] == True:
			for i in range(len(tebak['games'][msg_id]['asw'])):
				if text == tebak['games'][msg_id]['asw'][i].lower() and tebak['games'][msg_id]['saklar'] == True:
					wnr = user.first_name
					if wnr in tebak['games'][msg_id]['point']:
						tebak['games'][msg_id]['point'][wnr] += 1
					else:
						tebak['games'][msg_id]['point'][wnr] = 1
					if tebak['games'][msg_id]['point'][wnr] == 20:
						gamesJoin(msg_id)
						return 'Game telah selesai. Selamat buat '+wnr+', kamu pemenangnya.'
					else:
						if i != len(tebak['games'][msg_id]['asw']):
							tebak['games'][msg_id]['tmp'][i] = str(i+1)+'. '+tebak['games'][msg_id]['asw'][i]+' (1)'+' ['+wnr+']'
							tebak['games'][msg_id]['asw'][i] = tebak['games'][msg_id]['asw'][i]+' (*)'
						else:
							tebak['games'][msg_id]['tmp'].remove(str(tebak['games'][msg_id]['tmp'][i]))
							tebak['games'][msg_id]['tmp'].append(str(i+1)+'. '+tebak['games'][msg_id]['asw'][i]+' (1)'+' ['+wnr+']')
							tebak['games'][msg_id]['asw'].remove(str(tebak['games'][msg_id]['asw'][i]))
							tebak['games'][msg_id]['tmp'].append(tebak['games'][msg_id]['asw'][i]+' (*)')
					rsl,rnk = '',''
					for j in tebak['games'][msg_id]['tmp']:
						rsl += j+'\n'
					for k in tebak['games'][msg_id]['point']:
						rnk += '\n• '+k+' : '+str(tebak['games'][msg_id]['point'][k])
					if '_________' in str(tebak['games'][msg_id]['tmp']):
						isi = str(tebak['games'][msg_id]['quest'])+'\n'+rsl
						return isi
					else:
						if tebak['games'][msg_id]['saklar'] == True:
							tebak['games'][msg_id]['saklar'] = False
							isi = str(tebak['games'][msg_id]['quest'])+'\n'+rsl
							return isi + '\nPapan Poin :'+rnk
	else:
		return gamesJoin(msg_id)
	if text.lower() == "help":
		return 'Halo, ayo kita main family 100.\nKamu bisa add bot ini ke group chat kamu.\n\n/help : membuka pesan bantuan\n/mulai : mulai game\n/nyerah : menyerah dari game\n/next : Berpindah kesoal berikutnya\n/resetklasemen : hapus klasemen saat ini\n/lihatklasemen : lihat klasemen saat ini\n/aturan : aturan bermain\n/resetpaksa : reset bot nya, lakukan ini kalau kamu panik :(\n/keluar : suruh bot keluar'
	elif text.lower() == "/mulai":
		if tebak['games'][msg_id]['saklar'] == False:
			tebak['games'][msg_id]['saklar'] = True
			getQuest(msg_id)
			aa = ''
			for aswr in tebak['games'][msg_id]['tmp']:
				aa += aswr+'\n'
				q = tebak['games'][msg_id]['quest']+'\n'+aa
			return q
		else:
			aa = ''
			for aswr in tebak['games'][msg_id]['tmp']:
				aa += aswr+'\n'
			q = tebak['games'][msg_id]['quest']+'\n'+aa
			return 'Game sudah dimulai.\n\n' + q
	else: pass

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    user = update.message.from_user
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    text = update.message.text.encode('utf-8').decode()
    response = bots(user, chat_id, msg_id, text)
    if response == "null" or response == "" or response == None:
    	pass
    else:
    	update.message.reply_text(response)
    	return "ok"
    		
@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
	s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
	if s:
		return "webhook setup ok"
	else:
		return "webhook setup failed"

@app.route('/')
def index():
    return 'Family 100 Telegram Bot'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)

#!/usr/bin/env python

'''crontab run 
0 8 * * mon ~/WhiteBoxBot/whitebot.py >> ~/WhiteBoxBot/wb.log
'''
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib
import argparse
import os

from config import *

# Functions
def fileindex(len):
	if os.path.isfile('index.txt') == 0:
		print 'new index file'
		n = open('index.txt', 'a')
		n.write(str(0))
		n.close()
	f = open('index.txt', 'r+')
	index = int(f.read())
	if index == (len):
		val = 0
	else:
		val = index + 1 		
	f.seek(0)
	f.write(str(val))
	f.truncate()
	f.close()
	return index

parser = argparse.ArgumentParser()
parser.add_argument("-e", help="Email, enabled",action="store_true")
parser.add_argument("-v", help="Verbose, debug print enabled",action="store_true")
parser.add_argument("-c", help="Cronjob, change directory",action="store_true")		
args = parser.parse_args()

if args.c:
	os.chdir('/home/pi/WhiteBoxBot')

ncslist = ("KE7KMK","KE7KML","KE7KMM","KE7KMN","KE7KMO","PIMC")
ncsmax = len(ncslist) - 1
msg = MIMEMultipart()
if args.e:
	msg["To"] = '''Ed & Clare Kelm <twopilots@interisland.net>, 
		Basil Gunn <basil@pacabunga.com>, Jim McCorison <jimmcc@mccorison.com>, 
		Wayne Rankin <wa6mpg@yahoo.com>, Jim Hooper <jkhooper@rockisland.com>, 
		Dave Vandaveer <dave@rockisland.com>, Dan Drath <drathmarine@rockisland.com>'''
else:
	msg["To"] = "bhhoyer@gmail.com"
	print 'To List Disabled'
msg["From"] = "SJACS EC"
msg["Cc"] = "bhhoyer@icloud.com"
body = MIMEText('''Good Morning OMs

TEST ONLY White Box Drill Tomorrow

Net Control will post the POD (Plan Of the Day) on 2m JNBBS (and 220 if available)

Please be on Station with the POD in hand by 9:30am,
White Box Bot
''')
msg.attach(body)

#Is tomorrow the second or fourth?
tue = (datetime.date.today() + datetime.timedelta(days=1))
wbd =tue.day

if ((7 < wbd < 15) or (21 < wbd < 29)):
	msg["Subject"] = "White Box Drill Tomorrow NCS " + ncslist[fileindex(ncsmax)]
	smtp = smtplib.SMTP('smtp.gmail.com', 587)
	smtp.starttls()
	smtp.login(username,password)
	smtp.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
	smtp.quit()
	print msg["Subject"]
else:
	print 'not this time'
		
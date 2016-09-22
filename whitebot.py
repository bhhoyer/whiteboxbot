#!/usr/bin/env python

'''crontab runs 8am every Monday. If tomorrow is the second or fourth Tuesday 
send email with NCS and increment index.txt
1 8 * * mon /home/pi/WhiteBoxBot/whitebot.py >> /home/pi/WhiteBoxBot/wb.log 2>&1
'''
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib
import argparse
import os
from config import *

#creates index.txt if it doesn't exist then increments with rollover at limit
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

msg = MIMEMultipart()
if args.e:
	msg["To"] = tolist
else:
	msg["To"] = me
	print 'To List Disabled'
msg["From"] = "SJACS EC"
msg["Cc"] = me
body = MIMEText(body)
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
		
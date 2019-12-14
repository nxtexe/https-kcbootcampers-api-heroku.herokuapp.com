from common.database import Database
import uuid
from flask import session, make_response, redirect, url_for
from .user import User
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime

accepted = {"1and1.com": "smtp.1and1.com: 25",
					"airmail.net": "mail.airmail.net: 25",
					"aol.com": "smtp.aol.com: 25",
					"att.net": "outbound.att.net: 25",
					"bluewin.ch": "smtpauths.bluewin.ch: 25",
					"btconnect.com": "mail.btconnect.tom: 25",
					"comcast.net": "smtp.comcast.net: 25",
					"earthlink.net": "smtpauth.earthlink.net: 25",
					"gmail.com": "smtp.gmail.com: 587",
					"gmx.net": "mail.gmx.net: 25",
					"hotpop.com": "mail.hotpop.com: 25",
					"libero.it": "mail.libero.it: 25",
					"lycos.com": "smtp.lycos.com: 25",
					"o2.com": "smtp.o2.com: 25",
					"orange.net": "smtp.orange.net: 25",
					"outlook.com": "smtp.live.com: 25",
					"tin.it": "mail.tin.it: 25",
					"tiscali.co.uk": "smtp.tiscali.co.uk: 25",
					"verizon.net": "outgoing.verizon.net: 25",
					"virgin.net": "smtp.virgin.net: 25",
					"wanadoo.fr": "smtp.wanadoo.fr: 25",
					"yahoo.com": "mail.yahoo.com: 25"}

def send(email):
	template = open('models/forgot_password.tpl').read()
	endpoint = email.split('@')[1]
	for keys in accepted:
		if endpoint == keys:
			smtp_server = accepted[endpoint]
			break
		else:
			continue

	uri = uuid.uuid4().hex
	user = User.get_by_email(email)
	User.temp_password(email, uri)
	user.deactivate()
	link = ("https://kcbootcampers-api-heroku.herokuapp.com/change_password/auth/" + uri)
	rectify_link = ("https://kcbootcampers-api-heroku.herokuapp.com/change_password/auth/" + uri + "/rectify")
	resp = make_response(redirect(url_for('user_logout')))
	resp.set_cookie('email', email, expires=datetime.datetime.now() + datetime.timedelta(days=1))
	msg = MIMEMultipart()
	message = template.replace('<name>', email).replace('<link>', link).replace('<link2>', rectify_link)

	#setup the parameters of the message
	password = "passwords123"
	msg['From'] = "kc.bootcampers@gmail.com"
	msg['To'] = email
	msg['Subject'] = "Change Password"

	#add in the message body
	msg.attach(MIMEText(message, 'plain'))

	#create server
	server = smtplib.SMTP(smtp_server)

	server.starttls()

	#Login Credentials for sending the mail
	server.login(msg['From'], password)

	server.sendmail(msg['From'], msg['To'], msg.as_string())

	server.quit()

	session['email'] = None
	return resp
import mysql.connector
import requests
import smtplib, os, sys
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from html.parser import HTMLParser

class User:
  def __init__(self, uid, name, username, age, aadhar, serviceProvider, phoneNumber, profession, domain,  apartment, locality, pincode):
    self.Uid = uid
    self.Name = name
    self.Username = username
    self.Age = age
    self.Aadhar = aadhar
    self.ServiceProvider = serviceProvider
    self.PhoneNumber = phoneNumber
    self.Profession = profession
    self.Domain = domain
    self.Apartment = apartment
    self.Locality = locality
    self.Pincode = pincode
  def __str__(self):
  	return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(self.Uid, self.Name, self.Username, self.Age, self.Aadhar, self.ServiceProvider, self.PhoneNumber, self.Profession, self.Domain, self.Apartment, self.Locality, self.Pincode)

def setupdb():
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",				#select the user
		passwd="He@12345")					#Provide the password for your root user or some other user in which you have created the database
	return mydb

def getPhoneNumbers(uid):	
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT phoneNumber from phonenumber where uid = '{}'".format(uid)
	mycursor.execute(query)
	numbers = mycursor.fetchall()
	if(len(numbers)!=0):
		return numbers[0][0]
	else:
		return "Not Available"

def getAverageRating(uid):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT avg(rating) from ratingsandreviews where uidSP='{}'".format(uid)
	mycursor.execute(query)
	rating = mycursor.fetchall()
	if(rating[0][0] and rating[0][0]>=0):
		return round(rating[0][0],2)
	else:
		return -1

def getUserObject(uid):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")

	query = "SELECT * from user where uid = '{}'".format(uid)
	mycursor.execute(query)
	userrecord = mycursor.fetchall()
	averagerating = getAverageRating(uid)
	if(averagerating != 'Not Rated'):
		averagerating = int(averagerating)
	phone = getPhoneNumbers(uid)
	query = "SELECT * from address where uid = '{}'".format(uid)
	mycursor.execute(query)
	address = mycursor.fetchall()
	if(len(address)==0):
		lid = None
		apartment = None
	else:
		lid = address[0][2]
		apartment = address[0][1]

	if(lid):
		query = "SELECT locality, pin from location where lid = '{}'".format(lid)
		mycursor.execute(query)
		location = mycursor.fetchall()
		locality = location[0][0]
		pincode = location[0][1]
	else:
		locality = None
		pincode = None

	pid = userrecord[0][6]
	query = "SELECT profession, domain from professioncategory where pid = '{}'".format(pid)
	mycursor.execute(query)
	service = mycursor.fetchall()
	profession = service[0][0]
	domain = service[0][1]

	user = User(uid, userrecord[0][3], userrecord[0][1], userrecord[0][4], userrecord[0][5], userrecord[0][7], phone, profession, domain, apartment, locality, pincode)
	#print("yes",user)
	return user.__dict__
#[(1, 'Abbezolt', 'fBjAn', 'Sushant Kata', 18, 785139000000, 1, 'Yes', 1)]
#[(103, 'myjhonson', 'lol123', 'jhonson', 22, 489293018492, 'No', 1, None, '0')]
#name, username, age, aadhar, serviceProvider, phoneNumber, profession, domain,  apartment, locality, pincode, rating

"""
def isLocated(uid, locality):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT lid from location where locality = '{}'".format(locality)
	mycursor.execute(query)
	lids = mycursor.fetchall()
	lidlist = []
	string = ""	
	for i in lids:
		lidlist.append(i[0])
		string=string+str(i[0])+","
	lidtuple = tuple(lidlist)
	string = string[:-1]
	query = "SELECT * from address where uid = %s and lid in (%s)" %(uid,string)
	mycursor.execute(query)
	loc = mycursor.fetchall()
	if(len(loc)>0):
		print("select")
		return 1
	else:
		return 0
"""

def submitComplaint(uidss, uidsp, complaint):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT eid from employee WHERE availability = 'Available'"
	mycursor.execute(query)
	avaleids = mycursor.fetchall()
	if(avaleids):
		eid = avaleids[0][0]
	else:
		eid = 1
	query = "UPDATE employee set availability = 'Not Available' WHERE eid = {}".format(eid)
	mycursor.execute(query)

	query = "INSERT INTO complaints(uidSS, uidSP, complaint, eid) values(%s,%s,%s,%s)"
	values = (uidss, uidsp, complaint, eid)
	mycursor.execute(query, values)
	mydb.commit()
	print("reported")


def getserviceproviders(profession = None, locality = None, pincode = None, rating = None, sorting = None):
	print(profession)
	print(locality)
	print(pincode)
	print(sorting)
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	serviceproviders = []
	query = "SELECT uid from user where serviceProvider = 'yes'"
	mycursor.execute(query)
	spuids = mycursor.fetchall()
	print(spuids)
	for i in range(len(spuids)):
		spobject = getUserObject(spuids[i][0])
		sprating = getAverageRating(spuids[i][0])
		spobject['Rating'] = sprating
		serviceproviders.append(spobject)
	#print(serviceproviders)
	print(len(serviceproviders))
	rmvind = []
	if(profession):
		print("yo")
		for i in range(len(serviceproviders)):
			print(serviceproviders[i]['Profession'], end = ':')
			if(serviceproviders[i]['Profession'] != profession and serviceproviders[i]['Domain'] != profession):
				print("yes")
				rmvind.append(serviceproviders[i]['Uid'])

	if(locality):
		print("ok")
		for i in range(len(serviceproviders)):
			if(serviceproviders[i]['Locality']!=locality):
				rmvind.append(serviceproviders[i]['Uid'])

	if(pincode):
		print("no")
		for i in range(len(serviceproviders)):
			print(serviceproviders[i]['Pincode'])
			if(serviceproviders[i]['Pincode'] != int(pincode)):
				rmvind.append(serviceproviders[i]['Uid'])
	print(rmvind)
	if(rating):
		print("filetes = ", rating)
		for i in range(len(serviceproviders)):
			#print(serviceproviders[i]['Rating'])
			if(serviceproviders[i]['Rating'] == -1 or int(serviceproviders[i]['Rating']) < int(rating)):
				rmvind.append(serviceproviders[i]['Uid'])

	
	print(rmvind)
	finalsplist = []
	for i in serviceproviders:
		if(i['Uid'] not in rmvind):
			finalsplist.append(i)

	#print("fp:",finalsplist)
	print(len(finalsplist))
	if(sorting):
		if(sorting == 'Rating'):
			finalsplist.sort(reverse=True,key=lambda x: x['Rating'])
		else:
			finalsplist.sort(key=lambda x: x['Name'])
	return(finalsplist)


	"""
	if(profession == None and locality == None and pincode == None):
		query = "SELECT name,  from user where username = '{}'".format(username)
	elif(profession == None and locality == None and pincode != None):
		1
	elif(profession == None and locality != None and pincode == None):
		2
	elif(profession == None and locality != None and pincode != None):
		3
	elif(profession != None and locality == None and pincode == None):
		4
	elif(profession != None and locality == None and pincode != None):
		5
	elif(profession != None and locality != None and pincode == None):
		6
	elif(profession != None and locality != None and pincode != None):
		7
	{'Uid': 132, 'Name': 'simar jeet', 'Username': 'simmi', 'Age': 32, 'Aadhar': 838748374834, 'ServiceProvider': 'yes', 'PhoneNumber': -1, 'Profession': 'Plumber', 'Domain': 'Domestic Help', 'Apartment': None, 'Locality': None, 'Pincode': None}
	"""

def getName(uid):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT name from user where uid = '{}'".format(uid)
	mycursor.execute(query)
	name = mycursor.fetchall()
	return name[0][0]


def getpid(profession):
	pidlist = {'Cook':1,'Plumber':2,'Electrician':3,'House Cleaner':4,'Carpenter':5,'Painter':6,'Gardener':7,'Driver':8,'Pool Cleaner':9,'Guard':10,'Delivery Person':11,'Vegetable Seller':12,'Baby Sitter':13,'Pet Keeper':14,'Party Decorator':15,'Tutor':16,'Dentist':17,'ENT':18,'Washer':19,'Dry Cleaner':20}
	pid = pidlist[profession]
	return pid

def addSOS(uid, email):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT * from sosemailid WHERE uid = '{}' and emailID = '{}'".format(uid, email)
	mycursor.execute(query)
	exist = mycursor.fetchall()
	if(exist):
		return
	else:
		query = "INSERT INTO sosemailid (uid, emailID) VALUES(%s, %s)"
		values = (uid, email)
		mycursor.execute(query, values)
		mydb.commit()
		print("email added")

def getSOSEmails(uid):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT emailID from sosemailid WHERE uid = '{}'".format(uid)
	mycursor.execute(query)
	email = mycursor.fetchall()
	emailids = []
	for i in email:
		emailids.append(i[0])
	return emailids

def getuid(username):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT uid from user where username = '{}'".format(username)
	mycursor.execute(query)
	uid = mycursor.fetchall()
	return uid[0][0]

def getlid(locality, pincode):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT lid from location where locality = '{}' and pin = '{}'".format(locality, pincode)
	mycursor.execute(query)
	lid = mycursor.fetchall()
	return lid[0][0]

def getRatingsAndReviews(uid):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT * from ratingsandreviews where uidsp = '{}';".format(uid)
	mycursor.execute(query)
	reviews = mycursor.fetchall()
	finalreviewlist = []
	for i in reviews:
		serviceseeker = getName(i[0])
		finalreviewlist.append([serviceseeker, i[2], i[3]])
	if(len(finalreviewlist)==0):
		return None
	else:
		return finalreviewlist

def check_username(username):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query="SELECT * from user where username = '{}'".format(username)
	mycursor.execute(query)
	exist=mycursor.fetchall()
	if(len(exist)==0):
		return True
	else:
		return False

def checkLocalityPin(locality, pincode):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query="SELECT * from location where locality = '{}' and pin = '{}'".format(locality, pincode)
	mycursor.execute(query)
	exist=mycursor.fetchall()
	if(len(exist)==0):
		return False
	else:
		return True


def login(username, password):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query= "SELECT name from USER where username = '{}' and password = '{}'".format(username, password)
	mycursor.execute(query)
	exist=mycursor.fetchall()
	if(len(exist)==0):
		return False
	else:
		return True


def signup(name, username, password, age, aadharNumber, serviceProvider, pid):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query= "INSERT INTO user (username, password, name, age, aadharNumber, serviceProvider, pid) VALUES(%s, %s, %s, %s, %s, %s,%s)"
	values = (username, password, name, age, aadharNumber, serviceProvider, pid)
	mycursor.execute(query, values)
	mydb.commit()
	print("signup success")

def addphonenumber(uid, phone):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "INSERT INTO phonenumber (uid, phonenumber) VALUES(%s, %s)"
	values = (uid, phone)
	mycursor.execute(query, values)
	mydb.commit()

def completeProfile(username, phone, apartment, locality, pincode):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	lid = getlid(locality, pincode)
	uid = getuid(username)
	query = "INSERT INTO address (uid, apartment, lid) VALUES(%s, %s, %s)"
	values = (uid, apartment, lid)
	mycursor.execute(query, values)
	addphonenumber(uid, phone)
	query = "UPDATE user SET completeProfile = 1 WHERE username = '{}'".format(username)
	mycursor.execute(query)
	mydb.commit()
	print("Profile completed!")

def giveReview(uidss, uidsp, rating, review):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT * from ratingsandreviews WHERE uidSS = {} and uidSP = {}".format(uidss, uidsp)
	mycursor.execute(query)
	exist = mycursor.fetchall()
	if(exist):
		return -1
	query = "INSERT INTO ratingsandreviews (uidSS, uidSP, rating, review) VALUES(%s, %s, %s, %s)"
	values = (uidss, uidsp, rating, review)
	mycursor.execute(query, values)
	mydb.commit()
	print("review added")
	return 1


def addFavorite(uidss, uidsp):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "INSERT INTO favourites (uidSS, uidSP) VALUES(%s, %s)"
	values = (uidss, uidsp)
	mycursor.execute(query, values)
	mydb.commit()
	print("favorite added")

def removeFavorite(uidss, uidsp):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "DELETE FROM favourites  WHERE uidSS = {} and uidSP = {}".format(uidss, uidsp)
	mycursor.execute(query)
	mydb.commit()
	print("favorite removed")

def isFavorite(uidss, uidsp):
	mydb = setupdb()
	mycursor = mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT * FROM favourites  WHERE uidSS = {} and uidSP = {}".format(uidss, uidsp)
	mycursor.execute(query)
	check = mycursor.fetchall()
	if(len(check)==0):
		return False
	else:
		return True


def getFavorites(uidss):
	mydb = setupdb()
	mycursor= mydb.cursor()
	mycursor.execute("USE yelopagesyat")
	query = "SELECT * FROM favourites  WHERE uidSS = {}".format(uidss)
	mycursor.execute(query)
	fav = mycursor.fetchall()
	favorites = []
	for i in fav:
		favorites.append(getUserObject(i[1]))

	print(favorites)
	return favorites


def display_ip():
    """  Function To Print GeoIP Latitude & Longitude """
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    print("func",my_ip)
    geo_request = requests.get('https://get.geojs.io/v1/ip/geo/' +my_ip + '.json')
    geo_data = geo_request.json()
    return {'ip':my_ip, 'latitude': geo_data['latitude'], 'longitude': geo_data['longitude']}




def send_email(user_email, userdetails, livelocation):
	# lines to be changed 10, 11, 12, 15, 16
	
	attachments = []
	username = 'yelopagesmail'
	password = 'serviceprovider'
	host = 'smtp.gmail.com:587' 

	fromaddr = 'yelopagesmail@gmail.com' # less secure app allow karna padega
	toaddr  = user_email
	replyto = fromaddr

	msgsubject = "Your Contact on yelopages is asking for HELP!"

	htmlmsgtext = """<h2>Hi,</h2>"""
	htmlmsgtext	= htmlmsgtext+"""<p>Your friend might be in trouble right now please take the appropriate steps to contact and help him/her:<br> """
	htmlmsgtext=htmlmsgtext+"""<br></p><p><strong>Here are some contact and location details of your contact:</strong></p><p>"""+userdetails+"""<br><br>"""+livelocation+"""<br><br><b>TEAM YELOPAGES</b></p>"""

	######### isse ne nechhe ke code se koi matlab nahi hai ############

	class MLStripper(HTMLParser):
	    def __init__(self):
	        self.reset()
	        self.convert_charrefs=True
	        self.fed = []
	    def handle_data(self, d):
	        self.fed.append(d)
	    def get_data(self):
	        return ''.join(self.fed)

	def strip_tags(html):
	    s = MLStripper()
	    s.feed(html)
	    return s.get_data()

	########################################################################

	try:
	    # Make text version from HTML - First convert tags that produce a line break to carriage returns
	    msgtext = htmlmsgtext.replace('</br>',"\r").replace('<br />',"\r").replace('</p>',"\r")
	    # Then strip all the other tags out
	    msgtext = strip_tags(msgtext)

	    # necessary mimey stuff
	    msg = MIMEMultipart()
	    msg.preamble = 'This is a multi-part message in MIME format.\n'
	    msg.epilogue = ''

	    body = MIMEMultipart('alternative')
	    body.attach(MIMEText(msgtext))
	    body.attach(MIMEText(htmlmsgtext, 'html'))
	    msg.attach(body)
	    #print('attachments' in globals())
	    if len(attachments) > 0: # are there attachments?
	        for filename in attachments:
	            f = filename
	            print(f)
	            part = MIMEBase('application', "octet-stream")
	            part.set_payload( open(f,"rb").read() )
	            encoders.encode_base64(part)
	            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
	            msg.attach(part)

	    msg.add_header('From', fromaddr)
	    msg.add_header('To', toaddr)
	    msg.add_header('Subject', msgsubject)
	    msg.add_header('Reply-To', replyto)

	    # The actual email sendy bits
	    server = smtplib.SMTP(host)
	    server.set_debuglevel(False) # set to True for verbose output
	    try:
	        # gmail expect tls
	        server.starttls()
	        server.login(username,password)
	        server.sendmail(msg['From'], [msg['To']], msg.as_string())
	        print('Email sent')
	        server.quit() # bye bye
	    except:
	        # if tls is set for non-tls servers you would have raised an exception, so....
	        server.login(username,password)
	        server.sendmail(msg['From'], [msg['To']], msg.as_string())
	        print('Email sent')
	        server.quit() # sbye bye        
	except:
	    print ('Email NOT sent to %s successfully. %s ERR: %s %s %s ', str(toaddr), 'tete', str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2]) )
	    #just in case
#This email sending script was taken from an open source github repo. 
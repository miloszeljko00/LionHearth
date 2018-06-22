from flask import Flask, render_template, request, url_for, redirect, Response
import sqlite3
import json
from time import gmtime, strftime, sleep

ActiveIP = []
server = Flask(__name__)

user = ""
items=(),
char=""
logs=(),
@server.route('/')
def index():
	if str(request.remote_addr) in ActiveIP:
		print ActiveIP
		return render_template('indexLOGGED.html')
	else:
		return render_template('index.html')
@server.route('/changelogs')
def changelogs():
	if str(request.remote_addr) in ActiveIP:
		return render_template('changelogsLOGGED.html')
	else:
		return render_template('changelogs.html')
@server.route('/download')
def download():
	if str(request.remote_addr) in ActiveIP:
		return render_template('downloadLOGGED.html')
	else:
		return render_template('download.html')
@server.route('/register')
def register():
	try:
		ActiveIP.remove(str(request.remote_addr))
	except:
		pass
	return render_template('register.html')
@server.route('/shop')
def shop():
	if str(request.remote_addr) in ActiveIP:
		global user
		global items
		conn = sqlite3.connect('databases/database')
		c = conn.cursor()
		c.execute("SELECT c.name FROM characters c JOIN users u WHERE c.UserID=u.ID AND u.username=?",(user,))
		characters = c.fetchall()
		c.execute("SELECT coins FROM users WHERE username=?",(user,))
		coins = c.fetchall()
		if any (items):
			return render_template('shop.html',characters = characters, coins = coins,items=items)
		else:
			return render_template('shop.html',characters = characters, coins = coins)
	else:
		return redirect(url_for('register'))
@server.route('/login',methods=['POST'])
def login():
	global user
	if request.method == 'POST':
		user=request.form['username']
		pw=request.form['password']

	conn = sqlite3.connect('databases/database')
	c = conn.cursor()
	c.execute("SELECT * FROM users WHERE username=? AND password=?", (user,pw))
	korisnik = c.fetchall()
	if any(korisnik) :
		ActiveIP.append(str(request.remote_addr))
		return redirect(url_for('index')) #PASWORD TACAN
	else:
		return redirect(url_for('index'))

@server.route("/logout")
def logout():
	try:
		ActiveIP.remove(str(request.remote_addr))
	except:
		pass
	return redirect(url_for('index'))

@server.route('/newAcc',methods=['POST'])
def newAcc():
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
	
		conn = sqlite3.connect('databases/database')
		c = conn.cursor()
		c.execute("SELECT * FROM users WHERE username = ? ",(username,))
		korisnik=c.fetchall()
		if any (korisnik):
			for neko in korisnik:
				print neko
				print "Username taken!"
				conn.close()
				return redirect(url_for('register'))
		else:
			c.execute("SELECT * FROM users WHERE email = ? ",(email,))
			korisnik=c.fetchall()
			if any (korisnik):
				for neko in korisnik:
					print "Email taken!"
					conn.close()
					return redirect(url_for('register'))		
			else:
				c.execute("INSERT INTO users (username,password,email) VALUES(?,?,?)",(username,password,email))
				conn.commit()
				conn.close()
				return redirect(url_for('index')) #ULOGOVAN


@server.route('/category',methods=['POST'])
def category():
	if str(request.remote_addr) in ActiveIP:
		global items
		itemClass = request.form['itemClass']
		klasa = str.split(str(itemClass))
		conn = sqlite3.connect('databases/database')
		c = conn.cursor()
		c.execute("SELECT i.ItemID,i.ItemPrice,i.ItemName,i.ImageLink FROM items i JOIN ItemClasses c ON i.ItemClassID=c.ID JOIN ItemsSubClass s ON i.ItemSubClassID=s.ID WHERE s.SubClassName=? AND c.ClassName=?",(klasa[0],klasa[1]))
		items = c.fetchall()
		return redirect(url_for('shop'))
	else:
		return redirect(url_for('register'))

@server.route('/char',methods=['POST'])
def char():

	global char

	char=request.form['char']
	print char
	return redirect(url_for('shop'))

@server.route('/buy',methods=['POST'])
def buy():
	if str(request.remote_addr) in ActiveIP:
		if not (char==""):
			global logs
			buy = request.form['buy']
			conn = sqlite3.connect('databases/database')
			c = conn.cursor()
			c.execute("SELECT ItemID FROM items WHERE ItemID=?",(buy,))
			itemID=c.fetchone()
			c.execute("SELECT UserID,CharID FROM characters WHERE Name=?",(char,))
			IDs =c.fetchone()
			time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
			logs =(IDs[0],IDs[1],time,itemID[0]) 
			print logs
			c.execute("SELECT coins FROM users WHERE ID=?",(logs[0],))
			balance=c.fetchone()
			c.execute("SELECT ItemPrice FROM items WHERE ItemID=?",(logs[3],))
			price=c.fetchone()
			if (balance[0] > price[0]):
				c.execute("INSERT INTO Purchases (userID,charID,Time,ItemBought) VALUES(?,?,?,?)",(logs[0],logs[1],logs[2],logs[3]))
				conn.commit()
				remaining= balance[0]-price[0]
				c.execute("UPDATE users SET coins=? WHERE ID=?",(remaining,logs[0],))
				conn.commit()
				conn.close()
				return redirect(url_for('shop'))
			else:
				return "Not enough coins!"
		else:
			return "Select a Character!"
	else:
		return redirect(url_for('register'))

@server.route('/account')
def account():
	if str(request.remote_addr) in ActiveIP:
		conn = sqlite3.connect('databases/database')
		c = conn.cursor()
		c.execute("SELECT username,password,email,coins FROM users WHERE username=?",(user,))
		accs=c.fetchall()
		return render_template('account.html',accs=accs)
	else:		
		return redirect(url_for('register'))
@server.route('/characters')
def characters():
	if str(request.remote_addr) in ActiveIP:
		global user
		conn = sqlite3.connect('databases/database')
		c = conn.cursor()
		c.execute("SELECT cl.ClassImage,c.Name,r.Race,cl.Class,s.Spec FROM characters c JOIN Class cl ON (cl.ClassID=c.Class) JOIN Spec s ON (s.SpecID=c.Spec) JOIN Race r ON (r.RaceID=c.Race) JOIN users u ON(c.UserID=u.ID) WHERE u.username=?",(user,))
		characters=c.fetchall()
		return render_template('characters.html',characters=characters)
	else:	
		return redirect(url_for('register'))

@server.route('/logs')
def logs():
	if str(request.remote_addr) in ActiveIP:
		global user
		conn = sqlite3.connect('databases/database')
		c = conn.cursor()
		c.execute("SELECT c.Name,p.Time,i.ImageLink,i.ItemName,i.ItemPrice FROM Purchases p JOIN characters c ON (p.charID=c.CharID) JOIN items i ON(i.ItemID=P.ItemBought) JOIN users u ON (p.userID=u.ID) WHERE u.username=?",(user,))
		logs=c.fetchall()
		return render_template('Logs.html',logs=logs)
	else:
		return redirect(url_for('register'))

@server.route('/edit',methods=['POST'])
def edit():
	global user
	username = request.form['username']
	password = request.form['password']
	email = request.form['email']
	conn = sqlite3.connect('databases/database')
	c = conn.cursor()
	c.execute("SELECT username,password,email FROM users WHERE username=?",(user,))
	acc = c.fetchone()
	c.execute("SELECT username FROM users WHERE username=?",(username,))
	uname = c.fetchall()
	ime=""
	for uname1 in uname:
		ime = uname1[0]

	if any(uname):
		return "Username taken!"
	elif (ime==user):
		c.execute("SELECT password,email,ID FROM users WHERE username=?",(user,))
		edit=c.fetchone()
		c.execute("UPDATE users SET username=?,password=?,email=? WHERE ID=?",(username,password,edit[1],edit[2]))
		conn.commit()
		conn.close()
		return redirect(url_for('account'))

	else:
		c.execute("SELECT password,email,ID FROM users WHERE username=?",(user,))
		edit=c.fetchone()
		c.execute("UPDATE users SET username=?,password=?,email=? WHERE ID=?",(username,password,edit[1],edit[2]))
		conn.commit()
		conn.close()
		return redirect(url_for('account'))

if __name__ == '__main__':
	server.run(debug=True, host='0.0.0.0',port=2500)

from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from urllib.parse import quote
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work
from bson.errors import InvalidId # For catching InvalidId exception for ObjectId
import os
import time
import json

mongodb_host = os.environ.get('MONGO_HOST', 'mongodb')  # Use service name instead of localhost
# mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
# client = MongoClient(mongodb_host, mongodb_port)    #Configure the connection to the database
# db = client.camp2016    #Select the database
# todos = db.todo #Select the collection

for _ in range(5):  # Retry up to 5 times
    try:
        client = MongoClient(mongodb_host, mongodb_port, serverSelectionTimeoutMS=2000)
        db = client.camp2016
        db.command("ping")  # Check if MongoDB is ready
        print("Connected to MongoDB!")
        break
    except Exception as e:
        print(f"Waiting for MongoDB... {e}")
        time.sleep(3)
else:
    print("Failed to connect to MongoDB after 5 retries. Exiting.")
    exit(1)

todos = db.todo

app = Flask(__name__)
title = "TODO with Flask"
heading = "ToDo Reminder"
#modify=ObjectId()

@app.route('/health')
def health_check():
    return json.dumps({"status": "healthy"}), 200  # Liveness probe

@app.route('/ready')
def readiness_check():
    return json.dumps({"status": "ready"}), 200  # Readiness probe

def redirect_url():
	return request.args.get('next') or \
		request.referrer or \
		url_for('index')

@app.route("/list")
def lists ():
	#Display the all Tasks
	todos_l = todos.find()
	a1="active"
	return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)

@app.route("/")
@app.route("/uncompleted")
def tasks ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	a3="active"
	return render_template('index.html',a3=a3,todos=todos_l,t=title,h=heading)

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	# Re-directed URL i.e. PREVIOUS URL from where it came into this one
	return redirect(redir)
#	if(str(redir)=="http://localhost:5000/search"):
#		redir+="?key="+id+"&refer="+refer

	# return redirect(redir)

#@app.route("/add")
#def add():
#	return render_template('add.html',h=heading,t=title)

@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	todos.insert_one({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.delete_one({"_id":ObjectId(key)})
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update_one({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(refer=="id"):
		try:
			todos_l = todos.find({refer:ObjectId(key)})
			if not todos_l:
				return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="No such ObjectId is present")
		except InvalidId as err:
			pass
			return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="Invalid ObjectId format given")
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

@app.route("/about")
def about():
	return render_template('credits.html',t=title,h=heading)

@app.route("/health")
def health():
    try:
        db.command('ping')
        return "MongoDB connection successful!", 200
    except Exception as e:
        return f"MongoDB connection failed: {str(e)}", 500


if __name__ == "__main__":
	env = os.environ.get('FLASK_ENV', 'development')
	port = int(os.environ.get('PORT', 5000))
	debug = False if env == 'production' else True
	# app.run(debug=True)
	app.run(host="0.0.0.0", port=port, debug=debug)
	# app.run(host="0.0.0.0", port=5000)
	# Careful with the debug mode..
from models import Base, User, Bagel
from flask import Flask, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth() 

engine = create_engine('sqlite:///bagelShop.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

#ADD @auth.verify_password here
@auth.verify_password
def verify_password(username, password):
    try:
        user = session.query(User).filter_by(username=username).one()
        if user.verify_password(password):
            g.user = user
            print user.username
            return True
        else:
            return False
    except:
        print "User %s does not exist" % username
        return False
        #abort(400) #, {'Location': url_for('newUser')}

#ADD a /users route here
@app.route('/users', methods=['GET','POST'])
def newUser():
    if request.method=='GET':
        users = session.query(User).all()
        return jsonify(usernames = [user.serialize for user in users])
    elif request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            print "missing arguments"
            abort(400) 
        if session.query(User).filter_by(username = username).first() is not None:
            print "existing user"
            user = session.query(User).filter_by(username=username).first()
            return jsonify({'message':'user already exists'}), 200    
        user = User(username = username)
        user.hash_passwd(password)
        session.add(user)
        session.commit()
        return jsonify({'username' : user.username}), 201


@app.route('/bagels', methods = ['GET','POST'])
@auth.login_required
#protect this route with a required login
def showAllBagels():
    if request.method == 'GET':
        bagels = session.query(Bagel).all()
        return jsonify(bagels = [bagel.serialize for bagel in bagels])
    elif request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        picture = request.json.get('picture')
        price = request.json.get('price')
        newBagel = Bagel(name = name, description = description, picture = picture, price = price)
        session.add(newBagel)
        session.commit()
        return jsonify(newBagel.serialize)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

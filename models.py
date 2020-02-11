from flask import request, flash
from config import db, func, app
from flask_bcrypt import Bcrypt
import re
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
SpecialSym =['$', '@', '#', '%'] 

requests = db.Table('requests', 
        db.Column('accepted', db.Boolean),
        db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True), 
        db.Column('listing_id', db.Integer, db.ForeignKey('listings.id', ondelete='cascade', onupdate='cascade'), primary_key=True))
        
        
# users_notifications = db.Table('users_notifications', 
#         db.Column('notification_id', db.Integer, db.ForeignKey('notifications.id', ondelete='cascade')),
#         # db.Column('listing_id', db.Integer, db.ForeignKey('listings.id', ondelete='cascade'), primary_key=True),
#         db.Column('sender_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')), 
#         db.Column('receiver_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True))
        

class UserRequest(db.Model):
    __tablename__ = 'requests'
    __table_args__ = {'extend_existing': True} 

class User(db.Model):
    __tablename__ = 'users'	
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())   
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    listings_requested_by_this_user = db.relationship('Listing', secondary=requests, lazy='dynamic',backref=db.backref('users', lazy=True))
    # listings_notified_this_user = db.relationship('Listing', secondary=notifications, lazy='dynamic',backref=db.backref('notif_users', lazy=True))
    # notifications_by_users = db.relationship('User', secondary=users_notifications, primaryjoin=id==users_notifications.c.receiver_id, secondaryjoin=id==users_notifications.c.sender_id, lazy='dynamic',backref=db.backref('accept_decline_notifications', lazy=True))

    @classmethod
    def validate_user(cls, user_data):
        is_valid = True
        first_name = user_data["first_name"]
        last_name = user_data['last_name']
        passwd = user_data['password']
   
        if len(first_name) < 1:
            is_valid = False
            flash(u'First name cannot be blank.', 'first_name')
        if len(last_name) < 1:
            is_valid = False
            flash(u'Last name cannot be blank.', 'last_name')
        if (not first_name.isalpha() or not last_name.isalpha()) and len(first_name) > 0 and len(last_name) > 0:
            is_valid = False
            flash("First name and last name should contains only letters")
        if len(request.form['email']) < 1:
            flash("Email cannot be blank!", 'email')
        if not EMAIL_REGEX.match(request.form['email']) and len(request.form['email']) > 0:    # test whether a field matches the pattern
            flash("Invalid email address!", 'email')
        if len(passwd) < 8:
            is_valid = False
            flash("Password should be at least 8 characters.")
        if not any(char.isdigit() for char in passwd): 
            is_valid = False
            flash('Password should have at least one numeral')
            
        if not any(char.isupper() for char in passwd): 
            is_valid = False
            flash('Password should have at least one uppercase letter')
            
        if not any(char.islower() for char in passwd): 
            is_valid = False
            flash('Password should have at least one lowercase letter')
            
        if not any(char in SpecialSym for char in passwd):
            is_valid = False
            flash('Password should have at least one of the symbols $@#')
    
        if request.form['password'] != request.form['confirm_password']:
            is_valid = False
            flash("Password doesn't match", 'password')
        return is_valid

    @classmethod
    def add_new_user(cls, user_data):
        hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
        user_to_add = cls(first_name=user_data["first_name"], last_name=user_data["last_name"], email=user_data["email"], password=hashed_password)
        db.session.add(user_to_add)
        db.session.commit()
        return user_to_add

    @classmethod
    def validate_on_login(cls, user_data):
        result = User.query.filter_by(email=user_data['email']).first_or_404(description="Email doesn't exists")
        is_valid = True
        if len(user_data['email']) < 1:
            is_valid = False
            flash('Email cannot be blank')
        if not bcrypt.check_password_hash(result.password, user_data['password']):
            is_valid = False
            flash('Invalid email or password.')
        return is_valid

class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade", onupdate='cascade'), nullable=False)
    location_from = db.Column(db.String())
    location_to = db.Column(db.String())
    description = db.Column(db.String())
    date = db.Column(db.DateTime)
    price = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())   
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    user = db.relationship('User', foreign_keys=[user_id], backref="user_listings")
    # locationFrom = db.relationship('Location', foreign_keys=[location_from], backref="location_from")
    # locationTo = db.relationship('Location', foreign_keys=[location_to], backref="location_to")
    users_request_this_listing = db.relationship('User', secondary=requests, lazy='dynamic', backref=db.backref('listings', lazy=True))
    # users_notified_for_this_listing  = db.relationship('User', secondary=notifications, lazy='dynamic', backref=db.backref('notif_listings', lazy=True))

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id", ondelete="cascade", onupdate='cascade'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade", onupdate='cascade'), nullable=False)
    sender_id = db.Column(db.Integer)
    listing = db.relationship("Listing", foreign_keys=[listing_id], backref="notif_listings")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="notif_users")
    # __table_args__ = (ForeignKeyConstraint([sender_id, receiver_id],[User.id, User.id]))

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String())
    created_at = db.Column(db.DateTime, server_default=func.now())   
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
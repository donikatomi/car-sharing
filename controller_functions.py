from flask import render_template, request, redirect, session
from config import app, db
from models import User, Listing, UserRequest, Notification
from flask_bcrypt import Bcrypt
from datetime import datetime
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker


def landing_page():
    if ('user_id' in session):
        listings = Listing.query.order_by(Listing.updated_at.desc()).filter(Listing.user_id != session['user_id']).all()
        logged_in_user = User.query.filter_by(id=session['user_id']).first()
    else:
        listings = Listing.query.order_by(Listing.updated_at.desc()).all()
        logged_in_user = False
    for listing in listings:
        listing.month = listing.date.strftime("%B")
        listing.day = listing.date.day
    return render_template("index.html", listings=listings, logged_in_user=logged_in_user)

def register():
    return render_template("register.html")

def login():
    return render_template("login.html")

def on_register():
    validation_check = User.validate_user(request.form)
        
    if not validation_check:
        return redirect('/register')
    else:
        if request.form:
            new_user = User.add_new_user(request.form)
            session['user_id'] = new_user.id
        return redirect('/profile')

def on_login():
    validation_check = User.validate_on_login(request.form)
    if not validation_check:
        return redirect('/login')
    else:
        result = User.query.filter_by(email=request.form.get('email')).first_or_404(description="Email doesn't exist")
        session['user_id'] = result.id
        return redirect('/profile')

def logout():
    session.clear()
    return redirect('/')

def profile_dashboard():
    count=0
    if 'user_id' not in session:
        return redirect('/')     
    logged_in_user = User.query.filter_by(id=session['user_id']).first_or_404("Not logged in")  
    return render_template("profile_dashboard.html", logged_in_user=logged_in_user)

def my_listings():
    logged_in_user = User.query.filter_by(id=session['user_id']).first_or_404("Not logged in")
    listings = Listing.query.filter(Listing.user_id==session['user_id']).all()
    for listing in listings:
        listing.month = listing.date.strftime("%B")
        listing.day = listing.date.day
    return render_template("user_listings.html", listings=listings, logged_in_user=logged_in_user)

def create_listing():
    is_valid = True
    date =datetime.strptime(request.form.get("datepicker"), '%Y-%m-%d %I:%M')
    price = request.form.get("price")
    driving_from = request.form.get("from")
    going_to = request.form.get("to")
    description = f"Driving from {driving_from} to {going_to}"
    new_listing = Listing(user_id=session['user_id'], date=date, price=price, location_from=driving_from, location_to=going_to, description=description)
    db.session.add(new_listing)
    db.session.commit()
    return redirect('/profile')

def searchListing():
    if ('user_id' in session):
        logged_in_user = User.query.filter_by(id=session['user_id']).first()
    else:
        logged_in_user = False
    traveling_from = request.args.get('from')
    going_to = request.args.get('to')
    listings = Listing.query.filter_by(location_from=traveling_from, location_to=going_to).all()
    for listing in listings:
        listing.month = listing.date.strftime("%B")
        listing.day = listing.date.day
    return render_template("search_results.html", listings=listings, logged_in_user=logged_in_user)

def details(listing_id):
    listing = Listing.query.get(listing_id)
    listing.month = listing.date.strftime("%B")
    listing.day = listing.date.day
    listing.hour = listing.date.hour
    listing.minute = listing.date.minute
    if ('user_id' in session):
        logged_in_user = User.query.filter_by(id=session['user_id']).first()
        requester = listing.users_request_this_listing.filter_by(id=session['user_id']).first()
        return render_template("listing_details.html", listing=listing, logged_in_user=logged_in_user, requester=requester) 
    else:
        logged_in_user = False
        return redirect('/login')

def destroy(lid, methods=['POST']):
    if request:
        listing = Listing.query.get_or_404(lid, description="Listing doesn't exist")
        notification = Notification.query.filter_by(listing_id=lid).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()
        users = listing.users_request_this_listing.all()
        if users:
            for user in users:
                listing.users_request_this_listing.remove(user)
                db.session.commit()
        db.session.delete(listing)
        db.session.commit()
    return redirect('/my-listings')
        
    
def request_listing(listing_id, methods=['POST']):
    if request:
        logged_in_user = User.query.get(session['user_id'])
        existing_listing = Listing.query.get(listing_id)
        existing_listing.users_request_this_listing.append(logged_in_user)
        db.session.commit()
        # existing_listing.users_notified_for_this_listing.append(logged_in_user)
        # db.session.commit()
    return redirect(f'/{listing_id}/details')

def requests():
    sql = text('SELECT l.*, l.date AS ldate, r.accepted, strftime("%m", l.date) AS month, strftime("%d", l.date) AS day, u.first_name AS requester_name, u.last_name AS requester_lastname, u.id AS requester_id FROM listings l JOIN requests r ON l.id = r.listing_id JOIN users u ON r.user_id = u.id WHERE l.user_id = '+str(session['user_id'])+' ORDER BY l.date DESC')
    result = db.engine.execute(sql)
    listings = result.fetchall()
    logged_in_user = User.query.get(session['user_id'])  
    return render_template("requests.html", logged_in_user=logged_in_user, listings=listings)

def acceptListing(lid, requester_id, methods=['POST']):
    upd = UserRequest.query.filter_by(listing_id = lid, user_id = requester_id).first()
    upd.accepted = 1
    db.session.commit()
    new_notification = Notification(listing_id = lid, receiver_id = requester_id, sender_id=session['user_id'])
    db.session.add(new_notification)
    db.session.commit()

    return redirect ('/requests')

def declineListing(lid, requester_id, methods=['POST']):
    upd = UserRequest.query.filter_by(listing_id = lid, user_id = requester_id).first()
    upd.accepted = 0
    db.session.commit()
    new_notification = Notification(listing_id = lid, receiver_id = requester_id, sender_id=session['user_id'])
    db.session.add(new_notification)
    db.session.commit() 
    return redirect ('/requests')

def showNotifications():
    logged_in_user = User.query.get(session['user_id'])
    sql = text("SELECT l.id as listing_id, l.description, strftime('%m', l.date) AS month, strftime('%d', l.date) AS day, u.first_name, u.last_name, r.accepted  FROM notifications n JOIN listings l on n.listing_id = l.id JOIN requests r on n.listing_id = r.listing_id JOIN users u on n.sender_id = u.id WHERE n.receiver_id = "+str(session['user_id'])+";")
    result = db.engine.execute(sql)
    notifications = result.fetchall()
    for i in notifications:
        print(i.description)
    return render_template("notifications.html", notifications=notifications, logged_in_user=logged_in_user)

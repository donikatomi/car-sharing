from flask import render_template, request, redirect, session
from config import app, db
from models import User, Listing
from flask_bcrypt import Bcrypt
from datetime import datetime
app.secret_key = 'secret'
bcrypt = Bcrypt(app)


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
        result = User.query.filter_by(email=request.form.get('email')).first_or_404(description="Email doesn't exists")
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
    # existing_user = User.query.get(session['user_id'])
    # listings=Listing.query.all()
    # for single_listing in listings:
    #     single_listing.users_request_this_listing.all()
    #     print(single_listing.users_request_this_listing.all())
    #     db.session.commit()
    #     if single_listing.users_request_this_listing.all():
    #         count += 1
    return render_template("profile_dashboard.html", logged_in_user=logged_in_user)

def requests():
    logged_in_user = User.query.filter_by(id=session['user_id']).first_or_404("Not logged in")
    listings = Listing.query.filter_by(user_id=session['user_id']).all()
    
    return render_template("requests.html", logged_in_user=logged_in_user, listings=listings)

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
        return render_template("listing_details.html", listing=listing, logged_in_user=logged_in_user) 
    else:
        logged_in_user = False
        return redirect('/login')
    

def request_listing(listing_id, methods=['POST']):
    if request:
        existing_user = User.query.get(session['user_id'])
        existing_listing = Listing.query.get(listing_id)
        existing_listing.users_request_this_listing.append(existing_user)
        db.session.commit()
    return redirect(f'/{listing_id}/details')



def on_like(tweet_id):
    data = {'user_id':session['user_id'], 'tweet_id':tweet_id}
     
    tweet_id = data['tweet_id']
    user_id = data['user_id']
    existing_user = User.query.get(user_id)
    existing_tweet = Tweet.query.get(tweet_id)
    existing_tweet.users_liked_this_tweet.append(existing_user)
    print(existing_tweet.users_liked_this_tweet)
    #return existing_tweet
    db.session.commit() 
    return redirect('/dashboard')

def on_unlike(tweet_id):
    data = {'user_id': session['user_id']}
    existing_tweet = Tweet.query.get(tweet_id)
    existing_user = User.query.get(data['user_id'])
    existing_tweet.users_liked_this_tweet.remove(existing_user)
    db.session.commit()
    return redirect('/dashboard')

def on_details(tweet_id_route):
    tweet = Tweet.query.get(tweet_id_route)
    tweet_details = tweet.user 
    return render_template("tweet_details.html", tweet_details = tweet_details)

def destroy(tweet_id):
    tweet_instance_to_delete = Tweet.query.get_or_404(tweet_id)
    db.session.delete(tweet_instance_to_delete)
    db.session.commit()
    return redirect('/dashboard')

def edit(tweet_id):
    tweet = Tweet.query.filter_by(id=tweet_id).first()
    user_data = User.query.filter_by(id=session['user_id']).first() 
    return render_template('edit.html', tweet = tweet, user_data = user_data)

def update(tweet_id):
   data = {'content':request.form['content']}
   is_valid = True
   if len(data['content']) < 1 or len(data['content']) > 255:
       is_valid = False
       flash('Tweet must be between 1 and 255 characters long.')
   if is_valid:
       tweet_instance_to_update = Tweet.query.get(tweet_id)
       tweet_instance_to_update.content = data['content']
       db.session.commit()
       return redirect('/dashboard')
   else:
       return redirect(f'/tweets/{tweet_id}/edit')

def all_users():
    data = {'follower_id': session['user_id']}
    all_users = User.query.all()

    logged_in_user = User.query.get(data['follower_id'])
    follower = logged_in_user.users_following_this_user.all() 
   
    return render_template("users.html", logged_in_user = logged_in_user, all_users=all_users, follower=follower)

def on_follow(user_id):
    data = {'user_id': user_id, 'follower_id': session['user_id']}

    user = User.query.get(data['user_id'])
    existing_user = User.query.get(data['follower_id'])
    existing_user.users_following_this_user.append(user)
    db.session.commit()

    return redirect('/users')

def on_unfollow(user_id):
    data={'user_id': user_id, 'follower_id': session['user_id']}
    user = User.query.get(data['user_id'])
    existing_user = User.query.get(data['follower_id'])
    existing_user.users_following_this_user.remove(user)
    db.session.commit()
    return redirect('/users')
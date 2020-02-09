from flask import Flask
from config import app
from controller_functions import (landing_page, register, on_register, on_login, logout, 
profile_dashboard, create_listing, on_like, on_unlike, on_details, destroy, edit, update, 
all_users, on_follow, on_unfollow, login, searchListing, details, request_listing, requests)

app.add_url_rule("/", view_func=landing_page)
app.add_url_rule("/register", view_func=register)
app.add_url_rule("/login", view_func=login)
app.add_url_rule("/register_user", view_func=on_register, methods=['POST'])
app.add_url_rule("/login_user", view_func=on_login, methods=['POST'])
app.add_url_rule("/logout", view_func=logout)
app.add_url_rule("/profile", view_func=profile_dashboard)
app.add_url_rule("/create_listing", view_func=create_listing, methods=['POST'])
app.add_url_rule("/search", view_func=searchListing, methods=['GET'])
app.add_url_rule("/<int:listing_id>/details", view_func=details)
app.add_url_rule("/<int:listing_id>/request_listing", view_func=request_listing, methods=['POST'])
app.add_url_rule("/requests", view_func=requests)


app.add_url_rule("/tweets/<int:tweet_id>/add_like", view_func=on_like)
app.add_url_rule("/tweets/<tweet_id>/add_unlike", view_func=on_unlike)
app.add_url_rule("/details/<tweet_id_route>", view_func=on_details)
app.add_url_rule("/tweets/<int:tweet_id>/delete", view_func=destroy)
app.add_url_rule("/tweets/<tweet_id>/edit", view_func=edit)
app.add_url_rule("/tweets/<tweet_id>/update", view_func=update, methods=['POST'])
app.add_url_rule("/users", view_func=all_users)
app.add_url_rule("/users/<user_id>/follow", view_func=on_follow, methods=['POST'])
app.add_url_rule("/users/<user_id>/unfollow", view_func=on_unfollow, methods=['POST'])

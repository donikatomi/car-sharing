from flask import Flask
from config import app
from controller_functions import (landing_page, register, login, on_register, on_login, logout, 
profile_dashboard, my_listings, create_listing, searchListing, details, destroy, request_listing, requests, 
acceptListing, declineListing, showNotifications)

app.add_url_rule("/", view_func=landing_page)
app.add_url_rule("/register", view_func=register)
app.add_url_rule("/login", view_func=login)
app.add_url_rule("/register_user", view_func=on_register, methods=['POST'])
app.add_url_rule("/login_user", view_func=on_login, methods=['POST'])
app.add_url_rule("/logout", view_func=logout)
app.add_url_rule("/profile", view_func=profile_dashboard)
app.add_url_rule("/my-listings", view_func=my_listings)
app.add_url_rule("/create_listing", view_func=create_listing, methods=['POST'])
app.add_url_rule("/search", view_func=searchListing, methods=['GET'])
app.add_url_rule("/<int:listing_id>/details", view_func=details)
app.add_url_rule("/delete-listing/<int:lid>", view_func=destroy, methods=['POST'])
app.add_url_rule("/<int:listing_id>/request_listing", view_func=request_listing, methods=['POST'])
app.add_url_rule("/requests", view_func=requests)
app.add_url_rule("/<int:lid>/accept/<int:requester_id>", view_func=acceptListing, methods=['POST'])
app.add_url_rule("/<int:lid>/decline/<int:requester_id>", view_func=declineListing, methods=['POST'])
app.add_url_rule("/notifications", view_func=showNotifications)

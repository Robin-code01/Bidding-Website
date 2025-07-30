from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing_page/<int:auction_id>", views.listing_page, name="listing_page"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing_page/comment", views.comment, name="comment"),
    path("listing_page/close", views.close, name="close"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
]

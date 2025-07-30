from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Auctions, Bids, Comments


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auctions.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


@login_required
def new_listing(request):
    if request.method == "POST":
        auction_name = request.POST["auction_name"]
        item_name = request.POST["item_name"]
        item_description = request.POST["item_description"]
        starting_bid = request.POST["starting_bid"]
        item_image = request.POST["item_image"]
        status = request.POST["status"]
        item_category = request.POST["item_category"]
        if status != "Sale":
            return render(request, "auctions/new_listing.html", {
                "message": f"The status cam't be {status} while creating a new listing."
            })
        # Convert starting_bid to float
        try:
            starting_bid = float(starting_bid)
        except ValueError:
            return render(request, "auctions/new_listing.html", {
                "message": "Starting bid must be a number."
            })

        try:
            auction = Auctions(
                auction_name=auction_name,
                item_name=item_name,
                item_description=item_description,
                starting_bid=starting_bid,
                item_image=item_image,
                listed_by=request.user,
                current_bid=starting_bid,
                status=status,
                sold_to=None,
                item_category=item_category,
                current_bid_by=None,
            )
            auction.save()
        except Exception as e:
            return render(request, "auctions/new_listing.html", {
                "message": f"Something wrong happened: {e}"
            })
        return render(request, "auctions/new_listing.html", {
            "message": f"Lisiting for {auction_name} created successfully!"
        })

    return render(request, "auctions/new_listing.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def listing_page(request, auction_id):

    auction = Auctions.objects.get(pk=auction_id)
    if request.method == "POST" and request.user:

        try:
            bid = float(request.POST["bid"])
        except Exception as e:
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Bid needs to be a number: {e}"
            })

        if bid > auction.current_bid:
            auction.current_bid = bid
            auction.current_bid_by = request.user
            auction.save()
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Bid of ${auction.current_bid} placed successfully!"
            })

        elif (bid == auction.current_bid and
              auction.current_bid_by is None):
            auction.current_bid_by = request.user
            auction.save()
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Bid of ${auction.current_bid} placed successfully!"
            })

        else:
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Your bid must be higher than {auction.current_bid}"
            })

    elif request.method == "POST" and not request.user:
        return render(request, "auctions/listing_page.html", {
            "a": auction,
            "message_bid": "The user must be loged in to interact with the listings."
        })

    return render(request, "auctions/listing_page.html", {
        "a": auction
    })


def watchlist(request, auction_id):
    if request.method == "POST":
        pass

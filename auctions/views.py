from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    categories = [
        "Electronics",
        "Fashion",
        "Home & Garden",
        "Toys & Games",
        "Art & Collectibles",
        "Sports Equipment",
        "Antiques & Vintage",
        "Furniture",
        "Jewelry & Watches",
        "Vehicles",
        "Books & Magazines",
        "Music Instruments",
        "Tickets & Experiences",
        "Real Estate",
        "Pets & Animals",
        "Business & Industrial",
        "Health & Beauty",
        "Food & Beverage",
        "Crafts & DIY",
        "Miscellaneous"
    ]

    if request.method == "POST":
        auction_name = request.POST["auction_name"]
        item_name = request.POST["item_name"]
        item_description = request.POST["item_description"]
        starting_bid = request.POST["starting_bid"]
        item_image = request.POST["item_image"]
        status = request.POST["status"]
        item_category = request.POST.getlist("item_category[]")

        for category in item_category:
            if category not in categories:
                return render(request, "auctions/new_listing.html", {
                    "message": f"The category \"{category}\" is not defined"
                })

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
    all_comments = Comments.objects.all()

    comments = []

    for c in all_comments:
        if c.auction.auction_id == auction_id:
            comments.append(c)

    auction = Auctions.objects.get(pk=auction_id)
    if request.method == "POST" and request.user:

        try:
            bid = float(request.POST["bid"])
        except Exception as e:
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Bid needs to be a number: {e}",
                "comments": comments,
            })

        if bid > auction.current_bid:
            auction.current_bid = bid
            auction.current_bid_by = request.user

            new_bid = Bids(auction=auction, bid_amount=bid)

            auction.save()
            new_bid.save()
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Bid of ${auction.current_bid} placed successfully!",
                "comments": comments,
            })

        elif (bid == auction.current_bid and
              auction.current_bid_by is None):
            auction.current_bid_by = request.user

            new_bid = Bids(auction=auction, bid_amount=bid)

            auction.save()
            new_bid.save()
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Bid of ${auction.current_bid} placed successfully!",
                "comments": comments,
            })

        else:
            return render(request, "auctions/listing_page.html", {
                "a": auction,
                "message_bid": f"Your bid must be higher than {auction.current_bid}",
                "comments": comments,
            })

    elif request.method == "POST" and not request.user.is_authenticated:
        return render(request, "auctions/listing_page.html", {
            "a": auction,
            "message_bid": "The user must be loged in to interact with the listings.",
            "comments": comments,
        })

    return render(request, "auctions/listing_page.html", {
        "a": auction,
        "comments": comments,
    })


@login_required
def watchlist(request):
    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        auction = Auctions.objects.get(pk=auction_id)
        if "add_watchlist" in request.POST:
            request.user.watchlist.add(auction)
            messages.success(request, f"Added {
                             auction.auction_name} to yout watchlist")
            return redirect('auctions:listing_page', auction_id=auction.pk)
        elif "remove_watchlist" in request.POST:
            request.user.watchlist.remove(auction)
            messages.success(request, f"Removed {
                             auction.auction_name} to yout watchlist")
            return redirect('auctions:listing_page', auction_id=auction.pk)

    return render(request, "auctions/watchlist.html", {
        "wl": request.user.watchlist.all(),
    })


@login_required
def comment(request):
    if request.method == "POST":
        try:
            auction_id = request.POST["auction_id"]
            auction = Auctions.objects.get(pk=auction_id)
            comment_by = request.user
            comment_content = request.POST["comment_content"]

            comment = Comments(
                auction=auction,
                comment_by=comment_by,
                comment_content=comment_content,
            )

            comment.save()

#            return render(request, "auctions/listing_page.html", {
#                "a": auction,
#                "message_comment": "Commented Successfully",
#                "comments": Comments.objects.all(),
#            })
            messages.success(request, "Commented Successfuly")
            return redirect(reverse('auctions:listing_page', kwargs={"auction_id": auction_id}))

        except Exception as e:
            #            return render(request, "auctions/listing_page.html", {
            #                "a": auction,
            #                "message_comment": f"Error: {e}",
            #                "comments": Comments.objects.all(),
            #            })
            messages.error(request, f"Error: {e}")
            return redirect(reverse('auctions:listing_page', kwargs={"auction_id": auction_id}))

    return redirect("/")


@login_required
def close(request):
    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        auction = Auctions.objects.get(pk=auction_id)

        if request.user == auction.listed_by:
            auction.status = "Sold"
            auction.sold_to = auction.current_bid_by
            auction.save()
            messages.success(request, "Bid Closed Successfully!")
            return redirect(reverse('auctions:listing_page', kwargs={"auction_id": auction_id}))
        else:
            messages.error(request, "you thought you were so smort, ehh?")
            return redirect(reverse('auctions:listing_page', kwargs={"auction_id": auction_id}))

    return redirect("/")


def categories(request):
    categories = [
        "Electronics",
        "Fashion",
        "Home & Garden",
        "Toys & Games",
        "Art & Collectibles",
        "Sports Equipment",
        "Antiques & Vintage",
        "Furniture",
        "Jewelry & Watches",
        "Vehicles",
        "Books & Magazines",
        "Music Instruments",
        "Tickets & Experiences",
        "Real Estate",
        "Pets & Animals",
        "Business & Industrial",
        "Health & Beauty",
        "Food & Beverage",
        "Crafts & DIY",
        "Miscellaneous"
    ]
    return render(request, "auctions/categories.html", {
        "auctions": Auctions.objects.all(),
        "categories": categories,
    })


def category(request, category):
    auctions = Auctions.objects.all()

    required_auctions = []

    for auction in auctions:
        auction_categories = auction.item_category
        if category in auction_categories:
            required_auctions.append(auction)

    return render(request, "auctions/category.html", {
        "required_auctions": required_auctions,
        "category": category,
    })

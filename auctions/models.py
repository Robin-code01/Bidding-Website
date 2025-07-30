from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "auctions.Auctions",
        blank=True,
        related_name="watchlist_users",
    )  # ManyToManyField to Auctions model for watchlist functionality


class Auctions(models.Model):
    auction_id = models.BigAutoField(primary_key=True)
    auction_name = models.CharField(max_length=1000)
    # item_image = models.ImageField(upload_to='item_images/')
    item_image = models.CharField(
        max_length=10000, blank=True, null=True, default=None
    )
    item_category = models.CharField(max_length=1000, blank=True, null=True, default=None)
    item_name = models.CharField(max_length=1000, default="No Name")
    item_description = models.CharField(max_length=10000, default="None")
    starting_bid = models.FloatField()
    listing_creation_time = models.DateTimeField(auto_now_add=True)
    listed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listed_items"
    )
    current_bid = models.FloatField()
    current_bid_by = models.ForeignKey(
        User, blank=True, null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="winning_bids"
    )
    status = models.CharField(max_length=4, default="Sale")
    sold_to = models.ForeignKey(
        User, blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchased_items",
    )

    def __str__(self):
        if self.status != "Sold":
            return f"{self.auction_id}: {self.auction_name} selling {self.item_name} at the bid of ${self.current_bid}"

        return f"{self.auction_id}: {self.auction_name} sold {self.item_name} at the bid of ${self.current_bid} to {self.sold_to}"


class Bids(models.Model):
    bid_id = models.BigAutoField(primary_key=True)
    auction_id = models.ForeignKey(
        Auctions, on_delete=models.CASCADE, related_name="auction_bids"
    )
    bid_amount = models.FloatField()

    def __str__(self):
        return f"{self.bid_id}: ${self.bid_amount} for {self.auction_id}"


class Comments(models.Model):
    commment_id = models.BigAutoField(primary_key=True)
    auction_id = models.ForeignKey(
        Auctions, on_delete=models.CASCADE, related_name="auction_comments"
    )
    comment_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments"
    )
    comment_content = models.CharField(max_length=10000)

    def __str__(self):
        return f"{self.commment_id}: {self.comment_by} commented on {self.auction_id} that \"{self.comment_content}\""

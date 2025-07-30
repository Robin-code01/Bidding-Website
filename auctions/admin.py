from django.contrib import admin

from .models import Auctions, Bids, Comments, User

# Register your models here.

admin.site.register(Auctions)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(User)

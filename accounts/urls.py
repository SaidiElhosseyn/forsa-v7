from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',                               views.login_view,           name='login'),
    path('logout/',                              views.logout_view,          name='logout'),
    path('register/',                            views.register_choice,      name='register'),
    path('register/customer/',                   views.register_customer,    name='register_customer'),
    path('register/vendor/',                     views.register_vendor,      name='register_vendor'),
    path('profile/',                             views.profile_view,         name='profile'),
    path('profile/password/',                    views.password_change_view, name='password_change'),
    path('wishlist/',                            views.wishlist_page,        name='wishlist'),
    path('wishlist/toggle/<int:product_id>/',    views.wishlist_toggle,      name='wishlist_toggle'),
]

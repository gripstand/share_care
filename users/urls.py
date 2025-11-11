from django.contrib import admin
from django.urls import path, include, reverse_lazy
from . import views
from .views import AllUsers, CustomTwoFactorLoginView, CustomPasswordResetComplete, CustomPasswordResetDone, CustomPasswordResetConfirmView
from users.views import CustomTwoFactorLoginView
from django.contrib.auth import views as auth_views
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('create_user/', views.CreateUser, name='user_form'),
    path('list_users/', AllUsers.as_view(), name='list_users'),
    path('update_user/<int:pk>',views.UpdateUser.as_view(),name='update_user'),
    path('user_profile/<int:pk>',views.UserProfile,name='user_profile'),
    path('account/login/', CustomTwoFactorLoginView.as_view(), name='login'),
    #Renders the form for the user to enter their email address.
    path(
        'password_reset/', 
        auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        subject_template_name='registration/my_password_reset_subject.txt',
        email_template_name='registration/my_password_reset_email.html'),
        name='password_reset'
        ),
    #Informs the user that an email has been sent.
    path('password_reset/done/', CustomPasswordResetDone.as_view(),name='password_reset_done'),
   # Renders the form for the user to enter their new password.
    path(
        'reset/<uidb64>/<token>/', 
        CustomPasswordResetConfirmView.as_view(
            #template_name='registration/password_confirm_form.html',
            # success_url is defined in the view above, but kept here for clarity:
            success_url=reverse_lazy('custom_password_complete') 
        ), 
        name='password_reset_confirm'
        ),
    # Shows the final confirmation that the password has been changed.
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='custom_password_complete'),
    path('', include(tf_urls)),
    #path('account/login/', CustomTwoFactorLoginView.as_view(), name='login'),
    #path('', include('django.contrib.auth.urls')),

]
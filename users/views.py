from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import CustomUser
from django.views.generic import CreateView,DetailView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from two_factor.views.mixins import OTPRequiredMixin
from django.contrib.auth import views as auth_views, authenticate  
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login, get_user_model
from .forms import CustomUserForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse  # <-- NEW IMPORT
from django.conf import settings
from two_factor.views import LoginView



def is_admin_group(user):
    """Check if the user belongs to the 'admin' group."""
    return user.groups.filter(name='admin').exists()


# class CustomTwoFactorLoginView(LoginView):
#      template_name = 'two_factor/login.html'

User = get_user_model()

class CustomTwoFactorLoginView(LoginView):
    template_name = 'two_factor/login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        # 1. Attempt to manually retrieve the user object
        try:
            user_to_check = User.objects.get(username=username)
            
            # 2. CHECK 1: If the user is INACTIVE, display a specific error.
            if not user_to_check.is_active:
                messages.error(
                    self.request, 
                    "Your account is currently inactive. Please contact support."
                )
                return self.form_invalid(form)
            
            # 3. CHECK 2: If the user IS active, manually check the password.
            #    We use check_password() instead of authenticate() to avoid the ambiguity.
            if user_to_check.check_password(password):
                # Password is correct. Proceed with the two-factor flow.
                
                # NOTE: We must manually set the user on the form or request for 
                # the two_factor LoginView to pick it up, or call its own methods.
                
                # The cleanest way is to use the user_cache property expected by LoginView:
                form.user_cache = user_to_check
                return super().form_valid(form)
            
            # 4. If password check fails (and user is active), continue to generic error.

        except ObjectDoesNotExist:
            # User doesn't exist. Continue to generic error for security.
            pass
            
        # 5. Fallback: If any check failed (password incorrect or user non-existent), 
        #    return the generic error.
        return self.form_invalid(form)
        
    def form_invalid(self, form):
        # If we have a custom message (for inactive user), render that without 
        # the generic form error that would show below it.
        if messages.get_messages(self.request):
            return self.render_to_response(self.get_context_data(form=form))
        
        # Otherwise, display the standard generic error message.
        return super().form_invalid(form)


#@login_required
@user_passes_test(is_admin_group, login_url='/forbidden/', redirect_field_name=None)
def CreateUser(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_unusable_password()
            user.username = form.cleaned_data.get("email")
            user.save()
            # Redirect to the success URL after the user is saved
            return redirect('list_users')
        else:
            # If the form is invalid, re-render the page with errors
            context = {"form": form}
            return render(request, 'user_form.html', context)
    else:        
        form = CustomUserForm()
        context = {"form": form}
        return render(request, 'user_form.html', context)

User = get_user_model()

class AllUsers(OTPRequiredMixin, LoginRequiredMixin,ListView):
    model=User
    template_name='list_users.html'
    context_object_name='users'
    paginate_by=25
    def get_queryset(self):
        print (User.objects.count())
        return User.objects.all()
    
class UpdateUser(UserPassesTestMixin, UpdateView):
    model=User
    context_object_name='users'
    template_name='user_form.html'
    form_class=CustomUserForm
    success_url = reverse_lazy('list_users')
    login_url = reverse_lazy('login')
    raise_exception = False  # Redirects to login_url instead of raising 403
    def test_func(self):
        # Access the user object via self.request.user
        user = self.request.user
        # Check for membership in the 'admin' group
        return user.groups.filter(name='admin').exists()
    def handle_no_permission(self):
        """Redirects logged-in users who fail the test to the forbidden page."""
        # Check if the user is authenticated; if so, send them to the forbidden page
        if self.request.user.is_authenticated:
            return redirect('/forbidden/') 
        
        # If the user is NOT authenticated, the default mixin behavior takes over,
        # redirecting them to the login_url.
        return super().handle_no_permission()
    def form_valid(self, form):
        # 1. Call the parent clean method to ensure all other validation runs
        # cleaned_data = super().clean()
        # 2. Get the values from the form's cleaned data
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        print("user name is ", username)
        # 3. Perform your logic
        # Check if a title exists and the slug field is empty
        if email != username:
            # Set the slug field's value to the slugified title
            form.instance.username = email

        # 4. You MUST return the cleaned data dictionary
        return super().form_valid(form)
    
def UserProfile(request,pk):
    user=get_object_or_404(CustomUser, pk=pk)
    return render(request,'user_profile.html',context={'this_user':user})

class CustomPasswordResetDone(TemplateView):
    template_name = 'registration/password_reset_sent.html'

# class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
#     template_name = 'registration/password_confirm_form.html'

#     def get_success_url(self):
#         # Return a safe fallback URL, as the redirect will be manual
#         return reverse(settings.LOGIN_REDIRECT_URL) 

#     def form_valid(self, form):
#         # 1. Update the password
#         response = super().form_valid(form)
#         user = form.user
        
#         # 2. Log the user in
#         login(self.request, user)
        
#         # 3. CRITICAL MANUAL CHECK: Check if the user has a registered 2FA device
#         device = default_device(user)
        
#         if not device:
#             # If no device is found (new user), redirect to the package's setup URL
#             return redirect(reverse('two_factor:setup'))
        
#         else:
#             # If a device IS found (existing user), proceed to the standard success page.
#             # (Note: Existing users will still be required to provide a token 
#             # if they log in via the regular login flow, but after password reset, 
#             # this redirects them to the final destination.)
#             return redirect(settings.LOGIN_REDIRECT_URL)

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_confirm_form.html'

class CustomPasswordResetComplete(TemplateView):
    template_name = 'registration/password_reset_complete.html'


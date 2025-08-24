from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import CustomUser
from django.views.generic import CreateView,DetailView, ListView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, get_user_model
from .forms import CustomUserForm
from two_factor.views import LoginView


# Create your views here.

# class CustomUserCreateView(CreateView):
#     model = CustomUser
#     form_class = UserCreationForm# This should be your ModelForm
#     template_name = 'user_form.html'
#     success_url = '/success/'


class CustomTwoFactorLoginView(LoginView):
    template_name = 'two_factor/login.html'


@login_required
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
            return render(request, 'create_users.html', context)
    else:        
        form = CustomUserForm()
        context = {"form": form}
        return render(request, 'user_form.html', context)

User = get_user_model()

class AllUsers(LoginRequiredMixin,ListView):
    model=User
    template_name='list_users.html'
    context_object_name='users'
    paginate_by=25
    def get_queryset(self):
        print (User.objects.count())
        return User.objects.all()
    
class UpdateUser(UpdateView):
    model=User
    context_object_name='users'
    template_name='UserForm'
    form_class=CustomUserForm
    success_url = reverse_lazy('list_users')
    
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
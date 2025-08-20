from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import OuterRef, Subquery
from .models import Client, AddContacts, Goal, GoalUpdate, Actions
from equipment.models import Equipment, EquipmentStatus
from .forms import ClientForm, GoalForm, GoalUpdateForm, PhoneNumberFormSet, PhoneNumberFormSetUpdate, ActionForm
from django.forms import inlineformset_factory
from django.views.generic import CreateView,DetailView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import datetime, date

# Create your views here.
def index(request):
    return render(request,'client/index.html')




#### ________________  Contact Views --------------

def create_client(request):

    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        formset = PhoneNumberFormSet(request.POST)

        if client_form.is_valid() and formset.is_valid():
            client = client_form.save()
            formset.instance = client
            formset.save()
            return redirect('list_clients')
    else:
        client_form = ClientForm()
        formset = PhoneNumberFormSet()

    context = {
        'client_form': client_form,
        'formset': formset,
    }
    return render(request, 'clients/create_client.html', context)

class ListClients(ListView):
    model=Client
    context_object_name='clients'
    template_name='clients/list_clients.html'

class ClientDetails(DetailView):
    model=Client
    context_object_name='client'
    template_name='clients/client_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current client object
        current_client = self.get_object()

        # Create a subquery that finds the pk of the newest EquipmentStatus
        # for each unique equipment ID.
        newest_status = EquipmentStatus.objects.filter(
            equipment=OuterRef('pk')
        ).order_by('-status_date', '-pk')[:1].values('pk')
        
        # Filter the Equipment objects where the pk of their newest status
        # matches a status that belongs to the current contact.
        equipment_with_newest_status = Equipment.objects.filter(
            status_history__in=Subquery(newest_status),
            status_history__client=current_client
        ).distinct()

        context['recent_equipment_list'] = equipment_with_newest_status
        # This grabs all phone numbers based on the 'relate name' in the model
        context['client_add_contacts'] = current_client.phone_numbers.all()

        # Get the releate goals
        client_goals=current_client.goals.all()
        today = date.today()
        # Loop through each goal to calculate the days difference
        for goal in client_goals:
            # Calculate the timedelta
            delta = goal.goal_target_date - today
            
            # Add a new attribute to the goal object
            goal.days_to_go = delta.days
            goal.updates = goal.g_status_record.all()
        context['client_goals']=client_goals
        
        # Get the releate actions
    
        context['client_actions']=current_client.actions_for_client.all()

        
        return context

def update_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    if request.method == 'POST':
        client_form = ClientForm(request.POST, instance=client)
        formset = PhoneNumberFormSetUpdate(request.POST, instance=client)
        if client_form.is_valid() and formset.is_valid():
            client_form.save()
            formset.save()
            return redirect('list_clients')
    else:
        client_form = ClientForm(instance=client)
        if client.phone_numbers.exists():
            formset = PhoneNumberFormSetUpdate(instance=client)
        else:
            formset = PhoneNumberFormSet(instance=client)
    context = {
        'client_form': client_form,
        'formset': formset,
        'client': client, # Pass the entire object
        'client_id': client.id, # Pass the ID to the template
    }
    return render(request, 'clients/create_client.html', context)


#---------------------- GOALS --------------------------#

class CreateGoal(CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'clients/create_goal.html'
    success_url = reverse_lazy('list_clients')

    def get_initial(self):
        # Access the URL parameter 'client_id' from self.kwargs
        client_id = self.kwargs.get('client_id')
        
        # Look up the actual Client object from the database
        client_instance = get_object_or_404(Client, pk=client_id)
        
        # This is where you set initial values for the form's fields
        return {'client': client_instance}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        
        # Add the client instance to the context for template display
        client_id = self.kwargs.get('client_id')
        context['client'] = get_object_or_404(Client, pk=client_id)
        
        return context
    
#### ________________ GOAL UPDATE________________ ####
    
class CreateGoalUpdate(CreateView):
    model=GoalUpdate
    form_class=GoalUpdateForm
    template_name='clients/goal_update.html'
    success_url = reverse_lazy('list_clients')

    def get_initial(self):
        # Access the URL parameter 'goal_id' from self.kwargs
        goal_id = self.kwargs.get('goal_id')
        
        # Look up the actual Goal object from the database
        goal_instance = get_object_or_404(Goal, pk=goal_id)
        
        # This is where you set initial values for the form's fields
        return {'goal': goal_instance}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        
        # Add the goal instance to the context for template display
        goal_id = self.kwargs.get('goal_id')
        context['goal'] = get_object_or_404(Goal, pk=goal_id)
        
        return context
    
    # This is for conditional logic
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Get the related Goal object from the URL parameter
        goal_id = self.kwargs.get('goal_id')
        current_goal = get_object_or_404(Goal, pk=goal_id)
        
        # Check the condition on the Goal model's field
        if current_goal.goal_tack_type != 'Progress':
            kwargs['hide_progress_field'] = True
        
        return kwargs

#---------------------- Actions --------------------------#

class CreateAction(CreateView):
    model = Actions
    form_class = ActionForm
    template_name = 'clients/action.html'
    success_url = reverse_lazy('list_clients')

    def get_initial(self):
        # Access the URL parameter 'client_id' from self.kwargs
        client_id = self.kwargs.get('client_id')
        
        # Look up the actual Client object from the database
        client_instance = get_object_or_404(Client, pk=client_id)
        
        # This is where you set initial values for the form's fields
        return {'client': client_instance}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        
        # Add the client instance to the context for template display
        client_id = self.kwargs.get('client_id')
        context['client'] = get_object_or_404(Client, pk=client_id)
        
        return context
    
class ListActions(ListView):
    model=Actions
    context_object_name='actions'
    template_name='clients/list_actions.html'

class ActionDetails(DetailView):
    model=Actions
    context_object_name='action'
    template_name='clients/action_details.html'
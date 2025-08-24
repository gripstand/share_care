from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import OuterRef, Subquery
from .models import Client, AddContacts, Goal, GoalUpdate, Actions, Eval, Ticket
from equipment.models import Equipment, EquipmentStatus
from .forms import ClientForm, GoalForm, GoalUpdateForm, PhoneNumberFormSet, PhoneNumberFormSetUpdate, ActionForm, EvalForm, TicketForm
from django.forms import inlineformset_factory
from django.views.generic import CreateView,DetailView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import datetime, date

# Create your views here.
def index(request):
    return render(request,'client/index.html')




#### ________________  Client Views --------------
@login_required
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
    return render(request, 'create_client.html', context)

class ListClients(LoginRequiredMixin, ListView):
    model=Client
    context_object_name='clients'
    template_name='list_clients.html'

class ClientDetails(LoginRequiredMixin, DetailView):
    model=Client
    context_object_name='client'
    template_name='client_details.html'

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
        context['client_evals']=current_client.evals_for_client.all() #Note that you query this using the related name defined in the model

        
        return context

@login_required
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
    return render(request, 'create_client.html', context)


#---------------------- GOALS --------------------------#

class CreateGoal(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'create_goal.html'
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

class GoalDetails(LoginRequiredMixin, DetailView):
    model=Goal
    context_object_name='goal'
    template_name='goal_details.html'

    def get_context_data(self, **kwargs):
        # Call the parent class's get_context_data to get the default context
        context = super().get_context_data(**kwargs)
        
        # Access the current Goal object from the context
        goal_object = context['goal']
        
        # Use the related name to get all related GoalUpdate records
        # The related name is 'g_status_record'
        # .all() retrieves all related objects from the database
        goal_updates = goal_object.g_status_record.all()
        
        # Add the GoalUpdate records to the context
        context['goal_updates'] = goal_updates
        
        return context




#### ________________ GOAL UPDATE________________ ####
    
class CreateGoalUpdate(LoginRequiredMixin, CreateView):
    model=GoalUpdate
    form_class=GoalUpdateForm
    template_name='goal_update.html'
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

class CreateAction(LoginRequiredMixin, CreateView):
    model = Actions
    form_class = ActionForm
    template_name = 'action.html'
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
    
class ListActions(LoginRequiredMixin, ListView):
    model=Actions
    context_object_name='actions'
    template_name='list_actions.html'

class ActionDetails(LoginRequiredMixin, DetailView):
    model=Actions
    context_object_name='action'
    template_name='action_details.html'

class UpdateAction(LoginRequiredMixin, UpdateView):
    model = Actions
    form_class = ActionForm
    template_name = 'action.html'
    #success_url = reverse_lazy('list_clients')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.object.client  # Pass the client object to the template
        return context

    def get_object(self, queryset=None):
        action_id = self.kwargs.get('pk')
        return get_object_or_404(Actions, pk=action_id)
    
    def get_success_url(self):
        return reverse_lazy('action_detail', kwargs={'pk': self.object.pk})


class CreateTicket(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket.html'
    success_url = reverse_lazy('list_clients')

    def get_initial(self):
        # Access the URL parameter 'action_id' from self.kwargs
        action_id = self.kwargs.get('action_id')
        
        # Look up the actual Action object from the database
        action_instance = get_object_or_404(Actions, pk=action_id)
        
        # This is where you set initial values for the form's fields
        return {
            'action': action_instance,
            'ticket_created_by': self.request.user,  # Set the current user as the creator
            'ticket_date': date.today()  # Set today's date as the ticket date
        }

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super().get_context_data(**kwargs)
        
    #     # Add the action instance to the context for template display
    #     action_id = self.kwargs.get('action_id')
    #     context['action'] = get_object_or_404(Actions, pk=action_id)
        
    #     return context




#---------------------- Evaluations --------------------------#

class CreateEval(LoginRequiredMixin, CreateView):
    model = Eval
    form_class = EvalForm
    template_name = 'evaluation.html'
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
    
class UpdateEval(LoginRequiredMixin, UpdateView):
    model = Eval
    form_class = EvalForm
    template_name = 'evaluation.html'
    #success_url = reverse_lazy('list_clients')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.object.client  # Pass the client object to the template
        return context

    def get_object(self, queryset=None):
        eval_id = self.kwargs.get('pk')
        return get_object_or_404(Eval, pk=eval_id)
    
    def get_success_url(self):
        return reverse_lazy('eval_detail', kwargs={'pk': self.object.pk})
    
class EvalDetails(LoginRequiredMixin, DetailView):
    model=Eval
    context_object_name='eval'
    template_name='eval_details.html'
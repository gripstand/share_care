from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import OuterRef, Subquery
from .models import Client, AddContacts, Goal, GoalUpdate, Actions, Eval, Ticket, TicketUpdate
from equipment.models import Equipment, EquipmentStatus
from .forms import ClientForm, GoalForm, GoalUpdateForm, PhoneNumberFormSet, PhoneNumberFormSetUpdate, ActionForm, EvalForm, TicketForm, TicketUpdateFormSet, TicketUpdateForm
from django.forms import inlineformset_factory
from django.views.generic import CreateView,DetailView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import datetime, date
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Client
from .forms import ClientForm, PhoneNumberFormSet

# Create your views here.
def index(request):
    return render(request,'client/index.html')




#### ________________  Client Views --------------



class CreateClient(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'create_client.html'
    success_url = reverse_lazy('list_clients')

    def get_context_data(self, **kwargs):
        # Call the base class's get_context_data to get the default context
        data = super().get_context_data(**kwargs)

        # Ensure the main form is available if not already
        # CreateView typically adds 'form' to context, but you can explicitly set it if needed
        if 'form' not in data:
            data['form'] = self.get_form() # Get the form instance

        # Add the formset to the context
        if self.request.POST:
            data['formset'] = PhoneNumberFormSet(self.request.POST)
        else:
            data['formset'] = PhoneNumberFormSet()
        
        return data

    def form_valid(self, form):
        # Get the formset from the context to validate it
        context = self.get_context_data()
        formset = context['formset']

        # If the formset is valid, proceed to save both
        if formset.is_valid():
            self.object = form.save() # Save the main form first
            formset.instance = self.object # Associate the formset with the saved object
            formset.save() # Save the formset data
            return super().form_valid(form) # Redirect to success_url
        else:
            # If the formset is invalid, re-render the form with errors
            # You might want to pass formset errors back to the template here
            # For simplicity, this example re-renders the template with errors
            # Note: You'd need to ensure formset errors are displayed in your template
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

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

#@login_required
# def update_client(request, client_id):
#     client = get_object_or_404(Client, pk=client_id)

#     if request.method == 'POST':
#         client_form = ClientForm(request.POST, instance=client)
#         formset = PhoneNumberFormSetUpdate(request.POST, instance=client)
#         if client_form.is_valid() and formset.is_valid():
#             client_form.save()
#             formset.save()
#             return redirect('list_clients')
#     else:
#         client_form = ClientForm(instance=client)
#         if client.phone_numbers.exists():
#             formset = PhoneNumberFormSetUpdate(instance=client)
#         else:
#             formset = PhoneNumberFormSet(instance=client)
#     context = {
#         'client_form': client_form,
#         'formset': formset,
#         'client': client, # Pass the entire object
#         'client_id': client.id, # Pass the ID to the template
#     }
#     return render(request, 'create_client.html', context)

#

class ClientUpdateView(LoginRequiredMixin,UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'create_client.html' # Uses the same template
    success_url = reverse_lazy('list_clients')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = PhoneNumberFormSetUpdate(self.request.POST, instance=self.object)
        else:
            # Check if there are existing phone numbers to initialize the formset
            if self.object.phone_numbers.exists():
                data['formset'] = PhoneNumberFormSetUpdate(instance=self.object)
            else:
                data['formset'] = PhoneNumberFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            # If formset is invalid, return to the form with errors
            return self.render_to_response(self.get_context_data(form=form))


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
        initial = super().get_initial()
        # Access the URL parameter 'client_id' from self.kwargs
        #client_id = self.kwargs.get('client_id')
        
        # Look up the actual Client object from the database
        #client_instance = get_object_or_404(Client, pk=client_id)
        initial['action_user'] = self.request.user
        # This is where you set initial values for the form's fields
        #return {'client': client_instance}
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current client object
        current_action = self.get_object()

        # Get all tickets related to this action
        context['action_tickets'] = current_action.ticket_for_action.all()
        return context

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

# ---------------------- Tickets --------------------------#

class CreateTicket(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket.html'
    success_url = reverse_lazy('list_clients')

    def dispatch(self, request, *args, **kwargs):
        # Fetch the action object from the database once
        self.action_instance = get_object_or_404(Actions, pk=kwargs.get('action_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        # Use the stored action object
        return {
            'action': self.action_instance,
            'ticket_created_by': self.request.user,
            'ticket_date': date.today(),
        }
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # Use the stored action object
        data['action'] = self.action_instance
        # Add the formset logic as before
        if self.request.POST:
            data['formset'] = TicketUpdateFormSet(self.request.POST)
        else:
            data['formset'] = TicketUpdateFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        # Check if the formset is valid before saving anything
        if formset.is_valid():
            # Step 1: Save the main Ticket form. This creates the parent object.
            self.object = form.save()
            
            # Step 2: Associate the formset with the newly created Ticket object.
            formset.instance = self.object

            # Step 3: Iterate through each form in the formset and set the required user.
            for f in formset:
                # Only save the form if it's not marked for deletion
                if not f.cleaned_data.get('DELETE', False):
                    # Set the ticket_update_by field to the current user
                    f.instance.ticket_update_by = self.request.user

            # Step 4: Save the formset. The forms now have the required user value.
            formset.save()
            
            # Step 5: Redirect to the success URL
            return super().form_valid(form)
        else:
            # The formset's errors are a list, where each item is the errors for one form
            print("Formset is NOT valid. All errors:")
            print(formset.errors)
            
            # You can also iterate through each form to get specific errors
            for f in formset:
                if f.errors:
                    print("Errors for form:")
                    print(f.errors)
            
            return self.form_invalid(form)

class AddTicketUpdate(LoginRequiredMixin, CreateView):
    model = TicketUpdate
    form_class = TicketUpdateForm
    template_name = 'update_ticket.html'
    success_url = reverse_lazy('list_clients')

    def dispatch(self, request, *args, **kwargs):
        # Fetch the ticket object from the database once
        self.ticket_instance = get_object_or_404(Ticket, pk=kwargs.get('ticket_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
            # Use the stored ticket object
            return {
                'ticket': self.ticket_instance,
                'ticket_update_date': date.today(),
                'ticket_update_by': self.request.user,
            }

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['ticket'] = self.ticket_instance
        data['previous_updates'] = self.ticket_instance.updates_for_ticket.all().order_by('-ticket_update_date')
        return data

class TicketDetails(LoginRequiredMixin, DetailView):
    model=Ticket
    context_object_name='ticket'
    template_name='ticket_details.html'


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
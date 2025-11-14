from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from equipment.models import Equipment, EquipmentStatus
from django.contrib import messages
from .forms import EquipmentForm, EqStatusForm
from django.urls import reverse_lazy
from datetime import date
from django.db.models import Subquery, OuterRef


# Create your views here.

#### ________________ EQUIPMENT________________ ####

class CreateEquipment(CreateView):
    model=Equipment
    form_class=EquipmentForm
    #context_object_name='equipment'
    template_name='create_equipment.html'
    success_url=reverse_lazy('list_equipment')
    
    def form_valid(self, form):
        # Save the new Equipment instance first
        new_equipment = form.save()
        today = date.today()

        # Create the new EquipmentStatus record
        EquipmentStatus.objects.create(
            equipment=new_equipment,
            status='INV',
            status_date=today
        )
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Define a safe fallback URL using the {% url %} tag's reverse lookup
            fallback_url = reverse_lazy('list_equipment') # Example fallback
            
            # Get referer, falling back to the fallback_url if the header is missing
            referer_url = self.request.META.get('HTTP_REFERER')
            
            # IMPORTANT: Make sure the referer isn't the current page!
            if referer_url and referer_url != self.request.path:
                context['previous_url'] = referer_url
            else:
                context['previous_url'] = fallback_url
                
            return context

class ListEquipment(ListView):
    model = Equipment
    context_object_name = 'equipment'
    template_name = 'list_equipment.html'



    def get_queryset(self):
            # 1. Subquery to find the PK of the LATEST status record for the equipment
            # We explicitly use the model's related_name for clarity (though not required here)
            latest_status_pk_subquery = Subquery(
                # Start the query directly on the related model
                EquipmentStatus.objects.filter(
                    equipment=OuterRef('pk') # Use object reference instead of equipment_id
                ).order_by('-status_date', '-pk') # Ensure this field belongs to EquipmentStatus
                .values('pk')[:1] 
            )

            # 2. Annotate the main queryset with the PK
            annotated_queryset = super().get_queryset().annotate(
                latest_status_pk_annotated=latest_status_pk_subquery
            )
            
            # 3. Subquery to pull the status code
            latest_status_code = Subquery(
                EquipmentStatus.objects.filter(
                    pk=OuterRef('latest_status_pk_annotated')
                ).values('status')[:1]
            )
            
            # 4. Subquery to pull the status date
            latest_status_date = Subquery(
                EquipmentStatus.objects.filter(
                    pk=OuterRef('latest_status_pk_annotated')
                ).values('status_date')[:1] # Ensure 'status_date' is spelled correctly
            )

            # 5. Final Annotation and Return
            # Ensure all fields are correctly named here
            return annotated_queryset.annotate(
                latest_status_code=latest_status_code,
                latest_status_date=latest_status_date 
            ).order_by('eq_name')



class UpdateEquipment(UpdateView):
    model=Equipment
    form_class=EquipmentForm
    context_object_name='eq'
    template_name='create_equipment.html'
    success_url=reverse_lazy('list_equipment')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define a safe fallback URL using the {% url %} tag's reverse lookup
        fallback_url = reverse_lazy('list_equipment') # Example fallback
        
        # Get referer, falling back to the fallback_url if the header is missing
        referer_url = self.request.META.get('HTTP_REFERER')
        
        # IMPORTANT: Make sure the referer isn't the current page!
        if referer_url and referer_url != self.request.path:
            context['previous_url'] = referer_url
        else:
            context['previous_url'] = fallback_url
            
        return context

class DetailEquipment(DetailView):
    model=Equipment
    context_object_name='eq'
    template_name='equipment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current Equipment object from the view
        equipment = self.get_object()
        
        # Use the related_name to get all related status updates
        self.new_method(context, equipment)
        
        return context

    def new_method(self, context, equipment):
        context['status_updates'] = equipment.status_history.all().order_by('-status_date')

#### ________________ EQUIPMENT STATUS________________ ####

class CreateEqStatus(CreateView):
    model = EquipmentStatus
    form_class = EqStatusForm
    template_name = 'equipment_status.html'
    success_url = reverse_lazy('list_equipment')

    # The following function gets the last record saved for this equipment so it can pass that to the form in order to determine what status types are available
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Get the equipment instance from the URL
        eq_id = self.kwargs.get('eq_id')
        equipment = get_object_or_404(Equipment, pk=eq_id)
        
        # Find the last saved status for this equipment
        last_status_record = EquipmentStatus.objects.filter(
            equipment=equipment
        ).order_by('-status_date').first()
        
        # Pass the last status value to the form's __init__ method
        kwargs['last_status'] = last_status_record.status if last_status_record else None
        kwargs['last_client'] = last_status_record.client if last_status_record else None
        return kwargs

    # This function checks if the equipment is active before allowing the form to be displayed
    def dispatch(self, request, *args, **kwargs):
        eq_id = self.kwargs.get('eq_id')
        equipment_instance = get_object_or_404(Equipment, pk=eq_id)
        
        if equipment_instance.eq_active_status == False:
            messages.error(
                request, 
                f"You cannot add an update to inactive equipment."
            )
            return redirect('detail_equipment', pk=eq_id)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        # This to populate the form....
        # Access the URL parameter 'eq_id' from self.kwargs
        eq_id = self.kwargs.get('eq_id')
        
        # Look up the actual Equipment object from the database
        equipment_instance = get_object_or_404(Equipment, pk=eq_id)
            
        # Set the initial value for the 'equipment' foreign key field
        return {'equipment': equipment_instance}
    
    def get_context_data(self, **kwargs):
        # This to populate the template....
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        
        # Get the equipment ID from the URL
        eq_id = self.kwargs.get('eq_id')

        # Get the equipment object and add it to the context
        context['equipment'] = get_object_or_404(Equipment, pk=eq_id)

        # Define a safe fallback URL using the {% url %} tag's reverse lookup
        fallback_url = reverse_lazy('list_equipment') # Example fallback
        
        # Get referer, falling back to the fallback_url if the header is missing
        referer_url = self.request.META.get('HTTP_REFERER')
        
        # IMPORTANT: Make sure the referer isn't the current page!
        if referer_url and referer_url != self.request.path:
            context['previous_url'] = referer_url
        else:
            context['previous_url'] = fallback_url
            
        
        return context

    def form_valid(self, form):
        # The form has a hidden field for 'equipment'
        # The value is an ID, but the field expects an object.
        equipment_id = self.request.POST.get('equipment')
        equipment_instance = get_object_or_404(Equipment, pk=equipment_id)
        
        # Save the new EquipmentUpdate record first and assign it to self.object
        self.object = form.save()

        # Now that self.object exists, you can safely check its status
        if self.object.status == 'SUNSET':
            # You can access the related equipment instance directly from the new object
            # self.object.equipment is the same as equipment_instance here
            equipment_instance.eq_active_status = False
            equipment_instance.save()
        
        return super().form_valid(form)
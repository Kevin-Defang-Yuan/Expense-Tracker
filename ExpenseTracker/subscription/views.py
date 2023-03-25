from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy
from .models import Subscription
from .forms import CreateSubscriptionForm, TerminateSubscriptionForm
from base.models import Expense
from datetime import date, datetime
from django.contrib import messages
from base.views import CustomLoginRequiredMixin


"""
Subscription Create View
"""
class SubscriptionCreate(CustomLoginRequiredMixin, CreateView):
    model = Subscription
    template_name = 'subscription/subscription_create.html'
    success_url = reverse_lazy('subscription-list')
    form_class = CreateSubscriptionForm

    # We want the form to automatically know which user to submit the data
    def form_valid(self, form):
        form.instance.user = self.request.user

        # Automatically set indefinite to True (cause it is a subscription)
        form.instance.indefinite = True
        return super(SubscriptionCreate, self).form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(SubscriptionCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    # Function to set initial value for date field in forms to today
    def get_initial(self):
        if 'day' in self.request.GET:
            return {
                'start_date': datetime(int(self.request.GET['year']), int(self.request.GET['month']), int(self.request.GET['day']))
            }
        
        if 'month' in self.request.GET:
            return {
                'start_date': datetime(int(self.request.GET['year']), int(self.request.GET['month']), 1)
            }
        
        if 'year' in self.request.GET:
            return {
                'start_date': datetime(int(self.request.GET['year']), 1, 1)
            }
        return {
            'start_date': date.today()
        }
    
    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Subscription successfully created!')
        return self.request.session['previous_page']

"""
SubscriptionList view for all subscriptions
"""
class SubscriptionList(CustomLoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscription/subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

"""
Edit subscription view
"""
class SubscriptionUpdate(CustomLoginRequiredMixin, UpdateView):
    model = Subscription
    success_url = reverse_lazy('subscription-list')
    form_class = CreateSubscriptionForm
    template_name = 'subscription/subscription_update.html'
    context_object_name = 'subscription'

    def get_form_kwargs(self):
        kwargs = super(SubscriptionUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Subscription successfully updated!')
        return self.request.session['previous_page']

"""
Delete Subscription View
"""
class SubscriptionDelete(CustomLoginRequiredMixin, DeleteView):
    model = Subscription
    success_url = reverse_lazy('subscription-list')
    template_name = 'subscription/subscription_delete.html'
    context_object_name = 'subscription'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscription_id = self.kwargs.get('pk')

        # Find all related expenses
        expenses_under_subscription = Expense.objects.filter(user=self.request.user).filter(subscription=subscription_id)
        context['expenses_under_subscription'] = expenses_under_subscription
        return context
    
    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Subscription successfully deleted!')
        return self.request.session['previous_page']
"""
Cancel Subsription View
"""
class SubscriptionTerminate(CustomLoginRequiredMixin, UpdateView):
    model = Subscription
    context_object_name = 'subscription'
    template_name = 'subscription/subscription_terminate.html'
    success_url = reverse_lazy('subscription-list')
    form_class = TerminateSubscriptionForm

    def form_valid(self, form):
        today = date.today()

        # Set the end date as the day it is terminated
        form.instance.end_date = today

        # Set indefinite to False as it is terminated
        form.instance.indefinite = False


        return super(SubscriptionTerminate, self).form_valid(form)
    
    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Subscription successfully terminated!')
        return self.request.session['previous_page']

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Subscription
from .forms import CreateSubscriptionForm
from base.models import Expense

# Create your views here.
class SubscriptionCreate(LoginRequiredMixin, CreateView):
    model = Subscription
    template_name = 'subscription/subscription_create.html'
    success_url = reverse_lazy('subscription-list')
    form_class = CreateSubscriptionForm

    # We want the form to automatically know which user to submit the data
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(SubscriptionCreate, self).form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(SubscriptionCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SubscriptionList(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscription/subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class SubscriptionUpdate(LoginRequiredMixin, UpdateView):
    model = Subscription
    success_url = reverse_lazy('subscription-list')
    fields = '__all__'
    template_name = 'subscription/subscription_update.html'
    context_object_name = 'subscription'


class SubscriptionDelete(LoginRequiredMixin, DeleteView):
    model = Subscription
    success_url = reverse_lazy('subscription-list')
    template_name = 'subscription/subscription_delete.html'
    context_object_name = 'subscription'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscription_id = self.kwargs.get('pk')
        expenses_under_subscription = Expense.objects.filter(user=self.request.user).filter(subscription=subscription_id)
        context['expenses_under_subscription'] = expenses_under_subscription
        return context
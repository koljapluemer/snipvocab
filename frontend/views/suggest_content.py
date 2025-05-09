from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from frontend.models import ContentWish
from django import forms

class ContentWishForm(forms.ModelForm):
    class Meta:
        model = ContentWish
        fields = ['wish', 'extra_message']
        widgets = {
            'wish': forms.TextInput(attrs={'class': 'input', 'placeholder': 'What content would you like to see?'}),
            'extra_message': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Any additional details or context? (optional)'}),
        }

class SuggestContentView(FormView):
    template_name = 'frontend/suggest_content.html'
    form_class = ContentWishForm
    success_url = reverse_lazy('frontend:dashboard')

    def form_valid(self, form):
        wish = form.save(commit=False)
        wish.user = self.request.user
        wish.save()
        messages.success(self.request, 'Thank you for your suggestion! I will review it ASAP.')
        return super().form_valid(form)

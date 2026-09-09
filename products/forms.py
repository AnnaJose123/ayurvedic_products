import re
from django import forms
from .models import Enquiry, Product

class EnquiryForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_available=True),
        required=False,
        empty_label="-- Select Product (Optional) --",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_product'
        }),
        help_text="Choose a product you would like to enquire about."
    )

    class Meta:
        model = Enquiry
        fields = ['name', 'phone', 'product', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your full name',
                'id': 'id_name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 9876543210 or +919876543210',
                'id': 'id_phone'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Write your message or question here...',
                'id': 'id_message'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        if name.isdigit():
            raise forms.ValidationError("Name cannot consist only of numbers.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Strip common formatting spaces/hyphens for checking
        clean_num = phone.replace(" ", "").replace("-", "")
        # Validate standard 10 digit Indian number or +91 / 91 prefixed 10-digit number
        pattern = r'^(?:\+?91|0)?[6-9]\d{9}$'
        if not re.match(pattern, clean_num):
            raise forms.ValidationError("Please enter a valid 10-digit phone number (e.g. 9876543210 or +919876543210).")
        
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError("Message cannot be empty.")
        if len(message) < 5:
            raise forms.ValidationError("Please provide a message with at least 5 characters.")
        if len(message) > 1000:
            raise forms.ValidationError("Message is too long (maximum 1000 characters).")
        return message

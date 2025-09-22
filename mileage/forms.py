from django import forms
from .models import MileageLog
from clients.models import Client


class MileageLogForm(forms.ModelForm):
    """Form for creating and editing mileage logs."""
    
    class Meta:
        model = MileageLog
        fields = ['date', 'start_location', 'end_location', 'purpose', 'miles', 'client', 'start_address', 'end_address']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Home Office, Main Office'}),
            'end_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Client Company Name'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Client meeting, Site visit'}),
            'miles': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'start_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address including postcode'}),
            'end_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address including postcode'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter clients to only show those belonging to the current user
        if self.user:
            self.fields['client'].queryset = Client.objects.filter(user=self.user)
            self.fields['client'].empty_label = "Select a client"
            
            # Set default start location and address to user's profile
            try:
                profile = self.user.profile
                if profile.address_line_1:
                    address_parts = [profile.address_line_1]
                    if profile.address_line_2:
                        address_parts.append(profile.address_line_2)
                    address_parts.extend([profile.town, profile.post_code])
                    default_start_location = "Home Office"
                    default_start_address = ', '.join(address_parts)
                    
                    # Set initial values if not already set
                    if not self.initial.get('start_location'):
                        self.initial['start_location'] = default_start_location
                    if not self.initial.get('start_address'):
                        self.initial['start_address'] = default_start_address
            except:
                pass  # If profile doesn't exist, just continue
        
        # Add help text
        self.fields['miles'].help_text = "Enter the number of miles driven (can include decimals)"
        self.fields['client'].help_text = "Select the client for this business journey"
    
    def clean_miles(self):
        """Validate that miles is a positive number."""
        miles = self.cleaned_data.get('miles')
        if miles is not None and miles <= 0:
            raise forms.ValidationError("Miles must be greater than 0.")
        return miles
    
    def clean(self):
        """Additional validation."""
        cleaned_data = super().clean()
        start_location = cleaned_data.get('start_location')
        end_location = cleaned_data.get('end_location')
        
        if start_location and end_location and start_location.lower() == end_location.lower():
            raise forms.ValidationError("Start and end locations cannot be the same.")
        
        return cleaned_data



# forms.py

from django import forms
from .models import AirportRoute


class AirportRouteForm(forms.ModelForm):
    """Form for creating airport routes"""
    
    class Meta:
        model = AirportRoute
        fields = ['airport_code', 'parent', 'position', 'duration']
        widgets = {
            'airport_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., DXB, JFK, LHR'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'position': forms.Select(attrs={
                'class': 'form-control'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distance in km',
                'min': '0'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty label for parent selection
        self.fields['parent'].empty_label = "No Parent (Root Node)"
        self.fields['parent'].queryset = AirportRoute.objects.all()
        
        # Update duration field attributes
        self.fields['duration'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Distance in km from parent',
            'min': '0'
        })

    def clean(self):
        """Validate form data"""
        cleaned_data = super().clean()
        parent = cleaned_data.get("parent")
        position = cleaned_data.get("position")
        duration = cleaned_data.get("duration")

        # Root node validation
        if parent is None:
            if position != "ROOT":
                raise forms.ValidationError(
                    "Root node must have position 'ROOT'."
                )
            
            # Root node must have duration = 0
            if duration is not None and duration != 0:
                raise forms.ValidationError(
                    "Root node must have duration = 0 (no parent to travel from)."
                )
            # Auto-set duration to 0 for root
            cleaned_data['duration'] = 0
            
            # IMPORTANT: Check if a root already exists
            existing_root = AirportRoute.objects.filter(
                position='ROOT',
                parent=None
            )
            
            # Exclude current instance if editing
            if self.instance.pk:
                existing_root = existing_root.exclude(pk=self.instance.pk)
            
            if existing_root.exists():
                raise forms.ValidationError(
                    f"A root node already exists: {existing_root.first().airport_code}. "
                    "The system can only have ONE root node. Please select it as parent."
                )
        else:
            # Non-root node validation
            if position == "ROOT":
                raise forms.ValidationError(
                    "Only the root node can have position 'ROOT'."
                )
            
            # Child nodes must have duration > 0
            if duration is not None and duration <= 0:
                raise forms.ValidationError(
                    "Child nodes must have duration > 0 (distance from parent node)."
                )
            
            # Check for duplicate children
            duplicate = AirportRoute.objects.filter(
                parent=parent,
                position=position
            )
            
            # # Exclude current instance if editing
            # if self.instance.pk:
            #     duplicate = duplicate.exclude(pk=self.instance.pk)
            
            if duplicate.exists():
                position_name = dict(AirportRoute.POSITION_CHOICES)[position]
                raise forms.ValidationError(
                    f"A {position_name} child already exists for the selected parent."
                )

        return cleaned_data


class SearchLastReachableForm(forms.Form):
    """Form for searching the last reachable node"""
    
    DIRECTION_CHOICES = (
        ('left', 'Left'),
        ('right', 'Right'),
    )
    
    start_node = forms.ModelChoiceField(
        queryset=AirportRoute.objects.all(),
        label="Starting Airport Node",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label="Select an airport..."
    )
    
    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        label="Direction",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update queryset to show more details
        self.fields['start_node'].label_from_instance = lambda obj: (
            f"{obj.airport_code} ({obj.get_position_display()}) - {obj.duration}km"
        )
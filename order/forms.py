from django import forms


class OrderCheckoutForm(forms.Form):

    pay_methods = [
        ('CREDIT/DEBIT CARD', 'CREDIT/DEBIT CARD'),
        ('PAYPAL', 'PAYPAL')
    ]

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    payment = forms.ChoiceField(choices=pay_methods)
    comment = forms.CharField(max_length=600, required=False, widget=forms.Textarea, label='Comment(optional)')



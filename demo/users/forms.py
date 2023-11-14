from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=101)
    last_name = forms.CharField(max_length=101)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class StockChoiceForm(forms.Form):
    company_choices = [
        ('AAPL', 'Apple Inc. (AAPL)'),
        ('TSLA', 'Tesla, Inc. (TSLA)'),
        ('AMZN', 'Amazon.com, Inc. (AMZN)'),
    ]
    company = forms.ChoiceField(choices=company_choices, label='Select a company')

class StockBuyForm(forms.Form):
    STOCK_CHOICES = [
        ('AAPL', 'Apple Inc.'),
        ('TSLA', 'Tesla Inc.'),
        ('AMZN', 'Amazon.com Inc.'),
    ]
    call_type_choices = [('Short', 'Short'),
                         ('Long', 'Long')]
    
    symbol = forms.ChoiceField(choices=STOCK_CHOICES)
    amount = forms.IntegerField(min_value=1)
    call_type = forms.ChoiceField(choices=call_type_choices)

class StockSellForm(forms.Form):
    symbol_choices = [
        ('AAPL', 'AAPL - Apple Inc.'),
        ('AMZN', 'AMZN - Amazon.com Inc.'),
        ('TSLA', 'TSLA - Tesla Inc.'),
        # Add more options as needed
    ]

    symbol = forms.ChoiceField(label='Symbol', choices=symbol_choices)
    amount = forms.IntegerField(label='Amount', min_value=1)
    call_type = forms.ChoiceField(
        label='Transaction Type',
        choices=[
            ('Long', 'Long'),
            ('Short', 'Short'),
        ]
    )

class Stock_Graph_Choice(forms.Form):
    STOCK_CHOICES = [
        ('AAPL', 'Apple Inc.'),
        ('TSLA', 'Tesla Inc.'),
        ('AMZN', 'Amazon.com Inc.'),
    ]
    TIME_CHOICES = [
        ('8', '1 Week'),
        ('32', '1 Month'),
        ('183', '6 Months'),
        ('366', '1 Year'),
    ]
    symbol = forms.ChoiceField(choices=STOCK_CHOICES, label='Select Company Symbol', initial='AAPL')
    days = forms.ChoiceField(choices=TIME_CHOICES, label='Select Timeframe', initial='8')
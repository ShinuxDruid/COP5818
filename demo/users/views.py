from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils.safestring import mark_safe
from .forms import UserRegistrationForm, StockChoiceForm, StockBuyForm, StockSellForm, Stock_Graph_Choice, LoginForm
from .utils import get_stock_data
from .models import Transaction
import pandas as pd
import yfinance as yf
import json
from decimal import Decimal
from datetime import date 
from datetime import timedelta
from datetime import datetime

def home(request):
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created. You can log in now!')    
            return redirect('login')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'users/register.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('home')  # change 'home' to the name of your home page URL
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

TODAY = date.today().strftime("%Y-%m-%d")
START = date.today() - timedelta(days=365*3)

def load_data(ticker):
    data= yf.download(ticker, START, TODAY)
    data.reset_index(inplace = True)
    return data

@login_required
def stock_data_view(request):
    if request.method == 'POST':
        form = StockChoiceForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['company']
            stock_data = get_stock_data(symbol)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            context = {
                'stock_data': stock_data,
                'symbol': symbol,
                'current_date': current_date,
                'high': round(list(stock_data['High'].values())[0], 2),
                'low': round(list(stock_data['Low'].values())[0], 2),
                'open': round(list(stock_data['Open'].values())[0], 2),
                'close': round(list(stock_data['Close'].values())[0], 2),
                'volume': round(list(stock_data['Volume'].values())[0], 2)
            }
            return render(request, 'users/stock_data.html', context)
    else:
        form = StockChoiceForm()
    return render(request, 'users/stock_choice_form.html', {'form': form})

@login_required
def buy_stock(request):
    if request.method == 'POST':
        form = StockBuyForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            amount = form.cleaned_data['amount']
            call_type = form.cleaned_data['call_type']
            stock_data = yf.Ticker(symbol)
            current_price = Decimal(stock_data.history(period='1d')['Close'].iloc[-1])

            # Calculate shares
            shares = Decimal(amount) / current_price

            # Check if a transaction with the given symbol and call_type already exists for the user
            existing_transaction = Transaction.objects.filter(
                user=request.user,
                symbol=symbol,
                call_type=call_type
            ).first()

            if existing_transaction:
                # If the transaction exists, update the amount
                existing_transaction.amount = F('amount') + amount
                existing_transaction.shares = F('shares') + shares
                existing_transaction.save()
            else:
                # If the transaction does not exist, create a new one
                transaction = Transaction.objects.create(
                    user=request.user,
                    symbol=symbol,
                    amount=amount,
                    date=TODAY,
                    call_type=call_type,
                    shares=shares
                    # Set other fields as needed
                )
                transaction.save()

            # Redirect to a success page or wherever appropriate
            return redirect('users/success_page.html')

    else:
        form = StockBuyForm()
        symbol = form.initial.get('symbol')  # Get the initial symbol from the form
        if symbol:
            stock_data = yf.Ticker(symbol)
            current_price = stock_data.history(period='1d')['Close'].iloc[-1]

    return render(request, 'users/buy_stock.html', {'form': form})

def success_page(request):
    return render(request, 'users/success_page.html')

@login_required
def transaction_history(request):
    unique_symbols = Transaction.objects.filter(user=request.user).values('symbol').distinct()

    transactions_summary = []
    for symbol in unique_symbols:
        symbol = symbol['symbol']
        symbol_long_transactions = Transaction.objects.filter(user=request.user, symbol=symbol, call_type='Long')
        symbol_short_transactions = Transaction.objects.filter(user=request.user, symbol=symbol, call_type='Short')

        total_long_amount = symbol_long_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        total_short_amount = symbol_short_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        total_long_shares = symbol_long_transactions.aggregate(Sum('shares'))['shares__sum'] or 0
        total_short_shares = symbol_short_transactions.aggregate(Sum('shares'))['shares__sum'] or 0

        transactions_summary.append({
            'symbol': symbol,
            'total_long_amount': total_long_amount,
            'total_short_amount': total_short_amount,
            'total_long_shares': total_long_shares,
            'total_short_shares': total_short_shares,

        })

    return render(
        request,
        'users/transaction_history.html',
        {'transactions_summary': transactions_summary}
    )

@login_required
def sell_stock(request):
    user_holdings = Transaction.objects.filter(user=request.user).values('symbol', 'amount', 'call_type','shares')

    if request.method == 'POST':
        form = StockSellForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            amount = form.cleaned_data['amount']
            call_type = form.cleaned_data['call_type']

            existing_transaction = Transaction.objects.filter(
                user=request.user,
                symbol=symbol,
                call_type=call_type,
            ).first()

            if existing_transaction:
                if existing_transaction.amount >= amount:
                    existing_transaction.amount -= amount
                    existing_transaction.save()

                    # Check if the amount is now 0 and delete the transaction if true
                    if existing_transaction.amount == 0:
                        existing_transaction.delete()

                    return render(request, 'users/success_page.html')
                else:
                    error_message = 'Insufficient shares to sell'
            else:
                error_message = 'No shares to sell'

            return render(request, 'users/error_page.html', {'error_message': error_message})

    else:
        form = StockSellForm()

    return render(request, 'users/sell_stock.html', {'form': form, 'user_holdings': user_holdings})

def error_page(request):
    return render(request, error_page.html)

def get_stock_data_for_last_month(symbol):
    # Get stock data for the last month using yfinance
    end_date = pd.to_datetime("today").strftime('%Y-%m-%d')
    start_date = (pd.to_datetime("today") - pd.DateOffset(days=30)).strftime('%Y-%m-%d')
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    
    # Convert Timestamps to strings
    stock_data.index = stock_data.index.strftime('%Y-%m-%d %H:%M:%S')
    
    return stock_data

@login_required
def stock_graph_symbol(request, symbol='AAPL', days=7):
    if request.method == 'POST':
        # If the form is submitted, get the symbol from the form
        form = Stock_Graph_Choice(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            days = form.cleaned_data['days']
            # Redirect to the same view with the new symbol
            return redirect('stock_graph_symbol', symbol=symbol, days=days)
    else:
        # If it's a GET request, initialize the form with the default symbol
        form = Stock_Graph_Choice(initial={'symbol': symbol, 'days': days})
    # Set the end date to today
    end_date = datetime.today().strftime('%Y-%m-%d')
    # Calculate the start date based on the number of days requested
    start_date = (datetime.today() - timedelta(days=int(days))).strftime('%Y-%m-%d')
    # Fetch historical stock data using yfinance
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    # Prepare data for plotting
    stock_data = stock_data.reset_index()
    stock_data.set_index('Date', inplace=True)
    dates = stock_data.index.strftime('%Y-%m-%d')
    prices = stock_data['Close']
    dates_json = json.dumps(list(dates))
    prices_json = json.dumps(list(prices))
    # Pass data to the template
    context = {'symbol': symbol, 'dates_json': dates_json, 'prices_json': prices_json, 'form': form, 'days': days}
    return render(request, 'users/stock_graph_symbol.html', context)




from django.shortcuts import render,Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Item, Customer
from django.contrib.auth import authenticate, login, logout

def item_list(request):
    if request.user.is_authenticated:
        items = Item.objects.filter(customer=request.user.customer)
        # Check if this is the user's first login
        first_login = request.session.get('first_login', False)
        if first_login:
            request.session['first_login'] = False
            message = "Welcome! Start by adding your first item."
        else:
            message = None
    else:
        items = Item.objects.none()
        message = None
    return render(request, 'item_list.html', {
        'items': items,
        'message': message
    })

@login_required
def item_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        Item.objects.create(
            name=name, 
            description=description,
            customer=request.user.customer  # Always assign to current user
        )
        return redirect('item_list')
    return render(request, 'item_form.html')

@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk, customer=request.user.customer)  # Added ownership check
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.save()
        return redirect('item_list')
    return render(request, 'item_form.html', {'item': item})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk, customer=request.user.customer)  # Added ownership check
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'item_confirm_delete.html', {'item': item})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                return render(request, 'register.html', {'error': 'Username already exists'})
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                customer = Customer.objects.create(user=user)
                login(request, user)
                request.session['first_login'] = True  # This line sets the first login flag
                return redirect('item_list')
        else:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('item_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('item_list')

@login_required
def profile(request):
    customer = request.user.customer
    if request.method == 'POST':
        customer.user.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        customer.user.save()
        customer.save()
        return redirect('profile')
    return render(request, 'profile.html', {'customer': customer})
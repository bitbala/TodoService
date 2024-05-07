from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TodoItem
from django.contrib import messages
import requests
from django.utils.encoding import force_str

@login_required
def todo_list(request):
    todos = TodoItem.objects.filter(user=request.user)
    return render(request, 'todo_list.html', {'todos': todos})

@login_required
def todo_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        TodoItem.objects.create(user=request.user, title=title)
        messages.success(request, 'Todo item created successfully.')
        message = f"Hi, New to-do item {title} added."

        send_email(force_str(request.user), "New To-Do inserted", message)
        return redirect('todo_list')
    return render(request, 'todo_create.html')

def send_email(user_email, subject, message):
    # Set up the data for the POST request
    email_data = {
        "from_email": "todo-app-admin@todoapp.com",
        "to_email": user_email,
        "subject": subject,
        "message": message
    }
    # URL of the external service to send email
    url = 'http://127.0.0.1:8001/send-email/'
    try:
        print (email_data)
        response = requests.post(url, json=email_data)
        response.raise_for_status()
    except requests.RequestException as e:
        # Handle error, log it, etc.
        print(f"Failed to send email: {str(e)}")


@login_required
def todo_detail(request, todo_id):
    todo = get_object_or_404(TodoItem, id=todo_id, user=request.user)
    return render(request, 'todo_detail.html', {'todo': todo})

@login_required
def todo_update(request, todo_id):
    todo = get_object_or_404(TodoItem, id=todo_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        todo.title = title
        todo.save()
        messages.success(request, 'Todo item updated successfully.')
        return redirect('todo_list')
    return render(request, 'todo_update.html', {'todo': todo})

@login_required
def todo_delete(request, todo_id):
    todo = get_object_or_404(TodoItem, id=todo_id, user=request.user)
    if request.method == 'POST':
        title = todo.title
        todo.delete()
        messages.success(request, 'Todo item deleted successfully.')

        message = f"Todo item: {title} deleted successfully."
        send_email(force_str(request.user), "To-Do Deleted", message)
        return redirect('todo_list')
    return render(request, 'todo_delete.html', {'todo': todo})


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('todo_list')  # Redirect to todo list page after successful login
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
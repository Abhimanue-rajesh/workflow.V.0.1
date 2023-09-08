import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .models import *

#TODO need to add security features to all the views 

# Create your views here.
def login_page(request):
    if request.method == 'POST':
        login_data = request.POST

        username = login_data.get('username')
        password = login_data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                # Redirect manager to a different page.
                return redirect('manager_dashboard')
            else:
                # Redirect staff to a different page.
                return redirect('profile_staff')
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect('login_page')

    return render(request, 'login.html', {'page_title': 'Login Workflow'})


def logout_all(request):
    logout(request)
    return redirect('login_page')


def manager_dashboard(request):
    # Query completed tasks pending review
    staff_count = Staff.objects.count()
    task_count = Task.objects.count()
    pending_tasks_count = Task.objects.filter(status='Pending').count()
    review_count = Task.objects.filter(
        status='Waiting for Confirmation').count()

    completed_tasks = SelectedTask.objects.filter(
        completed=True, reviewed_by=None)
    print(completed_tasks)
    context = {
        'page_title': 'Manager Dashboard',
        'completed_tasks': completed_tasks,
        'staff_count': staff_count,
        'task_count': task_count,
        'pending_tasks_count': pending_tasks_count,
        'review_count': review_count,
    }
    return render(request, 'manager/manager_dashboard.html', context)


def add_staff(request):
    if request.method == 'POST':
        # Retrieve form data from the request
        username = request.POST['username']
        password = request.POST['password']
        conform_password = request.POST['conform_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']

        # Check if a user with the same username or email already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Username or email already exists.")
            return render(request, 'staff/add_staff.html')

        # check if the password and conform passwords are same
        if password != conform_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'staff/add_staff.html')

        # Create a new user and set the password (no need to hash it manually)
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # Create a new Staff instance and save it to the database
        Staff.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number
        )

        # Redirect to a success page or staff list page
        messages.info(request, "Staff has been added successfully")
        return redirect('manager_dashboard')

    context = {
        'page_title': 'Add Staff'
    }

    return render(request, 'staff/add_staff.html', context)


def view_staffs(request):
    # get all staff data from the database
    all_staff_data = Staff.objects.all()

    context = {
        'page_title': 'View Staffs',
        'all_staff_data': all_staff_data,

    }
    return render(request, 'staff/view_staffs.html', context)


def update_staff(request, id):
    # Get the object with the given ID
    staff = get_object_or_404(Staff, id=id)  # staff data before updating

    if request.method == 'POST':
        update_staff_data = request.POST

        new_username = update_staff_data.get('username')
        first_name = update_staff_data.get('first_name')
        last_name = update_staff_data.get('last_name')
        email = update_staff_data.get('email')
        phone_number = update_staff_data.get('phone_number')

        # Check if a user with the same email already exists
        if User.objects.filter(email=email).exclude(username=staff.user.username).exists():
            messages.error(request, "Email already exists.")
        else:
            # Check if the new username is different from the current one
            if new_username != staff.user.username:
                # Check if a user with the same username already exists
                if User.objects.filter(username=new_username).exists():
                    messages.error(request, "Username already exists.")
                else:
                    # Update the username
                    staff.user.username = new_username

            # Update other staff fields
            staff.user.first_name = first_name
            staff.user.last_name = last_name
            staff.user.email = email
            staff.first_name = first_name
            staff.last_name = last_name
            staff.email = email
            staff.phone_number = phone_number

            # Save the user and staff instances
            staff.user.save()
            staff.save()

            messages.success(request, "Staff details updated successfully")

            return redirect('view_staffs')

    context = {
        'page_title': 'Update Staff Details',
        'staff': staff,
    }
    return render(request, 'staff/update_staff.html', context)


def remove_staff(request, id):
    staff = get_object_or_404(Staff, id=id)
    # this will also delete the user associated with the staff
    staff.delete()
    return redirect('view_staffs')


def profile_staff(request):
    staff = Staff.objects.get(user=request.user)
    selected_tasks = SelectedTask.objects.filter(staff=staff)
    total_points = staff.total_selected_task_points()

    context = {
        'page_title': 'My Profile',
        'staff': staff,
        'selected_tasks': selected_tasks,
        'total_points':total_points,
    }
    return render(request, 'staff/staff_profile.html', context)


def add_task(request):
    if request.method == 'POST':
        task_data = request.POST

        title = task_data.get('title')

        # Check if a task with the same title already exists
        if Task.objects.filter(title=title).exists():
            messages.error(
                request, "A task with the same title already exists.")
        else:
            description = task_data.get('description')
            # Get the due_date as a string
            due_date_str = task_data.get('due_date')
            priority = task_data.get('priority')
            status = task_data.get('status')

            try:
                # Parse the due_date string into a datetime object
                due_date = datetime.strptime(
                    due_date_str, '%Y-%m-%d').date()  # Extract the date part

                # Get the current date without the time
                current_date = timezone.now().date()

                # Check if the due date is in the past
                if due_date < current_date:
                    messages.error(
                        request, "The due date cannot be in the past.")
                else:
                    new_task = Task(
                        title=title,
                        description=description,
                        due_date=due_date,
                        priority=priority,
                        status=status,
                    )
                    new_task.save()
                    messages.success(request, "Task added successfully")
                    return redirect('view_tasks')
            except ValueError:
                messages.error(
                    request, "Invalid date format for due date. Use YYYY-MM-DD format.")

    context = {
        'page_title': 'Add Task',
    }
    return render(request, 'task/add_task.html', context)


def view_tasks(request):
    tasks = Task.objects.all()

    if request.GET.get('search'):
        search_query = request.GET.get('search')
        tasks = tasks.filter(
            title__icontains=search_query)

    context = {
        'page_title': 'View Task',
        'tasks': tasks,
    }
    return render(request, 'task/view_tasks.html', context)


def update_task(request, id):
    task = get_object_or_404(Task, id=id)

    if request.method == 'POST':
        update_task_data = request.POST

        title = update_task_data.get('title')
        description = update_task_data.get('description')
        due_date = update_task_data.get('due_date')
        priority = update_task_data.get('priority')
        status = update_task_data.get('status')

        # Check if the updated title is different from the existing title
        if title != task.title:
            # Check if a task with the same title already exists
            if Task.objects.filter(title=title).exists():
                # Task with the same title already exists; handle this case as needed
                messages.error(
                    request, "A task with the same title already exists.")
            else:
                # The title is different, update it
                task.title = title

        # Check if the due date is in the past
        current_date = timezone.now().date()
        due_date = timezone.datetime.strptime(due_date, '%Y-%m-%d').date()
        if due_date < current_date:
            # Due date is in the past; handle this case as needed (e.g., show an error message)
            # You can use Django's messages framework to display an error message.
            messages.error(request, "The due date cannot be in the past.")
        else:
            # Update other task fields
            task.description = description
            task.due_date = due_date
            task.priority = priority
            task.status = status

            task.save()
            return redirect('view_tasks')

    context = {
        'page_title': 'Update Task',
        'task': task,
    }
    return render(request, 'task/update_task.html', context)


def remove_task(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    return redirect('view_tasks')


def select_task_staff(request, id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=id)

        # Ensure the task is not already selected by the staff
        if not SelectedTask.objects.filter(staff=request.user.staff, task=task).exists():
            selected_task = SelectedTask(staff=request.user.staff, task=task)
            selected_task.save()
            messages.success(request, "Task selected successfully.")
        else:
            messages.warning(request, "Task is already selected.")

    return redirect('view_tasks')


def remove_task_staff(request, id):
    staff = request.user.staff
    selected_task = get_object_or_404(SelectedTask, staff=staff, task_id=id)
    selected_task.delete()
    return redirect('profile_staff')


def mark_completed(request, id):
    try:
        staff = request.user.staff
        selected_task = get_object_or_404(SelectedTask, staff=staff, task_id=id)
        selected_task.completed = True
        selected_task.save()

        # Notify the manager that a task has been marked as completed
        manager_message = f"Task '{selected_task.task.title}' has been marked as completed by {selected_task.staff.user.username}."
        messages.success(request, manager_message)

    except ObjectDoesNotExist:
        # Handle the case when the SelectedTask with the provided id doesn't exist
        messages.error(request, "SelectedTask not found.")

    return redirect('profile_staff')

def mark_task_completed(request, id):
    try:
        task = Task.objects.get(id=id)
        selected_task = SelectedTask.objects.get(id=id)

        # Check if the task has not been reviewed already
        if selected_task.reviewed_by is None:
            task.status = 'completed'
            # Assign the manager who reviewed the task
            selected_task.reviewed_by = request.user
            task.save()
            selected_task.save()
            messages.success(
                request, f'Task "{task.title}" marked as completed.')
        else:
            messages.warning(
                request, f'Task "{task.title}" has already been reviewed.')

    except Task.DoesNotExist:
        messages.error(request, 'Task not found.')

    return redirect('manager_dashboard')

def organizational_dashboard(request):
    staff_members = Staff.objects.all()
    staff_scores = {
        'labels': [],  # List of staff names
        'data': [],    # List of staff scores
    }

    for staff in staff_members:
        total_points = staff.total_selected_task_points()
        staff_scores['labels'].append(staff.user.get_full_name()) 
        staff_scores['data'].append(total_points)

    context = {
        'page_title': 'Organizational Dashboard',
        'staff_scores': staff_scores,
    }
    return render(request, 'organizational_dashboard.html', context)


def leads(request):
    all_lead_data = Lead.objects.all()
    
    if request.GET.get('search'):
        search_query = request.GET.get('search')
        all_lead_data = all_lead_data.filter(customer_name__icontains=search_query)
        
    context = {
        'page_title': 'Lead',
        'leads': all_lead_data,
    }
    return render(request, 'leads/view_leads.html',context)

def add_lead(request):
    if request.method == 'POST':
        # Retrieve form data from the request
        lead_name = request.POST['lead_name']
        lead_contact = request.POST['lead_contact']
        lead_source = request.POST['lead_source']
        lead_location = request.POST['lead_location']
        interest = request.POST['interest']

        # Validate the phone number using regular expression
        if not re.match(r'^\d{10}$', lead_contact):
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return redirect('add_lead')

        # Check if a lead with the same name and location already exists
        existing_lead = Lead.objects.filter(customer_name=lead_name, customer_location=lead_location).first()
        if existing_lead:
            messages.error(request, "A lead with the same name and location already exists.")
            return redirect('add_lead')
        
        Lead.objects.create(
            customer_name =lead_name,
            contact_number = lead_contact,
            lead_source = lead_source,
            customer_location = lead_location,
            interest = interest,
        )

        messages.info(request, "Lead has been added successfully")
        return redirect('leads')
        
    context = {
        'page_title': 'Add Lead',
    }
    return render(request, 'leads/add_lead.html',context)

def update_lead(request, id):
    lead = get_object_or_404(Lead, id = id)

    if request.method == 'POST':
        update_lead_data = request.POST

        lead.customer_name = update_lead_data['lead_name']
        lead.contact_number = update_lead_data['lead_contact']
        lead.lead_source = update_lead_data['lead_source']
        lead.customer_location = update_lead_data['lead_location']
        lead.interest = update_lead_data['interest']
        
        # Validate the phone number using regular expression
        if not re.match(r'^\d{10}$', lead.contact_number):
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return redirect('update_lead', id=id)

        # Check for duplicate lead
        existing_lead = Lead.objects.exclude(id=id).filter(customer_name=lead.customer_name, customer_location=lead.customer_location).first()
        if existing_lead:
            messages.error(request, "A lead with the same name and location already exists.")
            return redirect('update_lead', id=id)
        
        lead.save()
        return redirect('leads')
    
    context = {
        'page_title': 'Update Lead',
        'lead' : lead,
    }
    return render(request, 'leads/update_lead.html',context)


def remove_lead(request, id):
    lead = get_object_or_404(Lead, id=id)
    lead.delete()
    return redirect('leads')
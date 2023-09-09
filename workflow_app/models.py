from django.contrib.auth.models import User
from django.db import models

# Define choices for Priority and Status
PRIORITY_CHOICES = (
    ('very_high', 'Very High'),
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
)

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('waiting_for_confirmation', 'Waiting for Confirmation'),
)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(default="no-email@workflow.com")
    phone_number = models.CharField(max_length=255)
    # Add other relevant staff information fields
    
    def total_selected_task_points(self):
        total_points = 0
        selected_tasks = SelectedTask.objects.filter(staff=self)
        for task in selected_tasks:
            total_points += task.task.points()
        return total_points

    def __str__(self):
        return self.user.username
    
    def delete(self, *args, **kwargs):
        # Remove the associated User instance using signals
        self.user.delete()
        super().delete(*args, **kwargs)


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(default="no-email@workflow.com")
    phone_number = models.CharField(max_length=255)
    # Add other relevant manager information fields

    def __str__(self):
        return self.user.username
    
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES,default='pending')
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()

    def points(self):
        if self.priority == 'Very High':
            return 30
        elif self.priority == 'High':
            return 10
        elif self.priority == 'Medium':
            return 5
        elif self.priority == 'Low':
            return 3
        else:
            return 0
    
    def __str__(self):
        return self.title

class AssignedTask(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date_assigned = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES)
    # You can add other fields related to the assignment here

    def __str__(self):
        return f"AssignedTask ID: {self.pk}, Staff: {self.staff.user.username}, Task: {self.task.title}, Status: {self.status}"

    
class SelectedTask(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date_selected = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False) 
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # You can add other fields related to the selection of tasks here

    def __str__(self):
        return f"SelectedTask ID: {self.pk}, Staff: {self.staff.user.username}, Task: {self.task.title}"

class Lead(models.Model):
    customer_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    interest_choices = [
        ('do_not_disturb', 'Do Not Disturb'),
        ('call_back_later', 'Call Back Later'),
        ('not_interested', 'Not Interested'),
        ('not_reachable', 'Not Reachable'),
        ('interested', 'Interested') 
    ]
    interest = models.CharField(max_length=20, choices=interest_choices)
    lead_source = models.CharField(max_length=255)
    customer_location = models.CharField(max_length=255)

    def __str__(self):
        return self.customer_name
from django.db import models
from django.contrib.auth.models import User
from account.models import *

class TicketStatus(models.Model):
    status = models.CharField(max_length=225)

    def __str__(self):
        return self.status

class TicketCategory(models.Model):
    category = models.CharField(max_length=225)

    def __str__(self):
        return self.category

class Ticket(models.Model):
    PRIORITY_CHOICES = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    )
    
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE)
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    status = models.ForeignKey(TicketStatus, on_delete=models.CASCADE)
    priority = models.CharField(max_length=225, choices=PRIORITY_CHOICES)
    due_date = models.DateField(null=True, blank=True)
    last_status_on = models.DateField(auto_now=True)
    content = models.TextField()

    def __str__(self):
        return f"Ticket #{self.id} - {self.alumni.member.user.username}"

class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    message = models.TextField()
    posted_on = models.DateField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reply to Ticket #{self.ticket.id} by {self.posted_by.username}"

class TicketAssignment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tickets')
    message = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    assigned_on = models.DateField(auto_now_add=True)
    respond_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Assignment for Ticket #{self.ticket.id} to {self.assigned_to.username}"

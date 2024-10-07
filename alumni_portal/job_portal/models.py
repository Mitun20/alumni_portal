from django.db import models
from django.contrib.auth.models import User
from account.models import *

# Job Post Model
class JobPost(models.Model):
    POST_TYPE_CHOICES = [
        ('Job', 'Job'),
        ('Internship', 'Internship'),
    ]

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    experience_level_from = models.IntegerField()
    experience_level_to = models.IntegerField()
    location = models.CharField(max_length=255)
    contact_email = models.EmailField(max_length=255)
    contact_link = models.URLField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill)
    salary_package = models.CharField(max_length=255, blank=True, null=True)
    dead_line = models.DateField()
    job_description = models.TextField()
    file = models.FileField(upload_to='job_files/', blank=True, null=True)
    post_type = models.CharField(max_length=225, choices=POST_TYPE_CHOICES)
    posted_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.job_title

# Application Model
class Application(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    mobile_number = models.CharField(max_length=25, blank=True, null=True)
    current_industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='current_industry')
    current_role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='current_role')
    total_years_of_experience = models.FloatField()
    skills = models.ManyToManyField(Skill)
    resume = models.FileField(upload_to='resumes/')
    notes_to_recruiter = models.TextField(blank=True, null=True)
    applied_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.full_name

# Business Directory Model
class BusinessDirectory(models.Model):
    business_name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(max_length=255, blank=True, null=True)
    industry_type = models.ForeignKey(Industry_Type, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    contact_email = models.EmailField(max_length=255)
    contact_number = models.CharField(max_length=25, blank=True, null=True)
    country_code = models.ForeignKey(Country, on_delete=models.CASCADE)
    are_you_part_of_management = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    listed_on = models.DateField(auto_now_add=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.business_name

# Job Comment Model
class JobComment(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"Comment by {self.comment_by.username} on {self.job.job_title}"

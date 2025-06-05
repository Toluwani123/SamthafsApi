from django.db import models

# Create your models here.

class HomePage(models.Model):
    background_image = models.ImageField(upload_to='home_page/')
    main_text = models.CharField(max_length=255)
    sub_text = models.CharField(max_length=255)


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
        ('industrial', 'Industrial'),
        ('interior', 'Interior'),
        ('exterior', 'Exterior'),
    ]
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    main_image = models.ImageField(upload_to='projects/',blank=True, null=True)
    overview = models.TextField()
    project_size = models.CharField(max_length=50)
    start_date = models.DateField()
    completion_date = models.DateField()
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    client_name = models.CharField(max_length=255)
    client_testimonial = models.TextField()
     
    def __str__(self):
        return self.title

class Challenge(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(max_length=255)
    description = models.TextField()
    solution = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.project.title}"

class TeamMember(models.Model):
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/')
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)  # For sorting members

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.full_name} - {self.role}"
    
class Phase(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases')
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return f"{self.title} - {self.project.title}"

class ProjectGallery(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='project_gallery/')



from .views import *
from django.urls import path

urlpatterns = [
    path("home/", HomePageView.as_view(), name="home"),
    path("projects/", ProjectView.as_view(), name="projects"),
    path("projects/<int:id>/", ProjectEditView.as_view(), name="project_edit"),
    path("team/", TeamMemberView.as_view(), name="team"),
    path("team/<int:id>/", TeamMemberRetrieveUpdateDestroy.as_view(), name="team_member_edit"),
    path('testimonials/', TestimonialListView.as_view(), name='testimonial-list'),
    
]

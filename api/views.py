from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import *
from rest_framework.response import Response
from .serializers import *
import json
# Create your views here.
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class HomePageView(generics.RetrieveUpdateAPIView):
    serializer_class = HomePageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self):
        return HomePage.objects.first()
    
class ProjectView(generics.ListCreateAPIView):
    """
    GET  /projects/   → list all projects (with prefetch for nested fields)
    POST /projects/   → create a new project, including phases/challenges/gallery.
    """
    queryset = Project.objects.all().prefetch_related('phases', 'gallery', 'challenges')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  

    def create(self, request, *args, **kwargs):
        print("\n--- STARTING PROJECT CREATE ---")

        # 1) Build a plain Python dict from request.data (instead of a QueryDict):
        mutable_data = {}
        for key in request.data:
            # request.data.get(key) returns the last value (as a string or file for that key)
            mutable_data[key] = request.data.get(key)

        # 2) If any nested field arrived as a JSON‐encoded string, parse it:
        for field in ['phases', 'challenges', 'gallery']:
            if field in mutable_data and isinstance(mutable_data[field], str):
                try:
                    parsed = json.loads(mutable_data[field])
                    print(f"View parsed {field}: {parsed}")

                    # If it somehow came in as [[…]] (double‐nested), unwrap one layer:
                    if (
                        isinstance(parsed, list)
                        and len(parsed) == 1
                        and isinstance(parsed[0], list)
                    ):
                        parsed = parsed[0]
                        print(f"Fixed double‐nested {field}: {parsed}")

                    mutable_data[field] = parsed

                except json.JSONDecodeError as exc:
                    return Response(
                        {"detail": f"Invalid JSON for '{field}': {exc}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # 3) Scan request.FILES for keys like "gallery[0][image]" → pull out those File objects.
        gallery_files = {}
        for key in request.FILES:
            if key.startswith('gallery[') and key.endswith('][image]'):
                try:
                    idx = int(key.split('[')[1].split(']')[0])
                    gallery_files[idx] = request.FILES[key]
                    print(f"Found gallery file at index {idx} → {key}")
                except (IndexError, ValueError):
                    pass

        # 4) Attach those files into the parsed list
        if 'gallery' in mutable_data and isinstance(mutable_data['gallery'], list):
            for idx, file_obj in gallery_files.items():
                if idx < len(mutable_data['gallery']):
                    mutable_data['gallery'][idx]['image'] = file_obj
                    print(f"Attached File to gallery[{idx}]['image']")

        # 5) Overwrite request._full_data so that DRF sees a plain dict
        request._full_data = mutable_data
        print("DATA BEING SENT TO SERIALIZER (create):", request._full_data)

        # 6) Call DRF's normal create()
        response = super().create(request, *args, **kwargs)

        # 7) (Optional) verify what got saved
        if response.status_code == status.HTTP_201_CREATED:
            new_id = response.data.get('id')
            try:
                project = Project.objects.get(id=new_id)
                print("After create → phases:", list(project.phases.values('title','description','order')))
                print("After create → challenges:", list(project.challenges.values('title','description','solution')))
                print("After create → gallery:", list(project.gallery.values('image')))
            except Project.DoesNotExist:
                pass

        print("--- PROJECT CREATE COMPLETE ---\n")
        return response
class ProjectEditView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Project.objects.all().prefetch_related('phases','gallery','challenges')
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    parser_classes   = [MultiPartParser, FormParser, JSONParser]  
    lookup_field     = 'id'

    def update(self, request, *args, **kwargs):
        print("\n--- STARTING PROJECT UPDATE ---")

        # 1) Build a true Python dict from request.data (instead of a QueryDict)
        mutable_data = {}
        for key in request.data:
            # request.data.get(key) will always give you the “last” value (a string)
            mutable_data[key] = request.data.get(key)

        # 2) Parse each nested‐JSON field (phases, challenges, gallery) if it’s a string
        for field in ['phases', 'challenges', 'gallery']:
            if field in mutable_data and isinstance(mutable_data[field], str):
                try:
                    parsed = json.loads(mutable_data[field])
                    print(f"View parsed {field}: {parsed}")

                    # If it ends up double‐nested ([[…]]), unwrap one layer:
                    if isinstance(parsed, list) and len(parsed)==1 and isinstance(parsed[0], list):
                        parsed = parsed[0]
                        print(f"Fixed double‐nested {field}: {parsed}")

                    mutable_data[field] = parsed   # now a plain Python list of dicts

                except json.JSONDecodeError as e:
                    return Response(
                        {"error": f"Invalid JSON for '{field}': {e}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # 3) Handle gallery files exactly as before:
        gallery_files = {}
        for key in list(request.FILES.keys()):
            # Expect keys like "gallery[0][image]", "gallery[1][image]", etc.
            if key.startswith('gallery[') and key.endswith('][image]'):
                idx = int(key.split('[')[1].split(']')[0])
                gallery_files[idx] = request.FILES[key]
                print(f"Found gallery file at index {idx} -> {key}")

        if 'gallery' in mutable_data and isinstance(mutable_data['gallery'], list):
            for idx, file_obj in gallery_files.items():
                if idx < len(mutable_data['gallery']):
                    mutable_data['gallery'][idx]['image'] = file_obj
                    print(f"Attached File to gallery[{idx}]['image']")

        # 4) Replace the entire request data with our new plain‐dict
        request._full_data = mutable_data

        # 5) Show exactly what DRF will see:
        print("DATA BEING SENT TO SERIALIZER:", request._full_data)

        # 6) Call the normal update() now that request._full_data is a true dict
        response = super().update(request, *args, **kwargs)

        # 7) Debug: verify the nested objects were recreated
        project = self.get_object()
        print("After update – phases:",     list(project.phases.values('title','description','order')))
        print("After update – challenges:", list(project.challenges.values('title','description','solution')))
        print("After update – gallery:",    list(map(lambda g: {'image':g.image.name}, project.gallery.all())))

        print("--- PROJECT UPDATE COMPLETE ---\n")
        return response


class TeamMemberView(generics.ListCreateAPIView):
    queryset = TeamMember.objects.all().order_by('order')
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TeamMemberRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'
    parser_classes = [MultiPartParser, FormParser]
    def update(self, request, *args, **kwargs):
        print("\n--- STARTING TEAM MEMBER UPDATE ---")
        kwargs['partial'] = True
        response = super().update(request, *args, **kwargs)
        print("--- TEAM MEMBER UPDATE COMPLETE ---\n")
        return response

class TestimonialListView(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Project.objects.exclude(client_testimonial='') \
                             .order_by('-completion_date')[:4]
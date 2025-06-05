from django.contrib.auth.models import User
from rest_framework import serializers, status
from .models import *
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'

class PhaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Phase
        fields = ['title', 'description', 'order']
    
class ProjectGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = ProjectGallery
        fields = ['image']
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True},
        }
class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'solution']

    
    
import json

class ProjectSerializer(serializers.ModelSerializer):
    phases = PhaseSerializer(many=True, required=False)
    gallery = ProjectGallerySerializer(many=True, required=False)
    challenges = ChallengeSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        phases_data = validated_data.pop('phases', [])
        gallery_data = validated_data.pop('gallery', [])
        challenge_data = validated_data.pop('challenges', [])
        project = Project.objects.create(**validated_data)
        
        for phase_data in phases_data:
            Phase.objects.create(project=project, **phase_data)
        
        for gallery_data in gallery_data:
            ProjectGallery.objects.create(project=project, **gallery_data)

        for challenge_data in challenge_data:
            Challenge.objects.create(project=project, **challenge_data)
        
        return project

    def update(self, instance, validated_data):
        print("VALIDATED DATA IN UPDATE:", validated_data)

        # 1) Update all non-nested fields:
        for attr, value in validated_data.items():
            if attr not in ('phases', 'gallery', 'challenges'):
                setattr(instance, attr, value)
        instance.save()

        # 2) Replace nested phases if provided
        if 'phases' in validated_data:
            print("Updating phases:", validated_data['phases'])
            instance.phases.all().delete()
            for pd in validated_data['phases']:
                Phase.objects.create(project=instance, **pd)

        # 3) Replace nested challenges if provided
        if 'challenges' in validated_data:
            print("Updating challenges:", validated_data['challenges'])
            instance.challenges.all().delete()
            for cd in validated_data['challenges']:
                Challenge.objects.create(project=instance, **cd)

        # 4) Replace nested gallery if provided
        if 'gallery' in validated_data:
            print("Updating gallery:", validated_data['gallery'])

            # a) Pull out the existing image files in positional order
            existing_images = [g.image for g in instance.gallery.all().order_by('id')]

            # b) Delete everything (we’ll recreate below)
            instance.gallery.all().delete()

            # c) Now loop through the submitted list by index
            for idx, gd in enumerate(validated_data['gallery']):
                # If the front‐end did NOT attach a new 'image', re‐use the old one at the same index:
                if not gd.get('image') and idx < len(existing_images):
                    ProjectGallery.objects.create(
                        project=instance,
                        image=existing_images[idx]
                    )
                else:
                    # Either a brand‐new File was provided, or no existing slot existed:
                    ProjectGallery.objects.create(project=instance, **gd)
        return instance


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('client_name', 'client_testimonial', 'completion_date')

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'full_name', 'role', 'image', 'description', 'order']
        extra_kwargs = {
            'id': {'read_only': True},
            'order': {'required': False}
        }
    def create(self, validated_data):
        team_member = TeamMember.objects.create(**validated_data)
        return team_member
    




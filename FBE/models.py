from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.conf import settings
from .models import Candidate, Category, Vote
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

def index(request):
    categories = Category.objects.prefetch_related('candidate_set').all()
    return render(request, 'voting/index.html', {'categories': categories})

@csrf_exempt
def process_vote(request, candidate_id):
    if request.method == 'POST':
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)
        
        # Simulate payment processing (replace with actual Mobile Money API)
        # In production, verify payment before recording vote
        transaction_id = f"VOTE-{uuid.uuid4().hex[:10].upper()}"
        
        # Record vote
        Vote.objects.create(
            candidate=candidate,
            phone_number=phone_number,
            transaction_id=transaction_id
        )
        
        return JsonResponse({
            'status': 'success',
            'transaction_id': transaction_id,
            'total_votes': candidate.total_votes()
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def live_results(request):
    candidates = Candidate.objects.all()
    results = {
        candidate.id: {
            'name': candidate.name,
            'votes': candidate.total_votes(),
            'revenue': candidate.total_revenue()
        } for candidate in candidates
    }
    return JsonResponse(results)

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidates/')
    bio = models.TextField()
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def total_votes(self):
        return self.vote_set.count()
    
    def total_revenue(self):
        # Consider moving 0.70 to a constant or settings
        REVENUE_MULTIPLIER = 0.70
        return self.vote_set.count() * REVENUE_MULTIPLIER

class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
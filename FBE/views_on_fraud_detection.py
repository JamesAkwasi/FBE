from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .models import Candidate, Vote
from .payments import MTNMobileMoney
from .fraud_detection import FraudDetector
import uuid
import json
from datetime import datetime

@csrf_exempt
def process_vote(request, candidate_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)
    
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        
        # Initialize fraud detection
        fraud_detector = FraudDetector()
        
        # Validate phone number
        if not fraud_detector.validate_phone_number(phone_number):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid Ghanaian mobile money number'
            }, status=400)
        
        # Check rate limits
        if not fraud_detector.check_rate_limit(phone_number):
            return JsonResponse({
                'status': 'error',
                'message': 'Voting too frequently. Please wait a minute.'
            }, status=429)
        
        # Check device fingerprint
        if not fraud_detector.check_device_fingerprint(request):
            return JsonResponse({
                'status': 'error',
                'message': 'Suspicious activity detected'
            }, status=403)
        
        # Check transaction velocity
        if not fraud_detector.check_transaction_velocity(phone_number):
            return JsonResponse({
                'status': 'error',
                'message': 'Maximum votes reached. Try again later.'
            }, status=429)
        
        # Process payment
        reference = f"VOTE-{uuid.uuid4().hex[:10].upper()}"
        momo = MTNMobileMoney()
        
        try:
            payment_result = momo.process_payment(
                phone_number=phone_number,
                amount=0.70,
                reference=reference
            )
            
            if payment_result.get('status') != 'SUCCESSFUL':
                raise Exception("Payment not successful")
            
            # Record vote
            Vote.objects.create(
                candidate=candidate,
                phone_number=phone_number,
                transaction_id=reference
            )
            
            return JsonResponse({
                'status': 'success',
                'transaction_id': reference,
                'total_votes': candidate.total_votes()
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Payment failed: {str(e)}'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing vote: {str(e)}'
        }, status=500)
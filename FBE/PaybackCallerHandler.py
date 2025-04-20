def momo_callback(request):
    """Handle MTN Mobile Money payment notifications"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reference = data.get('externalId')
            status = data.get('status')
            
            if status == 'SUCCESSFUL':
                # Verify the vote was recorded
                vote = Vote.objects.get(transaction_id=reference)
                vote.payment_confirmed = True
                vote.save()
                
            return JsonResponse({'status': 'received'})
            
        except Exception as e:
            return JsonResponse({'status': 'error'}, status=400)
    
    return JsonResponse({'status': 'invalid method'}, status=405
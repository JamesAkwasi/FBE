import requests
import base64
from datetime import datetime
import uuid
import hashlib
from django.conf import settings

class MTNMobileMoney:
    def _init_(self):
        self.api_key = settings.MOMO_API_KEY
        self.user_id = settings.MOMO_USER_ID
        self.primary_key = settings.MOMO_PRIMARY_KEY
        self.callback_url = settings.MOMO_CALLBACK_URL
        self.environment = settings.MOMO_ENVIRONMENT
        self.base_url = (
            "https://sandbox.momodeveloper.mtn.com" 
            if self.environment == "sandbox" 
            else "https://api.mtn.com"
        )

    def _get_auth_token(self):
        """Generate OAuth2 token for API access"""
        auth_string = f"{self.user_id}:{self.primary_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        
        response = requests.post(
            f"{self.base_url}/collection/token/",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        raise Exception("Failed to get auth token")

    def process_payment(self, phone_number, amount, reference):
        """Process mobile money payment"""
        token = self._get_auth_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Reference-Id': reference,
            'X-Target-Environment': self.environment,
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        
        payload = {
            "amount": str(amount),
            "currency": "GHS",
            "externalId": reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": "Beauty Pageant Voting",
            "payeeNote": f"Vote payment {reference}"
        }
        
        # First create payment request
        response = requests.post(
            f"{self.base_url}/collection/v1_0/requesttopay",
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 202]:
            # Check payment status
            status_response = requests.get(
                f"{self.base_url}/collection/v1_0/requesttopay/{reference}",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Ocp-Apim-Subscription-Key': self.api_key
                }
            )
            
            if status_response.status_code == 200:
                return status_response.json()
        
        raise Exception("Payment processing failed")
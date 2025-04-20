from django.core.cache import cache
from django.conf import settings
import re
from datetime import datetime, timedelta

class FraudDetector:
    def _init_(self):
        self.rate_limit = getattr(settings, 'FRAUD_RATE_LIMIT', 5)  # Max votes per minute
        self.phone_pattern = re.compile(r'^(0|\+233)[2-9]\d{8}$')
        self.min_vote_interval = timedelta(seconds=30)  # Minimum time between votes

    def validate_phone_number(self, phone_number):
        """Validate Ghanaian mobile money number format"""
        return bool(self.phone_pattern.match(phone_number))

    def check_rate_limit(self, phone_number):
        """Check if phone number is voting too frequently"""
        cache_key = f"vote_limit_{phone_number}"
        vote_count = cache.get(cache_key, 0)
        
        if vote_count >= self.rate_limit:
            return False
        
        cache.set(cache_key, vote_count + 1, timeout=60)
        return True

    def check_device_fingerprint(self, request):
        """Analyze device fingerprint for suspicious patterns"""
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check for suspicious IP patterns (example)
        if ip_address in getattr(settings, 'BLACKLISTED_IPS', []):
            return False
            
        # Check for bots/spoofed user agents
        if any(bot in user_agent.lower() for bot in ['bot', 'spider', 'curl', 'wget']):
            return False
            
        return True

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def check_transaction_velocity(self, phone_number):
        """Check for unusually high voting velocity"""
        from .models import Vote
        last_hour = datetime.now() - timedelta(hours=1)
        recent_votes = Vote.objects.filter(
            phone_number=phone_number,
            created_at__gte=last_hour
        ).count()
        
        return recent_votes < getattr(settings, 'MAX_HOURLY_VOTES', 20)
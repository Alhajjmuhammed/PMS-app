"""
Health check views for monitoring and operational status
"""
from django.http import JsonResponse
from django.db import connection
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
import time
import os


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """
    Basic health check endpoint for load balancers and monitoring
    """
    
    def get(self, request):
        """Return basic health status"""
        return JsonResponse({
            'status': 'healthy',
            'timestamp': int(time.time()),
            'service': 'hotel-pms-api'
        })


@method_decorator(csrf_exempt, name='dispatch') 
class DetailedHealthCheckView(View):
    """
    Detailed health check with database and service status
    """
    
    def get(self, request):
        """Return detailed health status including database connectivity"""
        health_data = {
            'status': 'healthy',
            'timestamp': int(time.time()),
            'service': 'hotel-pms-api',
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'checks': {}
        }
        
        # Database connectivity check
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                if result[0] == 1:
                    health_data['checks']['database'] = 'healthy'
                else:
                    health_data['checks']['database'] = 'unhealthy'
                    health_data['status'] = 'degraded'
        except Exception as e:
            health_data['checks']['database'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'unhealthy'
        
        # Check critical models
        try:
            from apps.rooms.models import Room
            from apps.properties.models import Property
            
            room_count = Room.objects.count()
            property_count = Property.objects.count()
            
            health_data['checks']['data'] = {
                'rooms': room_count,
                'properties': property_count,
                'status': 'healthy' if room_count > 0 and property_count > 0 else 'warning'
            }
        except Exception as e:
            health_data['checks']['data'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'
        
        # Return appropriate HTTP status
        status_code = 200
        if health_data['status'] == 'unhealthy':
            status_code = 503
        elif health_data['status'] == 'degraded':
            status_code = 200  # Still healthy but with warnings
            
        return JsonResponse(health_data, status=status_code)


@method_decorator([csrf_exempt, cache_page(60)], name='dispatch')
class ReadinessCheckView(View):
    """
    Readiness check for Kubernetes/container orchestration
    """
    
    def get(self, request):
        """Check if the service is ready to handle requests"""
        try:
            # Check database connectivity
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            
            # Check if migrations are up to date
            from django.core.management import execute_from_command_line
            from django.db import transaction
            
            return JsonResponse({
                'status': 'ready',
                'timestamp': int(time.time())
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'not_ready',
                'timestamp': int(time.time()),
                'error': str(e)
            }, status=503)


@method_decorator([csrf_exempt, cache_page(30)], name='dispatch')
class LivenessCheckView(View):
    """
    Liveness check for container orchestration
    """
    
    def get(self, request):
        """Simple liveness check"""
        return JsonResponse({
            'status': 'alive',
            'timestamp': int(time.time())
        })
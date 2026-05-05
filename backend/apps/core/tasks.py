"""
Core Celery tasks for Hotel PMS.
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Sum, Count, F, Q
from datetime import timedelta, date
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list, html_message=None):
    """
    Send email asynchronously.
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_list: List of recipient emails
        html_message: Optional HTML version
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent: {subject} to {recipient_list}")
        return f"Email sent successfully to {len(recipient_list)} recipients"
    
    except Exception as exc:
        logger.error(f"Email send failed: {subject} - {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_bulk_email_task(subject, message, recipient_list, html_message=None):
    """Send bulk emails asynchronously."""
    success_count = 0
    failed_recipients = []
    
    for recipient in recipient_list:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            failed_recipients.append(recipient)
    
    return {
        'success_count': success_count,
        'failed_count': len(failed_recipients),
        'failed_recipients': failed_recipients,
    }


@shared_task
def cleanup_expired_tokens():
    """Clean up expired authentication tokens."""
    from rest_framework.authtoken.models import Token
    from django.conf import settings
    
    expiration_hours = getattr(settings, 'TOKEN_EXPIRATION_HOURS', 24)
    expiration_time = timezone.now() - timedelta(hours=expiration_hours)
    
    expired_tokens = Token.objects.filter(created__lt=expiration_time)
    count = expired_tokens.count()
    expired_tokens.delete()
    
    logger.info(f"Cleaned up {count} expired tokens")
    return f"Deleted {count} expired tokens"


@shared_task
def cleanup_old_activity_logs(days=90):
    """Clean up activity logs older than specified days."""
    from apps.accounts.models import ActivityLog
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_logs = ActivityLog.objects.filter(timestamp__lt=cutoff_date)
    count = old_logs.count()
    old_logs.delete()
    
    logger.info(f"Cleaned up {count} old activity logs (older than {days} days)")
    return f"Deleted {count} old activity logs"


@shared_task
def generate_night_audit_task(property_id=None):
    """
    Generate night audit for properties.
    
    Runs nightly to:
    - Close business day
    - Generate reports
    - Update room rates
    - Process no-shows
    """
    from apps.properties.models import Property
    from apps.reports.models import NightAudit, DailyStatistics
    from apps.reservations.models import Reservation
    from apps.rooms.models import Room
    
    audit_date = date.today()
    properties = Property.objects.filter(is_active=True)
    
    if property_id:
        properties = properties.filter(id=property_id)
    
    results = []
    
    for prop in properties:
        try:
            # Check if audit already exists
            if NightAudit.objects.filter(property=prop, audit_date=audit_date).exists():
                logger.warning(f"Night audit already exists for {prop.name} on {audit_date}")
                continue
            
            # Get statistics
            total_rooms = Room.objects.filter(hotel=prop).count()
            occupied_rooms = Reservation.objects.filter(
                hotel=prop,
                check_in_date__lte=audit_date,
                check_out_date__gt=audit_date,
                status='CHECKED_IN'
            ).count()
            
            arrivals = Reservation.objects.filter(
                hotel=prop,
                check_in_date=audit_date,
                status__in=['CONFIRMED', 'CHECKED_IN']
            ).count()
            
            departures = Reservation.objects.filter(
                hotel=prop,
                check_out_date=audit_date,
                status__in=['CHECKED_IN', 'CHECKED_OUT']
            ).count()
            
            revenue = Reservation.objects.filter(
                hotel=prop,
                check_in_date__lte=audit_date,
                check_out_date__gt=audit_date,
                status='CHECKED_IN'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Create night audit
            audit = NightAudit.objects.create(
                property=prop,
                audit_date=audit_date,
                total_rooms=total_rooms,
                occupied_rooms=occupied_rooms,
                available_rooms=total_rooms - occupied_rooms,
                arrivals=arrivals,
                departures=departures,
                revenue=revenue,
                occupancy_rate=(occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0,
                status='COMPLETED',
                completed_at=timezone.now(),
            )
            
            # Create daily statistics
            DailyStatistics.objects.create(
                property=prop,
                date=audit_date,
                total_rooms=total_rooms,
                occupied_rooms=occupied_rooms,
                available_rooms=total_rooms - occupied_rooms,
                occupancy_rate=audit.occupancy_rate,
                revenue=revenue,
                arrivals=arrivals,
                departures=departures,
            )
            
            # Process no-shows
            no_shows = Reservation.objects.filter(
                hotel=prop,
                check_in_date=audit_date,
                status='CONFIRMED'
            )
            no_show_count = no_shows.update(status='NO_SHOW')
            
            audit.notes = f"Processed {no_show_count} no-shows"
            audit.save()
            
            results.append({
                'property': prop.name,
                'status': 'success',
                'occupancy': audit.occupancy_rate,
                'revenue': float(revenue),
            })
            
            logger.info(f"Night audit completed for {prop.name}")
        
        except Exception as e:
            logger.error(f"Night audit failed for {prop.name}: {str(e)}")
            results.append({
                'property': prop.name,
                'status': 'failed',
                'error': str(e),
            })
    
    return results


@shared_task
def send_reservation_reminder_task():
    """Send reminder emails for upcoming check-ins."""
    from apps.reservations.models import Reservation
    from apps.guests.models import Guest
    
    tomorrow = date.today() + timedelta(days=1)
    
    upcoming_reservations = Reservation.objects.filter(
        check_in_date=tomorrow,
        status='CONFIRMED'
    ).select_related('guest', 'hotel')
    
    sent_count = 0
    
    for reservation in upcoming_reservations:
        if reservation.guest and reservation.guest.email:
            try:
                subject = f"Reminder: Check-in Tomorrow at {reservation.hotel.name}"
                message = f"""
Dear {reservation.guest.get_full_name()},

This is a reminder that your check-in is tomorrow ({tomorrow}).

Reservation Details:
- Confirmation Number: {reservation.confirmation_code}
- Hotel: {reservation.hotel.name}
- Check-in: {reservation.check_in_date}
- Check-out: {reservation.check_out_date}
- Adults: {reservation.adults}, Children: {reservation.children}

We look forward to welcoming you!

Best regards,
{reservation.hotel.name}
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reservation.guest.email],
                    fail_silently=True,
                )
                sent_count += 1
            
            except Exception as e:
                logger.error(f"Failed to send reminder for reservation {reservation.id}: {str(e)}")
    
    logger.info(f"Sent {sent_count} reservation reminders")
    return f"Sent {sent_count} reminders"


@shared_task
def generate_daily_reports_task():
    """Generate daily reports for all properties."""
    from apps.properties.models import Property
    
    properties = Property.objects.filter(is_active=True)
    results = []
    
    for prop in properties:
        try:
            # Trigger night audit (which generates reports)
            result = generate_night_audit_task.delay(property_id=prop.id)
            results.append({'property': prop.name, 'task_id': result.id})
        except Exception as e:
            logger.error(f"Failed to schedule report for {prop.name}: {str(e)}")
    
    return results

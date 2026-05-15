"""
Core Celery tasks for Hotel PMS.
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, date
from decimal import Decimal
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
    - Post nightly room rate charges to every open guest folio
    - Process no-shows (CONFIRMED reservations that never checked in)
    - Flag overdue departures
    - Verify folio settlement for today's check-outs
    - Capture DailyStatistics snapshot (occupancy, ADR, RevPAR)
    """
    from apps.properties.models import Property
    from apps.reports.models import NightAudit, DailyStatistics
    from apps.reservations.models import Reservation
    from apps.rooms.models import Room
    from apps.billing.models import FolioCharge, ChargeCode

    audit_date = date.today()
    properties = Property.objects.filter(is_active=True)

    if property_id:
        properties = properties.filter(id=property_id)

    results = []

    for prop in properties:
        audit = None
        try:
            with transaction.atomic():
                # Skip if audit already completed for this date
                if NightAudit.objects.filter(
                    property=prop, business_date=audit_date, status='COMPLETED'
                ).exists():
                    logger.warning(f"Night audit already completed for {prop.name} on {audit_date}")
                    continue

                # Create (or re-use a stuck PENDING/IN_PROGRESS) audit record
                audit, _ = NightAudit.objects.get_or_create(
                    property=prop,
                    business_date=audit_date,
                    defaults={
                        'status': 'IN_PROGRESS',
                        'started_at': timezone.now(),
                    },
                )
                if audit.status not in ('IN_PROGRESS', 'PENDING'):
                    # Already rolled back — reset for retry
                    audit.status = 'IN_PROGRESS'
                    audit.started_at = timezone.now()
                    audit.save(update_fields=['status', 'started_at'])

                # ----------------------------------------------------------------
                # Room counts
                # ----------------------------------------------------------------
                total_rooms = Room.objects.filter(hotel=prop).count()

                occupied_reservations = Reservation.objects.filter(
                    hotel=prop,
                    check_in_date__lte=audit_date,
                    check_out_date__gt=audit_date,
                    status='CHECKED_IN',
                ).prefetch_related('rooms__room', 'rooms__room_type')

                occupied_rooms = occupied_reservations.count()

                arrivals = Reservation.objects.filter(
                    hotel=prop,
                    check_in_date=audit_date,
                    status__in=['CONFIRMED', 'CHECKED_IN'],
                ).count()

                departures = Reservation.objects.filter(
                    hotel=prop,
                    check_out_date=audit_date,
                    status__in=['CHECKED_IN', 'CHECKED_OUT'],
                ).count()

                # ----------------------------------------------------------------
                # Step 1 — Post nightly room rate charges to every open folio
                # ----------------------------------------------------------------
                room_charge_code, _ = ChargeCode.objects.get_or_create(
                    code='ROOM',
                    defaults={
                        'name': 'Room Rate',
                        'category': 'ROOM',
                        'default_amount': Decimal('0'),
                    },
                )

                room_revenue = Decimal('0')
                for reservation in occupied_reservations:
                    try:
                        folio = reservation.folio
                    except Exception:
                        # No folio attached to this reservation — skip
                        continue

                    if folio.status == 'CLOSED':
                        continue

                    for res_room in reservation.rooms.all():
                        # Idempotency guard: skip if a ROOM charge already exists
                        # for this folio on today's date
                        already_posted = FolioCharge.objects.filter(
                            folio=folio,
                            charge_code=room_charge_code,
                            charge_date=audit_date,
                        ).exists()

                        rate = res_room.rate_per_night or Decimal('0')
                        room_revenue += rate

                        if already_posted:
                            continue

                        room_label = (
                            res_room.room.room_number
                            if res_room.room
                            else (res_room.room_type.name if res_room.room_type else 'Room')
                        )
                        FolioCharge.objects.create(
                            folio=folio,
                            charge_code=room_charge_code,
                            description=f'Room rate for {audit_date} - Room {room_label}',
                            unit_price=rate,
                            quantity=1,
                            charge_date=audit_date,
                        )

                audit.room_rates_posted = True
                audit.save(update_fields=['room_rates_posted'])

                # ----------------------------------------------------------------
                # Step 2 — Flag overdue departures (checked-in past check-out date)
                # ----------------------------------------------------------------
                overdue_count = Reservation.objects.filter(
                    hotel=prop,
                    check_out_date__lt=audit_date,
                    status='CHECKED_IN',
                ).count()
                audit.departures_checked = True
                audit.save(update_fields=['departures_checked'])

                # ----------------------------------------------------------------
                # Step 3 — Process no-shows
                # ----------------------------------------------------------------
                no_show_count = Reservation.objects.filter(
                    hotel=prop,
                    check_in_date=audit_date,
                    status='CONFIRMED',
                ).update(status='NO_SHOW')
                audit.no_shows_processed = True
                audit.save(update_fields=['no_shows_processed'])

                # ----------------------------------------------------------------
                # Step 4 — Check folio settlement for today's check-outs
                # ----------------------------------------------------------------
                unsettled_count = 0
                for res in Reservation.objects.filter(
                    hotel=prop,
                    check_out_date=audit_date,
                    status='CHECKED_OUT',
                ):
                    try:
                        if res.folio.balance > 0:
                            unsettled_count += 1
                    except Exception:
                        pass
                audit.folios_settled = (unsettled_count == 0)
                audit.save(update_fields=['folios_settled'])

                # ----------------------------------------------------------------
                # Compute key metrics
                # ----------------------------------------------------------------
                occupancy_rate = (
                    Decimal(occupied_rooms) / Decimal(total_rooms) * 100
                    if total_rooms > 0
                    else Decimal('0')
                )
                adr = room_revenue / occupied_rooms if occupied_rooms > 0 else Decimal('0')
                revpar = room_revenue / total_rooms if total_rooms > 0 else Decimal('0')

                # ----------------------------------------------------------------
                # Finalise NightAudit record
                # ----------------------------------------------------------------
                notes_parts = [f"Processed {no_show_count} no-shows."]
                if overdue_count:
                    notes_parts.append(f"{overdue_count} overdue departure(s).")
                if unsettled_count:
                    notes_parts.append(f"{unsettled_count} unsettled folio(s).")

                audit.status = 'COMPLETED'
                audit.rooms_sold = occupied_rooms
                audit.arrivals_count = arrivals
                audit.departures_count = departures
                audit.room_revenue = room_revenue
                audit.total_revenue = room_revenue
                audit.completed_at = timezone.now()
                audit.notes = ' '.join(notes_parts)
                audit.save()

                # ----------------------------------------------------------------
                # Create / update DailyStatistics snapshot
                # ----------------------------------------------------------------
                DailyStatistics.objects.update_or_create(
                    property=prop,
                    date=audit_date,
                    defaults={
                        'total_rooms': total_rooms,
                        'rooms_sold': occupied_rooms,
                        'available_rooms': max(total_rooms - occupied_rooms, 0),
                        'occupancy_percent': occupancy_rate,
                        'room_revenue': room_revenue,
                        'total_revenue': room_revenue,
                        'arrivals': arrivals,
                        'departures': departures,
                        'in_house': occupied_rooms,
                        'adr': adr,
                        'revpar': revpar,
                    },
                )

                results.append({
                    'property': prop.name,
                    'status': 'success',
                    'occupancy': float(occupancy_rate),
                    'revenue': float(room_revenue),
                    'no_shows': no_show_count,
                    'overdue_departures': overdue_count,
                    'unsettled_folios': unsettled_count,
                })

                logger.info(f"Night audit completed for {prop.name}: {occupied_rooms} rooms sold, revenue {room_revenue}")

        except Exception as e:
            logger.error(f"Night audit failed for {prop.name}: {str(e)}")
            if audit is not None:
                try:
                    audit.status = 'ROLLED_BACK'
                    audit.notes = f"Failed: {str(e)}"
                    audit.save(update_fields=['status', 'notes'])
                except Exception:
                    pass
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
Dear {reservation.guest.full_name},

This is a reminder that your check-in is tomorrow ({tomorrow}).

Reservation Details:
- Confirmation Number: {reservation.confirmation_number}
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

"""
Channel Manager Integration Services
Handles rate sync, availability sync, and OTA reservation webhooks
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging
import requests
from django.db import transaction
from django.utils import timezone

from apps.channels.models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation, SyncLog
)
from apps.rates.models import RatePlan, RoomRate
from apps.rooms.models import Room, RoomType
from apps.reservations.models import Reservation, ReservationRoom
from apps.guests.models import Guest
from apps.properties.models import Property

logger = logging.getLogger(__name__)


class ChannelSyncError(Exception):
    """Custom exception for channel sync errors"""
    pass


class BaseChannelService:
    """Base service for channel integrations"""
    
    def __init__(self, property_channel: PropertyChannel):
        self.property_channel = property_channel
        self.channel = property_channel.channel
        self.property = property_channel.property
        self.api_key = self.channel.api_key
        self.api_secret = self.channel.api_secret
        self.property_code = property_channel.property_code
        self.base_url = self._get_base_url()
    
    def _get_base_url(self) -> str:
        """Get API base URL based on channel type"""
        urls = {
            'booking.com': 'https://supply-xml.booking.com/hotels/ota',
            'expedia': 'https://services.expediapartnercentral.com/eqc/ar',
            'airbnb': 'https://api.airbnb.com/v2',
            'agoda': 'https://partnerapi.agoda.com/xml',
        }
        return urls.get(self.channel.type, '')
    
    def _create_headers(self) -> Dict[str, str]:
        """Create API request headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    def _log_sync(
        self,
        sync_type: str,
        status: str,
        message: str,
        records_synced: int = 0,
        error_details: Optional[str] = None
    ):
        """Create sync log entry"""
        SyncLog.objects.create(
            channel=self.channel,
            type=sync_type,
            status=status,
            message=message,
            records_synced=records_synced,
            error_details=error_details
        )


class RateSyncService(BaseChannelService):
    """Service for syncing rates to channel managers"""
    
    def sync_rates(
        self,
        start_date: date,
        end_date: date,
        room_types: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Sync rates for specified date range and room types
        """
        try:
            # Get room types to sync
            room_type_qs = RoomType.objects.filter(property=self.property)
            if room_types:
                room_type_qs = room_type_qs.filter(id__in=room_types)
            
            total_synced = 0
            errors = []
            
            for room_type in room_type_qs:
                try:
                    # Get channel mapping for this room type
                    mapping = RoomTypeMapping.objects.filter(
                        property_channel=self.property_channel,
                        room_type=room_type
                    ).first()
                    
                    if not mapping:
                        logger.warning(f"No mapping found for {room_type.name} on {self.channel.name}")
                        continue
                    
                    # Get rates for date range
                    rates = RoomRate.objects.filter(
                        room_type=room_type,
                        date__gte=start_date,
                        date__lte=end_date
                    )
                    
                    # Build rate sync payload
                    rate_data = self._build_rate_payload(mapping, rates)
                    
                    # Send to channel API
                    response = self._push_rates(rate_data)
                    
                    # Record sync
                    for rate in rates:
                        RateUpdate.objects.update_or_create(
                            property_channel=self.property_channel,
                            room_type=room_type,
                            date=rate.date,
                            rate_plan=rate.rate_plan if hasattr(rate, 'rate_plan') else self.property_channel.rate_plan,
                            defaults={
                                'rate': rate.rate,
                                'status': 'SENT' if response.get('success') else 'FAILED',
                                'sent_at': timezone.now()
                            }
                        )
                    
                    total_synced += rates.count()
                    
                except Exception as e:
                    error_msg = f"Error syncing {room_type.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            status = 'success' if not errors else 'partial'
            self._log_sync(
                'rates',
                status,
                f'Synced {total_synced} rates',
                records_synced=total_synced,
                error_details='\n'.join(errors) if errors else None
            )
            
            return {
                'success': status == 'success',
                'total_synced': total_synced,
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Rate sync failed: {str(e)}"
            self._log_sync('rates', 'failed', error_msg, error_details=str(e))
            raise ChannelSyncError(error_msg)
    
    def _build_rate_payload(
        self,
        mapping: RoomTypeMapping,
        rates: List[RoomRate]
    ) -> Dict[str, Any]:
        """Build API payload for rate sync"""
        return {
            'property_code': self.property_code,
            'room_type_code': mapping.channel_room_type_code,
            'rates': [
                {
                    'date': rate.date.isoformat(),
                    'rate': float(rate.rate),
                    'extra_person_rate': float(rate.extra_person_rate) if rate.extra_person_rate else None,
                    'currency': 'USD',
                }
                for rate in rates
            ]
        }
    
    def _push_rates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Push rates to channel API"""
        # This is a mock implementation
        # Real implementation would use channel-specific API
        logger.info(f"Pushing rates to {self.channel.name}: {payload}")
        return {'success': True}


class AvailabilitySyncService(BaseChannelService):
    """Service for syncing availability to channel managers"""
    
    def sync_availability(
        self,
        start_date: date,
        end_date: date,
        room_types: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Sync availability for specified date range and room types
        """
        try:
            room_type_qs = RoomType.objects.filter(property=self.property)
            if room_types:
                room_type_qs = room_type_qs.filter(id__in=room_types)
            
            total_synced = 0
            errors = []
            
            for room_type in room_type_qs:
                try:
                    mapping = RoomTypeMapping.objects.filter(
                        property_channel=self.property_channel,
                        room_type=room_type
                    ).first()
                    
                    if not mapping:
                        continue
                    
                    # Calculate availability for each date
                    current_date = start_date
                    availability_data = []
                    
                    while current_date <= end_date:
                        # Count total rooms
                        total_rooms = Room.objects.filter(
                            room_type=room_type,
                            status='available'
                        ).count()
                        
                        # Count occupied/reserved rooms
                        occupied = ReservationRoom.objects.filter(
                            room__room_type=room_type,
                            reservation__check_in_date__lte=current_date,
                            reservation__check_out_date__gt=current_date,
                            reservation__status__in=['CONFIRMED', 'CHECKED_IN']
                        ).count()
                        
                        available = total_rooms - occupied
                        
                        availability_data.append({
                            'date': current_date,
                            'available': max(0, available),
                            'total': total_rooms
                        })
                        
                        # Create/update sync record
                        AvailabilityUpdate.objects.update_or_create(
                            property_channel=self.property_channel,
                            room_type=room_type,
                            date=current_date,
                            defaults={
                                'availability': available,
                                'status': 'SENT',
                                'sent_at': timezone.now()
                            }
                        )
                        
                        current_date += timedelta(days=1)
                    
                    # Push to channel
                    payload = self._build_availability_payload(mapping, availability_data)
                    response = self._push_availability(payload)
                    
                    total_synced += len(availability_data)
                    
                except Exception as e:
                    error_msg = f"Error syncing availability for {room_type.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            status = 'success' if not errors else 'partial'
            self._log_sync(
                'availability',
                status,
                f'Synced {total_synced} availability records',
                records_synced=total_synced,
                error_details='\n'.join(errors) if errors else None
            )
            
            return {
                'success': status == 'success',
                'total_synced': total_synced,
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Availability sync failed: {str(e)}"
            self._log_sync('availability', 'failed', error_msg, error_details=str(e))
            raise ChannelSyncError(error_msg)
    
    def _build_availability_payload(
        self,
        mapping: RoomTypeMapping,
        availability_data: List[Dict]
    ) -> Dict[str, Any]:
        """Build API payload for availability sync"""
        return {
            'property_code': self.property_code,
            'room_type_code': mapping.channel_room_type_code,
            'availability': [
                {
                    'date': item['date'].isoformat(),
                    'available': item['available'],
                }
                for item in availability_data
            ]
        }
    
    def _push_availability(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Push availability to channel API"""
        logger.info(f"Pushing availability to {self.channel.name}")
        return {'success': True}


class ReservationWebhookService(BaseChannelService):
    """Service for processing OTA reservation webhooks"""
    
    @transaction.atomic
    def process_reservation(self, webhook_data: Dict[str, Any]) -> Reservation:
        """
        Process incoming reservation from OTA
        """
        try:
            # Extract reservation details
            guest_data = webhook_data.get('guest', {})
            reservation_data = webhook_data.get('reservation', {})
            
            # Find or create guest
            guest = self._find_or_create_guest(guest_data)
            
            # Find room type from channel mapping
            channel_room_code = reservation_data.get('room_type_code')
            mapping = RoomTypeMapping.objects.filter(
                property_channel=self.property_channel,
                channel_room_code=channel_room_code
            ).first()
            
            if not mapping:
                raise ChannelSyncError(f"No mapping found for room code: {channel_room_code}")
            
            # Create reservation
            reservation = Reservation.objects.create(
                property=self.property,
                guest=guest,
                channel_confirmation_code=reservation_data.get('confirmation_code'),
                check_in_date=datetime.fromisoformat(reservation_data['check_in']).date(),
                check_out_date=datetime.fromisoformat(reservation_data['check_out']).date(),
                adults=reservation_data.get('adults', 1),
                children=reservation_data.get('children', 0),
                status='CONFIRMED',
                total_amount=Decimal(reservation_data.get('total_amount', 0)),
                special_requests=reservation_data.get('special_requests', ''),
            )
            
            # Assign room if available
            available_room = Room.objects.filter(
                room_type=mapping.room_type,
                status='available'
            ).first()
            
            if available_room:
                ReservationRoom.objects.create(
                    reservation=reservation,
                    room=available_room,
                    rate_per_night=Decimal(reservation_data.get('rate_per_night', 0)),
                    total_rate=Decimal(reservation_data.get('total_amount', 0)),
                    guest_name=guest.get_full_name()
                )
            
            # Record sync - create ChannelReservation record
            ChannelReservation.objects.create(
                property_channel=self.property_channel,
                reservation=reservation,
                channel_booking_id=reservation_data.get('id'),
                guest_name=guest.get_full_name(),
                check_in_date=reservation.check_in_date,
                check_out_date=reservation.check_out_date,
                room_type_code=channel_room_code,
                rate_amount=Decimal(reservation_data.get('rate_per_night', 0)),
                total_amount=reservation.total_amount,
                status='PROCESSED',
                processed_at=timezone.now(),
                raw_data=reservation_data
            )
            
            self._log_sync(
                'reservations',
                'success',
                f'Created reservation from {self.channel.name}: {reservation.confirmation_code}',
                records_synced=1
            )
            
            return reservation
            
        except Exception as e:
            error_msg = f"Failed to process reservation webhook: {str(e)}"
            self._log_sync('reservations', 'failed', error_msg, error_details=str(e))
            raise ChannelSyncError(error_msg)
    
    def _find_or_create_guest(self, guest_data: Dict[str, Any]) -> Guest:
        """Find existing guest or create new one"""
        email = guest_data.get('email')
        
        if email:
            guest = Guest.objects.filter(email=email).first()
            if guest:
                return guest
        
        # Create new guest
        return Guest.objects.create(
            first_name=guest_data.get('first_name', ''),
            last_name=guest_data.get('last_name', ''),
            email=email,
            phone=guest_data.get('phone', ''),
            country=guest_data.get('country', ''),
            address=guest_data.get('address', ''),
            city=guest_data.get('city', ''),
            postal_code=guest_data.get('postal_code', ''),
        )


def sync_channel_rates(property_channel_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    """Convenience function to sync rates for a channel"""
    property_channel = PropertyChannel.objects.get(id=property_channel_id)
    service = RateSyncService(property_channel)
    return service.sync_rates(start_date, end_date)


def sync_channel_availability(property_channel_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    """Convenience function to sync availability for a channel"""
    property_channel = PropertyChannel.objects.get(id=property_channel_id)
    service = AvailabilitySyncService(property_channel)
    return service.sync_availability(start_date, end_date)


def process_channel_webhook(property_channel_id: int, webhook_data: Dict[str, Any]) -> Reservation:
    """Convenience function to process OTA webhook"""
    property_channel = PropertyChannel.objects.get(id=property_channel_id)
    service = ReservationWebhookService(property_channel)
    return service.process_reservation(webhook_data)

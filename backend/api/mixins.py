"""
Multi-Tenancy Mixins for Views

Provides consistent property filtering across all API endpoints.
"""
from django.db.models import QuerySet


class PropertyFilterMixin:
    """
    Mixin to automatically filter querysets by user's assigned property.
    
    Usage:
        class MyView(PropertyFilterMixin, generics.ListAPIView):
            property_field = 'hotel'  # or 'property' or 'reservation__hotel'
            ...
    
    The mixin will automatically filter the queryset in get_queryset().
    Override property_field to specify the correct filter path for your model.
    """
    
    # Override this in your view class
    property_field = 'property'  # Default: direct property FK
    
    # Set to True for global master data (ChargeCode, Channel, etc.)
    is_global_data = False
    
    def get_property_filtered_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Filter queryset by user's assigned property.
        
        Args:
            queryset: Base queryset to filter
            
        Returns:
            Filtered queryset (or unfiltered if is_global_data=True)
        """
        # Global master data - no filtering
        if self.is_global_data:
            return queryset
        
        # Get user's assigned property
        prop = self.request.user.assigned_property
        
        # No property assigned - return empty queryset for safety
        if not prop:
            return queryset.none()
        
        # Build filter kwargs dynamically
        filter_kwargs = {self.property_field: prop}
        
        return queryset.filter(**filter_kwargs)
    
    def get_queryset(self):
        """
        Override to include property filtering.
        
        View classes can still override this method and call
        self.get_property_filtered_queryset(qs) to apply property filter.
        """
        if hasattr(super(), 'get_queryset'):
            qs = super().get_queryset()
        else:
            # Fallback to model default queryset
            qs = self.queryset if self.queryset is not None else self.model.objects.all()
        
        return self.get_property_filtered_queryset(qs)


class HotelFilterMixin(PropertyFilterMixin):
    """
    Convenience mixin for models using 'hotel' as property field.
    
    Many legacy models use 'hotel' instead of 'property' as FK name.
    """
    property_field = 'hotel'


class ReservationHotelFilterMixin(PropertyFilterMixin):
    """
    Convenience mixin for models related through Reservation.
    (e.g., Folio, Payment via reservation__hotel)
    """
    property_field = 'reservation__hotel'


class RoomHotelFilterMixin(PropertyFilterMixin):
    """
    Convenience mixin for models related through Room.
    (e.g., HousekeepingTask via room__hotel)
    """
    property_field = 'room__hotel'


# Usage Examples:
#
# 1. Direct property FK:
#     class MaintenanceRequestListView(PropertyFilterMixin, generics.ListAPIView):
#         property_field = 'property'  # or omit, it's the default
#
# 2. Hotel FK (legacy):
#     class RoomListView(HotelFilterMixin, generics.ListAPIView):
#         pass  # automatically filters by hotel field
#
# 3. Via Reservation:
#     class FolioListView(ReservationHotelFilterMixin, generics.ListAPIView):
#         pass  # automatically filters by reservation__hotel
#
# 4. Global master data:
#     class ChargeCodeListView(PropertyFilterMixin, generics.ListAPIView):
#         is_global_data = True  # No property filtering
#
# 5. Custom override:
#     class MyComplexView(PropertyFilterMixin, generics.ListAPIView):
#         property_field = 'some__complex__path__to__hotel'
#
#         def get_queryset(self):
#             qs = super().get_queryset()  # Gets property-filtered qs
#             # Add additional filters
#             return qs.filter(status='ACTIVE')

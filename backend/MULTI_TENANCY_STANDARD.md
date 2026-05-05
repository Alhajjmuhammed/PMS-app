"""
Multi-Tenancy Filtering Standard for PMS Application

This document defines the standardized approach for implementing multi-tenancy
data isolation across all API endpoints.

## Core Principle
Every queryset MUST filter by the authenticated user's assigned property to ensure
complete data isolation between hotel properties.

## Standard Pattern

### Direct Property Relationship
When the model has a direct ForeignKey to Property:

```python
def get_queryset(self):
    qs = MyModel.objects.all()
    prop = self.request.user.assigned_property
    if prop:
        qs = qs.filter(property=prop)
    return qs
```

### Hotel Relationship (older models use 'hotel' field name)
When the model has a ForeignKey named 'hotel':

```python
def get_queryset(self):
    qs = MyModel.objects.all()
    prop = self.request.user.assigned_property
    if prop:
        qs = qs.filter(hotel=prop)
    return qs
```

### Related Through Another Model
When filtering via a relationship:

```python
def get_queryset(self):
    qs = MyModel.objects.all()
    prop = self.request.user.assigned_property
    if prop:
        # Use double-underscore notation for relationships
        qs = qs.filter(reservation__hotel=prop)
    return qs
```

## Field Naming Convention

**Going Forward:** Use `property` as the ForeignKey field name for consistency.

**Legacy:** Many existing models use `hotel` - maintain for backward compatibility
but document in model docstring.

## Property Field Reference by Model

| Model | Property Field | Pattern |
|-------|---------------|---------|
| Reservation | hotel | `filter(hotel=prop)` |
| Room | hotel | `filter(hotel=prop)` |
| Folio | reservation__hotel | `filter(reservation__hotel=prop)` |
| Payment | folio__reservation__hotel | `filter(folio__reservation__hotel=prop)` |
| FolioCharge | folio__reservation__hotel | `filter(folio__reservation__hotel=prop)` |
| HousekeepingTask | room__hotel | `filter(room__hotel=prop)` |
| MaintenanceRequest | property | `filter(property=prop)` |
| PropertyChannel | property | `filter(property=prop)` |
| Guest | property | `filter(property=prop)` |
| User | assigned_property | N/A (filter other models by this) |

## Implementation Checklist

For every ListAPIView, RetrieveAPIView, and related views:

- [ ] Override `get_queryset()` method
- [ ] Get property: `prop = self.request.user.assigned_property`
- [ ] Check if property exists: `if prop:`
- [ ] Apply appropriate filter based on model's property field
- [ ] Use select_related/prefetch_related for foreign key paths
- [ ] Document the filter pattern in view docstring

## Anti-Patterns to Avoid

❌ **Don't:**
```python
# Inconsistent variable naming
property_obj = self.request.user.assigned_property  # Too verbose
p = self.request.user.assigned_property  # Too terse

# Missing null check
qs = qs.filter(hotel=self.request.user.assigned_property)  # Could be None!

# Mixing patterns in same file
qs.filter(hotel=prop)  # Line 10
qs.filter(property=prop)  # Line 50 - Different field name, confusing
```

✓ **Do:**
```python
# Consistent, clear, safe
prop = self.request.user.assigned_property
if prop:
    qs = qs.filter(hotel=prop)
return qs
```

## Special Cases

### Global Master Data
Some models are intentionally GLOBAL and shared across all properties:
- ChargeCode (billing categories)
- Channel (OTA/GDS definitions)
- Permission/Role definitions

These models should NOT be filtered by property and should be documented as:
```python
class ChargeCodeListView(generics.ListAPIView):
    \"\"\"
    NOTE: Intentionally GLOBAL - ChargeCode is master data shared system-wide.
    \"\"\"
    def get_queryset(self):
        return ChargeCode.objects.filter(is_active=True)
```

### Cross-Property Access (Admin/Support)
For system administrators who need cross-property access:
```python
def get_queryset(self):
    qs = MyModel.objects.all()
    
    # System admin can see all properties
    if self.request.user.role == 'ADMIN' and not self.request.user.assigned_property:
        return qs
    
    # Regular users filtered by property
    prop = self.request.user.assigned_property
    if prop:
        qs = qs.filter(hotel=prop)
    return qs
```

## Testing Multi-Tenancy

Every endpoint should be tested with:
1. User from Property A - should only see Property A data
2. User from Property B - should only see Property B data  
3. User with no assigned property - should see minimal/no data
4. Admin user - appropriate access based on requirements

## Migration Path

1. Audit all views in `api/v1/*/views.py`
2. Identify missing multi-tenancy filters
3. Update to standard pattern
4. Add unit tests for data isolation
5. Run integration tests with multi-property test data

## Related Files

- Permission classes: `backend/api/permissions.py`
- User model: `backend/apps/accounts/models.py`
- Property model: `backend/apps/properties/models.py`

Last Updated: April 17, 2026

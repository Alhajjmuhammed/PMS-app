"""
Multi-Tenancy Isolation Tests
=============================
Proves that Hotel A staff CANNOT access Hotel B's data via the API.
Each test:
  1. Creates data belonging to Hotel B
  2. Authenticates as a Hotel A user
  3. Attempts to access / mutate Hotel B's data
  4. Asserts 404 (not 200, not 403) — object does not exist in this tenant's scope
"""

import pytest
from datetime import date, timedelta
import uuid
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status as http_status

from apps.properties.models import Property
from apps.rooms.models import Room, RoomType, RoomBlock
from apps.guests.models import Guest, GuestDocument, GuestPreference
from apps.reservations.models import Reservation, GroupBooking
from apps.billing.models import Folio, FolioCharge, Payment, Invoice, CashierShift
from apps.housekeeping.models import HousekeepingTask, AmenityInventory, LinenInventory
from apps.maintenance.models import MaintenanceRequest
from apps.rates.models import RatePlan, RoomRate, DateRate, Season, Package
from apps.channels.models import Channel, PropertyChannel, AvailabilityUpdate
from apps.pos.models import Outlet, POSOrder
from apps.reports.models import NightAudit, DailyStatistics
from apps.notifications.models import NotificationTemplate
from apps.frontdesk.models import WalkIn

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def hotel_a(db):
    return Property.objects.create(
        name="Hotel Alpha", code=f"ALPHA-{uuid.uuid4().hex[:6]}",
        address="1 Alpha St", phone="111-0001", city="Alphaville", country="US"
    )


@pytest.fixture
def hotel_b(db):
    return Property.objects.create(
        name="Hotel Beta", code=f"BETA-{uuid.uuid4().hex[:6]}",
        address="2 Beta Ave", phone="111-0002", city="Betacity", country="US"
    )


@pytest.fixture
def staff_a(hotel_a):
    """Front-desk staff for Hotel A."""
    return User.objects.create_user(
        email=f"staff_a_{uuid.uuid4().hex[:6]}@hotelalpha.com",
        password="pass_alpha_123",
        role="FRONT_DESK",
        assigned_property=hotel_a,
        first_name="Alice",
        last_name="Alpha",
        is_active=True,
    )


@pytest.fixture
def manager_a(hotel_a):
    """Manager for Hotel A."""
    return User.objects.create_user(
        email=f"manager_a_{uuid.uuid4().hex[:6]}@hotelalpha.com",
        password="pass_alpha_mgr",
        role="MANAGER",
        assigned_property=hotel_a,
        first_name="Alice",
        last_name="Manager",
        is_active=True,
    )


@pytest.fixture
def staff_b(hotel_b):
    """Front-desk staff for Hotel B."""
    return User.objects.create_user(
        email=f"staff_b_{uuid.uuid4().hex[:6]}@hotelbeta.com",
        password="pass_beta_123",
        role="FRONT_DESK",
        assigned_property=hotel_b,
        first_name="Bob",
        last_name="Beta",
        is_active=True,
    )


@pytest.fixture
def superadmin(db):
    """Superadmin with no assigned_property — sees all data."""
    return User.objects.create_user(
        email=f"superadmin_{uuid.uuid4().hex[:6]}@pms.com",
        password="super_admin_pass",
        role="ADMIN",
        assigned_property=None,
        first_name="Super",
        last_name="Admin",
        is_active=True,
        is_staff=True,
    )


@pytest.fixture
def accountant_a(hotel_a):
    """Accountant for Hotel A — can access billing endpoints."""
    return User.objects.create_user(
        email=f"accountant_a_{uuid.uuid4().hex[:6]}@hotelalpha.com",
        password="pass_acct_123",
        role="ACCOUNTANT",
        assigned_property=hotel_a,
        first_name="Anna",
        last_name="Accountant",
        is_active=True,
    )


@pytest.fixture
def housekeeper_a(hotel_a):
    """Housekeeping staff for Hotel A."""
    return User.objects.create_user(
        email=f"housekeeper_a_{uuid.uuid4().hex[:6]}@hotelalpha.com",
        password="pass_hk_123",
        role="HOUSEKEEPING",
        assigned_property=hotel_a,
        first_name="Hannah",
        last_name="Housekeeper",
        is_active=True,
    )


@pytest.fixture
def maintenance_worker_a(hotel_a):
    """Maintenance staff for Hotel A."""
    return User.objects.create_user(
        email=f"maintenance_a_{uuid.uuid4().hex[:6]}@hotelalpha.com",
        password="pass_mnt_123",
        role="MAINTENANCE",
        assigned_property=hotel_a,
        first_name="Mike",
        last_name="Maintenance",
        is_active=True,
    )


@pytest.fixture
def room_type_b(hotel_b):
    return RoomType.objects.create(
        hotel=hotel_b, name="Deluxe B", code="DLX_B", base_rate=150
    )


@pytest.fixture
def room_b(hotel_b, room_type_b):
    return Room.objects.create(
        hotel=hotel_b,
        room_type=room_type_b,
        room_number=f"B{uuid.uuid4().hex[:4].upper()}",
        status="VC",
        fo_status="VACANT",
        is_active=True,
    )


@pytest.fixture
def guest_b(hotel_b, staff_b):
    """Guest whose only reservation is at Hotel B."""
    return Guest.objects.create(
        first_name="Bob",
        last_name="Betaguest",
        phone="999-9999",
    )


@pytest.fixture
def reservation_b(hotel_b, guest_b, room_type_b):
    import uuid
    return Reservation.objects.create(
        hotel=hotel_b,
        guest=guest_b,
        confirmation_number=f"BETA-{uuid.uuid4().hex[:8].upper()}",
        check_in_date=date.today(),
        check_out_date=date.today() + timedelta(days=2),
        status="CONFIRMED",
        adults=1,
    )


@pytest.fixture
def folio_b(reservation_b, guest_b):
    import uuid
    return Folio.objects.create(
        folio_number=f"F-{uuid.uuid4().hex[:8].upper()}",
        reservation=reservation_b,
        guest=guest_b,
        status="OPEN",
        total_charges=0,
        total_payments=0,
        total_taxes=0,
    )


@pytest.fixture
def hk_task_b(room_b):
    return HousekeepingTask.objects.create(
        room=room_b,
        task_type="CLEANING",
        priority="NORMAL",
        status="PENDING",
        scheduled_date=date.today(),
    )


@pytest.fixture
def maintenance_b(hotel_b, room_b):
    return MaintenanceRequest.objects.create(
        property=hotel_b,
        room=room_b,
        request_number=f"MNT-{uuid.uuid4().hex[:8].upper()}",
        title="Broken AC",
        description="AC not working",
        priority="HIGH",
        status="PENDING",
    )


def client_for(user):
    """Return an authenticated APIClient for the given user."""
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ---------------------------------------------------------------------------
# Additional fixtures for extended modules
# ---------------------------------------------------------------------------

@pytest.fixture
def room_type_a(hotel_a):
    return RoomType.objects.create(
        hotel=hotel_a, name="Deluxe A", code=f"DLX_A_{uuid.uuid4().hex[:4]}", base_rate=120
    )


@pytest.fixture
def rate_plan_b(hotel_b):
    return RatePlan.objects.create(
        property=hotel_b,
        name="BAR Beta",
        code=f"BAR_{uuid.uuid4().hex[:4]}",
        rate_type="BAR",
    )


@pytest.fixture
def date_rate_b(hotel_b, room_type_b, rate_plan_b):
    from datetime import date, timedelta
    return DateRate.objects.create(
        room_type=room_type_b,
        rate_plan=rate_plan_b,
        date=date.today() + timedelta(days=30),
        rate="199.00",
    )


@pytest.fixture
def channel_global():
    code = f"OTA_{uuid.uuid4().hex[:6].upper()}"
    return Channel.objects.get_or_create(
        code=code,
        defaults={"name": f"TestOTA {code}", "channel_type": "OTA"},
    )[0]


@pytest.fixture
def property_channel_b(hotel_b, channel_global):
    return PropertyChannel.objects.create(
        property=hotel_b,
        channel=channel_global,
        property_code=f"BETA_{uuid.uuid4().hex[:6]}",
    )


@pytest.fixture
def availability_update_b(property_channel_b, room_type_b):
    from datetime import date, timedelta
    return AvailabilityUpdate.objects.create(
        property_channel=property_channel_b,
        room_type=room_type_b,
        date=date.today() + timedelta(days=1),
        availability=5,
        status="PENDING",
    )


@pytest.fixture
def outlet_b(hotel_b):
    return Outlet.objects.create(
        property=hotel_b,
        name="Beta Restaurant",
        code=f"REST_{uuid.uuid4().hex[:4]}",
        outlet_type="RESTAURANT",
    )


@pytest.fixture
def pos_order_b(outlet_b, staff_b):
    return POSOrder.objects.create(
        outlet=outlet_b,
        server=staff_b,
        guest_name="Beta Guest",
        status="OPEN",
    )


@pytest.fixture
def night_audit_b(hotel_b):
    from datetime import date
    import uuid as _uuid
    # Use a unique past date to avoid unique_together constraint collisions
    audit_date = date(2020, 1, int(_uuid.uuid4().int % 28) + 1)
    return NightAudit.objects.create(
        property=hotel_b,
        business_date=audit_date,
        status="PENDING",
    )


@pytest.fixture
def daily_stats_b(hotel_b):
    from datetime import date
    import uuid as _uuid
    stats_date = date(2019, 1, int(_uuid.uuid4().int % 28) + 1)
    return DailyStatistics.objects.create(
        property=hotel_b,
        date=stats_date,
        total_rooms=10,
    )


@pytest.fixture
def invoice_b(folio_b):
    return Invoice.objects.create(
        folio=folio_b,
        invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
        status="DRAFT",
        bill_to_name="Beta Guest",
        subtotal="0.00",
        tax_amount="0.00",
        total="0.00",
    )


@pytest.fixture
def payment_b(folio_b, staff_b):
    return Payment.objects.create(
        folio=folio_b,
        payment_method="CASH",
        amount="100.00",
        status="COMPLETED",
        received_by=staff_b,
    )


@pytest.fixture
def season_b(hotel_b):
    from datetime import date
    return Season.objects.create(
        property=hotel_b,
        name="Beta High Season",
        start_date=date(2026, 12, 1),
        end_date=date(2027, 2, 28),
    )


@pytest.fixture
def package_b(hotel_b, rate_plan_b):
    from datetime import date
    return Package.objects.create(
        property=hotel_b,
        name="Beta Package",
        code=f"PKG_{uuid.uuid4().hex[:4]}",
        description="Beta test package",
        rate_plan=rate_plan_b,
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
    )


@pytest.fixture
def group_booking_b(hotel_b, staff_b):
    from datetime import date, timedelta
    return GroupBooking.objects.create(
        hotel=hotel_b,
        name="Beta Group",
        code=f"GRP-{uuid.uuid4().hex[:8].upper()}",
        contact_name="Beta Contact",
        check_in_date=date.today() + timedelta(days=60),
        check_out_date=date.today() + timedelta(days=67),
        status="TENTATIVE",
        created_by=staff_b,
    )


@pytest.fixture
def room_block_b(room_b, staff_b):
    from datetime import date, timedelta
    return RoomBlock.objects.create(
        room=room_b,
        reason="MAINTENANCE",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=12),
        created_by=staff_b,
    )


@pytest.fixture
def cashier_shift_b(hotel_b, staff_b):
    from django.utils import timezone
    return CashierShift.objects.create(
        user=staff_b,
        property=hotel_b,
        shift_start=timezone.now(),
        opening_balance="0.00",
    )


# ---------------------------------------------------------------------------
# Room isolation
# ---------------------------------------------------------------------------

class TestRoomIsolation:
    def test_hotel_a_staff_cannot_get_hotel_b_room(self, staff_a, room_b):
        r = client_for(staff_a).get(f"/api/v1/rooms/{room_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff can read Hotel B room!"
        )

    def test_hotel_a_staff_cannot_update_hotel_b_room_status(self, staff_a, room_b):
        r = client_for(staff_a).post(
            f"/api/v1/rooms/{room_b.id}/status/",
            {"status": "CLEAN"},
            format="json",
        )
        assert r.status_code in (http_status.HTTP_404_NOT_FOUND, http_status.HTTP_403_FORBIDDEN), (
            f"Expected 403/404 but got {r.status_code} — Hotel A staff mutated Hotel B room!"
        )

    def test_hotel_a_staff_room_list_excludes_hotel_b(self, staff_a, room_b):
        r = client_for(staff_a).get("/api/v1/rooms/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert room_b.id not in ids, "Hotel B room appears in Hotel A staff's room list!"

    def test_superadmin_can_see_all_rooms(self, superadmin, room_b):
        r = client_for(superadmin).get(f"/api/v1/rooms/{room_b.id}/")
        assert r.status_code == http_status.HTTP_200_OK, (
            f"Superadmin should see all rooms but got {r.status_code}"
        )


# ---------------------------------------------------------------------------
# Reservation isolation
# ---------------------------------------------------------------------------

class TestReservationIsolation:
    def test_hotel_a_staff_cannot_get_hotel_b_reservation(self, staff_a, reservation_b):
        r = client_for(staff_a).get(f"/api/v1/reservations/{reservation_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff can read Hotel B reservation!"
        )

    def test_hotel_a_staff_reservation_list_excludes_hotel_b(self, staff_a, reservation_b):
        r = client_for(staff_a).get("/api/v1/reservations/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert reservation_b.id not in ids, "Hotel B reservation in Hotel A's list!"

    def test_hotel_a_staff_cannot_cancel_hotel_b_reservation(self, staff_a, reservation_b):
        r = client_for(staff_a).post(
            f"/api/v1/reservations/{reservation_b.id}/cancel/",
            {"reason": "test"},
            format="json",
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff cancelled Hotel B reservation!"
        )


# ---------------------------------------------------------------------------
# Folio / Billing isolation
# ---------------------------------------------------------------------------

class TestFolioIsolation:
    def test_hotel_a_staff_cannot_get_hotel_b_folio(self, accountant_a, folio_b):
        r = client_for(accountant_a).get(f"/api/v1/billing/folios/{folio_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B folio!"
        )

    def test_hotel_a_staff_cannot_add_charge_to_hotel_b_folio(self, accountant_a, folio_b):
        r = client_for(accountant_a).post(
            f"/api/v1/billing/folios/{folio_b.id}/add-charge/",
            {"charge_code_id": 1, "unit_price": "100.00", "quantity": 1},
            format="json",
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff added charge to Hotel B folio!"
        )

    def test_hotel_a_staff_cannot_close_hotel_b_folio(self, accountant_a, folio_b):
        r = client_for(accountant_a).post(f"/api/v1/billing/folios/{folio_b.id}/close/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff closed Hotel B folio!"
        )

    def test_hotel_a_staff_folio_list_excludes_hotel_b(self, accountant_a, folio_b):
        r = client_for(accountant_a).get("/api/v1/billing/folios/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert folio_b.id not in ids, "Hotel B folio appears in Hotel A's folio list!"


# ---------------------------------------------------------------------------
# Guest isolation
# ---------------------------------------------------------------------------

class TestGuestIsolation:
    def test_hotel_a_staff_cannot_get_hotel_b_guest_detail(self, staff_a, guest_b, reservation_b):
        """guest_b has a reservation at hotel_b only — hotel_a staff should not see them."""
        r = client_for(staff_a).get(f"/api/v1/guests/{guest_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B guest!"
        )

    def test_hotel_a_staff_guest_list_excludes_hotel_b_guests(self, staff_a, guest_b, reservation_b):
        r = client_for(staff_a).get("/api/v1/guests/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert guest_b.id not in ids, "Hotel B guest appears in Hotel A's guest list!"


# ---------------------------------------------------------------------------
# Housekeeping isolation
# ---------------------------------------------------------------------------

class TestHousekeepingIsolation:
    def test_hotel_a_staff_cannot_start_hotel_b_task(self, housekeeper_a, hk_task_b):
        r = client_for(housekeeper_a).post(f"/api/v1/housekeeping/tasks/{hk_task_b.id}/start/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff started Hotel B housekeeping task!"
        )

    def test_hotel_a_staff_cannot_complete_hotel_b_task(self, housekeeper_a, hk_task_b):
        r = client_for(housekeeper_a).post(
            f"/api/v1/housekeeping/tasks/{hk_task_b.id}/complete/",
            {"notes": "done"},
            format="json",
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff completed Hotel B task!"
        )

    def test_hotel_a_staff_cannot_update_hotel_b_room_status_via_hk(self, housekeeper_a, room_b):
        r = client_for(housekeeper_a).post(
            f"/api/v1/housekeeping/room-status/{room_b.id}/update/",
            {"status": "CLEAN"},
            format="json",
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff set Hotel B room status via HK!"
        )


# ---------------------------------------------------------------------------
# Maintenance isolation
# ---------------------------------------------------------------------------

class TestMaintenanceIsolation:
    def test_hotel_a_staff_cannot_view_hotel_b_maintenance_request(self, maintenance_worker_a, maintenance_b):
        r = client_for(maintenance_worker_a).get(f"/api/v1/maintenance/{maintenance_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B maintenance request!"
        )

    def test_hotel_a_staff_cannot_start_hotel_b_maintenance(self, maintenance_worker_a, maintenance_b):
        r = client_for(maintenance_worker_a).post(f"/api/v1/maintenance/{maintenance_b.id}/start/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff started Hotel B maintenance!"
        )

    def test_hotel_a_staff_cannot_complete_hotel_b_maintenance(self, maintenance_worker_a, maintenance_b):
        r = client_for(maintenance_worker_a).post(
            f"/api/v1/maintenance/{maintenance_b.id}/complete/",
            {"notes": "fixed"},
            format="json",
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff completed Hotel B maintenance!"
        )

    def test_hotel_a_staff_cannot_assign_hotel_b_maintenance(self, manager_a, maintenance_worker_a, maintenance_b):
        r = client_for(manager_a).post(
            f"/api/v1/maintenance/requests/{maintenance_b.id}/assign/",
            {"assigned_to": maintenance_worker_a.id},
            format="json",
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff assigned Hotel B maintenance!"
        )


# ---------------------------------------------------------------------------
# Cross-property list contamination — aggregate check
# ---------------------------------------------------------------------------

class TestListIsolation:
    """Verify that every list endpoint returns ONLY the requesting user's property data."""

    def test_rooms_list_only_own_property(self, staff_a, room_b):
        r = client_for(staff_a).get("/api/v1/rooms/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        for item in items:
            assert item.get("hotel") != room_b.hotel_id, \
                f"Room from Hotel B (id={item['id']}) leaked into Hotel A list!"

    def test_reservations_list_only_own_property(self, staff_a, reservation_b):
        r = client_for(staff_a).get("/api/v1/reservations/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        for item in items:
            assert item.get("hotel") != reservation_b.hotel_id, \
                f"Reservation from Hotel B (id={item['id']}) leaked into Hotel A list!"

    def test_folios_list_only_own_property(self, accountant_a, folio_b):
        r = client_for(accountant_a).get("/api/v1/billing/folios/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert folio_b.id not in ids, "Hotel B folio leaked into Hotel A folio list!"


# ---------------------------------------------------------------------------
# Rate plan isolation
# ---------------------------------------------------------------------------

class TestRateIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_rate_plan(self, manager_a, rate_plan_b):
        r = client_for(manager_a).get(f"/api/v1/rates/plans/{rate_plan_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B rate plan!"
        )

    def test_hotel_a_manager_rate_plan_list_excludes_hotel_b(self, manager_a, rate_plan_b):
        r = client_for(manager_a).get("/api/v1/rates/plans/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert rate_plan_b.id not in ids, "Hotel B rate plan leaked into Hotel A list!"

    def test_hotel_a_manager_cannot_get_hotel_b_date_rate(self, manager_a, date_rate_b):
        r = client_for(manager_a).get(f"/api/v1/rates/date-rates/{date_rate_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B date rate!"
        )

    def test_hotel_a_manager_date_rate_list_excludes_hotel_b(self, manager_a, date_rate_b):
        r = client_for(manager_a).get("/api/v1/rates/date-rates/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert date_rate_b.id not in ids, "Hotel B date rate leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Channel isolation
# ---------------------------------------------------------------------------

class TestChannelIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_property_channel(self, manager_a, property_channel_b):
        r = client_for(manager_a).get(f"/api/v1/channels/property-channels/{property_channel_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B channel!"
        )

    def test_hotel_a_manager_channel_list_excludes_hotel_b(self, manager_a, property_channel_b):
        r = client_for(manager_a).get("/api/v1/channels/property-channels/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert property_channel_b.id not in ids, "Hotel B channel leaked into Hotel A list!"

    def test_hotel_a_staff_cannot_get_hotel_b_availability_update(self, staff_a, availability_update_b):
        r = client_for(staff_a).get(f"/api/v1/channels/availability-updates/{availability_update_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B availability update!"
        )

    def test_hotel_a_staff_availability_update_list_excludes_hotel_b(self, staff_a, availability_update_b):
        r = client_for(staff_a).get("/api/v1/channels/availability-updates/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert availability_update_b.id not in ids, "Hotel B availability update leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# POS isolation
# ---------------------------------------------------------------------------

class TestPOSIsolation:
    def test_hotel_a_staff_cannot_get_hotel_b_pos_order(self, staff_a, pos_order_b):
        r = client_for(staff_a).get(f"/api/v1/pos/orders/{pos_order_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B POS order!"
        )

    def test_hotel_a_staff_pos_order_list_excludes_hotel_b(self, staff_a, pos_order_b):
        r = client_for(staff_a).get("/api/v1/pos/orders/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert pos_order_b.id not in ids, "Hotel B POS order leaked into Hotel A list!"

    def test_hotel_a_staff_outlet_list_excludes_hotel_b(self, staff_a, outlet_b):
        r = client_for(staff_a).get("/api/v1/pos/outlets/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert outlet_b.id not in ids, "Hotel B outlet leaked into Hotel A outlet list!"


# ---------------------------------------------------------------------------
# Reports / Night Audit isolation
# ---------------------------------------------------------------------------

class TestReportsIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_night_audit(self, manager_a, night_audit_b):
        r = client_for(manager_a).get(f"/api/v1/reports/night-audits/{night_audit_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B night audit!"
        )

    def test_hotel_a_manager_night_audit_list_excludes_hotel_b(self, manager_a, night_audit_b):
        r = client_for(manager_a).get("/api/v1/reports/night-audits/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert night_audit_b.id not in ids, "Hotel B night audit leaked into Hotel A list!"

    def test_hotel_a_manager_cannot_start_hotel_b_night_audit(self, manager_a, night_audit_b):
        r = client_for(manager_a).post(f"/api/v1/reports/night-audits/{night_audit_b.id}/start/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager started Hotel B night audit!"
        )

    def test_hotel_a_manager_daily_stats_list_excludes_hotel_b(self, manager_a, daily_stats_b):
        r = client_for(manager_a).get("/api/v1/reports/daily-stats/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert daily_stats_b.id not in ids, "Hotel B daily stats leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Billing — Invoice and Payment isolation
# ---------------------------------------------------------------------------

class TestBillingInvoicePaymentIsolation:
    def test_hotel_a_accountant_cannot_get_hotel_b_invoice(self, accountant_a, invoice_b):
        r = client_for(accountant_a).get(f"/api/v1/billing/invoices/{invoice_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A accountant read Hotel B invoice!"
        )

    def test_hotel_a_accountant_invoice_list_excludes_hotel_b(self, accountant_a, invoice_b):
        r = client_for(accountant_a).get("/api/v1/billing/invoices/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert invoice_b.id not in ids, "Hotel B invoice leaked into Hotel A list!"

    def test_hotel_a_accountant_cannot_get_hotel_b_payment(self, accountant_a, payment_b):
        r = client_for(accountant_a).get(f"/api/v1/billing/payments/{payment_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A accountant read Hotel B payment!"
        )

    def test_hotel_a_accountant_payment_list_excludes_hotel_b(self, accountant_a, payment_b):
        r = client_for(accountant_a).get("/api/v1/billing/payments/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert payment_b.id not in ids, "Hotel B payment leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Season isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSeasonIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_season(self, manager_a, season_b):
        r = client_for(manager_a).get(f"/api/v1/rates/seasons/{season_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B season!"
        )

    def test_hotel_a_manager_season_list_excludes_hotel_b(self, manager_a, season_b):
        r = client_for(manager_a).get("/api/v1/rates/seasons/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert season_b.id not in ids, "Hotel B season leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Package isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPackageIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_package(self, manager_a, package_b):
        r = client_for(manager_a).get(f"/api/v1/rates/packages/{package_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B package!"
        )

    def test_hotel_a_manager_package_list_excludes_hotel_b(self, manager_a, package_b):
        r = client_for(manager_a).get("/api/v1/rates/packages/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert package_b.id not in ids, "Hotel B package leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Group booking isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestGroupBookingIsolation:
    def test_hotel_a_staff_cannot_get_hotel_b_group_booking(self, staff_a, group_booking_b):
        r = client_for(staff_a).get(f"/api/v1/reservations/groups/{group_booking_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B group booking!"
        )

    def test_hotel_a_staff_group_booking_list_excludes_hotel_b(self, staff_a, group_booking_b):
        r = client_for(staff_a).get("/api/v1/reservations/groups/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert group_booking_b.id not in ids, "Hotel B group booking leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Room block isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRoomBlockIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_room_block(self, manager_a, room_block_b):
        r = client_for(manager_a).get(f"/api/v1/rooms/blocks/{room_block_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B room block!"
        )

    def test_hotel_a_manager_room_block_list_excludes_hotel_b(self, manager_a, room_block_b):
        r = client_for(manager_a).get("/api/v1/rooms/blocks/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert room_block_b.id not in ids, "Hotel B room block leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Room type isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRoomTypeIsolation:
    def test_hotel_a_manager_cannot_get_hotel_b_room_type(self, manager_a, room_type_b):
        r = client_for(manager_a).get(f"/api/v1/rooms/types/{room_type_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B room type!"
        )

    def test_hotel_a_staff_room_type_list_excludes_hotel_b(self, staff_a, room_type_b):
        r = client_for(staff_a).get("/api/v1/rooms/types/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert room_type_b.id not in ids, "Hotel B room type leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Cashier shift isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCashierShiftIsolation:
    def test_hotel_a_accountant_cannot_get_hotel_b_cashier_shift(self, accountant_a, cashier_shift_b):
        r = client_for(accountant_a).get(f"/api/v1/billing/cashier-shifts/{cashier_shift_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A accountant read Hotel B cashier shift!"
        )

    def test_hotel_a_accountant_cashier_shift_list_excludes_hotel_b(self, accountant_a, cashier_shift_b):
        r = client_for(accountant_a).get("/api/v1/billing/cashier-shifts/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert cashier_shift_b.id not in ids, "Hotel B cashier shift leaked into Hotel A list!"


# ---------------------------------------------------------------------------
# Additional fixtures for inventory / notifications / walkin
# ---------------------------------------------------------------------------

@pytest.fixture
def room_a(hotel_a, room_type_a):
    return Room.objects.create(
        hotel=hotel_a,
        room_type=room_type_a,
        room_number=f"A{uuid.uuid4().hex[:4].upper()}",
        status="VC",
        fo_status="VACANT",
        is_active=True,
    )


@pytest.fixture
def amenity_inventory_b(hotel_b):
    return AmenityInventory.objects.create(
        hotel=hotel_b,
        name="Beta Shampoo",
        code=f"SHAM_{uuid.uuid4().hex[:4]}",
        quantity=100,
        reorder_level=20,
        unit_cost="1.50",
    )


@pytest.fixture
def linen_inventory_b(hotel_b):
    return LinenInventory.objects.create(
        hotel=hotel_b,
        linen_type="SHEET",
        quantity_total=50,
        quantity_in_use=10,
        quantity_in_laundry=5,
        quantity_damaged=2,
        reorder_level=15,
    )


@pytest.fixture
def notification_template_b(hotel_b):
    return NotificationTemplate.objects.create(
        property=hotel_b,
        name="Beta Welcome Email",
        template_type="EMAIL",
        subject="Welcome to Beta Hotel",
        body="Dear guest, welcome!",
    )


@pytest.fixture
def walk_in_b(hotel_b, room_type_b):
    return WalkIn.objects.create(
        property=hotel_b,
        first_name="Beta",
        last_name="Walkin",
        phone="555-0002",
        room_type=room_type_b,
        check_in_date=date.today() + timedelta(days=1),
        check_out_date=date.today() + timedelta(days=3),
        adults=1,
        rate_per_night="150.00",
    )


# ---------------------------------------------------------------------------
# Housekeeping inventory isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestHousekeepingInventoryIsolation:
    def test_hotel_a_housekeeper_amenity_inventory_list_excludes_hotel_b(
        self, housekeeper_a, amenity_inventory_b
    ):
        r = client_for(housekeeper_a).get("/api/v1/housekeeping/inventory/amenities/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert amenity_inventory_b.id not in ids, \
            "Hotel B amenity inventory leaked into Hotel A list!"

    def test_hotel_a_housekeeper_cannot_get_hotel_b_amenity_inventory(
        self, housekeeper_a, amenity_inventory_b
    ):
        r = client_for(housekeeper_a).get(
            f"/api/v1/housekeeping/inventory/amenities/{amenity_inventory_b.id}/"
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B amenity inventory!"
        )

    def test_hotel_a_housekeeper_linen_inventory_list_excludes_hotel_b(
        self, housekeeper_a, linen_inventory_b
    ):
        r = client_for(housekeeper_a).get("/api/v1/housekeeping/inventory/linens/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert linen_inventory_b.id not in ids, \
            "Hotel B linen inventory leaked into Hotel A list!"

    def test_hotel_a_housekeeper_cannot_get_hotel_b_linen_inventory(
        self, housekeeper_a, linen_inventory_b
    ):
        r = client_for(housekeeper_a).get(
            f"/api/v1/housekeeping/inventory/linens/{linen_inventory_b.id}/"
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B linen inventory!"
        )


# ---------------------------------------------------------------------------
# Notification template isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestNotificationTemplateIsolation:
    def test_hotel_a_manager_notification_template_list_excludes_hotel_b(
        self, manager_a, notification_template_b
    ):
        r = client_for(manager_a).get("/api/v1/notifications/templates/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert notification_template_b.id not in ids, \
            "Hotel B notification template leaked into Hotel A list!"

    def test_hotel_a_manager_cannot_get_hotel_b_notification_template(
        self, manager_a, notification_template_b
    ):
        r = client_for(manager_a).get(
            f"/api/v1/notifications/templates/{notification_template_b.id}/"
        )
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A manager read Hotel B notification template!"
        )


# ---------------------------------------------------------------------------
# Walk-in isolation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestWalkInIsolation:
    def test_hotel_a_staff_walk_in_list_excludes_hotel_b(self, staff_a, walk_in_b):
        r = client_for(staff_a).get("/api/v1/frontdesk/walk-ins/")
        assert r.status_code == http_status.HTTP_200_OK
        items = r.data.get("results") if "results" in r.data else r.data
        ids = [item["id"] for item in items]
        assert walk_in_b.id not in ids, "Hotel B walk-in leaked into Hotel A list!"

    def test_hotel_a_staff_cannot_get_hotel_b_walk_in(self, staff_a, walk_in_b):
        r = client_for(staff_a).get(f"/api/v1/frontdesk/walk-ins/{walk_in_b.id}/")
        assert r.status_code == http_status.HTTP_404_NOT_FOUND, (
            f"Expected 404 but got {r.status_code} — Hotel A staff read Hotel B walk-in!"
        )


# ---------------------------------------------------------------------------
# CREATE injection — prove property is always forced from authenticated user
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateInjection:
    """
    POST requests that include a foreign hotel's ID in the body must NOT
    create the object under that hotel. The view must enforce assigned_property.
    After our fixes, the created object's hotel/property must equal hotel_a,
    not hotel_b.
    """

    def test_room_create_ignores_injected_hotel(
        self, manager_a, hotel_a, hotel_b, room_type_a
    ):
        payload = {
            "room_number": f"INJ{uuid.uuid4().hex[:4].upper()}",
            "room_type": room_type_a.id,
            "hotel": hotel_b.id,   # ← injected wrong hotel
            "status": "VC",
            "fo_status": "VACANT",
            "floor": 1,
        }
        r = client_for(manager_a).post("/api/v1/rooms/create/", payload, format="json")
        # Either rejected OR created under hotel_a — never hotel_b
        if r.status_code == http_status.HTTP_201_CREATED:
            assert r.data.get("hotel") != hotel_b.id, (
                "CREATE injection succeeded — room was created under Hotel B by Hotel A staff!"
            )
        else:
            assert r.status_code in (
                http_status.HTTP_400_BAD_REQUEST,
                http_status.HTTP_403_FORBIDDEN,
            ), f"Unexpected status {r.status_code}"

    def test_room_type_create_ignores_injected_hotel(
        self, manager_a, hotel_a, hotel_b
    ):
        payload = {
            "name": f"InjType {uuid.uuid4().hex[:4]}",
            "code": f"INJ_{uuid.uuid4().hex[:4]}",
            "hotel": hotel_b.id,   # ← injected wrong hotel
            "base_rate": "100.00",
        }
        r = client_for(manager_a).post("/api/v1/rooms/types/", payload, format="json")
        if r.status_code == http_status.HTTP_201_CREATED:
            assert r.data.get("hotel") != hotel_b.id, (
                "CREATE injection succeeded — room type was created under Hotel B by Hotel A staff!"
            )
        else:
            assert r.status_code in (
                http_status.HTTP_400_BAD_REQUEST,
                http_status.HTTP_403_FORBIDDEN,
            ), f"Unexpected status {r.status_code}"

    def test_group_booking_create_ignores_injected_hotel(
        self, staff_a, hotel_a, hotel_b
    ):
        payload = {
            "name": f"Injected Group {uuid.uuid4().hex[:4]}",
            "code": f"INJ-{uuid.uuid4().hex[:6].upper()}",
            "contact_name": "Injector",
            "hotel": hotel_b.id,   # ← injected wrong hotel
            "check_in_date": str(date.today() + timedelta(days=90)),
            "check_out_date": str(date.today() + timedelta(days=97)),
            "status": "TENTATIVE",
        }
        r = client_for(staff_a).post("/api/v1/reservations/groups/", payload, format="json")
        if r.status_code == http_status.HTTP_201_CREATED:
            assert r.data.get("hotel") != hotel_b.id, (
                "CREATE injection succeeded — group booking was created under Hotel B by Hotel A staff!"
            )
        else:
            assert r.status_code in (
                http_status.HTTP_400_BAD_REQUEST,
                http_status.HTTP_403_FORBIDDEN,
            ), f"Unexpected status {r.status_code}"

    def test_walk_in_create_ignores_injected_property(
        self, staff_a, hotel_a, hotel_b, room_type_a
    ):
        payload = {
            "property": hotel_b.id,  # ← injected wrong property
            "first_name": "Injected",
            "last_name": "Guest",
            "phone": "555-9999",
            "room_type": room_type_a.id,
            "check_in_date": str(date.today() + timedelta(days=1)),
            "check_out_date": str(date.today() + timedelta(days=3)),
            "adults": 1,
            "rate_per_night": "150.00",
        }
        r = client_for(staff_a).post("/api/v1/frontdesk/walk-ins/", payload, format="json")
        if r.status_code == http_status.HTTP_201_CREATED:
            assert r.data.get("property") != hotel_b.id, (
                "CREATE injection succeeded — walk-in was created under Hotel B by Hotel A staff!"
            )
        else:
            assert r.status_code in (
                http_status.HTTP_400_BAD_REQUEST,
                http_status.HTTP_403_FORBIDDEN,
            ), f"Unexpected status {r.status_code}"

    def test_night_audit_create_ignores_injected_property(
        self, manager_a, hotel_a, hotel_b
    ):
        import uuid as _uuid
        audit_date = date(2015, 6, int(_uuid.uuid4().int % 28) + 1)
        payload = {
            "property": hotel_b.id,  # ← injected wrong property
            "business_date": str(audit_date),
            "status": "PENDING",
        }
        r = client_for(manager_a).post("/api/v1/reports/night-audits/", payload, format="json")
        if r.status_code == http_status.HTTP_201_CREATED:
            assert r.data.get("property") != hotel_b.id, (
                "CREATE injection succeeded — night audit was created under Hotel B by Hotel A staff!"
            )
        else:
            assert r.status_code in (
                http_status.HTTP_400_BAD_REQUEST,
                http_status.HTTP_403_FORBIDDEN,
            ), f"Unexpected status {r.status_code}"

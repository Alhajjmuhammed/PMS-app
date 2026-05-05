'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Layout from '@/components/Layout';
import Link from 'next/link';
import clsx from 'clsx';
import {
  BuildingOfficeIcon,
  CalendarDaysIcon,
  UsersIcon,
  BanknotesIcon,
  WrenchScrewdriverIcon,
  SparklesIcon,
  PlusIcon,
  ArrowRightOnRectangleIcon,
  ArrowLeftOnRectangleIcon,
  ChartBarIcon,
  ShoppingCartIcon,
  MoonIcon,
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  HomeIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline';

interface DashboardStats {
  total_rooms: number;
  occupied_rooms: number;
  available_rooms: number;
  occupancy_rate: number;
  total_reservations_today: number;
  check_ins_today: number;
  check_outs_today: number;
  revenue_today: number;
  pending_maintenance: number;
  housekeeping_pending: number;
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  if (h < 21) return 'Good evening';
  return 'Good night';
}



/* --- Stat Card ------------------------------------------- */
interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  gradient: string;
}

function StatCard({ label, value, sub, icon: Icon, gradient }: StatCardProps) {
  return (
    <div className="relative bg-white rounded-2xl p-5 shadow-sm border border-slate-100 overflow-hidden group hover:shadow-md transition-shadow">
      <div className={clsx('absolute inset-0 opacity-0 group-hover:opacity-[0.03] transition-opacity', gradient)} />
      <div className="flex items-start justify-between gap-3">
        <div className={clsx('w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm', gradient)}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
      <div className="mt-4">
        <p className="text-3xl font-bold text-slate-900 leading-none tabular-nums">{value}</p>
        <p className="text-sm font-medium text-slate-500 mt-1.5">{label}</p>
        {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
      </div>
    </div>
  );
}

/* --- Quick Action ----------------------------------------- */
interface QuickActionProps {
  label: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  bg: string;
  iconColor: string;
}

function QuickAction({ label, href, icon: Icon, bg, iconColor }: QuickActionProps) {
  return (
    <Link
      href={href}
      className={clsx(
        'flex flex-col items-center gap-3 py-5 px-3 rounded-2xl font-medium text-sm transition-all border hover:scale-[1.02] active:scale-[0.98]',
        bg,
      )}
    >
      <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center', iconColor)}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <span className="text-center leading-tight text-slate-700 font-semibold text-xs">{label}</span>
    </Link>
  );
}

/* --- Section Header --------------------------------------- */
function SectionHeader({ title, sub }: { title: string; sub?: string }) {
  return (
    <div className="mb-4">
      <h3 className="text-base font-bold text-slate-800">{title}</h3>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </div>
  );
}

/* --- ADMIN / MANAGER --------------------------------------- */
function AdminManagerDashboard({ stats }: { stats: DashboardStats | null }) {
  const occ = stats?.occupancy_rate ?? 0;
  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Occupied Rooms"   value={`${stats?.occupied_rooms ?? 0} / ${stats?.total_rooms ?? 0}`} sub={`${stats?.available_rooms ?? 0} available`} icon={BuildingOfficeIcon}        gradient="bg-gradient-to-br from-blue-500 to-blue-600" />
        <StatCard label="Check-ins Today"  value={stats?.check_ins_today ?? 0}          sub={`${stats?.total_reservations_today ?? 0} total reservations`} icon={ArrowRightOnRectangleIcon}  gradient="bg-gradient-to-br from-emerald-500 to-emerald-600" />
        <StatCard label="Check-outs Today" value={stats?.check_outs_today ?? 0}         sub="Scheduled departures" icon={ArrowLeftOnRectangleIcon}   gradient="bg-gradient-to-br from-amber-500 to-orange-500" />
        <StatCard label="Revenue Today"    value={`$${(stats?.revenue_today ?? 0).toLocaleString()}`} sub="Today's earnings" icon={BanknotesIcon} gradient="bg-gradient-to-br from-violet-500 to-purple-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Occupancy */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
          <SectionHeader title="Room Occupancy" sub="Live occupancy rate" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-4xl font-bold text-slate-900 tabular-nums">{occ}%</span>
            <div className={clsx('w-16 h-16 rounded-full flex items-center justify-center border-4',
              occ >= 80 ? 'border-emerald-400 bg-emerald-50' : occ >= 50 ? 'border-blue-400 bg-blue-50' : 'border-amber-400 bg-amber-50')}>
              <HomeIcon className={clsx('w-7 h-7', occ >= 80 ? 'text-emerald-500' : occ >= 50 ? 'text-blue-500' : 'text-amber-500')} />
            </div>
          </div>
          <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden mb-4">
            <div className={clsx('h-full rounded-full transition-all duration-1000',
              occ >= 80 ? 'bg-gradient-to-r from-emerald-400 to-emerald-500' :
              occ >= 50 ? 'bg-gradient-to-r from-blue-400 to-blue-500' :
              'bg-gradient-to-r from-amber-400 to-orange-400')}
              style={{ width: `${Math.min(occ, 100)}%` }} />
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'Occupied',  value: stats?.occupied_rooms  ?? 0, color: 'text-blue-600',    bg: 'bg-blue-50' },
              { label: 'Available', value: stats?.available_rooms ?? 0, color: 'text-emerald-600', bg: 'bg-emerald-50' },
              { label: 'Total',     value: stats?.total_rooms     ?? 0, color: 'text-slate-700',   bg: 'bg-slate-50' },
            ].map((item) => (
              <div key={item.label} className={clsx('text-center p-2.5 rounded-xl', item.bg)}>
                <p className={clsx('text-xl font-bold', item.color)}>{item.value}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">{item.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Today's activity */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
          <SectionHeader title="Today's Activity" sub="Real-time movement overview" />
          <div className="space-y-4">
            {[
              { label: 'Check-ins',    value: stats?.check_ins_today          ?? 0, color: 'bg-gradient-to-r from-emerald-400 to-emerald-500', text: 'text-emerald-600' },
              { label: 'Check-outs',   value: stats?.check_outs_today         ?? 0, color: 'bg-gradient-to-r from-amber-400 to-orange-400',    text: 'text-amber-600' },
              { label: 'Reservations', value: stats?.total_reservations_today ?? 0, color: 'bg-gradient-to-r from-blue-400 to-blue-500',       text: 'text-blue-600' },
            ].map((item) => {
              const max = Math.max(stats?.total_rooms ?? 1, item.value, 1);
              const pct = Math.min(100, (item.value / max) * 100);
              return (
                <div key={item.label}>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-slate-600 font-medium">{item.label}</span>
                    <span className={clsx('font-bold tabular-nums', item.text)}>{item.value}</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className={clsx('h-full rounded-full transition-all duration-1000', item.color)} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Operations */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
          <SectionHeader title="Operations Status" sub="Pending tasks by department" />
          <div className="space-y-3">
            <div className="flex items-center gap-3.5 p-4 rounded-2xl bg-gradient-to-br from-orange-50 to-amber-50 border border-orange-100">
              <div className="w-11 h-11 rounded-xl bg-orange-100 flex items-center justify-center flex-shrink-0">
                <WrenchScrewdriverIcon className="w-5 h-5 text-orange-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-orange-800">Maintenance</p>
                <p className="text-xs text-orange-500 mt-0.5">{stats?.pending_maintenance ?? 0} task{(stats?.pending_maintenance ?? 0) !== 1 ? 's' : ''} pending</p>
              </div>
              <span className="text-3xl font-black text-orange-600 tabular-nums">{stats?.pending_maintenance ?? 0}</span>
            </div>
            <div className="flex items-center gap-3.5 p-4 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100">
              <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <SparklesIcon className="w-5 h-5 text-emerald-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-emerald-800">Housekeeping</p>
                <p className="text-xs text-emerald-500 mt-0.5">{stats?.housekeeping_pending ?? 0} room{(stats?.housekeeping_pending ?? 0) !== 1 ? 's' : ''} to clean</p>
              </div>
              <span className="text-3xl font-black text-emerald-600 tabular-nums">{stats?.housekeeping_pending ?? 0}</span>
            </div>
          </div>
        </div>
      </div>

      <div>
        <SectionHeader title="Quick Actions" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: 'New Reservation', href: '/reservations/new', icon: CalendarDaysIcon,         bg: 'bg-blue-50 hover:bg-blue-100 border-blue-100',       iconColor: 'bg-blue-500' },
            { label: 'Check In',        href: '/checkin',          icon: ArrowRightOnRectangleIcon, bg: 'bg-emerald-50 hover:bg-emerald-100 border-emerald-100', iconColor: 'bg-emerald-500' },
            { label: 'Check Out',       href: '/checkin',          icon: ArrowLeftOnRectangleIcon,  bg: 'bg-amber-50 hover:bg-amber-100 border-amber-100',     iconColor: 'bg-amber-500' },
            { label: 'Guests',          href: '/guests',           icon: UsersIcon,                 bg: 'bg-teal-50 hover:bg-teal-100 border-teal-100',        iconColor: 'bg-teal-500' },
            { label: 'Reports',         href: '/reports',          icon: ChartBarIcon,              bg: 'bg-violet-50 hover:bg-violet-100 border-violet-100',  iconColor: 'bg-violet-500' },
            { label: 'Night Audit',     href: '/night-audit',      icon: MoonIcon,                  bg: 'bg-slate-50 hover:bg-slate-100 border-slate-200',     iconColor: 'bg-slate-700' },
          ].map((a) => <QuickAction key={a.label} {...a} />)}
        </div>
      </div>
    </>
  );
}

/* --- FRONT DESK -------------------------------------------- */
function FrontDeskDashboard({ stats }: { stats: DashboardStats | null }) {
  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Available Rooms"  value={stats?.available_rooms ?? 0}          sub={`${stats?.total_rooms ?? 0} total rooms`}    icon={BuildingOfficeIcon}        gradient="bg-gradient-to-br from-blue-500 to-blue-600" />
        <StatCard label="Check-ins Today"  value={stats?.check_ins_today ?? 0}          sub="Arrivals expected"                           icon={ArrowRightOnRectangleIcon} gradient="bg-gradient-to-br from-emerald-500 to-emerald-600" />
        <StatCard label="Check-outs Today" value={stats?.check_outs_today ?? 0}         sub="Departures scheduled"                        icon={ArrowLeftOnRectangleIcon}  gradient="bg-gradient-to-br from-amber-500 to-orange-500" />
        <StatCard label="Reservations"     value={stats?.total_reservations_today ?? 0} sub="Today's bookings"                            icon={CalendarDaysIcon}          gradient="bg-gradient-to-br from-violet-500 to-purple-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
          <SectionHeader title="Room Availability" sub="Current snapshot" />
          <div className="space-y-3">
            {[
              { label: 'Occupied',  value: stats?.occupied_rooms  ?? 0, total: stats?.total_rooms ?? 1, bar: 'bg-gradient-to-r from-blue-400 to-blue-500',     badge: 'bg-blue-50 text-blue-700' },
              { label: 'Available', value: stats?.available_rooms ?? 0, total: stats?.total_rooms ?? 1, bar: 'bg-gradient-to-r from-emerald-400 to-emerald-500', badge: 'bg-emerald-50 text-emerald-700' },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-slate-600 font-medium">{item.label}</span>
                  <span className={clsx('font-bold px-2 rounded-full text-xs py-0.5', item.badge)}>{item.value}</span>
                </div>
                <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className={clsx('h-full rounded-full transition-all duration-1000', item.bar)}
                    style={{ width: `${Math.min(100, (item.value / item.total) * 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
          <SectionHeader title="Quick Actions" />
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'New Reservation', href: '/reservations/new', icon: CalendarDaysIcon,         bg: 'bg-blue-50 hover:bg-blue-100 border-blue-100',       iconColor: 'bg-blue-500' },
              { label: 'Check In',        href: '/checkin',          icon: ArrowRightOnRectangleIcon, bg: 'bg-emerald-50 hover:bg-emerald-100 border-emerald-100', iconColor: 'bg-emerald-500' },
              { label: 'Check Out',       href: '/checkin',          icon: ArrowLeftOnRectangleIcon,  bg: 'bg-amber-50 hover:bg-amber-100 border-amber-100',     iconColor: 'bg-amber-500' },
              { label: 'Guest List',      href: '/guests',           icon: UsersIcon,                 bg: 'bg-teal-50 hover:bg-teal-100 border-teal-100',        iconColor: 'bg-teal-500' },
            ].map((a) => <QuickAction key={a.label} {...a} />)}
          </div>
        </div>
      </div>
    </>
  );
}

/* --- HOUSEKEEPING ------------------------------------------ */
function HousekeepingDashboard({ stats }: { stats: DashboardStats | null }) {
  const pending = stats?.housekeeping_pending ?? 0;
  const total = stats?.total_rooms ?? 0;
  const occupied = stats?.occupied_rooms ?? 0;
  const clean = Math.max(0, total - pending - occupied);

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard label="Rooms to Clean" value={pending} sub="Pending housekeeping" icon={SparklesIcon}       gradient="bg-gradient-to-br from-amber-500 to-orange-500" />
        <StatCard label="Clean Rooms"    value={clean}   sub="Ready for guests"     icon={CheckCircleIcon}    gradient="bg-gradient-to-br from-emerald-500 to-teal-500" />
        <StatCard label="Total Rooms"    value={total}   sub="In this property"     icon={BuildingOfficeIcon} gradient="bg-gradient-to-br from-blue-500 to-blue-600" />
      </div>

      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 max-w-lg">
        <SectionHeader title="Cleaning Progress" sub="Today's housekeeping overview" />
        <div className="w-full h-4 bg-slate-100 rounded-full overflow-hidden mb-3">
          <div className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full transition-all duration-1000"
            style={{ width: total > 0 ? `${Math.min(100, (clean / total) * 100)}%` : '0%' }} />
        </div>
        <div className="flex justify-between text-xs text-slate-500 mb-5">
          <span>{clean} cleaned</span>
          <span>{pending} pending</span>
        </div>
        <QuickAction label="View Room Status" href="/housekeeping" icon={ClipboardDocumentListIcon} bg="bg-emerald-50 hover:bg-emerald-100 border-emerald-100" iconColor="bg-emerald-500" />
      </div>
    </>
  );
}

/* --- MAINTENANCE ------------------------------------------- */
function MaintenanceDashboard({ stats }: { stats: DashboardStats | null }) {
  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
        <StatCard label="Pending Tasks" value={stats?.pending_maintenance ?? 0} sub="Awaiting completion" icon={ExclamationTriangleIcon} gradient="bg-gradient-to-br from-red-500 to-rose-600" />
        <StatCard label="Total Rooms"   value={stats?.total_rooms ?? 0}         sub="In this property"    icon={BuildingOfficeIcon}       gradient="bg-gradient-to-br from-blue-500 to-blue-600" />
      </div>
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 max-w-sm">
        <SectionHeader title="Quick Actions" />
        <div className="grid grid-cols-2 gap-3">
          <QuickAction label="All Tasks"   href="/maintenance" icon={WrenchScrewdriverIcon} bg="bg-orange-50 hover:bg-orange-100 border-orange-100" iconColor="bg-orange-500" />
          <QuickAction label="Room Status" href="/rooms"       icon={BuildingOfficeIcon}     bg="bg-blue-50 hover:bg-blue-100 border-blue-100"       iconColor="bg-blue-500" />
        </div>
      </div>
    </>
  );
}

/* --- ACCOUNTANT -------------------------------------------- */
function AccountantDashboard({ stats }: { stats: DashboardStats | null }) {
  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Revenue Today"      value={`$${(stats?.revenue_today ?? 0).toLocaleString()}`} sub="Today's earnings"         icon={BanknotesIcon}      gradient="bg-gradient-to-br from-emerald-500 to-teal-600" />
        <StatCard label="Total Reservations" value={stats?.total_reservations_today ?? 0}               sub="Active today"             icon={CalendarDaysIcon}   gradient="bg-gradient-to-br from-blue-500 to-blue-600" />
        <StatCard label="Occupied Rooms"     value={stats?.occupied_rooms ?? 0}                         sub={`of ${stats?.total_rooms ?? 0} total`} icon={BuildingOfficeIcon} gradient="bg-gradient-to-br from-violet-500 to-purple-600" />
        <StatCard label="Occupancy Rate"     value={`${stats?.occupancy_rate ?? 0}%`}                   sub="Current rate"             icon={ChartBarIcon}       gradient="bg-gradient-to-br from-amber-500 to-orange-500" />
      </div>
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
        <SectionHeader title="Finance Quick Actions" />
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-w-md">
          {[
            { label: 'Billing',     href: '/billing',     icon: BanknotesIcon,  bg: 'bg-emerald-50 hover:bg-emerald-100 border-emerald-100', iconColor: 'bg-emerald-500' },
            { label: 'Reports',     href: '/reports',     icon: ChartBarIcon,   bg: 'bg-violet-50 hover:bg-violet-100 border-violet-100',   iconColor: 'bg-violet-500' },
            { label: 'Night Audit', href: '/night-audit', icon: MoonIcon,       bg: 'bg-slate-50 hover:bg-slate-100 border-slate-200',      iconColor: 'bg-slate-700' },
          ].map((a) => <QuickAction key={a.label} {...a} />)}
        </div>
      </div>
    </>
  );
}

/* --- POS STAFF --------------------------------------------- */
function PosStaffDashboard({ stats }: { stats: DashboardStats | null }) {
  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
        <StatCard label="Active Guests"  value={stats?.occupied_rooms ?? 0}                          sub="Currently checked in" icon={UsersIcon}     gradient="bg-gradient-to-br from-blue-500 to-blue-600" />
        <StatCard label="Revenue Today"  value={`$${(stats?.revenue_today ?? 0).toLocaleString()}`} sub="Today's sales"        icon={BanknotesIcon} gradient="bg-gradient-to-br from-emerald-500 to-teal-600" />
      </div>
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 max-w-sm">
        <SectionHeader title="Quick Actions" />
        <div className="grid grid-cols-2 gap-3">
          <QuickAction label="POS"        href="/pos"    icon={ShoppingCartIcon} bg="bg-blue-50 hover:bg-blue-100 border-blue-100"   iconColor="bg-blue-500" />
          <QuickAction label="Guest List" href="/guests" icon={UsersIcon}        bg="bg-teal-50 hover:bg-teal-100 border-teal-100"   iconColor="bg-teal-500" />
        </div>
      </div>
    </>
  );
}

/* --- GUEST ------------------------------------------------- */
function GuestDashboard() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="w-20 h-20 rounded-3xl bg-blue-50 flex items-center justify-center">
        <HomeIcon className="w-10 h-10 text-blue-500" />
      </div>
      <h2 className="text-2xl font-bold text-slate-800">Welcome</h2>
      <p className="text-slate-500 text-sm max-w-xs text-center">
        Use the menu to access your reservation details and hotel services.
      </p>
    </div>
  );
}

/* --- SUPERADMIN Dashboard ---------------------------------- */
interface PropertyItem {
  id: number;
  name: string;
  code: string;
  property_type: string;
  city: string;
  country: string;
  star_rating: number;
  total_rooms: number;
  is_active: boolean;
}

function SuperAdminDashboard() {
  const [properties, setProperties] = useState<PropertyItem[]>([]);
  const [userCount, setUserCount] = useState<number | null>(null);
  const [propLoading, setPropLoading] = useState(true);

  useEffect(() => {
    api.get<PropertyItem[]>('/api/v1/properties/')
      .then((r) => setProperties(Array.isArray(r.data) ? r.data : (r.data as any).results ?? []))
      .catch(() => {})
      .finally(() => setPropLoading(false));

    api.get('/api/v1/auth/users/')
      .then((r: any) => {
        const data = r.data;
        setUserCount(Array.isArray(data) ? data.length : (data.count ?? data.results?.length ?? null));
      })
      .catch(() => {});
  }, []);

  const typeColors: Record<string, string> = {
    HOTEL: 'bg-blue-100 text-blue-700',
    RESORT: 'bg-emerald-100 text-emerald-700',
    MOTEL: 'bg-amber-100 text-amber-700',
    HOSTEL: 'bg-violet-100 text-violet-700',
    APARTMENT: 'bg-pink-100 text-pink-700',
    VILLA: 'bg-teal-100 text-teal-700',
    GUESTHOUSE: 'bg-orange-100 text-orange-700',
  };

  return (
    <>
      {/* System stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Total Properties"
          value={propLoading ? '…' : properties.length}
          sub="Registered in system"
          icon={GlobeAltIcon}
          gradient="bg-gradient-to-br from-amber-500 to-orange-500"
        />
        <StatCard
          label="Active Properties"
          value={propLoading ? '…' : properties.filter((p) => p.is_active).length}
          sub="Currently operating"
          icon={BuildingOfficeIcon}
          gradient="bg-gradient-to-br from-emerald-500 to-teal-600"
        />
        <StatCard
          label="System Users"
          value={userCount ?? '…'}
          sub="Across all properties"
          icon={UsersIcon}
          gradient="bg-gradient-to-br from-violet-500 to-purple-600"
        />
      </div>

      {/* Quick actions for system admin */}
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
        <SectionHeader title="System Actions" sub="Manage all properties and users" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <QuickAction label="Manage Properties"   href="/property"   icon={GlobeAltIcon}    bg="bg-amber-50 border-amber-100"   iconColor="bg-amber-500" />
          <QuickAction label="Manage All Users"    href="/users"      icon={UsersIcon}       bg="bg-violet-50 border-violet-100" iconColor="bg-violet-500" />
          <QuickAction label="Audit Logs"          href="/audit-logs" icon={ClipboardDocumentListIcon} bg="bg-slate-50 border-slate-200" iconColor="bg-slate-600" />
          <QuickAction label="Django Admin Panel"  href="http://localhost:8000/admin" icon={WrenchScrewdriverIcon} bg="bg-red-50 border-red-100" iconColor="bg-red-500" />
        </div>
      </div>

      {/* Properties list */}
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
        <SectionHeader title="All Properties" sub="Full system overview" />
        {propLoading ? (
          <div className="flex items-center justify-center py-10">
            <div className="w-8 h-8 border-4 border-amber-400 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : properties.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-sm">No properties found.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {properties.map((prop) => (
              <Link
                key={prop.id}
                href="/property"
                className="flex items-start gap-3 p-4 rounded-xl border border-slate-100 hover:border-amber-200 hover:bg-amber-50/30 transition-all group"
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                  <BuildingOfficeIcon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold text-slate-800 text-sm truncate">{prop.name}</p>
                    <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded-full', typeColors[prop.property_type] ?? 'bg-slate-100 text-slate-600')}>
                      {prop.property_type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5 truncate">{prop.city}, {prop.country}</p>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="text-xs text-slate-500">{prop.total_rooms} rooms</span>
                    <span className={clsx('text-[10px] font-semibold px-1.5 py-0.5 rounded-full', prop.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600')}>
                      {prop.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

/* --- Main Dashboard Page ----------------------------------- */
export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const isSuperAdmin = user?.is_superuser === true;

  useEffect(() => {
    if (!authLoading && !user) router.push('/login');
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user && !isSuperAdmin) {
      api.get<DashboardStats>('/api/v1/frontdesk/dashboard/stats/')
        .then((r) => setStats(r.data))
        .catch(() => {})
        .finally(() => setLoading(false));
    } else if (user && isSuperAdmin) {
      setLoading(false);
    }
  }, [user, isSuperAdmin]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-slate-500 text-sm">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });

  const role = user?.role ?? '';
  const isAdminOrManager = role === 'ADMIN' || role === 'MANAGER';

  function renderRoleDashboard() {
    if (isSuperAdmin)            return <SuperAdminDashboard />;
    if (isAdminOrManager)        return <AdminManagerDashboard stats={stats} />;
    if (role === 'FRONT_DESK')   return <FrontDeskDashboard stats={stats} />;
    if (role === 'HOUSEKEEPING') return <HousekeepingDashboard stats={stats} />;
    if (role === 'MAINTENANCE')  return <MaintenanceDashboard stats={stats} />;
    if (role === 'ACCOUNTANT')   return <AccountantDashboard stats={stats} />;
    if (role === 'POS_STAFF')    return <PosStaffDashboard stats={stats} />;
    if (role === 'GUEST')        return <GuestDashboard />;
    return <AdminManagerDashboard stats={stats} />;
  }

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-6">

        {/* -- Page header -- */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl font-bold text-slate-900">
                {getGreeting()}, {user?.first_name}!
              </h1>
            </div>
            <p className="text-slate-500 text-sm mt-1">
              {today}
              {!isSuperAdmin && user?.assigned_property?.name && (
                <span className="ml-2 text-slate-400 font-medium">· {user.assigned_property.name}</span>
              )}
              {isSuperAdmin && (
                <span className="ml-2 text-amber-600 font-medium">· System Administrator</span>
              )}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className={clsx(
              'text-xs font-bold px-3 py-1.5 rounded-full',
              isSuperAdmin        ? 'bg-amber-100 text-amber-800' :
              role === 'ADMIN'        ? 'bg-red-100 text-red-700' :
              role === 'MANAGER'      ? 'bg-violet-100 text-violet-700' :
              role === 'FRONT_DESK'   ? 'bg-blue-100 text-blue-700' :
              role === 'HOUSEKEEPING' ? 'bg-emerald-100 text-emerald-700' :
              role === 'MAINTENANCE'  ? 'bg-orange-100 text-orange-700' :
              role === 'ACCOUNTANT'   ? 'bg-amber-100 text-amber-700' :
              role === 'POS_STAFF'    ? 'bg-pink-100 text-pink-700' :
              'bg-slate-100 text-slate-600',
            )}>
              {isSuperAdmin ? 'SUPERADMIN' : role.replace('_', ' ')}
            </span>

            {(isAdminOrManager || role === 'FRONT_DESK') && (
              <Link
                href="/reservations/new"
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm shadow-blue-900/20"
              >
                <PlusIcon className="w-4 h-4" />
                New Reservation
              </Link>
            )}
          </div>
        </div>

        {/* -- Role-based content -- */}
        {renderRoleDashboard()}

      </div>
    </Layout>
  );
}


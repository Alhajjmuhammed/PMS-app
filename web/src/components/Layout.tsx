'use client';

import { ReactNode, useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import {
  HomeIcon,
  CalendarDaysIcon,
  BuildingOfficeIcon,
  UsersIcon,
  ArrowRightOnRectangleIcon,
  ArrowLeftOnRectangleIcon,
  SparklesIcon,
  WrenchScrewdriverIcon,
  ShoppingCartIcon,
  BanknotesIcon,
  ChartBarIcon,
  MoonIcon,
  SignalIcon,
  TagIcon,
  UserGroupIcon,
  BuildingLibraryIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  MagnifyingGlassIcon,
  GlobeAltIcon,
  ServerStackIcon,
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

const ALL_ROLES = [
  'ADMIN', 'MANAGER', 'FRONT_DESK', 'HOUSEKEEPING',
  'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF', 'GUEST',
];

type NavItem = {
  name: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  roles: string[];
};

type NavGroup = {
  label?: string;
  items: NavItem[];
};

const navGroups: NavGroup[] = [
  {
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, roles: ALL_ROLES },
    ],
  },
  {
    label: 'Front Office',
    items: [
      { name: 'Reservations',   href: '/reservations', icon: CalendarDaysIcon,         roles: ['ADMIN', 'MANAGER', 'FRONT_DESK'] },
      { name: 'Rooms',          href: '/rooms',        icon: BuildingOfficeIcon,        roles: ['ADMIN', 'MANAGER', 'FRONT_DESK', 'HOUSEKEEPING'] },
      { name: 'Guests',         href: '/guests',       icon: UsersIcon,                 roles: ['ADMIN', 'MANAGER', 'FRONT_DESK'] },
      { name: 'Check-in / Out', href: '/checkin',      icon: ArrowRightOnRectangleIcon, roles: ['ADMIN', 'MANAGER', 'FRONT_DESK'] },
    ],
  },
  {
    label: 'Operations',
    items: [
      { name: 'Housekeeping', href: '/housekeeping', icon: SparklesIcon,          roles: ['ADMIN', 'MANAGER', 'HOUSEKEEPING'] },
      { name: 'Maintenance',  href: '/maintenance',  icon: WrenchScrewdriverIcon, roles: ['ADMIN', 'MANAGER', 'MAINTENANCE'] },
      { name: 'POS',          href: '/pos',          icon: ShoppingCartIcon,      roles: ['ADMIN', 'MANAGER', 'POS_STAFF'] },
    ],
  },
  {
    label: 'Finance',
    items: [
      { name: 'Billing',     href: '/billing',     icon: BanknotesIcon, roles: ['ADMIN', 'MANAGER', 'ACCOUNTANT', 'FRONT_DESK'] },
      { name: 'Reports',     href: '/reports',     icon: ChartBarIcon,  roles: ['ADMIN', 'MANAGER', 'ACCOUNTANT'] },
      { name: 'Night Audit', href: '/night-audit', icon: MoonIcon,      roles: ['ADMIN', 'MANAGER', 'ACCOUNTANT'] },
    ],
  },
  {
    label: 'Management',
    items: [
      { name: 'Channels',   href: '/channels',   icon: SignalIcon,                roles: ['ADMIN', 'MANAGER'] },
      { name: 'Rates',      href: '/rates',      icon: TagIcon,                   roles: ['ADMIN', 'MANAGER'] },
      { name: 'Users',      href: '/users',      icon: UserGroupIcon,             roles: ['ADMIN', 'MANAGER'] },
      { name: 'Property',   href: '/property',   icon: BuildingLibraryIcon,       roles: ['ADMIN'] },
      { name: 'Audit Logs', href: '/audit-logs', icon: ClipboardDocumentListIcon, roles: ['ADMIN'] },
    ],
  },
  {
    items: [
      { name: 'Settings', href: '/settings', icon: Cog6ToothIcon, roles: ALL_ROLES },
    ],
  },
];

const ROLE_BADGE: Record<string, string> = {
  ADMIN:        'bg-red-50    text-red-600',
  MANAGER:      'bg-violet-50 text-violet-600',
  FRONT_DESK:   'bg-blue-50   text-blue-600',
  HOUSEKEEPING: 'bg-emerald-50 text-emerald-600',
  MAINTENANCE:  'bg-orange-50 text-orange-600',
  ACCOUNTANT:   'bg-amber-50  text-amber-600',
  POS_STAFF:    'bg-pink-50   text-pink-600',
  GUEST:        'bg-slate-100 text-slate-600',
  SUPERADMIN:   'bg-amber-100 text-amber-800',
};

export default function Layout({ children, title }: LayoutProps) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    }
    return false;
  });

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed));
  }, [sidebarCollapsed]);

  const allItems = navGroups.flatMap((g) => g.items);

  const isSuperAdmin = user?.is_superuser === true;

  // Superadmin gets a dedicated system-level menu — NOT per-hotel menus
  const superAdminNavGroups: NavGroup[] = [
    {
      items: [
        { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, roles: [] },
      ],
    },
    {
      label: 'Properties',
      items: [
        { name: 'All Properties', href: '/property',   icon: GlobeAltIcon,          roles: [] },
        { name: 'System Users',   href: '/users',      icon: UserGroupIcon,         roles: [] },
      ],
    },
    {
      label: 'System',
      items: [
        { name: 'Reports',    href: '/reports',     icon: ChartBarIcon,              roles: [] },
        { name: 'Audit Logs', href: '/audit-logs',  icon: ClipboardDocumentListIcon, roles: [] },
        { name: 'Settings',   href: '/settings',    icon: Cog6ToothIcon,             roles: [] },
      ],
    },
  ];

  const visibleGroups = isSuperAdmin
    ? superAdminNavGroups
    : navGroups
        .map((group) => ({
          ...group,
          items: group.items.filter((item) => user?.role && item.roles.includes(user.role)),
        }))
        .filter((group) => group.items.length > 0);

  const currentItem = allItems.find(
    (item) =>
      pathname === item.href ||
      (item.href !== '/dashboard' && pathname.startsWith(item.href + '/')),
  );
  const isAllowed = isSuperAdmin || !currentItem || !user?.role || currentItem.roles.includes(user.role);
  const currentTitle = title || currentItem?.name || 'Dashboard';

  const userInitials = user
    ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase()
    : '?';
  const roleBadge = isSuperAdmin
    ? ROLE_BADGE['SUPERADMIN']
    : (user?.role ? (ROLE_BADGE[user.role] ?? 'bg-slate-100 text-slate-600') : '');
  const roleLabel = isSuperAdmin ? 'SUPERADMIN' : (user?.role?.replace('_', ' ') ?? '');

  /* ---- Sidebar JSX (reused by desktop & mobile drawer) ---- */
  const sidebarContent = (collapsed: boolean) => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className={clsx(
        'flex items-center h-16 border-b border-white/10 flex-shrink-0',
        collapsed ? 'justify-center px-2' : 'gap-3 px-5',
      )}>
        <div className="w-9 h-9 rounded-xl bg-blue-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-900/40">
          <BuildingLibraryIcon className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-white font-bold text-[15px] leading-none tracking-tight">Hotel PMS</p>
            <p className="text-slate-400 text-[11px] mt-1 truncate max-w-[140px]">
              {isSuperAdmin ? 'System Administrator' : (user?.assigned_property?.name ?? 'Property Management')}
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className={clsx('flex-1 overflow-y-auto py-4', collapsed ? 'px-1' : 'px-3')}>
        {visibleGroups.map((group, gi) => (
          <div key={gi} className={gi > 0 ? 'mt-5' : ''}>
            {!collapsed && group.label && (
              <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-500 select-none">
                {group.label}
              </p>
            )}
            {collapsed && group.label && gi > 0 && (
              <div className="my-2 mx-1 border-t border-slate-700/50" />
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const active =
                  pathname === item.href ||
                  (item.href !== '/dashboard' && pathname.startsWith(item.href + '/'));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setSidebarOpen(false)}
                    title={collapsed ? item.name : undefined}
                    className={clsx(
                      'group flex items-center rounded-xl text-sm transition-all duration-150 select-none',
                      collapsed ? 'justify-center p-2.5' : 'gap-3 px-3 py-2.5',
                      active
                        ? 'bg-white text-slate-900 font-semibold shadow-sm'
                        : 'text-slate-400 font-medium hover:bg-slate-800 hover:text-white',
                    )}
                  >
                    <item.icon
                      className={clsx(
                        'w-[18px] h-[18px] flex-shrink-0 transition-colors',
                        active
                          ? 'text-blue-600'
                          : 'text-slate-500 group-hover:text-slate-300',
                      )}
                    />
                    {!collapsed && (
                      <>
                        <span className="flex-1 truncate">{item.name}</span>
                        {active && (
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0" />
                        )}
                      </>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="flex-shrink-0 border-t border-white/10 p-3">
        {collapsed ? (
          <div className="flex flex-col items-center gap-1">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow">
              {userInitials}
            </div>
            <button
              onClick={logout}
              title="Sign out"
              className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-700 transition-colors"
            >
              <ArrowLeftOnRectangleIcon className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-slate-800 transition-colors group">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow">
              {userInitials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate leading-none">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-slate-500 text-[11px] mt-0.5 truncate group-hover:text-slate-400">
                {user?.email}
              </p>
            </div>
            <button
              onClick={logout}
              title="Sign out"
              className="flex-shrink-0 p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-700 transition-colors"
            >
              <ArrowLeftOnRectangleIcon className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Desktop sidebar */}
      <aside className={clsx('hidden md:flex flex-col bg-[#0f172a] flex-shrink-0 transition-[width] duration-300 ease-in-out', sidebarCollapsed ? 'w-16' : 'w-60 lg:w-64')}>
        {sidebarContent(sidebarCollapsed)}
      </aside>

      {/* Mobile overlay + drawer */}
      {sidebarOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="fixed inset-y-0 left-0 z-50 w-64 flex flex-col bg-[#0f172a] shadow-2xl md:hidden">
            {sidebarContent(false)}
          </aside>
        </>
      )}

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="bg-white border-b border-slate-100 h-16 flex items-center justify-between px-4 sm:px-6 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors"
            >
              <Bars3Icon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="hidden md:flex p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors"
            >
              <Bars3Icon className="w-5 h-5" />
            </button>
            <nav className="hidden sm:flex items-center gap-1.5 text-sm">
              <span className="text-slate-400">Home</span>
              <span className="text-slate-300">/</span>
              <span className="text-slate-800 font-semibold">{currentTitle}</span>
            </nav>
            <span className="sm:hidden text-base font-semibold text-slate-800">{currentTitle}</span>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2">
            <div className="hidden lg:flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-50 transition-all">
              <MagnifyingGlassIcon className="w-4 h-4 text-slate-400 flex-shrink-0" />
              <input
                type="text"
                placeholder="Search..."
                className="bg-transparent text-sm text-slate-600 placeholder-slate-400 outline-none w-36"
              />
            </div>
            <button className="relative p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors">
              <BellIcon className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-1.5 h-1.5 bg-red-500 rounded-full ring-2 ring-white" />
            </button>
            <div className="flex items-center gap-2 pl-2 border-l border-slate-100 ml-1">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                {userInitials}
              </div>
              {(user?.role || isSuperAdmin) && (
                <span className={clsx('hidden sm:inline text-xs font-semibold px-2.5 py-1 rounded-full', roleBadge)}>
                  {roleLabel}
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {isAllowed ? (
            children
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-4 p-8">
              <div className="w-20 h-20 bg-red-50 rounded-3xl flex items-center justify-center">
                <XMarkIcon className="w-10 h-10 text-red-400" />
              </div>
              <div className="text-center">
                <h2 className="text-xl font-bold text-slate-800">Access Denied</h2>
                <p className="text-slate-500 mt-1 text-sm">
                  You don&apos;t have permission to view this page.
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

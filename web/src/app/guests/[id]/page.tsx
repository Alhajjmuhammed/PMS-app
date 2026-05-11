'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function GuestDetailPage() {
  const router = useRouter();
  useEffect(() => { router.replace('/guests'); }, [router]);
  return null;
}

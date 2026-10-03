'use client';

import dynamic from 'next/dynamic';
import type { HotspotData } from '@/lib/api';

const FireMap = dynamic(
  () => import('@/components/FireMap'),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[500px] items-center justify-center">
        Loading fire map...
      </div>
    ),
  }
);

export default function FireMapWrapper({ hotspotsData, center }: { hotspotsData: HotspotData[]; center: [number, number] | null }) {
  return <FireMap hotspotsData={hotspotsData} center={center} />;
}
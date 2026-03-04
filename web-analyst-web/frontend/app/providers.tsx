'use client';

import { SpaceProvider } from '../src/features/spaces/application/SpaceContext';

export default function Providers({ children }: { children: React.ReactNode }) {
  return <SpaceProvider>{children}</SpaceProvider>;
}

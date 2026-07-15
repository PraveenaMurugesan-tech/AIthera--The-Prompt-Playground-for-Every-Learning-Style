import React from 'react';
import { ProviderStatusCard } from './ProviderStatusCard';
import type { ExtendedProviderState } from './ProviderStatusCard';

interface ProviderGridProps {
  providers: ExtendedProviderState[];
}

export const ProviderGrid: React.FC<ProviderGridProps> = ({ providers }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {providers.map((provider) => (
        <ProviderStatusCard key={provider.id} provider={provider} />
      ))}
    </div>
  );
};

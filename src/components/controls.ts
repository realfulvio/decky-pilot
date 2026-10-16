import type { ComponentType, ReactNode } from 'react';
export interface Controls {
  Group: ComponentType<{children: ReactNode; className?: string; direction?: 'vertical' | 'horizontal'}>;
  Button: ComponentType<{children: ReactNode; onClick: () => void; disabled?: boolean}>;
  Input: ComponentType<{label: string; value: string; onChange: (value: string) => void; secret?: boolean}>;
  Toggle: ComponentType<{label: string; checked: boolean; onChange: (value: boolean) => void}>;
  Select: ComponentType<{label: string; value: string; options: {value: string; label: string}[]; onChange: (value: string) => void}>;
  Section: ComponentType<{title: string; children: ReactNode}>;
}

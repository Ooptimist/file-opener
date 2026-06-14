import type { CSSProperties } from 'react';

export const modalBackdropStyle: CSSProperties = {
  backdropFilter: 'blur(10px)',
  WebkitBackdropFilter: 'blur(10px)'
};

export const modalSurfaceStyle: CSSProperties = {
  backdropFilter: 'blur(24px) saturate(150%)',
  WebkitBackdropFilter: 'blur(24px) saturate(150%)'
};

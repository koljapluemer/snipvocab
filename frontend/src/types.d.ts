declare global {
  interface Window {
    goatcounter: {
      no_onload?: boolean;
      count: (options: { path: string }) => void;
    };
  }
}

export {}; 
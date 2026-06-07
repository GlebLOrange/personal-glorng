/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GA_ENABLED?: string;
  readonly VITE_GA_ID?: string;
  readonly VITE_AI_CHAT_ENABLED?: string;
  readonly VITE_AI_SEARCH_ENABLED?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}

interface Window {
  dataLayer?: unknown[][];
  gtag?: (...args: unknown[]) => void;
}

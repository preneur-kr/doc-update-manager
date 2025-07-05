export interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatResponse {
  answer: string;
  is_fallback: boolean;
  timestamp?: string;
  search_results?: any[];
}

// Vite env type augmentation
interface ImportMetaEnv {
  VITE_API_BASE_URL: string;
  DEV: boolean;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import viteCompression from 'vite-plugin-compression';

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    // 번들 분석기 (개발/빌드 시 사용)
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
    // Gzip 압축 (프로덕션)
    ...(mode === 'production' ? [
      viteCompression({
        algorithm: 'gzip',
        ext: '.gz',
      }),
      viteCompression({
        algorithm: 'brotliCompress',
        ext: '.br',
      })
    ] : [])
  ],
  // 트리 셰이킹 최적화 (프로덕션에서만)
  esbuild: mode === 'production' ? {
    drop: ['console', 'debugger'], // 프로덕션에서 console 제거
  } : {},
  define: {
    __DEV__: JSON.stringify(mode === 'development'), // 개발 모드 플래그
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    target: 'esnext',
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // React 핵심 라이브러리
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom')) {
            return 'vendor-react';
          }
          
          // 이모지 피커 (별도 청크로 분리)
          if (id.includes('emoji-picker-react')) {
            return 'vendor-emoji';
          }
          
          // 아이콘 라이브러리
          if (id.includes('@heroicons/react')) {
            return 'vendor-icons';
          }
          
          // 기타 node_modules 라이브러리들
          if (id.includes('node_modules')) {
            return 'vendor-libs';
          }
          
          // 훅과 유틸리티 분리
          if (id.includes('/hooks/') || id.includes('/utils/')) {
            return 'app-utils';
          }
          
          // 컴포넌트 분리
          if (id.includes('/components/')) {
            return 'app-components';
          }
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
    // 청크 크기 경고 임계값 증가 (기본 500kb에서 1mb로)
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 5174,
    host: true,
  },
  preview: {
    port: 4173,
    host: true,
  },
}));

/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'src/**/*.test.{ts,tsx}',
        'src/**/*.spec.{ts,tsx}',
        'src/vite-env.d.ts',
        'dist/',
        'coverage/',
        'public/',
        '*.config.{js,ts}',
        'src/main.tsx', // 앱 진입점은 제외
        'src/styles/', // 스타일 파일들 제외
      ],
      include: [
        'src/**/*.{ts,tsx}',
      ],
      all: true,
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      }
    },
    // 테스트 파일 매칭 패턴
    include: [
      'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ],
    // 테스트 타임아웃 설정
    testTimeout: 10000,
    hookTimeout: 10000,
    // 병렬 테스트 실행 설정
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        minThreads: 1,
        maxThreads: 4
      }
    },
    // 워치 모드 설정
    watch: false,
    // 리포터 설정
    reporters: ['verbose'],
  },
  // Vitest와 Vite의 resolve 설정 공유
  resolve: {
    alias: {
      '@': '/src',
    },
  },
}) 
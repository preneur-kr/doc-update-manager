import '@testing-library/jest-dom'
import { afterEach, vi, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'

// 각 테스트 후 DOM 정리
afterEach(() => {
  cleanup()
})

// 전역 테스트 설정
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// ResizeObserver 모킹 (일부 컴포넌트에서 필요)
Object.defineProperty(globalThis, 'ResizeObserver', {
  value: vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })),
  writable: true,
})

// IntersectionObserver 모킹
Object.defineProperty(globalThis, 'IntersectionObserver', {
  value: vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
    unobserve: vi.fn(),
  })),
  writable: true,
})

// window.scrollTo 모킹
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true,
})

// localStorage 모킹
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// sessionStorage 모킹
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
})

// fetch 모킹을 위한 글로벌 설정
Object.defineProperty(globalThis, 'fetch', {
  value: vi.fn(),
  writable: true,
})

// console 에러 억제 (테스트 중 불필요한 로그 제거)
const originalError = console.error
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
}) 
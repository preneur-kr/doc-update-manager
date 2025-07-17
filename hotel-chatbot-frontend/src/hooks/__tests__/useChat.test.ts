import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useChat } from '../useChat'
import { ChatService } from '../../services/chatService'

// ChatService 모킹
vi.mock('../../services/chatService')

const mockChatService = vi.mocked(ChatService)

describe('useChat', () => {
  let mockServiceInstance: any

  beforeEach(() => {
    mockServiceInstance = {
      initializeConnection: vi.fn(),
      sendMessage: vi.fn(),
      destroy: vi.fn(),
    }
    
    mockChatService.mockImplementation(() => mockServiceInstance)
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('초기화', () => {
    it('초기 상태가 올바르게 설정되어야 함', () => {
      const { result } = renderHook(() => useChat())

      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0].content).toContain('안녕하세요')
      expect(result.current.isLoading).toBe(false)
      expect(result.current.apiStatus).toBe('checking')
      expect(result.current.isChatStarted).toBe(false)
    })

    it('ChatService가 올바른 옵션으로 초기화되어야 함', () => {
      const mockOnError = vi.fn()
      renderHook(() => useChat({ onError: mockOnError }))

      expect(mockChatService).toHaveBeenCalledWith({
        onApiStatusChange: expect.any(Function),
        onError: mockOnError,
      })
    })

    it('autoStart가 true일 때 자동으로 연결을 초기화해야 함', () => {
      renderHook(() => useChat({ autoStart: true }))

      expect(mockServiceInstance.initializeConnection).toHaveBeenCalled()
    })

    it('autoStart가 false일 때 자동 연결을 하지 않아야 함', () => {
      renderHook(() => useChat({ autoStart: false }))

      expect(mockServiceInstance.initializeConnection).not.toHaveBeenCalled()
    })
  })

  describe('메시지 전송', () => {
    it('성공적인 메시지 전송 시 사용자 메시지와 봇 응답이 추가되어야 함', async () => {
      mockServiceInstance.sendMessage.mockResolvedValue({
        success: true,
        response: '테스트 응답입니다.',
      })

      const { result } = renderHook(() => useChat())

      await act(async () => {
        await result.current.sendMessage('테스트 메시지')
      })

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(3) // 웰컴 + 사용자 + 봇
        expect(result.current.messages[1].content).toBe('테스트 메시지')
        expect(result.current.messages[1].isUser).toBe(true)
        expect(result.current.messages[2].content).toBe('테스트 응답입니다.')
        expect(result.current.messages[2].isUser).toBe(false)
      })
    })

    it('빈 메시지는 전송되지 않아야 함', async () => {
      const { result } = renderHook(() => useChat())
      const initialMessageCount = result.current.messages.length

      await act(async () => {
        await result.current.sendMessage('')
      })

      expect(result.current.messages).toHaveLength(initialMessageCount)
      expect(mockServiceInstance.sendMessage).not.toHaveBeenCalled()
    })

    it('공백만 있는 메시지는 전송되지 않아야 함', async () => {
      const { result } = renderHook(() => useChat())
      const initialMessageCount = result.current.messages.length

      await act(async () => {
        await result.current.sendMessage('   ')
      })

      expect(result.current.messages).toHaveLength(initialMessageCount)
      expect(mockServiceInstance.sendMessage).not.toHaveBeenCalled()
    })

    it('메시지 전송 실패 시 에러 메시지가 추가되어야 함', async () => {
      mockServiceInstance.sendMessage.mockResolvedValue({
        success: false,
        response: '전송에 실패했습니다.',
      })

      const { result } = renderHook(() => useChat())

      await act(async () => {
        await result.current.sendMessage('테스트 메시지')
      })

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(3)
        expect(result.current.messages[2].content).toBe('전송에 실패했습니다.')
        expect(result.current.messages[2].isUser).toBe(false)
      })
    })

    it('로딩 상태가 올바르게 관리되어야 함', async () => {
      // 프로미스를 직접 제어하기 위한 설정
      let resolvePromise: (value: any) => void
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      mockServiceInstance.sendMessage.mockReturnValue(promise)

      const { result } = renderHook(() => useChat())

      // 메시지 전송 시작
      act(() => {
        result.current.sendMessage('테스트 메시지')
      })

      // 로딩 상태 확인
      expect(result.current.isLoading).toBe(true)

      // 프로미스 해결
      await act(async () => {
        resolvePromise!({ success: true, response: '응답' })
        await promise
      })

      // 로딩 완료 확인
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })
  })

  describe('채팅 제어', () => {
    it('채팅 시작 시 isChatStarted가 true가 되어야 함', () => {
      const { result } = renderHook(() => useChat())

      act(() => {
        result.current.startChat()
      })

      expect(result.current.isChatStarted).toBe(true)
    })

    it('채팅 종료 시 상태가 초기화되어야 함', () => {
      const { result } = renderHook(() => useChat())

      // 채팅 시작 및 메시지 추가
      act(() => {
        result.current.startChat()
        result.current.addMessage({
          id: 'test',
          content: '테스트 메시지',
          isUser: true,
          timestamp: new Date(),
        })
      })

      expect(result.current.isChatStarted).toBe(true)
      expect(result.current.messages.length).toBeGreaterThan(1)

      // 채팅 종료
      act(() => {
        result.current.exitChat()
      })

      expect(result.current.isChatStarted).toBe(false)
      expect(result.current.messages).toHaveLength(1) // 웰컴 메시지만 남음
    })
  })

  describe('메시지 관리', () => {
    it('개별 메시지 추가가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useChat())
      const testMessage = {
        id: 'test-1',
        content: '테스트 메시지',
        isUser: true,
        timestamp: new Date(),
      }

      act(() => {
        result.current.addMessage(testMessage)
      })

      expect(result.current.messages).toContain(testMessage)
    })

    it('다중 메시지 추가가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useChat())
      const testMessages = [
        {
          id: 'test-1',
          content: '메시지 1',
          isUser: true,
          timestamp: new Date(),
        },
        {
          id: 'test-2',
          content: '메시지 2',
          isUser: false,
          timestamp: new Date(),
        },
      ]

      act(() => {
        result.current.addMessages(testMessages)
      })

      expect(result.current.messages).toEqual(
        expect.arrayContaining(testMessages)
      )
    })

    it('히스토리 클리어 시 웰컴 메시지만 남아야 함', () => {
      const { result } = renderHook(() => useChat())

      // 메시지 추가
      act(() => {
        result.current.addMessage({
          id: 'test',
          content: '테스트',
          isUser: true,
          timestamp: new Date(),
        })
      })

      expect(result.current.messages.length).toBeGreaterThan(1)

      // 히스토리 클리어
      act(() => {
        result.current.clearHistory()
      })

      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0].content).toContain('안녕하세요')
    })
  })

  describe('연결 관리', () => {
    it('수동 연결 초기화가 작동해야 함', () => {
      const { result } = renderHook(() => useChat({ autoStart: false }))

      act(() => {
        result.current.initializeConnection()
      })

      expect(mockServiceInstance.initializeConnection).toHaveBeenCalled()
    })
  })

  describe('정리(Cleanup)', () => {
    it('컴포넌트 언마운트 시 ChatService가 정리되어야 함', () => {
      const { unmount } = renderHook(() => useChat())

      unmount()

      expect(mockServiceInstance.destroy).toHaveBeenCalled()
    })
  })

  describe('API 상태 변경', () => {
    it('API 상태 변경이 올바르게 반영되어야 함', () => {
      const { result } = renderHook(() => useChat())

      // ChatService 생성자에 전달된 onApiStatusChange 함수를 가져옴
      const [[{ onApiStatusChange }]] = mockChatService.mock.calls

      act(() => {
        onApiStatusChange('connected')
      })

      expect(result.current.apiStatus).toBe('connected')

      act(() => {
        onApiStatusChange('disconnected')
      })

      expect(result.current.apiStatus).toBe('disconnected')
    })
  })
}) 
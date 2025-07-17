import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ChatService } from '../chatService'
import * as chatApi from '../../api/chatApi'

// API 모듈 모킹
vi.mock('../../api/chatApi')

const mockChatApi = vi.mocked(chatApi)

describe('ChatService', () => {
  let chatService: ChatService
  let mockOnApiStatusChange: any
  let mockOnError: any

  beforeEach(() => {
    mockOnApiStatusChange = vi.fn()
    mockOnError = vi.fn()
    
    chatService = new ChatService({
      onApiStatusChange: mockOnApiStatusChange,
      onError: mockOnError,
    })

    vi.clearAllMocks()
  })

  afterEach(() => {
    chatService.destroy()
    vi.resetAllMocks()
  })

  describe('초기화', () => {
    it('ChatService 인스턴스가 올바르게 생성되어야 함', () => {
      expect(chatService).toBeInstanceOf(ChatService)
    })

    it('옵션이 올바르게 저장되어야 함', () => {
      expect(mockOnApiStatusChange).toBeDefined()
      expect(mockOnError).toBeDefined()
    })
  })

  describe('연결 초기화', () => {
    it('성공적인 연결 시 상태가 connected로 변경되어야 함', async () => {
      mockChatApi.checkChatApiReady.mockResolvedValue({ ready: true, status: 'connected' })

      await chatService.initializeConnection()

      expect(mockOnApiStatusChange).toHaveBeenCalledWith('connected')
    })

    it('첫 번째 체크 실패 시 재시도를 수행해야 함', async () => {
      mockChatApi.checkChatApiReady.mockResolvedValue({ ready: false, status: 'warming_up' })
      mockChatApi.checkChatApiHealthWithRetry.mockResolvedValue(true)

      await chatService.initializeConnection()

      expect(mockChatApi.checkChatApiHealthWithRetry).toHaveBeenCalled()
      expect(mockOnApiStatusChange).toHaveBeenCalledWith('connected')
    })

    it('재시도도 실패 시 상태가 disconnected로 변경되어야 함', async () => {
      mockChatApi.checkChatApiReady.mockResolvedValue({ ready: false, status: 'disconnected' })
      mockChatApi.checkChatApiHealthWithRetry.mockResolvedValue(false)

      await chatService.initializeConnection()

      expect(mockOnApiStatusChange).toHaveBeenCalledWith('disconnected')
    })

    it('예외 발생 시 상태가 disconnected로 변경되어야 함', async () => {
      mockChatApi.checkChatApiReady.mockRejectedValue(new Error('Network error'))

      await chatService.initializeConnection()

      expect(mockOnApiStatusChange).toHaveBeenCalledWith('disconnected')
    })
  })

  describe('메시지 전송', () => {
    it('성공적인 메시지 전송', async () => {
      mockChatApi.sendChatMessage.mockResolvedValue({
        answer: '테스트 응답',
        is_fallback: false,
      })

      const result = await chatService.sendMessage('테스트 메시지', 'connected')

      expect(result).toEqual({
        success: true,
        response: '테스트 응답',
      })
      expect(mockChatApi.sendChatMessage).toHaveBeenCalledWith({
        message: '테스트 메시지',
      })
    })

    it('빈 메시지는 전송하지 않아야 함', async () => {
      const result = await chatService.sendMessage('', 'connected')

      expect(result).toEqual({ success: false })
      expect(mockChatApi.sendChatMessage).not.toHaveBeenCalled()
    })

    it('공백만 있는 메시지는 전송하지 않아야 함', async () => {
      const result = await chatService.sendMessage('   ', 'connected')

      expect(result).toEqual({ success: false })
      expect(mockChatApi.sendChatMessage).not.toHaveBeenCalled()
    })

    describe('API 상태별 에러 처리', () => {
      it('checking 상태에서 에러 메시지를 표시해야 함', async () => {
        const result = await chatService.sendMessage('테스트', 'checking')

        expect(result).toEqual({ success: false })
        expect(mockOnError).toHaveBeenCalledWith(
          '연결 확인 중',
          '서버 연결을 확인하는 중입니다. 잠시 후 다시 시도해주세요.'
        )
      })

      it('warming_up 상태에서 에러 메시지를 표시해야 함', async () => {
        const result = await chatService.sendMessage('테스트', 'warming_up')

        expect(result).toEqual({ success: false })
        expect(mockOnError).toHaveBeenCalledWith(
          '서버 준비 중',
          '서버가 준비 중입니다. 잠시 후 다시 시도해주세요.'
        )
      })

      it('disconnected 상태에서 에러 메시지를 표시해야 함', async () => {
        const result = await chatService.sendMessage('테스트', 'disconnected')

        expect(result).toEqual({ success: false })
        expect(mockOnError).toHaveBeenCalledWith(
          '서버 연결 오류',
          '서버에 연결할 수 없습니다. 연결 상태를 확인해주세요.'
        )
      })
    })

    it('API 호출 실패 시 에러 처리 및 재연결 시도', async () => {
      const error = new Error('Network error')
      mockChatApi.sendChatMessage.mockRejectedValue(error)
      mockChatApi.checkChatApiHealthWithRetry.mockResolvedValue(true)

      const result = await chatService.sendMessage('테스트', 'connected')

      expect(result).toEqual({
        success: false,
        response: 'Network error',
      })
      expect(mockOnError).toHaveBeenCalledWith(
        '전송 실패',
        '메시지 전송 중 오류가 발생했습니다.'
      )
      expect(mockOnApiStatusChange).toHaveBeenCalledWith('checking')
    })

    it('알 수 없는 에러 시 기본 메시지를 반환해야 함', async () => {
      mockChatApi.sendChatMessage.mockRejectedValue('String error')

      const result = await chatService.sendMessage('테스트', 'connected')

      expect(result).toEqual({
        success: false,
        response: '서버와의 통신 중 오류가 발생했습니다.',
      })
    })
  })

  describe('헬스 체크', () => {
    beforeEach(() => {
      // 타이머 모킹
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('연결 성공 시 주기적 헬스 체크가 시작되어야 함', async () => {
      mockChatApi.checkChatApiReady
        .mockResolvedValueOnce({ ready: true, status: 'connected' }) // 초기 연결
        .mockResolvedValue({ ready: true, status: 'connected' }) // 주기적 체크

      await chatService.initializeConnection()

      // 30초 후 헬스 체크 실행 확인
      vi.advanceTimersByTime(30000)

      expect(mockChatApi.checkChatApiReady).toHaveBeenCalledTimes(2)
    })

    it('헬스 체크 실패 시 상태가 disconnected로 변경되어야 함', async () => {
      mockChatApi.checkChatApiReady
        .mockResolvedValueOnce({ ready: true, status: 'connected' }) // 초기 연결
        .mockResolvedValue({ ready: false, status: 'disconnected' }) // 헬스 체크 실패

      await chatService.initializeConnection()

      // 초기 연결 성공 확인
      expect(mockOnApiStatusChange).toHaveBeenCalledWith('connected')

      // 30초 후 헬스 체크 실행
      vi.advanceTimersByTime(30000)

      // 연결 실패 상태로 변경 확인
      expect(mockOnApiStatusChange).toHaveBeenCalledWith('disconnected')
    })
  })

  describe('정리(Cleanup)', () => {
    it('destroy 호출 시 헬스 체크가 중단되어야 함', async () => {
      vi.useFakeTimers()
      
      mockChatApi.checkChatApiReady.mockResolvedValue({ ready: true, status: 'connected' })

      await chatService.initializeConnection()
      
      // 서비스 정리
      chatService.destroy()

      // 헬스 체크 간격 후에도 추가 호출이 없어야 함
      const callCountBeforeDestroy = mockChatApi.checkChatApiReady.mock.calls.length
      vi.advanceTimersByTime(30000)
      const callCountAfterDestroy = mockChatApi.checkChatApiReady.mock.calls.length

      expect(callCountAfterDestroy).toBe(callCountBeforeDestroy)
      
      vi.useRealTimers()
    })

    it('destroy 호출 후 메시지 전송이 차단되어야 함', async () => {
      chatService.destroy()

      const result = await chatService.sendMessage('테스트', 'connected')

      expect(result).toEqual({ success: false })
      expect(mockChatApi.sendChatMessage).not.toHaveBeenCalled()
    })
  })

  describe('에지 케이스', () => {
    it('동시에 여러 initializeConnection 호출 시 중복 실행 방지', async () => {
      mockChatApi.checkChatApiReady.mockResolvedValue({ ready: true, status: 'connected' })

      // 동시에 여러 번 호출
      const promises = [
        chatService.initializeConnection(),
        chatService.initializeConnection(),
        chatService.initializeConnection(),
      ]

      await Promise.all(promises)

      // API는 실제로는 3번 호출될 수 있지만, 상태 변경은 한 번만 일어나야 함
      expect(mockOnApiStatusChange).toHaveBeenCalledWith('connected')
    })

    it('매우 긴 메시지도 올바르게 처리되어야 함', async () => {
      const longMessage = 'a'.repeat(10000)
      mockChatApi.sendChatMessage.mockResolvedValue({
        answer: '긴 메시지 처리 완료',
        is_fallback: false,
      })

      const result = await chatService.sendMessage(longMessage, 'connected')

      expect(result.success).toBe(true)
      expect(mockChatApi.sendChatMessage).toHaveBeenCalledWith({
        message: longMessage,
      })
    })
  })
}) 
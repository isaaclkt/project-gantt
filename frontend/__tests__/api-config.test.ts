import { ApiError, getErrorMessage, ERROR_CODES } from '@/lib/api-config'

describe('api-config', () => {
  describe('ApiError', () => {
    it('creates error with correct properties', () => {
      const error = new ApiError('test error', 401, ERROR_CODES.UNAUTHORIZED)
      expect(error.message).toBe('test error')
      expect(error.status).toBe(401)
      expect(error.code).toBe('UNAUTHORIZED')
      expect(error.name).toBe('ApiError')
    })

    it('defaults code to UNKNOWN_ERROR', () => {
      const error = new ApiError('test', 500)
      expect(error.code).toBe('UNKNOWN_ERROR')
    })

    it('is instance of Error', () => {
      const error = new ApiError('test', 400)
      expect(error).toBeInstanceOf(Error)
      expect(error).toBeInstanceOf(ApiError)
    })
  })

  describe('getErrorMessage', () => {
    it('returns message for NETWORK_ERROR', () => {
      const error = new ApiError('', 0, ERROR_CODES.NETWORK_ERROR)
      const msg = getErrorMessage(error)
      expect(msg).toContain('conectar')
    })

    it('returns message for UNAUTHORIZED', () => {
      const error = new ApiError('', 401, ERROR_CODES.UNAUTHORIZED)
      const msg = getErrorMessage(error)
      expect(msg).toContain('expirada')
    })

    it('returns message for FORBIDDEN', () => {
      const error = new ApiError('', 403, ERROR_CODES.FORBIDDEN)
      const msg = getErrorMessage(error)
      expect(msg).toContain('permissão')
    })

    it('returns message for NOT_FOUND', () => {
      const error = new ApiError('', 404, ERROR_CODES.NOT_FOUND)
      const msg = getErrorMessage(error)
      expect(msg).toContain('encontrado')
    })

    it('returns message for VALIDATION_ERROR with custom message', () => {
      const error = new ApiError('Email is required', 400, ERROR_CODES.VALIDATION_ERROR)
      const msg = getErrorMessage(error)
      expect(msg).toBe('Email is required')
    })

    it('returns message for SERVER_ERROR', () => {
      const error = new ApiError('', 500, ERROR_CODES.SERVER_ERROR)
      const msg = getErrorMessage(error)
      expect(msg).toContain('servidor')
    })

    it('returns generic message for regular Error', () => {
      const error = new Error('Something went wrong')
      const msg = getErrorMessage(error)
      expect(msg).toBe('Something went wrong')
    })

    it('returns generic message for unknown type', () => {
      const msg = getErrorMessage('string error')
      expect(msg).toContain('inesperado')
    })
  })

  describe('ERROR_CODES', () => {
    it('has all expected codes', () => {
      expect(ERROR_CODES.NETWORK_ERROR).toBe('NETWORK_ERROR')
      expect(ERROR_CODES.UNAUTHORIZED).toBe('UNAUTHORIZED')
      expect(ERROR_CODES.FORBIDDEN).toBe('FORBIDDEN')
      expect(ERROR_CODES.NOT_FOUND).toBe('NOT_FOUND')
      expect(ERROR_CODES.VALIDATION_ERROR).toBe('VALIDATION_ERROR')
      expect(ERROR_CODES.SERVER_ERROR).toBe('SERVER_ERROR')
      expect(ERROR_CODES.UNKNOWN_ERROR).toBe('UNKNOWN_ERROR')
    })
  })
})

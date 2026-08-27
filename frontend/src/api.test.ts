import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { listDocuments, queryApi } from './api'

beforeEach(() => {
  vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.test')
  sessionStorage.setItem('id_token', 'test-token')
})

afterEach(() => {
  vi.unstubAllEnvs()
  vi.restoreAllMocks()
  sessionStorage.clear()
})

test('maps the private document API contract without exposing owner data', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
    documents: [{ documentId: 'doc-a', filename: 'evidence.txt', status: 'READY', sizeBytes: 1024 }],
  }), { status: 200 })))

  const documents = await listDocuments()

  expect(documents).toEqual([{ id: 'doc-a', filename: 'evidence.txt', status: 'READY', sizeLabel: '1 KB' }])
  expect(fetch).toHaveBeenCalledWith('https://api.example.test/documents', expect.objectContaining({
    headers: expect.objectContaining({ authorization: 'Bearer test-token' }),
  }))
})

test('sends an optional document scope and returns citations', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
    answer: 'Grounded.',
    citations: [{ documentId: 'doc-a', filename: 'evidence.txt' }],
    insufficientContext: false,
  }), { status: 200 })))

  const answer = await queryApi.ask('What is supported?', 'doc-a')
  const request = vi.mocked(fetch).mock.calls[0][1]

  expect(JSON.parse(String(request?.body))).toEqual({ question: 'What is supported?', documentId: 'doc-a' })
  expect(answer.citations).toHaveLength(1)
})

test('clears an expired session after an unauthorized response', async () => {
  const expired = vi.fn()
  window.addEventListener('auth:expired', expired)
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 401 })))

  await expect(listDocuments()).rejects.toThrow('Your session expired')

  expect(sessionStorage.getItem('id_token')).toBeNull()
  expect(expired).toHaveBeenCalledOnce()
  window.removeEventListener('auth:expired', expired)
})

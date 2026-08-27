import { accessToken, refreshCognitoSession, signOut } from './auth'
import type { DocumentItem, DocumentStatus, DocumentsApi, QueryAnswer, QueryApi } from './contracts'

const REQUEST_TIMEOUT_MS = 20_000
const INGESTION_ATTEMPTS = 20

type ApiDocument = {
  documentId: string
  filename: string
  status: DocumentStatus
  sizeBytes?: number
}

function apiBaseUrl(): string {
  const value = import.meta.env.VITE_API_BASE_URL
  if (!value) throw new Error('The private API is not configured.')
  return value
}

function mapDocument(document: ApiDocument): DocumentItem {
  return {
    id: document.documentId,
    filename: document.filename,
    status: document.status,
    sizeLabel: `${Math.max(1, Math.ceil((document.sizeBytes ?? 0) / 1024))} KB`,
  }
}

async function authenticatedFetch(path: string, init: RequestInit = {}, retry = true): Promise<Response> {
  const token = accessToken()
  if (!token) throw new Error('Your session expired. Sign in again.')
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  try {
    const response = await fetch(`${apiBaseUrl()}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { ...init.headers, authorization: `Bearer ${token}` },
    })
    if (response.status === 401 && retry && await refreshCognitoSession()) {
      return authenticatedFetch(path, init, false)
    }
    if (response.status === 401) {
      signOut()
      window.dispatchEvent(new Event('auth:expired'))
      throw new Error('Your session expired. Sign in again.')
    }
    return response
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('The request timed out. Please try again.')
    }
    throw error
  } finally {
    window.clearTimeout(timer)
  }
}

async function requireOk(response: Response, message: string): Promise<Response> {
  if (!response.ok) throw new Error(message)
  return response
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const response = await requireOk(
    await authenticatedFetch('/documents'),
    'Could not load your private documents.',
  )
  const payload: { documents: ApiDocument[] } = await response.json()
  return payload.documents.map(mapDocument)
}

async function waitForReady(documentId: string): Promise<DocumentItem> {
  for (let attempt = 0; attempt < INGESTION_ATTEMPTS; attempt += 1) {
    const response = await requireOk(
      await authenticatedFetch(`/documents/${documentId}`),
      'Could not read ingestion status.',
    )
    const payload: { document: ApiDocument } = await response.json()
    const document = mapDocument(payload.document)
    if (document.status === 'READY') return document
    if (document.status === 'FAILED') throw new Error('Document ingestion failed safely.')
    await new Promise((resolve) => window.setTimeout(resolve, Math.min(1_500 + attempt * 250, 4_000)))
  }
  throw new Error('Indexing is still running. Reload later to see its current status.')
}

export const documentsApi: DocumentsApi = {
  async upload(file): Promise<DocumentItem> {
    const preparedResponse = await requireOk(
      await authenticatedFetch('/documents/presign', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ filename: file.name, sizeBytes: file.size, contentType: file.type }),
      }),
      'Could not prepare a private upload.',
    )
    const prepared: { documentId: string; uploadUrl: string } = await preparedResponse.json()
    let uploaded: Response
    try {
      uploaded = await fetch(prepared.uploadUrl, {
        method: 'PUT',
        headers: { 'content-type': file.type },
        body: file,
      })
    } catch {
      throw new Error('Could not reach private storage.')
    }
    if (!uploaded.ok) throw new Error('The private upload failed.')
    await requireOk(
      await authenticatedFetch(`/documents/${prepared.documentId}/finalize`, { method: 'POST' }),
      'The upload arrived but could not be finalized.',
    )
    await requireOk(
      await authenticatedFetch(`/documents/${prepared.documentId}/ingest`, { method: 'POST' }),
      'The upload arrived but indexing could not start.',
    )
    return waitForReady(prepared.documentId)
  },
}

export const queryApi: QueryApi = {
  async ask(question, documentId): Promise<QueryAnswer> {
    const response = await requireOk(
      await authenticatedFetch('/query', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ question: question.trim(), ...(documentId ? { documentId } : {}) }),
      }),
      'The grounded query could not be completed.',
    )
    return response.json()
  },
}

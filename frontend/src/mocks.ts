import { accessToken } from './auth'
import type { DocumentItem, DocumentsApi, DocumentStatus, QueryApi } from './contracts'

function sizeLabel(sizeBytes: number): string {
  return `${Math.max(1, Math.ceil(sizeBytes / 1024))} KB`
}

type ApiDocument = { documentId: string; filename: string; status: DocumentStatus; sizeBytes?: number }

function mapApiDocument(document: ApiDocument): DocumentItem {
  return {
    id: document.documentId,
    filename: document.filename,
    status: document.status,
    sizeLabel: sizeLabel(document.sizeBytes ?? 0),
  }
}

export async function listCognitoDocuments(): Promise<DocumentItem[]> {
  const token = accessToken()
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!token || !apiBaseUrl) return []
  const response = await fetch(`${apiBaseUrl}/documents`, { headers: { authorization: `Bearer ${token}` } })
  if (!response.ok) throw new Error('Could not load your private documents.')
  const payload: { documents: ApiDocument[] } = await response.json()
  return payload.documents.map(mapApiDocument)
}

async function waitForReady(apiBaseUrl: string, token: string, documentId: string): Promise<DocumentItem> {
  for (let attempt = 0; attempt < 12; attempt += 1) {
    const response = await fetch(`${apiBaseUrl}/documents/${documentId}`, { headers: { authorization: `Bearer ${token}` } })
    if (!response.ok) throw new Error('Could not read ingestion status.')
    const payload: { document: ApiDocument } = await response.json()
    const document = mapApiDocument(payload.document)
    if (document.status === 'READY') return document
    if (document.status === 'FAILED') throw new Error('Document ingestion failed safely.')
    await new Promise((resolve) => setTimeout(resolve, 2000))
  }
  throw new Error('Document ingestion is still running; its status will remain available.')
}

export const mockDocumentsApi: DocumentsApi = { async upload(file) { return { id: crypto.randomUUID(), filename: file.name, status: 'READY', sizeLabel: sizeLabel(file.size) } } }
export const mockQueryApi: QueryApi = { async ask(question, documents) { const source = documents[0]; return { answer: `Mocked grounded response: “${question.trim()}” can be investigated using ${source.filename}. Connect the retrieval adapter in a later phase.`, citations: [{ documentId: source.id, filename: source.filename, location: 'local mock source' }], insufficientContext: false } } }

export const cognitoQueryApi: QueryApi = { async ask(question): Promise<import('./contracts').QueryAnswer> {
  const token = accessToken()
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!token || !apiBaseUrl) throw new Error('You must sign in before asking a question.')
  let response: Response
  try {
    response = await fetch(`${apiBaseUrl}/query`, { method: 'POST', headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' }, body: JSON.stringify({ question: question.trim() }) })
  } catch {
    throw new Error('Could not reach the grounded query service.')
  }
  if (!response.ok) throw new Error('The grounded query could not be completed.')
  return response.json()
} }

export const cognitoDocumentsApi: DocumentsApi = { async upload(file): Promise<DocumentItem> {
  const token = accessToken()
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!token || !apiBaseUrl) throw new Error('You must sign in before uploading.')
  let response: Response
  try {
    response = await fetch(`${apiBaseUrl}/documents/presign`, { method: 'POST', headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' }, body: JSON.stringify({ filename: file.name, sizeBytes: file.size, contentType: file.type }) })
  } catch {
    throw new Error('Could not reach the private upload service.')
  }
  if (!response.ok) throw new Error('Could not prepare a private upload.')
  const prepared: { documentId: string; uploadUrl: string } = await response.json()
  let uploaded: Response
  try {
    uploaded = await fetch(prepared.uploadUrl, { method: 'PUT', headers: { 'content-type': file.type }, body: file })
  } catch {
    throw new Error('Could not reach private storage.')
  }
  if (!uploaded.ok) throw new Error('The private upload failed.')
  const finalized = await fetch(`${apiBaseUrl}/documents/${prepared.documentId}/finalize`, { method: 'POST', headers: { authorization: `Bearer ${token}` } })
  if (!finalized.ok) throw new Error('The upload arrived but could not be finalized.')
  const ingestion = await fetch(`${apiBaseUrl}/documents/${prepared.documentId}/ingest`, { method: 'POST', headers: { authorization: `Bearer ${token}` } })
  if (!ingestion.ok) throw new Error('The upload arrived but ingestion could not start.')
  return waitForReady(apiBaseUrl, token, prepared.documentId)
} }

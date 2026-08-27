import { accessToken } from './auth'
import type { DocumentItem, DocumentsApi, DocumentStatus, QueryApi } from './contracts'

function sizeLabel(sizeBytes: number): string {
  return `${Math.max(1, Math.ceil(sizeBytes / 1024))} KB`
}

export async function listCognitoDocuments(): Promise<DocumentItem[]> {
  const token = accessToken()
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!token || !apiBaseUrl) return []
  const response = await fetch(`${apiBaseUrl}/documents`, { headers: { authorization: `Bearer ${token}` } })
  if (!response.ok) throw new Error('Could not load your private documents.')
  const payload: { documents: Array<{ documentId: string; filename: string; status: DocumentStatus; sizeBytes?: number }> } = await response.json()
  return payload.documents.map((document) => ({
    id: document.documentId,
    filename: document.filename,
    status: document.status,
    sizeLabel: sizeLabel(document.sizeBytes ?? 0),
  }))
}

export const mockDocumentsApi: DocumentsApi = { async upload(file) { return { id: crypto.randomUUID(), filename: file.name, status: 'READY', sizeLabel: sizeLabel(file.size) } } }
export const mockQueryApi: QueryApi = { async ask(question, documents) { const source = documents[0]; return { answer: `Mocked grounded response: “${question.trim()}” can be investigated using ${source.filename}. Connect the retrieval adapter in a later phase.`, citations: [{ documentId: source.id, filename: source.filename, location: 'local mock source' }], insufficientContext: false } } }

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
  return { id: prepared.documentId, filename: file.name, status: 'UPLOADED', sizeLabel: sizeLabel(file.size) }
} }

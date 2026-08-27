import type { DocumentsApi, QueryApi } from './contracts'

export const mockDocumentsApi: DocumentsApi = { async upload(file) { return { id: crypto.randomUUID(), filename: file.name, status: 'READY', sizeLabel: `${Math.max(1, Math.ceil(file.size / 1024))} KB` } } }
export const mockQueryApi: QueryApi = { async ask(question, documents) { const source = documents[0]; return { answer: `Mocked grounded response: “${question.trim()}” can be investigated using ${source.filename}. Connect the retrieval adapter in a later phase.`, citations: [{ documentId: source.id, filename: source.filename, location: 'local mock source' }], insufficientContext: false } } }

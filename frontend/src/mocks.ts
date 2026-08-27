import type { DocumentsApi, QueryApi } from './contracts'

function sizeLabel(sizeBytes: number): string {
  return `${Math.max(1, Math.ceil(sizeBytes / 1024))} KB`
}

export const mockDocumentsApi: DocumentsApi = {
  async upload(file) {
    return {
      id: crypto.randomUUID(),
      filename: file.name,
      status: 'READY',
      sizeLabel: sizeLabel(file.size),
    }
  },
}

export const mockQueryApi: QueryApi = {
  async ask(question) {
    return {
      answer: `Mocked grounded response for “${question.trim()}”.`,
      citations: [{ documentId: 'local', filename: 'Local mock source' }],
      insufficientContext: false,
    }
  },
}

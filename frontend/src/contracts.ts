export type DocumentStatus = 'PENDING_UPLOAD' | 'UPLOADED' | 'INGESTING' | 'READY' | 'FAILED'
export interface DocumentItem { id: string; filename: string; status: DocumentStatus; sizeLabel: string }
export interface Citation { documentId: string; filename: string; location?: string }
export interface QueryAnswer { answer: string; citations: Citation[]; insufficientContext: boolean }
export interface DocumentsApi { upload(file: File): Promise<DocumentItem> }
export interface QueryApi { ask(question: string, documentId?: string): Promise<QueryAnswer> }

import { useEffect, useMemo, useState } from 'react'
import { documentsApi, listDocuments, queryApi } from './api'
import { cognitoConfigured, completeCognitoLogin, restoreCognitoSession, signOut, signOutFromCognito, startCognitoLogin } from './auth'
import type { Citation, DocumentItem, QueryAnswer } from './contracts'
import { mockDocumentsApi, mockQueryApi } from './mocks'
import './App.css'

const allowedExtensions = ['pdf', 'txt', 'md']

function citationLabel(citation: Citation): string {
  return citation.location ? `${citation.filename} · ${citation.location}` : citation.filename
}

function statusMark(status: DocumentItem['status']): string {
  if (status === 'READY') return '✓'
  if (status === 'FAILED') return '×'
  return '↻'
}

function App() {
  const [signedIn, setSignedIn] = useState(false)
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedDocumentId, setSelectedDocumentId] = useState('all')
  const [notice, setNotice] = useState('Choose a document to begin a private research session.')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<QueryAnswer | null>(null)
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)

  const readyDocuments = useMemo(
    () => documents.filter((document) => document.status === 'READY'),
    [documents],
  )

  useEffect(() => {
    const expire = () => {
      setSignedIn(false)
      setDocuments([])
      setNotice('Your session expired. Sign in again to continue.')
    }
    window.addEventListener('auth:expired', expire)
    completeCognitoLogin()
      .then((session) => session ?? restoreCognitoSession())
      .then((session) => {
        if (!session) return
        setSignedIn(true)
        setNotice('Secure session restored. Loading your private archive…')
        if (cognitoConfigured) {
          void listDocuments()
            .then((items) => {
              setDocuments(items)
              setNotice(items.length ? 'Your private archive is ready.' : 'Add your first private source.')
            })
            .catch((error: unknown) => setNotice(error instanceof Error ? error.message : 'Documents could not be loaded.'))
        }
      })
      .catch((error: unknown) => setNotice(error instanceof Error ? error.message : 'Sign-in failed.'))
    return () => window.removeEventListener('auth:expired', expire)
  }, [])

  async function uploadDocument(): Promise<void> {
    if (!selectedFile || uploading) return
    const extension = selectedFile.name.split('.').pop()?.toLowerCase()
    if (!extension || !allowedExtensions.includes(extension)) {
      setNotice('Use a PDF, TXT, or Markdown file for this prototype.')
      return
    }
    setUploading(true)
    setNotice('Encrypting upload, then indexing private source passages…')
    try {
      const document = await (cognitoConfigured ? documentsApi : mockDocumentsApi).upload(selectedFile)
      setDocuments((current) => [document, ...current.filter((item) => item.id !== document.id)])
      setNotice(`${document.filename} is indexed and ready for grounded retrieval.`)
      setSelectedFile(null)
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'The upload could not be completed.')
    } finally {
      setUploading(false)
    }
  }

  async function askQuestion(): Promise<void> {
    if (!question.trim() || readyDocuments.length === 0 || asking) return
    setAsking(true)
    setAnswer(null)
    setNotice('Retrieving owner-matched passages and checking the evidence…')
    try {
      const documentId = selectedDocumentId === 'all' ? undefined : selectedDocumentId
      const result = await (cognitoConfigured ? queryApi : mockQueryApi).ask(question, documentId)
      setAnswer(result)
      setNotice(result.insufficientContext ? 'The archive does not contain enough evidence.' : 'Answer prepared only from your private sources.')
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'The query could not be completed.')
    } finally {
      setAsking(false)
    }
  }

  function leaveWorkspace(): void {
    if (cognitoConfigured) signOutFromCognito()
    else signOut()
    setSignedIn(false)
    setDocuments([])
    setAnswer(null)
  }

  if (!signedIn) {
    return (
      <main className="welcome">
        <div className="folio">01 / PRIVATE KNOWLEDGE</div>
        <p className="eyebrow">PRIVATE DOCUMENT RESEARCH</p>
        <h1>Find the proof.<br />Keep it yours.</h1>
        <p className="lede">A source-first research desk where every answer must earn its citation.</p>
        <button className="primary" onClick={() => cognitoConfigured ? void startCognitoLogin() : setSignedIn(true)}>
          {cognitoConfigured ? 'Sign in securely' : 'Enter demo workspace'} <span>→</span>
        </button>
        <p className="fine-print">{cognitoConfigured ? 'Cognito · Authorization Code + PKCE' : 'Local mock session · no network calls in tests'}</p>
      </main>
    )
  }

  return (
    <main className="workspace">
      <header>
        <a className="wordmark" href="#top">ARCHIVE / <em>RAG</em></a>
        <button className="text-button" onClick={leaveWorkspace}>Sign out</button>
      </header>
      <section className="masthead" id="top">
        <div><p className="eyebrow">YOUR RESEARCH DESK</p><h1>Ask only what your documents can answer.</h1></div>
        <p className="status">● {cognitoConfigured ? 'PRIVATE MODE' : 'LOCAL MODE'}<br /><span>{cognitoConfigured ? 'Authenticated · owner-filtered' : 'Mocked · browser-only'}</span></p>
      </section>
      <p className="notice" role="status" aria-live="polite">{notice}</p>
      <div className="desk-grid">
        <section className="panel documents">
          <div className="panel-heading"><p className="eyebrow">01 / DOCUMENTS</p><span>{documents.length.toString().padStart(2, '0')} FILES</span></div>
          <label className="dropzone">
            <input aria-label="Choose document" type="file" accept=".pdf,.txt,.md" disabled={uploading} onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} />
            <span>{selectedFile ? selectedFile.name : 'Choose a source document'}</span>
            <small>PDF · TXT · MD · 100 KB MAX</small>
          </label>
          <button className="primary upload" disabled={!selectedFile || uploading} onClick={uploadDocument}>
            {uploading ? 'Indexing source' : 'Add to archive'} <span>{uploading ? '↻' : '+'}</span>
          </button>
          <ul className="document-list">
            {documents.length === 0 ? <li className="empty">Your archive is waiting for its first source.</li> : documents.map((document) => (
              <li key={document.id} className={`document-${document.status.toLowerCase()}`}>
                <span className="file-mark">{document.filename.split('.').pop()}</span>
                <div><strong>{document.filename}</strong><small>{document.status.replace('_', ' ')} · {document.sizeLabel}</small></div>
                <b aria-label={document.status}>{statusMark(document.status)}</b>
              </li>
            ))}
          </ul>
        </section>
        <section className="panel query">
          <div className="panel-heading"><p className="eyebrow">02 / QUESTION</p><span>GROUNDED ONLY</span></div>
          <label className="scope-label" htmlFor="document-scope">Search scope</label>
          <select id="document-scope" value={selectedDocumentId} onChange={(event) => setSelectedDocumentId(event.target.value)} disabled={readyDocuments.length === 0 || asking}>
            <option value="all">All ready documents</option>
            {readyDocuments.map((document) => <option key={document.id} value={document.id}>{document.filename}</option>)}
          </select>
          <textarea aria-label="Ask a question" maxLength={1000} placeholder="What would you like to verify?" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <div className="query-meta"><span>{question.length} / 1000</span><span>{readyDocuments.length} sources ready</span></div>
          <button className="primary" disabled={!question.trim() || readyDocuments.length === 0 || asking} onClick={askQuestion}>
            {asking ? 'Checking evidence' : 'Search sources'} <span>{asking ? '↻' : '→'}</span>
          </button>
          {answer && <article className={`answer ${answer.insufficientContext ? 'answer-empty' : ''}`}>
            <p className="eyebrow">ANSWER / {answer.insufficientContext ? 'INSUFFICIENT EVIDENCE' : 'GROUNDED'}</p>
            <p>{answer.answer}</p>
            {answer.citations.length > 0 && <div className="citations" aria-label="Citations">{answer.citations.map((citation) => <span className="citation" key={citation.documentId}>{citationLabel(citation)}</span>)}</div>}
          </article>}
        </section>
      </div>
    </main>
  )
}

export default App

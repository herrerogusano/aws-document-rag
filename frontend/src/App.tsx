import { useEffect, useState } from 'react'
import { cognitoConfigured, completeCognitoLogin, restoreCognitoSession, signOut, startCognitoLogin } from './auth'
import type { Citation, DocumentItem, QueryAnswer } from './contracts'
import { cognitoDocumentsApi, listCognitoDocuments, mockDocumentsApi, mockQueryApi } from './mocks'
import './App.css'

const allowedExtensions = ['pdf', 'txt', 'md']

function citationLabel(citation: Citation): string {
  return citation.location ? `${citation.filename} · ${citation.location}` : citation.filename
}

function App() {
  const [signedIn, setSignedIn] = useState(false)
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [notice, setNotice] = useState('Choose a document to begin a private research session.')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<QueryAnswer | null>(null)

  useEffect(() => {
    completeCognitoLogin().then((session) => session ?? restoreCognitoSession()).then((session) => {
      if (session) {
        setSignedIn(true)
        setNotice('Signed in with Cognito; the protected API accepted your JWT.')
        if (cognitoConfigured) void listCognitoDocuments().then(setDocuments).catch(() => setNotice('Signed in, but documents could not be loaded.'))
      }
    }).catch((error: unknown) => setNotice(error instanceof Error ? error.message : 'Sign-in failed.'))
  }, [])

  async function uploadDocument(): Promise<void> {
    if (!selectedFile) return
    const extension = selectedFile.name.split('.').pop()?.toLowerCase()
    if (!extension || !allowedExtensions.includes(extension)) {
      setNotice('Use a PDF, TXT, or Markdown file for this prototype.')
      return
    }
    setNotice('Reading document locally…')
    try {
      const document = await (cognitoConfigured ? cognitoDocumentsApi : mockDocumentsApi).upload(selectedFile)
      setDocuments((current) => [document, ...current])
      setNotice(`${document.filename} was uploaded privately and is awaiting ingestion.`)
      setSelectedFile(null)
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'The upload could not be completed.')
    }
  }

  async function askQuestion(): Promise<void> {
    if (!question.trim() || documents.length === 0) return
    setNotice('Finding local source passages…')
    const result = await mockQueryApi.ask(question, documents)
    setAnswer(result)
    setNotice('Answer prepared from the mock document source.')
  }

  if (!signedIn) {
    return (
      <main className="welcome">
        <p className="eyebrow">PRIVATE DOCUMENT RESEARCH</p>
        <h1>Find the proof.<br />Keep it yours.</h1>
        <p className="lede">A local prototype for grounded answers, designed around document ownership from the first screen.</p>
        <button className="primary" onClick={() => cognitoConfigured ? void startCognitoLogin() : setSignedIn(true)}>{cognitoConfigured ? 'Sign in securely' : 'Enter demo workspace'} <span>→</span></button>
        <p className="fine-print">{cognitoConfigured ? 'Cognito · Authorization Code + PKCE' : 'Mock sign-in only · No document leaves this browser in Phase 1'}</p>
      </main>
    )
  }

  return (
    <main className="workspace">
      <header><a className="wordmark" href="#top">ARCHIVE / <em>RAG</em></a><button className="text-button" onClick={() => { signOut(); setSignedIn(false) }}>Sign out</button></header>
      <section className="masthead" id="top"><div><p className="eyebrow">YOUR RESEARCH DESK</p><h1>Ask only what your documents can answer.</h1></div><p className="status">● LOCAL MODE<br /><span>Mocked, source-grounded</span></p></section>
      <p className="notice" role="status">{notice}</p>
      <div className="desk-grid">
        <section className="panel documents"><div className="panel-heading"><p className="eyebrow">01 / DOCUMENTS</p><span>{documents.length.toString().padStart(2, '0')} FILES</span></div>
          <label className="dropzone"><input aria-label="Choose document" type="file" accept=".pdf,.txt,.md" onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} /><span>{selectedFile ? selectedFile.name : 'Choose a source document'}</span><small>PDF · TXT · MD</small></label>
          <button className="primary upload" disabled={!selectedFile} onClick={uploadDocument}>Add to archive <span>+</span></button>
          <ul className="document-list">{documents.length === 0 ? <li className="empty">Your archive is waiting for its first source.</li> : documents.map((document) => <li key={document.id}><span className="file-mark">{document.filename.split('.').pop()}</span><div><strong>{document.filename}</strong><small>{document.status.replace('_', ' ')} · {document.sizeLabel}</small></div><b>✓</b></li>)}</ul>
        </section>
        <section className="panel query"><div className="panel-heading"><p className="eyebrow">02 / QUESTION</p><span>GROUNDED ONLY</span></div>
          <textarea aria-label="Ask a question" placeholder="What would you like to verify?" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button className="primary" disabled={!question.trim() || documents.length === 0} onClick={askQuestion}>Search sources <span>→</span></button>
          {answer && <article className="answer"><p className="eyebrow">ANSWER / MOCKED</p><p>{answer.answer}</p><div>{answer.citations.map((citation) => <span className="citation" key={citation.documentId}>{citationLabel(citation)}</span>)}</div></article>}
        </section>
      </div>
    </main>
  )
}

export default App

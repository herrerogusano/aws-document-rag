import { useState } from 'react'
import type { Citation, DocumentItem, QueryAnswer } from './contracts'
import { mockDocumentsApi, mockQueryApi } from './mocks'
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

  async function uploadDocument(): Promise<void> {
    if (!selectedFile) return
    const extension = selectedFile.name.split('.').pop()?.toLowerCase()
    if (!extension || !allowedExtensions.includes(extension)) {
      setNotice('Use a PDF, TXT, or Markdown file for this prototype.')
      return
    }
    setNotice('Reading document locally…')
    const document = await mockDocumentsApi.upload(selectedFile)
    setDocuments((current) => [document, ...current])
    setNotice(`${document.filename} is ready for grounded questions.`)
    setSelectedFile(null)
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
        <button className="primary" onClick={() => setSignedIn(true)}>Enter demo workspace <span>→</span></button>
        <p className="fine-print">Mock sign-in only · No document leaves this browser in Phase 1</p>
      </main>
    )
  }

  return (
    <main className="workspace">
      <header><a className="wordmark" href="#top">ARCHIVE / <em>RAG</em></a><button className="text-button" onClick={() => setSignedIn(false)}>Sign out</button></header>
      <section className="masthead" id="top"><div><p className="eyebrow">YOUR RESEARCH DESK</p><h1>Ask only what your documents can answer.</h1></div><p className="status">● LOCAL MODE<br /><span>Mocked, source-grounded</span></p></section>
      <p className="notice" role="status">{notice}</p>
      <div className="desk-grid">
        <section className="panel documents"><div className="panel-heading"><p className="eyebrow">01 / DOCUMENTS</p><span>{documents.length.toString().padStart(2, '0')} FILES</span></div>
          <label className="dropzone"><input aria-label="Choose document" type="file" accept=".pdf,.txt,.md" onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} /><span>{selectedFile ? selectedFile.name : 'Choose a source document'}</span><small>PDF · TXT · MD</small></label>
          <button className="primary upload" disabled={!selectedFile} onClick={uploadDocument}>Add to archive <span>+</span></button>
          <ul className="document-list">{documents.length === 0 ? <li className="empty">Your archive is waiting for its first source.</li> : documents.map((document) => <li key={document.id}><span className="file-mark">{document.filename.split('.').pop()}</span><div><strong>{document.filename}</strong><small>READY · {document.sizeLabel}</small></div><b>✓</b></li>)}</ul>
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

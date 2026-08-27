import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import App from './App'

test('requires mock sign-in before showing documents', async () => {
  const user = userEvent.setup()
  render(<App />)
  expect(screen.getByText('Enter demo workspace')).toBeInTheDocument()
  await user.click(screen.getByText('Enter demo workspace'))
  expect(screen.getByText('YOUR RESEARCH DESK')).toBeInTheDocument()
})

test('rejects an unsupported upload type', async () => {
  const user = userEvent.setup({ applyAccept: false })
  render(<App />)
  await user.click(screen.getByText('Enter demo workspace'))
  const file = new File(['content'], 'unsafe.exe', { type: 'application/octet-stream' })
  await user.upload(screen.getByLabelText('Choose document'), file)
  await user.click(screen.getByText('Add to archive'))
  expect(screen.getByText('Use a PDF, TXT, or Markdown file for this prototype.')).toBeInTheDocument()
})

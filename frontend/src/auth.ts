export interface AuthSession { ownerId?: string }

const config = {
  domain: import.meta.env.VITE_COGNITO_DOMAIN,
  clientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirectUri: import.meta.env.VITE_COGNITO_REDIRECT_URI,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
}

export const cognitoConfigured = Boolean(
  config.domain && config.clientId && config.redirectUri && import.meta.env.MODE !== 'test',
)

function base64Url(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes)).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '')
}

async function challengeFor(verifier: string): Promise<string> {
  const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))
  return base64Url(new Uint8Array(hash))
}

export async function startCognitoLogin(): Promise<void> {
  if (!cognitoConfigured) throw new Error('Cognito configuration is missing.')
  const verifier = base64Url(crypto.getRandomValues(new Uint8Array(48)))
  sessionStorage.setItem('pkce_verifier', verifier)
  const parameters = new URLSearchParams({
    client_id: config.clientId,
    response_type: 'code',
    scope: 'openid email',
    redirect_uri: config.redirectUri,
    code_challenge_method: 'S256',
    code_challenge: await challengeFor(verifier),
  })
  window.location.assign(`${config.domain}/login?${parameters}`)
}

export async function completeCognitoLogin(): Promise<AuthSession | null> {
  const code = new URLSearchParams(window.location.search).get('code')
  if (!code || !cognitoConfigured) return null
  const verifier = sessionStorage.getItem('pkce_verifier')
  if (!verifier) throw new Error('The sign-in session expired. Please try again.')
  const response = await fetch(`${config.domain}/oauth2/token`, {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code', code, client_id: config.clientId, redirect_uri: config.redirectUri, code_verifier: verifier,
    }),
  })
  if (!response.ok) throw new Error('Sign-in could not be completed.')
  const tokens: { id_token: string } = await response.json()
  const profile = await validateToken(tokens.id_token)
  sessionStorage.setItem('id_token', tokens.id_token)
  sessionStorage.removeItem('pkce_verifier')
  window.history.replaceState({}, document.title, window.location.pathname)
  return profile
}

async function validateToken(token: string): Promise<AuthSession> {
  const apiResponse = await fetch(`${config.apiBaseUrl}/me`, {
    headers: { authorization: `Bearer ${token}` },
  })
  if (!apiResponse.ok) throw new Error('Signed in, but the protected API rejected the session.')
  const profile: { ownerId: string } = await apiResponse.json()
  return { ownerId: profile.ownerId }
}

export function signOut(): void { sessionStorage.removeItem('id_token') }

export function accessToken(): string | null { return sessionStorage.getItem('id_token') }

export async function restoreCognitoSession(): Promise<AuthSession | null> {
  const token = accessToken()
  return token && cognitoConfigured ? validateToken(token) : null
}

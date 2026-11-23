// Public citizen endpoints only. Vite embeds the public base URL at build time.
export function apiUrl(path, base = import.meta.env?.VITE_API_BASE_URL || '') {
  return base.trim().replace(/\/+$/, '').replace(/\/api$/, '') + path
}

export function sourceUrl(value, page) {
  try {
    const url = new URL(value)
    if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) return null
    if (Number.isInteger(page) && page > 0) url.hash = `page=${page}`
    return url.href
  } catch { return null }
}

export class ApiError extends Error {
  constructor(code, status) { super(code); this.code = code; this.status = status }
}

export async function api(path, options = {}) {
  const controller = new AbortController()
  const abort = () => controller.abort()
  if (options.signal?.aborted) controller.abort()
  options.signal?.addEventListener('abort', abort, { once: true })
  const timeout = setTimeout(abort, 65000)
  try {
    const response = await fetch(apiUrl(path), {
      ...options,
      headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
      signal: controller.signal,
    })
    if (!response.ok) {
      const body = await response.text()
      if (!body.trim() && [500, 502, 503, 504].includes(response.status)) throw new ApiError('offline', response.status)
      throw new ApiError(response.status === 429 ? 'rateLimit' : 'httpError', response.status)
    }
    const data = await response.json().catch(() => { throw new ApiError('invalidResponse') })
    if (!validPayload(path, data)) throw new ApiError('invalidResponse')
    return data
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (controller.signal.aborted) throw new ApiError('timeout')
    throw new ApiError('networkError')
  } finally {
    clearTimeout(timeout)
    options.signal?.removeEventListener('abort', abort)
  }
}

const text = value => typeof value === 'string'
const count = value => Number.isInteger(value) && value >= 0
const object = value => value && typeof value === 'object' && !Array.isArray(value)
const optionalText = value => value == null || text(value)

// OpenAPI leaves responses untyped. These checks follow the inspected backend
// serializers; optional document metadata remains optional, never fabricated.
export function validPayload(path, data) {
  if (!object(data)) return false
  if (path === '/api/documents') return count(data.total) && count(data.passages) &&
    Array.isArray(data.documents) && data.documents.every(d => object(d) && text(d.document_id) && count(d.passages) &&
      ['title', 'language', 'source_url', 'status'].every(key => optionalText(d[key])))
  if (path === '/api/ask') return text(data.answer) && typeof data.answerable === 'boolean' &&
    Array.isArray(data.sources) && data.sources.every(s => object(s) && text(s.id) && text(s.text) &&
      (s.page == null || (Number.isInteger(s.page) && s.page > 0)) &&
      ['title', 'section', 'source_url', 'language', 'status'].every(key => optionalText(s[key])))
  if (path.startsWith('/api/quiz?')) return text(data.id) && text(data.title) && Array.isArray(data.questions) &&
    new Set(data.questions.map(q => q?.id)).size === data.questions.length &&
    data.questions.every(q => object(q) && text(q.id) && text(q.question) && Array.isArray(q.options) && q.options.length > 0 && q.options.every(text))
  if (path === '/api/quiz/submit') return count(data.correct) && count(data.total) && data.correct <= data.total &&
    typeof data.score === 'number' && Number.isFinite(data.score) && data.score >= 0 && data.score <= 100 &&
    Array.isArray(data.corrections) && data.corrections.every(c => object(c) && text(c.id) && typeof c.correct === 'boolean' &&
      ['explanation', 'source', 'source_url'].every(key => optionalText(c[key])))
  return false
}

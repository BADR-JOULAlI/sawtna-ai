// TEST ONLY: representative payloads following inspected backend serializers.
// These are not a replacement for live API integration or current legal advice.
export const source = {
  id: 'test-article-62', document_id: 'constitution-test-fr', title: 'Constitution de 2011',
  source_url: 'https://maroc.ma/sites/default/files/2024-10/constitution_du_1er_juillet_2011.pdf',
  language: 'fr', section: 'Article 62', page: 20, status: 'reviewed',
  text: 'Les membres de la Chambre des représentants sont élus pour cinq ans au suffrage universel direct.',
}
export const documents = { documents: [
  { document_id: source.document_id, title: source.title, source_url: source.source_url, language: 'fr', status: 'reviewed', passages: 6 },
  { document_id: 'constitution-test-ar', title: 'دستور المملكة المغربية', source_url: 'https://www.sgg.gov.ma/Portals/0/constitution/constitution_2011_Ar.pdf', language: 'ar', status: 'pending_review', passages: 3 },
], total: 2, passages: 9 }
export const answer = { request_id: 'test-request', answer: source.text, language: 'fr', sources: [source], answerable: true, mode: 'extractive', latency_ms: 20 }
const questions = {
  fr: ['Quel principe la Constitution associe-t-elle au vote ?', ['Un droit personnel et un devoir national', 'Une obligation de soutenir un parti', 'Un mandat transmissible']],
  ar: ['كيف يصف الدستور التصويت؟', ['حق شخصي وواجب وطني', 'واجب دعم حزب معين', 'تفويض قابل للنقل']],
  darija: ['Kifach kaywsef الدستور التصويت؟', ['7e9 chakhsi w wajib watani', 'Khassek tsaned chi 7izb', 'T9der t3ti sotek l chi wa7ed']],
}
export const quiz = (language = 'fr') => ({ id: 'test-quiz', title: {fr:'Les fondamentaux du vote',ar:'أساسيات التصويت',darija:"L’asasiyat dyal tswit"}[language], questions: [{ id: 'vote', question: questions[language][0], options: questions[language][1] }] })
export const result = (language = 'fr') => ({ correct: 1, total: 1, score: 100, corrections: [{ id: 'vote', correct: true, answer: 0, explanation: questions[language][1][0], source: 'Article 30', source_url: source.source_url }] })
export async function mockCitizen(page) {
  await page.route('**/api/**', async route => {
    const url = new URL(route.request().url())
    const body = route.request().postDataJSON()
    if(url.pathname === '/api/documents') return route.fulfill({json: documents})
    if(url.pathname === '/api/ask') return route.fulfill({json: {...answer, language:body.language}})
    if(url.pathname === '/api/quiz') return route.fulfill({json:quiz(url.searchParams.get('language'))})
    if(url.pathname === '/api/quiz/submit') return route.fulfill({json:result(body.language)})
    throw new Error(`Unexpected citizen request: ${url.pathname}`)
  })
}

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { apiUrl, sourceUrl, validPayload, api } from '../src/api.js'
import { answer, documents, quiz, result } from './fixtures.js'

test('public base URL retains proxy and avoids duplicate /api', () => {
  for(const base of ['', '/', '/api', '/api/']) assert.equal(apiUrl('/api/ask',base),'/api/ask')
  for(const base of ['https://example.test', 'https://example.test/', 'https://example.test/api/']) assert.equal(apiUrl('/api/ask',base),'https://example.test/api/ask')
})
test('source links accept HTTP(S), replace fragments, reject executable or credentialed URLs', () => {
  assert.equal(sourceUrl('https://example.test/a.pdf#old', 3),'https://example.test/a.pdf#page=3')
  for(const url of ['javascript:alert(1)', 'data:text/html,hello', '/relative', 'https://user:pass@example.test']) assert.equal(sourceUrl(url),null)
})
test('validates actual citizen payloads and permits missing optional metadata', () => {
  for(const [path,payload] of [['/api/ask',answer],['/api/documents',documents],['/api/quiz?language=fr',quiz()],['/api/quiz/submit',result()]]) {
    assert.equal(validPayload(path,payload),true)
    for(const value of [null, [], {}, 'html']) assert.equal(validPayload(path,value),false)
  }
  assert.equal(validPayload('/api/documents',{documents:[{document_id:'doc',passages:1}],total:1,passages:1}),true)
  assert.equal(validPayload('/api/ask',{...answer,sources:[null]}),false)
  assert.equal(validPayload('/api/ask',{...answer,sources:[{...answer.sources[0],page:{invalid:true}}]}),false)
  assert.equal(validPayload('/api/quiz/submit',{...result(),score:NaN}),false)
  assert.equal(validPayload('/api/quiz?language=fr',{...quiz(),questions:[quiz().questions[0],quiz().questions[0]]}),false)
})
test('HTTP, JSON, malformed payload and network failures have stable localized error codes', async t => {
  for(const [response,code] of [[new Response('',{status:429}),'rateLimit'],[new Response('',{status:503}),'offline'],[new Response('',{status:502}),'offline'],[new Response('Service unavailable',{status:503}),'httpError'],[new Response('<html>'),'invalidResponse'],[Response.json({}),'invalidResponse']]) {
    t.mock.method(globalThis,'fetch',async()=>response)
    await assert.rejects(api('/api/documents'),e=>e.code===code)
    t.mock.restoreAll()
  }
  t.mock.method(globalThis,'fetch',async()=>{throw new TypeError('offline')})
  await assert.rejects(api('/api/documents'),e=>e.code==='networkError')
})
test('requests time out and clean up without automatic retry', async t => {
  t.mock.timers.enable({apis:['setTimeout']})
  let calls=0
  t.mock.method(globalThis,'fetch',(_url,{signal})=>new Promise((_resolve,reject)=>{
    calls++;signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')))
  }))
  const pending=assert.rejects(api('/api/ask',{method:'POST',body:'{}'}),e=>e.code==='timeout')
  t.mock.timers.tick(65000)
  await pending
  assert.equal(calls,1)
})

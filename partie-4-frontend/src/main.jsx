import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { ArrowUpRight, ArrowLeft, ArrowRight, Check, CornerDownLeft, Menu, RotateCcw, Search, X } from 'lucide-react'
import '@fontsource/newsreader/400.css'
import '@fontsource/newsreader/500.css'
import '@fontsource/newsreader/400-italic.css'
import '@fontsource/ibm-plex-sans-arabic/400.css'
import '@fontsource/ibm-plex-sans-arabic/500.css'
import '@fontsource/ibm-plex-sans-arabic/600.css'
import '@fontsource/ibm-plex-mono/400.css'
import './styles.css'
import './creative.css'
import { api, sourceUrl } from './api.js'
import { interfaceCopy } from './interface-copy.js'

/* ------------------------------------------------------------------ copy */

const COPY = {
  fr: {
    assistant:'Assistant', library:'Bibliothèque', quiz:'Quiz citoyen', language:'Langue', menu:'Menu', close:'Fermer', skip:'Aller au contenu',
    tagline:'Éducation électorale au Maroc', motto:'L’information, avant l’opinion.',
    scopeTitle:'Un repère fiable pour comprendre la vie civique.',
    scopeBody:'Posez une question sur les institutions, les élections ou la participation. La réponse est construite à partir des textes du corpus, et chaque passage cité renvoie au document d’origine.',
    ask:'Quelle est votre question ?', placeholder:'Comment les membres de la Chambre des représentants sont-ils élus ?',
    send:'Envoyer la question', sendShort:'Envoyer', hint:'Entrée pour envoyer · Maj + Entrée pour aller à la ligne',
    searching:'Lecture des documents en cours', suggestions:'Questions fréquentes',
    promptExamples:['Comment sont élus les représentants ?','Quelle différence entre les deux Chambres ?','Comment sont élus les conseils des communes ?'],
    howTitle:'Comment ça marche', how:['Votre question est comparée aux passages du corpus.','Les passages les plus proches sont retenus et cités.','Sans source suffisante, l’assistant le dit au lieu d’inventer.'],
    scopeLabel:'Périmètre', scopeTopics:'Constitution de 2011, lois organiques, institutions élues, collectivités territoriales.',
    scopeLimit:'L’assistant ne consulte pas le web. Il ne recommande ni parti ni candidat.',
    answerable:'Réponse fondée sur le corpus', unanswered:'Aucune source suffisante', noEvidence:'Le corpus disponible ne permet pas de répondre de façon fiable. Essayez une question plus précise sur les institutions ou les élections au Maroc.',
    sources:'Passages cités', sourceCount:'sources', openSource:'Ouvrir le document', page:'p.', sourcePending:'à relire', nextQuestion:'Poser une autre question',
    scoreNote:'Les citations sont reproduites dans leur langue d’origine.',
    pendingNotice:'Une partie du corpus attend encore une relecture humaine. Vérifiez le document original avant de vous appuyer sur une réponse.',
    sourceLabel:'Sources documentaires', libraryTitle:'Les textes, à la source.', libraryIntro:'Tous les documents utilisés par l’assistant, avec leur lien officiel.',
    librarySearch:'Rechercher un document', docs:'documents', passages:'passages', reviewed:'Relu', pending:'En relecture', noSources:'Aucun document ne correspond à cette recherche.',
    colDoc:'Document', colLang:'Langue', colPassages:'Passages', colStatus:'Statut',
    quizTitle:'Testez vos connaissances.', quizIntro:'Des questions sur le vote et les institutions. La correction n’apparaît qu’après l’envoi, avec l’article de la Constitution correspondant.',
    validate:'Voir mes résultats', restart:'Recommencer', results:'Votre résultat', answered:'répondues', correct:'Juste', wrong:'À revoir', expected:'Réponse attendue',
    errorTitle:'La demande n’a pas abouti.', retry:'Réessayer', offline:'Le serveur ne répond pas. Vérifiez que le backend tourne sur le port 8010, puis réessayez.',
    notice:'Réponses fondées sur le corpus disponible. Les dates de scrutin et les évolutions législatives doivent être vérifiées auprès des autorités compétentes.',
    footer:'Projet étudiant indépendant, sans affiliation politique.', country:'Maroc',
  },
  ar: {
    assistant:'المساعد', library:'المكتبة', quiz:'اختبار المعرفة', language:'اللغة', menu:'القائمة', close:'إغلاق', skip:'الانتقال إلى المحتوى',
    tagline:'التربية الانتخابية بالمغرب', motto:'المعلومة قبل الرأي.',
    scopeTitle:'مرجع موثوق لفهم الحياة المدنية.',
    scopeBody:'اطرح سؤالا حول المؤسسات أو الانتخابات أو المشاركة. تُبنى الإجابة من نصوص الوثائق، وكل مقطع مقتبس يحيل إلى مصدره الأصلي.',
    ask:'ما هو سؤالك؟', placeholder:'كيف يتم انتخاب أعضاء مجلس النواب؟',
    send:'إرسال السؤال', sendShort:'إرسال', hint:'Enter للإرسال · Shift + Enter لسطر جديد',
    searching:'جاري قراءة الوثائق', suggestions:'أسئلة متكررة',
    promptExamples:['كيف يتم انتخاب أعضاء مجلس النواب؟','ما الفرق بين مجلس النواب ومجلس المستشارين؟','كيف يتم انتخاب مجالس الجماعات؟'],
    howTitle:'كيف يعمل', how:['يُقارن سؤالك بمقاطع الوثائق.','تُعتمد المقاطع الأقرب ويُستشهد بها.','إن لم يوجد مصدر كاف، يصرّح المساعد بذلك بدل الاختلاق.'],
    scopeLabel:'النطاق', scopeTopics:'دستور 2011، القوانين التنظيمية، المؤسسات المنتخبة، الجماعات الترابية.',
    scopeLimit:'لا يتصفح المساعد الإنترنت، ولا يوصي بأي حزب أو مرشح.',
    answerable:'إجابة مستندة إلى الوثائق', unanswered:'لا يوجد مصدر كاف', noEvidence:'الوثائق المتاحة لا تكفي لإجابة موثوقة. جرّب سؤالا أدق حول المؤسسات أو الانتخابات في المغرب.',
    sources:'المقاطع المقتبسة', sourceCount:'مصادر', openSource:'فتح الوثيقة', page:'ص.', sourcePending:'قيد المراجعة', nextQuestion:'طرح سؤال آخر',
    scoreNote:'تُعرض الاقتباسات بلغتها الأصلية.',
    pendingNotice:'جزء من الوثائق لم يراجعه شخص بعد. يُرجى الرجوع إلى الوثيقة الأصلية قبل الاعتماد على أي جواب.',
    sourceLabel:'مصادر موثقة', libraryTitle:'المعلومة من مصدرها.', libraryIntro:'جميع الوثائق التي يعتمدها المساعد، مع روابطها الرسمية.',
    librarySearch:'البحث عن وثيقة', docs:'وثائق', passages:'مقاطع', reviewed:'تمت المراجعة', pending:'قيد المراجعة', noSources:'لا توجد وثيقة مطابقة.',
    colDoc:'الوثيقة', colLang:'اللغة', colPassages:'المقاطع', colStatus:'الحالة',
    quizTitle:'اختبر معلوماتك.', quizIntro:'أسئلة حول التصويت والمؤسسات. يظهر التصحيح بعد الإرسال فقط، مع فصل الدستور المعني.',
    validate:'عرض النتيجة', restart:'إعادة الاختبار', results:'نتيجتك', answered:'مُجابة', correct:'صحيح', wrong:'راجع', expected:'الإجابة الصحيحة',
    errorTitle:'تعذّر إتمام الطلب.', retry:'إعادة المحاولة', offline:'الخادم لا يستجيب. تحقق من تشغيل الخدمة على المنفذ 8010 ثم أعد المحاولة.',
    notice:'الأجوبة مرتبطة بالوثائق المتاحة. يجب التحقق من تواريخ الاقتراع والتعديلات القانونية لدى الجهات المختصة.',
    footer:'مشروع طلابي مستقل بدون انتماء سياسي.', country:'المغرب',
  },
  darija: {
    assistant:'L’mosa3id', library:'L’maktaba', quiz:'Quiz', language:'Logha', menu:'Menu', close:'Sedd', skip:'Sir l contenu',
    tagline:'Tarbiya intikhabiya f Lmaghrib', motto:'Lma3louma 9bel rra2y.',
    scopeTitle:'Ma3louma wad7a 3la l7ayat lmadaniya.',
    scopeBody:'Sowel 3la lmo2assassat, lintikhabat wla lmoucharka. Jawab kayt9ad men lwata2i9, w kol ma9ta3 kayrja3 l masdar dyalo.',
    ask:'Chno sou2al dyalek?', placeholder:'Kifach kaytntakhbo a3da2 majlis nowab?',
    send:'Sift sou2al', sendShort:'Sift', hint:'Entrée bach tsift · Maj + Entrée l str jdid',
    searching:'Kan9raw lwata2i9', suggestions:'As2ila li kaytsawlo bzaf',
    promptExamples:['Kifach kaytntakhbo nowab?','Chno lfar9 bin nowab w lmoustacharin?','Kifach kaytntakhbo majalis ljama3iya?'],
    howTitle:'Kifach khddam', how:['Sou2alek kayt9arn m3a lma9ati3.','Lma9ati3 l9rab kaytkhtaro w kayt9tabso.','Ila ma kanch masdar kafi, kaygoulha bla ma ykhtare3.'],
    scopeLabel:'Nita9', scopeTopics:'Dostour 2011, l9awanin tanzimiya, lmo2assassat lmontakhaba, ljama3at torabiya.',
    scopeLimit:'Ma kay9ellebch f web, w ma kaynsa7 b 7ta 7izb wla moracha7.',
    answerable:'Jawab men lwata2i9', unanswered:'Ma l9inach masdar kaykfi', noEvidence:'Lwata2i9 li 3endna ma kafiyach bach njawbo b thi9a. Jarrab sou2al awda7 3la lmo2assassat wella lintikhabat f Lmaghrib.',
    sources:'Lma9ati3 lmo9tabasa', sourceCount:'masadir', openSource:'7ell lwatika', page:'p.', sourcePending:'khassha moraja3a', nextQuestion:'Sowel sou2al akhor',
    scoreNote:'L’i9tibas kayb9a b loghat lmasdar l’asli.',
    pendingNotice:'Chi ma9ati3 mazal ma raaja3hom ta wahed. Chouf lwatika l asliya 9bel ma t3tamed 3la chi jawab.',
    sourceLabel:'Lmasadir', libraryTitle:'Rje3 l lmasdar.', libraryIntro:'Ga3 lwata2i9 li kaykhddem biha lmosa3id, m3a lien rasmi.',
    librarySearch:'9elleb 3la watika', docs:'wata2i9', passages:'ma9ati3', reviewed:'Mraja3', pending:'F lmoraja3a', noSources:'Ma kayna 7ta watika b had smiya.',
    colDoc:'Watika', colLang:'Logha', colPassages:'Ma9ati3', colStatus:'7ala',
    quizTitle:'Jrreb ma3loumatek.', quizIntro:'As2ila 3la tswit w lmo2assassat. Tashih kayban ghir mn b3d ma tsift, m3a lfasl dyal dostour.',
    validate:'Chouf natija', restart:'3awed', results:'Natijtek', answered:'jawbti', correct:'S7i7', wrong:'3awed chouf', expected:'Jawab s7i7',
    errorTitle:'Talab ma tsalach.', retry:'3awed', offline:'Serveur ma kayjawbch. T2ekked bli backend khddam 3la port 8010 w 3awed.',
    notice:'Lajwiba 7sab lwata2i9 li kaynin. Les dates w taghyirat l9awanin khass tverifyihom m3a ljiha lmas2oula.',
    footer:'Projet étudiant mosta9ill, bla intima2 siyasi.', country:'Lmaghrib',
  },
}

const PAGES = ['assistant', 'library', 'quiz']
const LANGS = [['fr', 'Français'], ['ar', 'العربية'], ['darija', 'Darija']]

/* ------------------------------------------------------------------- api */

const pad = n => String(n).padStart(2, '0')

/* ------------------------------------------------------------ primitives */

function Brand() {
  return (
    <a href="#assistant" className="brand" aria-label="Sawtna, accueil">
      <svg viewBox="0 0 24 24" aria-hidden="true" className="brand-mark">
        <path d="M4 10v4M9 6v12M14 8v8M19 11v2" />
      </svg>
      <span className="brand-word">sawtna</span>
    </a>
  )
}

function ErrorNote({ error, retry, t }) {
  const code = error?.code || error
  const language = Object.keys(COPY).find(lang => COPY[lang] === t) || 'fr'
  const message = ['offline', 'timeout', 'networkError'].includes(code) ? t.offline : (interfaceCopy[language]?.[code] || t.errorTitle)
  return (
    <div className="error-note" role="alert">
      <p className="error-title">{t.errorTitle}</p>
      <p>{message}</p>
      {retry && <button type="button" className="link-button" onClick={retry}><RotateCcw size={13} />{t.retry}</button>}
    </div>
  )
}

function PageHead({ kicker, title, intro, children }) {
  return (
    <header className="page-head">
      <p className="kicker">{kicker}</p>
      <h1>{title}</h1>
      {intro && <p className="lede">{intro}</p>}
      {children}
    </header>
  )
}

/* ------------------------------------------------------------- assistant */

function Assistant({ t, language, documents }) {
  const [question, setQuestion] = useState('')
  const [sent, setSent] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const input = useRef(null)
  const answerRef = useRef(null)
  useEffect(() => { if (result) answerRef.current?.focus() }, [result])
  const request = useRef(null)
  useEffect(() => () => request.current?.abort(), [])
  const pendingCorpus = (documents?.documents || []).some(d => d.status !== 'reviewed')

  async function ask(event) {
    event?.preventDefault()
    const q = question.trim()
    if (q.length < 3 || loading || request.current) return
    const controller = new AbortController()
    request.current = controller
    setLoading(true); setError(''); setSent(q); setResult(null)
    try {
      setResult(await api('/api/ask', { method: 'POST', body: JSON.stringify({ question: q, language }), signal: controller.signal }))

    } catch (e) { if (!controller.signal.aborted) setError(e) } finally { request.current = null; setLoading(false) }
  }

  function reset() {
    setResult(null); setQuestion(''); setSent(''); setError('')
    requestAnimationFrame(() => input.current?.focus())
  }

  return (
    <div className="assistant">
      <div className="assistant-main">
        <div className="assistant-intro"><PageHead kicker={t.motto} title={t.scopeTitle} intro={t.scopeBody} /><figure className="civic-visual"><img src="/images/civic-square.svg" alt="" width="900" height="650" /><figcaption><span>SAWTNA</span><span>{t.country} · <b lang="ar">صوتنا</b></span></figcaption></figure></div>

        <form className={'composer' + (loading ? ' is-loading' : '')} onSubmit={ask} aria-busy={loading}>
          <label htmlFor="question" className="composer-label">{t.ask}</label>
          <textarea
            ref={input} id="question" rows={3} maxLength={1500} dir="auto"
            value={question} placeholder={t.placeholder}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); ask() } }}
          />
          <div className="composer-foot">
            <span className="hint"><CornerDownLeft size={12} aria-hidden="true" />{t.hint}</span>
            <span className="count" aria-hidden="true">{question.length}/1500</span>
            <button type="submit" className="send send-button" aria-label={t.send} disabled={loading || question.trim().length < 3}>
              {t.sendShort}<ArrowRight size={15} className="flip-rtl" aria-hidden="true" />
            </button>
          </div>
        </form>

        {loading && (
          <div className="reading" role="status">
            <span className="reading-bar" aria-hidden="true" />{t.searching}…
          </div>
        )}
        {error && <ErrorNote error={error} retry={() => ask()} t={t} />}

        {!result && !loading && (
          <section className="suggestions" aria-label={t.suggestions}>
            <h2 className="small-heading">{t.suggestions}</h2>
            <ol>
              {t.promptExamples.map((text, i) => (
                <li key={text}>
                  <button type="button" onClick={() => { setQuestion(text); input.current?.focus() }}>
                    <span className="num">{pad(i + 1)}</span>
                    <span className="suggestion-text">{text}</span>
                    <ArrowUpRight size={15} aria-hidden="true" />
                  </button>
                </li>
              ))}
            </ol>
          </section>
        )}

        {result && (
          <article tabIndex={-1} ref={answerRef} className={'answer response-section' + (result.answerable ? '' : ' is-empty')} aria-live="polite">
            <p className="answer-status">
              <span className="dot" aria-hidden="true" />
              {result.answerable ? t.answerable : t.unanswered}
              {!!result.sources.length && <span className="muted"> · {result.sources.length} {t.sourceCount}</span>}
            </p>
            <h2 className="question-sent" dir="auto">{sent}</h2>
            <p className="answer-body" dir="auto">
              {result.answerable ? result.answer : t.noEvidence}
              {result.answerable && result.sources.map((_, i) => (
                <a key={i} href={'#src-' + (i + 1)} onClick={e => { e.preventDefault(); document.getElementById('src-' + (i + 1))?.focus() }} className="ref">[{i + 1}]</a>
              ))}
            </p>

            {!!result.sources.length && (
              <section className="citations" aria-label={t.sources}>
                <h3 className="small-heading">{t.sources}</h3>
                <ol className="citation-list">
                  {result.sources.map((s, i) => (
                    <li className="citation" tabIndex={-1} id={'src-' + (i + 1)} key={s.id || i}>
                      <span className="citation-num">{i + 1}</span>
                      <div>
                        <p className="citation-meta">
                          <span className="citation-title">{s.section || s.title}</span>
                          {s.page && <span>{t.page} {s.page}</span>}
                          {s.status && s.status !== 'reviewed' && <span className="tag">{t.sourcePending}</span>}
                        </p>
                        <blockquote dir="auto">{s.text}</blockquote>
                        {sourceUrl(s.source_url, s.page) && <a href={sourceUrl(s.source_url, s.page)} target="_blank" rel="noreferrer">
                          {t.openSource}<ArrowUpRight size={13} aria-hidden="true" />
                        </a>}
                      </div>
                    </li>
                  ))}
                </ol>
                <p className="footnote">{t.scoreNote}</p>
              </section>
            )}
            <button type="button" className="link-button" onClick={reset}>
              <ArrowLeft size={14} className="flip-rtl" aria-hidden="true" />{t.nextQuestion}
            </button>
          </article>
        )}
      </div>

      <aside className="margin">
        {pendingCorpus && <p className="margin-warning" role="note">{t.pendingNotice}</p>}
        <section>
          <h2 className="small-heading">{t.howTitle}</h2>
          <ol className="steps">{t.how.map(s => <li key={s}>{s}</li>)}</ol>
        </section>
        <section>
          <h2 className="small-heading">{t.scopeLabel}</h2>
          <p>{t.scopeTopics}</p>
          <p className="muted">{t.scopeLimit}</p>
        </section>
        {documents && (
          <section className="corpus-figure">
            <span className="figure">{documents.passages}</span>
            <span className="muted">{t.passages} · {documents.total} {t.docs}</span>
          </section>
        )}
      </aside>
    </div>
  )
}

/* --------------------------------------------------------------- library */

function LibraryPage({ t, documents, refresh, error }) {
  const [search, setSearch] = useState('')
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return (documents?.documents || []).filter(d => ((d.title || d.document_id) + ' ' + (d.language || '')).toLowerCase().includes(q))
  }, [documents, search])

  return (
    <div className="narrow">
      <div className="section-intro library-intro"><PageHead kicker={t.sourceLabel} title={t.libraryTitle} intro={t.libraryIntro} /><img src="/images/civic-library.svg" alt="" width="640" height="420" /></div>
      <div className="toolbar library-toolbar">
        <label className="search">
          <Search size={15} aria-hidden="true" />
          <input type="search" aria-label={t.librarySearch} placeholder={t.librarySearch} value={search} onChange={e => setSearch(e.target.value)} />
        </label>
        {documents && <span className="muted mono">{documents.total} {t.docs} · {documents.passages} {t.passages}</span>}
      </div>

      {error ? <ErrorNote error={error} retry={refresh} t={t} /> : !documents ? (
        <div className="skeleton-list" role="status" aria-label={t.searching}>{[0, 1, 2].map(i => <span key={i} />)}</div>
      ) : (
        <div className="ledger" role="table" aria-label={t.libraryTitle}>
          <div className="ledger-row ledger-head" role="row">
            <span role="columnheader">#</span><span role="columnheader">{t.colDoc}</span>
            <span role="columnheader">{t.colLang}</span><span role="columnheader">{t.colPassages}</span>
            <span role="columnheader">{t.colStatus}</span><span role="columnheader" />
          </div>
          {filtered.map((doc, i) => (
            <div className="ledger-row document" role="row" key={doc.document_id}>
              <span role="cell" className="mono muted">{pad(i + 1)}</span>
              <span role="cell" className="doc-title" dir="auto">{doc.title || doc.document_id}</span>
              <span role="cell" className="mono">{doc.language?.toUpperCase() || '—'}</span>
              <span role="cell" className="mono">{doc.passages}</span>
              <span role="cell"><span className={'status ' + (doc.status === 'reviewed' ? 'ok' : 'wait')}>{doc.status === 'reviewed' ? t.reviewed : doc.status ? t.pending : '—'}</span></span>
              <span role="cell">
                {sourceUrl(doc.source_url) && <a className="document-link" href={sourceUrl(doc.source_url)} target="_blank" rel="noreferrer" aria-label={t.openSource + ' : ' + (doc.title || doc.document_id)}>
                  <ArrowUpRight size={17} />
                </a>}
              </span>
            </div>
          ))}
          {!filtered.length && <p className="empty empty-state">{t.noSources}</p>}
        </div>
      )}
    </div>
  )
}

/* ------------------------------------------------------------------ quiz */

function QuizPage({ t, language }) {
  const [quiz, setQuiz] = useState(null)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const resultRef = useRef(null)
  const quizRequest = useRef(null)
  const submitLock = useRef(false)
  useEffect(() => { if (result) resultRef.current?.focus() }, [result])
  useEffect(() => () => quizRequest.current?.abort(), [])

  async function load() {
    quizRequest.current?.abort()
    const controller = new AbortController()
    quizRequest.current = controller
    setError(''); setResult(null); setAnswers({}); setQuiz(null)
    try { setQuiz(await api('/api/quiz?language=' + language, {signal: controller.signal})) } catch (e) { if (!controller.signal.aborted) setError(e) }
  }
  useEffect(() => { load() }, [language])

  async function submit(event) {
    event?.preventDefault(); if (busy || submitLock.current) return; submitLock.current = true; setBusy(true); setError('')
    try {
      setResult(await api('/api/quiz/submit', { method: 'POST', body: JSON.stringify({ language, answers }) }))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (e) { setError(e) } finally { submitLock.current = false; setBusy(false) }
  }

  const done = Object.keys(answers).length
  const total = quiz?.questions.length || 0
  const letters = language === 'ar' ? ['أ', 'ب', 'ج'] : ['A', 'B', 'C']

  return (
    <div className="narrow">
      <div className="section-intro quiz-intro"><PageHead kicker={t.quiz} title={t.quizTitle} intro={t.quizIntro} /><img src="/images/civic-quiz.svg" alt="" width="640" height="420" /></div>
      {error && <ErrorNote error={error} retry={quiz ? submit : load} t={t} />}

      {result ? (
        <>
          <div ref={resultRef} tabIndex={-1} className="quiz-result" role="status">
            <div>
              <p className="small-heading">{t.results}</p>
              <p className="score"><span>{result.correct}</span>/{result.total}</p>
            </div>
            <p className="score-pct mono">{result.score}<small>/100</small></p>
          </div>
          <ol className="corrections">
            {result.corrections.map((c, i) => {
              const q = quiz?.questions.find(x => x.id === c.id)
              return (
                <li key={c.id} className={c.correct ? 'is-right' : 'is-wrong'}>
                  <span className="mark" aria-hidden="true">{c.correct ? <Check size={14} /> : <X size={14} />}</span>
                  <div>
                    <p className="small-heading">{pad(i + 1)} · {c.correct ? t.correct : t.wrong}</p>
                    {q && <p className="correction-q">{q.question}</p>}
                    <p><span className="muted">{t.expected} : </span>{c.explanation}</p>
                    {sourceUrl(c.source_url) && <a href={sourceUrl(c.source_url)} target="_blank" rel="noreferrer">{c.source}<ArrowUpRight size={13} aria-hidden="true" /></a>}
                  </div>
                </li>
              )
            })}
          </ol>
          <button type="button" className="button primary-button" onClick={load}><RotateCcw size={14} />{t.restart}</button>
        </>
      ) : quiz ? (
        <form onSubmit={submit} className="quiz-form">
          <p className="progress mono" aria-live="polite">
            <span className="progress-track" aria-hidden="true"><i style={{ inlineSize: (done / total) * 100 + '%' }} /></span>
            {done}/{total} {t.answered}
          </p>
          {quiz.questions.map((q, i) => (
            <fieldset key={q.id}>
              <legend><span className="num">{pad(i + 1)}</span>{q.question}</legend>
              <div className="options">
                {q.options.map((option, index) => (
                  <label key={index} className={answers[q.id] === index ? 'selected' : ''}>
                    <input type="radio" name={q.id} value={index} disabled={busy} checked={answers[q.id] === index}
                      onChange={() => setAnswers({ ...answers, [q.id]: index })} />
                    <span className="letter" aria-hidden="true">{letters[index] || String.fromCharCode(65 + index)}</span>
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
          <button className="button" type="submit" disabled={busy || !total || done !== total}>
            {t.validate}<ArrowRight size={15} className="flip-rtl" aria-hidden="true" />
          </button>
        </form>
      ) : !error && (
        <div className="skeleton-list" aria-hidden="true">{[0, 1, 2, 3].map(i => <span key={i} />)}</div>
      )}
    </div>
  )
}

/* ------------------------------------------------------------------- app */

function readPage() {
  const h = location.hash.slice(1)
  return PAGES.includes(h) ? h : 'assistant'
}

function App() {
  const [page, setPage] = useState(readPage)
  const [language, setLanguage] = useState(() => {
    try { const saved = localStorage.getItem('sawtna-lang'); return COPY[saved] ? saved : 'fr' } catch { return 'fr' }
  })
  const [menu, setMenu] = useState(false)
  const [documents, setDocuments] = useState(null)
  const [corpusError, setCorpusError] = useState('')
  const t = COPY[language] || COPY.fr

  async function refresh() {
    setCorpusError('')
    try { setDocuments(await api('/api/documents')) } catch (e) { setCorpusError(e) }
  }

  useEffect(() => {
    refresh()
    const onHash = () => { setPage(readPage()); setMenu(false); window.scrollTo(0, 0) }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    document.documentElement.lang = language === 'darija' ? 'ary-Latn' : language
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr'
    try { localStorage.setItem('sawtna-lang', language) } catch {}
  }, [language])

  useEffect(() => { document.title = `Sawtna — ${t[page]}` }, [page, language])

  return (
    <div className="app">
      <a className="skip-link" href="#main" onClick={e => { e.preventDefault(); document.getElementById("main")?.focus() }}>{t.skip}</a>

      <header className="masthead">
        <div className="masthead-top">
          <Brand />
          <span className="tagline">{t.tagline}</span>
          <div className="masthead-end">
            <label className="lang">
              <span className="sr-only">{t.language}</span>
              <select value={language} onChange={e => setLanguage(e.target.value)}>
                {LANGS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </label>
            <button type="button" className="menu-button" aria-label="Menu" aria-expanded={menu} aria-controls="primary-nav" onClick={() => setMenu(!menu)}>
              {menu ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>
        <nav id="primary-nav" className={'tabs' + (menu ? ' is-open' : '')} aria-label="Navigation principale">
          {PAGES.map((id, i) => (
            <a key={id} href={'#' + id} aria-current={page === id ? 'page' : undefined}>
              <span className="tab-num" aria-hidden="true">{pad(i + 1)}</span>{t[id]}
            </a>
          ))}
        </nav>
      </header>

      <main id="main" tabIndex={-1} key={page + language} className={'content page-' + page}>
        {page === 'library' ? <LibraryPage t={t} documents={documents} refresh={refresh} error={corpusError} />
          : page === 'quiz' ? <QuizPage t={t} language={language} />
          : <Assistant t={t} language={language} documents={documents} />}
      </main>

      <footer className="colophon">
        <span className="brand-word small">sawtna</span>
        <p>{t.notice}</p>
        <p className="muted">{t.footer} · {t.country}</p>
      </footer>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)

import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { ArrowUpRight, ArrowRight, ArrowUp, BookOpen, MessageSquare, ChartNoAxesCombined, Check, ChevronRight, CircleHelp, ExternalLink, FileText, Globe2, Library, LoaderCircle, LockKeyhole, Menu, RefreshCw, RotateCcw, Search, ShieldCheck, X } from 'lucide-react'
import './styles.css'

const COPY = {
  fr: {
    assistant:'Assistant', library:'Bibliothèque', quiz:'Quiz citoyen', dashboard:'Tableau de bord', language:'Langue',
    title:<>Comprendre le vote.<br/><span>En toute clarté.</span></>,
    intro:'Un espace pour mieux comprendre les institutions et les élections au Maroc. Posez vos questions, explorez les textes, vérifiez les sources.',
    eyebrow:'L’information, avant l’opinion.', ask:'Quelle est votre question ?', placeholder:'Ex. Comment les membres de la Chambre des représentants sont-ils élus ?',
    send:'Envoyer la question', searching:'Recherche dans les documents…', suggestions:'Pour commencer', sourceLabel:'Sources documentaires', noSources:'Aucune source pertinente', sources:'Passages de référence',
    question:'Votre question', newQuestion:'Nouvelle question', openSource:'Consulter le document', neutral:'Une information neutre', neutralBody:'Aucune recommandation de candidat ou de parti.', cited:'Des sources à consulter', citedBody:'Chaque passage renvoie au texte utilisé.', private:'Votre question reste privée', privateBody:'Seuls des compteurs d’usage sont conservés.',
    libraryTitle:'Les textes, à la source.', libraryIntro:'Consultez les documents présents dans le corpus et retrouvez leurs références officielles.',
    librarySearch:'Rechercher un document', reviewed:'Extraits vérifiés', passages:'passages', docs:'document', reference:'Texte de référence · 2011',
    quizTitle:'Testez vos connaissances.', quizIntro:'Quatre questions pour mieux comprendre les principes du vote et les institutions. Les corrections citent la Constitution de 2011.',
    validate:'Voir mes résultats', restart:'Recommencer', results:'Votre résultat', completed:'Quiz terminé', questionN:'Question', correct:'Bonne réponse', wrong:'À revoir',
    notice:'Réponses fondées sur le corpus disponible. Les dates de scrutin et les évolutions législatives doivent être vérifiées auprès des autorités compétentes.',
    serviceError:'Le service est indisponible. Vérifiez le démarrage local, puis réessayez.', retry:'Réessayer',
    promptExamples:['Comment sont élus les représentants ?', 'Quelle différence entre les deux Chambres ?', 'Comment sont élus les conseils des communes ?'],
    examplesTitles:['La Chambre des représentants', 'Les institutions', 'La démocratie locale'],
    local:'Éducation électorale · Maroc', footer:'Un projet étudiant indépendant. Sans affiliation politique.',
    scoreNote:'Les citations sont présentées dans leur langue d’origine.', clear:'Effacer',
  },
  ar: {
    assistant:'المساعد', library:'المكتبة', quiz:'اختبار المعرفة', dashboard:'لوحة المؤشرات', language:'اللغة',
    title:<>نفهم التصويت.<br/><span>بكل وضوح.</span></>,
    intro:'فضاء لفهم المؤسسات والانتخابات بالمغرب. اطرح سؤالك، اكتشف النصوص وتحقق من المصادر.',
    eyebrow:'المعلومة قبل الرأي.', ask:'ما هو سؤالك؟', placeholder:'مثلا: كيف يتم انتخاب أعضاء مجلس النواب؟',
    send:'إرسال السؤال', searching:'جاري البحث في الوثائق…', suggestions:'ابدأ من هنا', sourceLabel:'مصادر موثقة', noSources:'لا يوجد مصدر مناسب', sources:'المقاطع المرجعية',
    question:'سؤالك', newQuestion:'سؤال جديد', openSource:'قراءة الوثيقة', neutral:'معلومات محايدة', neutralBody:'بدون توصية بمرشح أو حزب.', cited:'مصادر قابلة للتحقق', citedBody:'كل مقطع مرتبط بالنص الأصلي.', private:'سؤالك يبقى خاصا', privateBody:'نحتفظ فقط بإحصائيات الاستعمال.',
    libraryTitle:'المعلومة من مصدرها.', libraryIntro:'اكتشف الوثائق الموجودة في قاعدة المعرفة ومراجعها الرسمية.', librarySearch:'البحث عن وثيقة', reviewed:'مقاطع متحقق منها', passages:'مقاطع', docs:'وثيقة', reference:'نص مرجعي · 2011',
    quizTitle:'اختبر معلوماتك.', quizIntro:'أربعة أسئلة حول التصويت والمؤسسات. التصحيح يستند إلى دستور 2011.', validate:'عرض النتيجة', restart:'إعادة الاختبار', results:'نتيجتك', completed:'اكتمل الاختبار', questionN:'السؤال', correct:'إجابة صحيحة', wrong:'راجع الإجابة',
    notice:'الأجوبة مرتبطة بالوثائق المتاحة. يجب التحقق من تواريخ الاقتراع والتعديلات القانونية لدى الجهات المختصة.',
    serviceError:'الخدمة غير متاحة حاليا. تحقق من تشغيل الخدمات وحاول مجددا.', retry:'إعادة المحاولة',
    promptExamples:['كيف يتم انتخاب أعضاء مجلس النواب؟', 'ما الفرق بين مجلس النواب ومجلس المستشارين؟', 'كيف يتم انتخاب مجالس الجماعات؟'],
    examplesTitles:['مجلس النواب', 'المؤسسات', 'الديمقراطية المحلية'], local:'التربية الانتخابية · المغرب', footer:'مشروع طلابي مستقل بدون انتماء سياسي.', scoreNote:'نحافظ على لغة المصدر الأصلي في الاقتباسات.', clear:'مسح',
  },
  darija: {
    assistant:'L’mosa3id', library:'L’maktaba', quiz:'Quiz', dashboard:'Tableau de bord', language:'Logha',
    title:<>Nfahmo tswit.<br/><span>B wodou7.</span></>,
    intro:'Blassa bach tfhem lmo2assassat w lintikhabat f lmaghrib. Swel, 9ra lwata2i9 w t2ekked men lmasdar.',
    eyebrow:'Lma3louma 9bel rra2y.', ask:'Chno sou2al dyalek?', placeholder:'Matalan: kifach kaytntakhbo a3da2 majlis nowab?',
    send:'Sift sou2al', searching:'Kan9ellbo f lwata2i9…', suggestions:'Bda men hna', sourceLabel:'Lmasadir', noSources:'Ma l9inach masdar kaykfi', sources:'Lma9ati3 men lmasadir',
    question:'Sou2al dyalek', newQuestion:'Sou2al jdid', openSource:'7ell lwatika', neutral:'Ma3louma mo7ayida', neutralBody:'Bla tawsiya b chi moracha7 wella 7izb.', cited:'Lmasadir wad7in', citedBody:'Kol ma9ta3 mربوط b nass l2asli.', private:'Sou2alek kayb9a khass', privateBody:'Kan7efdo ghir i7sa2iyat listi3mal.',
    libraryTitle:'Rje3 l lmasdar.', libraryIntro:'Chouf lwata2i9 li kaynin f lcorpus w lmaraji3 dyalhom.', librarySearch:'9elleb 3la watika', reviewed:'Ma9ati3 mverifyin', passages:'ma9ati3', docs:'watika', reference:'Nass marji3i · 2011',
    quizTitle:'Jrreb ma3loumatek.', quizIntro:'4 as2ila 3la tswit w lmo2assassat. Tashih kayrje3 l dostour 2011.', validate:'Chouf natija', restart:'3awed', results:'Natijtek', completed:'Saliti lquiz', questionN:'Sou2al', correct:'Jawab s7i7', wrong:'3awed chouf',
    notice:'Lajwiba 7sab lwata2i9 li kaynin. Les dates w taghyirat l9awanin khas tverifyihom m3a ljiha lmas2oula.',
    serviceError:'Service ma khddamch daba. T2ekked men démarrage w 3awed.', retry:'3awed',
    promptExamples:['Kifach kaytntakhbo nowab?', 'Chno lfar9 bin nowab w lmoustacharin?', 'Kifach kaytntakhbo majalis ljama3iya?'],
    examplesTitles:['Majlis nowab', 'Lmo2assassat', 'Democratie ma7aliya'], local:'Tarbiya intikhabiya · Lmaghrib', footer:'Projet étudiant mosta9ill, bla intima2 siyasi.', scoreNote:'L’i9tibas kayb9a b loghat lmasdar l’asli.', clear:'Mse7',
  },
}

async function api(path, options={}) {
  const response = await fetch((import.meta.env.VITE_API_BASE_URL||'')+path, { ...options, headers:{'Content-Type':'application/json', ...options.headers}, signal:AbortSignal.timeout(65000) })
  if (!response.ok) {
    const payload = await response.json().catch(()=>({}))
    throw new Error(typeof payload.detail === 'string' ? payload.detail : 'Service indisponible ('+response.status+')')
  }
  return response.json()
}
const CITIZEN_BASE = location.pathname.includes('dashboard') ? (import.meta.env.VITE_CITIZEN_URL || 'http://127.0.0.1:5175') : ''
const IconButton = ({children, ...props}) => <button className="icon-button" {...props}>{children}</button>
function Brand() {
  return <a href={CITIZEN_BASE+'#assistant'} className="brand" aria-label="Sawtna AI, accueil"><span className="brand-symbol"><svg viewBox="0 0 30 30" fill="none" aria-hidden="true"><path d="M5 11v8m7-14v20m7-17v14m7-10v6" stroke="currentColor" strokeWidth="3.5"/></svg></span><span>sawtna<span className="brand-dot">.</span><small>AI</small></span></a>
}
function EmptyError({error, retry, t}) {
  return <div className="error-panel" role="alert"><CircleHelp size={21}/><div><strong>{t.serviceError}</strong><p>{error}</p>{retry && <button className="text-button" onClick={retry}>{t.retry} <RefreshCw size={14}/></button>}</div></div>
}
function Assistant({t, language}) {
  const [question,setQuestion]=useState(''), [result,setResult]=useState(null), [sent,setSent]=useState(''), [loading,setLoading]=useState(false), [error,setError]=useState('')
  const input=useRef(null), answer=useRef(null)
  async function ask(event) {
    event?.preventDefault()
    if(question.trim().length<3 || loading) return
    setLoading(true); setError(''); setSent(question)
    try {
      const data=await api('/api/ask',{method:'POST',body:JSON.stringify({question,language})})
      setResult(data)
      setTimeout(()=>answer.current?.scrollIntoView({behavior:'smooth',block:'start'}),100)
    } catch(e) {setError(e.message)}
    finally {setLoading(false)}
  }
  return <>
    <div className="section-intro"><p className="overline"><span className="tiny-rule"/>{t.eyebrow}</p><h1>{t.title}</h1><p className="lede">{t.intro}</p></div>
    <section className="composer-section" aria-label={t.ask}>
      <form className={'composer '+(loading?'is-loading':'')} onSubmit={ask}>
        <div className="composer-label"><MessageSquare size={17}/><label htmlFor="question">{t.ask}</label><span>FR / AR / DAR</span></div>
        <textarea ref={input} id="question" maxLength={1500} value={question} onChange={e=>setQuestion(e.target.value)} placeholder={t.placeholder} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();ask()}}}/>
        <div className="composer-bottom"><span><ShieldCheck size={14}/>{t.private}</span><button type="submit" className="send-button" aria-label={t.send} disabled={loading||question.trim().length<3}>{loading?<LoaderCircle className="spin" size={20}/>:<ArrowUp size={21}/>}</button></div>
      </form>
      {loading&&<div className="loading-line" role="status"><LoaderCircle className="spin" size={16}/>{t.searching}</div>}
      {error&&<EmptyError error={error} retry={ask} t={t}/>}
      <div className="suggestion-header"><span>{t.suggestions}</span><span>01 — 03</span></div>
      <div className="suggestions">{t.promptExamples.map((text,i)=><button key={text} onClick={()=>{setQuestion(text);input.current?.focus()}}><span className="suggestion-number">0{i+1}</span><span><small>{t.examplesTitles[i]}</small><strong>{text}</strong></span><ArrowUpRight size={19}/></button>)}</div>
    </section>
    {result&&<section className="response-section" ref={answer} aria-label={t.sources}>
      <div className="response-heading"><span className="label">{t.question}</span><IconButton title={t.clear} onClick={()=>{setResult(null);setQuestion('')}}><X size={18}/></IconButton></div>
      <h2 className="question-sent">{sent}</h2><p className="answer-lead" role="status">{result.answer}</p>
      <div className="citation-list">{result.sources.map((source,i)=><article className="citation" key={source.id}>
        <div className="citation-number">{String(i+1).padStart(2,'0')}</div><div><div className="citation-meta"><FileText size={14}/>{source.section || source.title}{source.page&&<span>p. {source.page}</span>}</div><blockquote dir="auto">{source.text}</blockquote><a href={source.source_url+(source.page?'#page='+source.page:'')} target="_blank" rel="noreferrer">{t.openSource}<ExternalLink size={13}/></a></div>
      </article>)}</div>
      <p className="response-footnote"><BookOpen size={14}/>{t.scoreNote}</p>
    </section>}
    <div className="trust-grid">{[[ShieldCheck,t.neutral,t.neutralBody],[BookOpen,t.cited,t.citedBody],[LockKeyhole,t.private,t.privateBody]].map(([Icon,title,body])=><div key={title}><Icon size={20} strokeWidth={1.5}/><h3>{title}</h3><p>{body}</p></div>)}</div>
  </>
}
function LibraryPage({t,documents,refresh,error}) {
  const [search,setSearch]=useState('')
  const filtered=(documents?.documents||[]).filter(d=>(d.title+' '+d.language).toLowerCase().includes(search.toLowerCase()))
  return <><div className="section-intro compact"><p className="overline">{t.sourceLabel}</p><h1>{t.libraryTitle}</h1><p className="lede">{t.libraryIntro}</p></div>
    <div className="library-toolbar"><div className="search-input"><Search size={18}/><input aria-label={t.librarySearch} placeholder={t.librarySearch} value={search} onChange={e=>setSearch(e.target.value)}/></div><span>{documents?.total||0} {t.docs} · {documents?.passages||0} {t.passages}</span></div>
    {error?<EmptyError error={error} retry={refresh} t={t}/>:<div className="document-list">{filtered.map(doc=><article className="document" key={doc.document_id}><div className="doc-icon"><FileText size={28} strokeWidth={1.4}/></div><div className="doc-content"><p className="label">{t.reference}</p><h2>{doc.title}</h2><p>{doc.passages} {t.passages} <span>·</span> {doc.language.toUpperCase()} <span>·</span> {t.reviewed}</p></div><a className="document-link" href={doc.source_url} target="_blank" rel="noreferrer" aria-label={t.openSource}><ArrowUpRight size={23}/></a></article>)}{!filtered.length&&<p className="empty-state">{t.noSources}</p>}</div>}
    <div className="info-note"><ShieldCheck size={20}/><p>{t.notice}</p></div>
  </>
}
function QuizPage({t,language}) {
  const [quiz,setQuiz]=useState(null), [answers,setAnswers]=useState({}), [result,setResult]=useState(null), [error,setError]=useState(''), [busy,setBusy]=useState(false)
  async function load(){setError('');setResult(null);setAnswers({});try{setQuiz(await api('/api/quiz?language='+language))}catch(e){setError(e.message)}}
  useEffect(()=>{load()},[language])
  async function submit(event) {event.preventDefault();setBusy(true);setError('');try{setResult(await api('/api/quiz/submit',{method:'POST',body:JSON.stringify({language,answers})}))}catch(e){setError(e.message)}finally{setBusy(false)}}
  return <><div className="section-intro compact"><p className="overline">{t.quiz}</p><h1>{t.quizTitle}</h1><p className="lede">{t.quizIntro}</p></div>{error&&<EmptyError error={error} retry={load} t={t}/>}
    {result?<><div className="quiz-result"><div><p className="overline">{t.completed}</p><h2>{t.results}</h2><p>{result.correct} / {result.total}</p></div><strong>{result.score}<small>/100</small></strong></div><div className="corrections">{result.corrections.map((c,i)=><article key={c.id}><span className={'correction-status '+(c.correct?'correct':'')}>{c.correct?<Check size={18}/>:<RotateCcw size={18}/>}</span><div><p className="label">{t.questionN} {i+1} · {c.correct?t.correct:t.wrong}</p><h3>{c.explanation}</h3><a href={c.source_url} target="_blank" rel="noreferrer">{c.source}<ExternalLink size={13}/></a></div></article>)}</div><button className="primary-button" onClick={load}>{t.restart}<RotateCcw size={16}/></button></>
    :quiz?<form onSubmit={submit} className="quiz-form"><div className="quiz-progress"><span>{Object.keys(answers).length} / {quiz.questions.length}</span><div><i style={{width:(Object.keys(answers).length/quiz.questions.length*100)+'%'}}/></div></div>{quiz.questions.map((q,i)=><fieldset key={q.id}><legend><span className="question-index">{String(i+1).padStart(2,'0')}</span>{q.question}</legend><div className="quiz-options">{q.options.map((option,index)=><label key={index} className={answers[q.id]===index?'selected':''}><input type="radio" name={q.id} value={index} checked={answers[q.id]===index} onChange={()=>setAnswers({...answers,[q.id]:index})}/><span>{option}</span></label>)}</div></fieldset>)}<button className="primary-button" type="submit" disabled={busy||Object.keys(answers).length!==quiz.questions.length}>{t.validate}{busy?<LoaderCircle className="spin" size={17}/>:<ArrowRight size={17}/>}</button></form>:<LoaderCircle className="spin" size={24}/>}
  </>
}
function Dashboard({t}) {
  const [key,setKey]=useState(''), [summary,setSummary]=useState(null), [error,setError]=useState(''), [busy,setBusy]=useState(false)
  async function load(event){event?.preventDefault();setBusy(true);setError('');try{setSummary(await api('/api/admin/summary',{headers:{'X-Admin-Key':key}}))}catch(e){setError(e.message)}finally{setBusy(false)}}
  const max=Math.max(1,...(summary?.daily||[]).map(d=>d.count))
  return <><div className="section-intro compact"><p className="overline">Analytics</p><h1>L’usage, en perspective.</h1><p className="lede">Suivez l’apprentissage et la qualité de la recherche à partir de statistiques agrégées.</p></div>
    {!summary?<form className="admin-gate" onSubmit={load}><LockKeyhole size={26}/><h2>Accès au tableau de bord</h2><p>Les indicateurs sont réservés à l’équipe du projet.</p><label htmlFor="admin-key">Clé administrateur</label><input id="admin-key" type="password" value={key} onChange={e=>setKey(e.target.value)} autoComplete="off" required/><button className="primary-button" disabled={busy}>Ouvrir le tableau de bord{busy?<LoaderCircle className="spin" size={16}/>:<ArrowRight size={16}/>}</button>{error&&<p role="alert" className="inline-error">{error}</p>}</form>
    :<><div className="dashboard-toolbar"><span><i className="status-dot"/>Données enregistrées · actualisation à la demande</span><button className="text-button" onClick={load} disabled={busy}><RefreshCw size={15} className={busy?'spin':''}/>Actualiser</button></div>{error&&<EmptyError error={error} retry={load} t={t}/>}
      <div className="kpi-grid">{[['Questions posées',summary.questions,'Toutes langues confondues'],['Réponses sourcées',summary.answer_rate+'%',summary.answered+' questions avec un passage pertinent'],['Quiz terminés',summary.quizzes_completed,'Score moyen : '+summary.average_quiz_score+'/100'],['Temps de réponse',summary.average_latency_ms, 'millisecondes en moyenne']].map(([name,value,note])=><article className="kpi" key={name}><span className="label">{name}</span><strong>{value}</strong><p>{note}</p></article>)}</div>
      <div className="chart-grid"><section className="chart-panel"><div className="panel-heading"><h2>Questions sur 7 jours</h2><span>UTC</span></div><div className="bar-chart" role="img" aria-label="Nombre de questions par jour">{summary.daily.map(day=><div key={day.day} className="bar-column"><span>{day.count}</span><div className="bar-track"><i style={{height:(day.count/max*100)+'%'}}/></div><small>{new Date(day.day+'T12:00:00Z').toLocaleDateString('fr-FR',{day:'2-digit',month:'2-digit'})}</small></div>)}</div>{!summary.questions&&<p className="chart-empty">Les premières questions feront apparaître votre activité.</p>}</section>
      <section className="chart-panel"><div className="panel-heading"><h2>Langues des questions</h2><Globe2 size={18}/></div><div className="language-bars">{summary.languages.map(lang=><div key={lang.language}><div><strong>{{fr:'Français',ar:'العربية',darija:'Darija'}[lang.language]}</strong><span>{lang.count}</span></div><div className="language-track"><i style={{width:(summary.questions?lang.count/summary.questions*100:0)+'%'}}/></div></div>)}</div><p className="chart-caption">Répartition des requêtes enregistrées, sans historique individuel.</p></section></div>
      <div className="chart-grid"><section className="service-panel"><h2>État des services</h2>{Object.entries(summary.services.dependencies).map(([name,ok])=><div className="service-row" key={name}><span>{name==='nlp'?'Embeddings NLP':'Analytics'}</span><span className="service-value"><i className={'status-dot '+(!ok?'offline':'')}/>{ok?'Disponible':'Indisponible'}</span></div>)}<div className="service-row"><span>Base documentaire</span><strong>{summary.corpus.passages} passages</strong></div><div className="service-row"><span>Stockage</span><strong>{summary.services.database}</strong></div></section><section className="privacy-panel"><ShieldCheck size={26}/><h2>Mesurer sans profiler.</h2><p>{summary.privacy}</p><p>Les indicateurs décrivent l’usage du service, jamais les opinions des utilisateurs.</p></section></div>
    </>}
  </>
}
function App(){
  const [page,setPage]=useState(location.hash.slice(1)||(location.pathname.includes('dashboard')?'dashboard':'assistant')), [language,setLanguage]=useState('fr'), [menu,setMenu]=useState(false), [documents,setDocuments]=useState(null), [corpusError,setCorpusError]=useState('')
  const t=COPY[language]
  async function refresh(){setCorpusError('');try{setDocuments(await api('/api/documents'))}catch(e){setCorpusError(e.message)}}
  useEffect(()=>{
    refresh()
    const changed=()=>{
      const next=location.hash.slice(1)||'assistant'
      if(next==='main') return
      if(CITIZEN_BASE && next!=='dashboard'){location.href=CITIZEN_BASE+'#'+next;return}
      setPage(next);setMenu(false);window.scrollTo(0,0)
    }
    window.addEventListener('hashchange',changed)
    return()=>window.removeEventListener('hashchange',changed)
  },[])
  useEffect(()=>{document.documentElement.lang=language==='darija'?'ar-MA':language;document.documentElement.dir=language==='ar'?'rtl':'ltr'},[language])
  const nav=[['assistant',MessageSquare,t.assistant],['library',Library,t.library],['quiz',CircleHelp,t.quiz]]
  return <div className="app">
    <a className="skip-link" href="#main">Aller au contenu</a>
    <aside className={'sidebar '+(menu?'is-open':'')}><Brand/><p className="sidebar-description">{t.local}</p><nav aria-label="Navigation principale">{nav.map(([id,Icon,label])=><a key={id} className={page===id?'active':''} href={'#'+id}><Icon size={19} strokeWidth={1.7}/>{label}{page===id&&<span className="nav-dot"/>}</a>)}</nav><div className="sidebar-bottom"><div className="corpus-card"><BookOpen size={19}/><span>{t.sourceLabel}<strong>{documents?.passages??'—'} {t.passages}</strong></span></div><a className={page==='dashboard'?'active dashboard-link':'dashboard-link'} href="#dashboard"><ChartNoAxesCombined size={18}/>{t.dashboard}<ArrowUpRight size={15}/></a><p>{t.footer}</p></div></aside>
    {menu&&<button className="mobile-scrim" aria-label="Fermer le menu" onClick={()=>setMenu(false)}/>}
    <div className="main-column"><header className="topbar"><div className="breadcrumb"><IconButton aria-label="Menu" onClick={()=>setMenu(!menu)}><Menu size={21}/></IconButton><span>Sawtna AI</span><ChevronRight size={13}/><strong>{t[page]||t.assistant}</strong></div><div className="topbar-end"><span className="edition">Apprendre. Comprendre. Participer.</span><div className="language-picker"><Globe2 size={15}/><select aria-label={t.language} value={language} onChange={e=>setLanguage(e.target.value)}><option value="fr">Français</option><option value="ar">العربية</option><option value="darija">Darija</option></select></div></div></header>
    <main id="main" key={page} className={'content page-'+page}>{page==='library'?<LibraryPage t={t} documents={documents} refresh={refresh} error={corpusError}/>:page==='quiz'?<QuizPage t={t} language={language}/>:page==='dashboard'?<Dashboard t={t}/>:<Assistant t={t} language={language}/>}</main>
    <footer className="site-footer"><span>sawtna<span className="brand-dot">.</span> <small>AI</small></span><p>{t.notice}</p><span className="footer-country">Maroc</span></footer></div>
  </div>
}
createRoot(document.getElementById('root')).render(<App/>)

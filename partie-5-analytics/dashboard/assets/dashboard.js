
const $ = selector => document.querySelector(selector);

const accessForm = $('#access-form');
const accessKey = $('#admin-key');
const accessError = $('#access-error');
const accessSubmit = $('#access-submit');
const accessPanel = $('#access-panel');
const dashboard = $('#dashboard-content');
const dashboardError = $('#dashboard-error');
const refreshButton = $('#refresh-button');

let adminKey = '';

const languageNames = {
  fr: 'Français',
  ar: 'العربية',
  darija: 'Darija',
  en: 'English'
};

const serviceNames = {
  nlp: 'Service NLP',
  analytics: 'Service Analytics',
  backend: 'Backend'
};

const number = value =>
  new Intl.NumberFormat('fr-FR', {
    maximumFractionDigits: 1
  }).format(value ?? 0);

$('#current-date').textContent =
  new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date());

$('#toggle-password').addEventListener('click', () => {
  const visible = accessKey.type === 'text';
  accessKey.type = visible ? 'password' : 'text';
  $('#toggle-password').textContent =
    visible ? 'Afficher' : 'Masquer';
});

function showError(node, message) {
  node.textContent = message;
  node.hidden = false;
}


function setBusy(busy) {
  accessSubmit.disabled = busy
  accessSubmit.firstChild.textContent = busy ? 'Chargement… ' : 'Ouvrir le tableau de bord '
  refreshButton.disabled = busy
}

async function loadSummary() {
  dashboardError.hidden = true
  setBusy(true)
  try {
    const response = await fetch('/api/admin/summary', {
      headers: { 'X-Admin-Key': adminKey },
      cache: 'no-store',
    })
    if (response.status === 401 || response.status === 403) {
      adminKey = ''
      dashboard.hidden = true
      accessPanel.hidden = false
      accessKey.value = ''
      showError(accessError, 'Clé administrateur invalide. Vérifie la clé et réessaie.')
      return
    }
    if (!response.ok) throw new Error(`Le service a répondu avec le code ${response.status}.`)
    render(await response.json())
    accessError.hidden = true
    accessPanel.hidden = true
    dashboard.hidden = false
  } catch (error) {
    const message = 'Impossible de charger les indicateurs. Vérifie la connexion au service Analytics puis réessaie.'
    if (dashboard.hidden) showError(accessError, message)
    else showError(dashboardError, message)
  } finally {
    setBusy(false)
  }
}

function render(summary) {
  document.querySelector('#metric-questions').textContent = number(summary.questions)
  document.querySelector('#metric-answer-rate').textContent = `${number(summary.answer_rate)} %`
  document.querySelector('#metric-answered').textContent = `${number(summary.answered)} réponses avec un passage pertinent`
  document.querySelector('#metric-quizzes').textContent = number(summary.quizzes_completed)
  document.querySelector('#metric-quiz-score').textContent = `Score moyen ${number(summary.average_quiz_score)} / 100`
  document.querySelector('#metric-latency').textContent = summary.questions ? number(summary.average_latency_ms) : '—'
  document.querySelector('#updated-at').textContent = `Actualisé à ${new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' }).format(new Date())}`
  document.querySelector('#corpus-count').textContent = `${number(summary.corpus?.passages)} passages · ${number(summary.corpus?.total)} documents`
  document.querySelector('#storage-name').textContent = summary.services?.database || 'Non renseigné'
  document.querySelector('#privacy-copy').textContent = summary.privacy || 'Les statistiques sont agrégées et ne contiennent pas le texte des questions.'
  renderDaily(summary.daily || [])
  renderLanguages(summary.languages || [], summary.questions || 0)
  renderServices(summary.services?.dependencies || {})
}

function renderDaily(days) {
  const chart = document.querySelector('#daily-chart')
  chart.replaceChildren()
  const max = Math.max(1, ...days.map(day => day.count || 0))
  for (const day of days) {
    const column = document.createElement('div')
    column.className = 'day-column'
    const value = document.createElement('span')
    value.className = 'day-value'
    value.textContent = number(day.count)
    const track = document.createElement('div')
    track.className = 'day-track'
    const bar = document.createElement('i')
    bar.className = 'day-bar'
    bar.style.height = `${day.count ? Math.max(4, day.count / max * 100) : 0}%`
    track.append(bar)
    const label = document.createElement('span')
    label.className = 'day-label'
    label.textContent = new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: '2-digit', timeZone: 'UTC' }).format(new Date(`${day.day}T12:00:00Z`))
    column.append(value, track, label)
    chart.append(column)
  }
  document.querySelector('#daily-empty').hidden = days.some(day => day.count > 0)
}

function renderLanguages(languages, total) {
  const list = document.querySelector('#language-list')
  list.replaceChildren()
  document.querySelector('#language-total').textContent = `${number(total)} questions`
  for (const item of languages) {
    const row = document.createElement('div')
    const head = document.createElement('div')
    head.className = 'language-row-head'
    const label = document.createElement('strong')
    label.textContent = languageNames[item.language] || item.language
    const count = document.createElement('span')
    count.textContent = number(item.count)
    head.append(label, count)
    const track = document.createElement('div')
    track.className = 'language-track'
    const bar = document.createElement('i')
    bar.className = 'language-bar'
    bar.style.width = `${total ? item.count / total * 100 : 0}%`
    track.append(bar)
    row.append(head, track)
    list.append(row)
  }
}

function renderServices(dependencies) {
  const list = document.querySelector('#service-list')
  list.replaceChildren()
  for (const [name, available] of Object.entries(dependencies)) {
    const row = document.createElement('div')
    row.className = 'service-row'
    const label = document.createElement('span')
    label.textContent = serviceNames[name] || name
    const status = document.createElement('strong')
    status.className = `service-status${available ? '' : ' is-down'}`
    const dot = document.createElement('i')
    const value = document.createElement('span')
    value.textContent = available ? 'Disponible' : 'Indisponible'
    status.append(dot, value)
    row.append(label, status)
    list.append(row)
  }
}

accessForm.addEventListener('submit', event => {
  event.preventDefault()
  adminKey = accessKey.value
  loadSummary()
})
refreshButton.addEventListener('click', loadSummary)

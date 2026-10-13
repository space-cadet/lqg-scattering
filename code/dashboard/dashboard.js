/* Rendering uses the same data model and schema as the command-line importer. */
let DATA = {}, DATA_URL;
let currentTab = 'runs', sortCol = null, sortAsc = true, filteredRuns = [], selectedRun = null;
const model = InfoDashData;
const el = id => document.getElementById(id);
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));

function resourceURL(path) {
  if (!path) return '';
  const url = new URL(path, DATA_URL);
  return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
}

async function loadData() {
  try {
    DATA_URL = new URL(new URLSearchParams(location.search).get('data') || 'data.json', location.href);
    if (DATA_URL.origin !== location.origin) throw new Error('Select a data file served by this dashboard.');
    const responses = await Promise.all([fetch(DATA_URL), fetch('data.schema.json')]);
    if (responses.some(response => !response.ok)) throw new Error('Could not load the data file or schema.');
    const [input, schema] = await Promise.all(responses.map(response => response.json()));
    DATA = model.normalize(input);
    const errors = model.validate(DATA, schema);
    if (errors.length) throw new Error(errors.join('\n'));
    el('projectName').textContent = DATA.project.name;
    el('projectSubtitle').textContent = DATA.project.subtitle || '';
    document.title = `${DATA.project.name} — InfoDash`;
    renderTabs(); renderSummary(); renderRuns(); renderFigures(); configureCharts(); renderPerformance(); renderTheory();
  } catch (error) {
    const message = document.createElement('pre');
    message.className = 'error'; message.setAttribute('role', 'alert');
    message.textContent = `Could not display this dashboard:\n${error.message}`;
    document.querySelector('.container').replaceChildren(message);
  }
}

function renderTabs() {
  const defaults = [
    {id:'runs', label:'Runs & Studies'},
    {id:'figures', label:'Figure Archive'},
    {id:'performance', label:'Charts'},
    {id:'theory', label:'Tasks & Numerical Notes'}
  ];
  const configured = DATA.tabs || [];
  const tabs = defaults.map(tab => ({...tab, ...configured.find(item => item.id === tab.id)}));
  const buttons = tabs.map(tab => {
    const button = document.createElement('button');
    button.className = 'tab'; button.textContent = tab.label; button.dataset.tab = tab.id;
    button.id = `${tab.id}TabButton`; button.setAttribute('role', 'tab'); button.setAttribute('aria-controls', `${tab.id}Tab`);
    button.onclick = () => switchTab(tab.id); return button;
  });
  el('tabBar').replaceChildren(...buttons);
  el('tabBar').onkeydown = event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    const available = [...el('tabBar').querySelectorAll('[role="tab"]')];
    const current = available.indexOf(document.activeElement);
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? available.length - 1
      : (current + (event.key === 'ArrowRight' ? 1 : -1) + available.length) % available.length;
    event.preventDefault(); available[next].focus(); switchTab(available[next].dataset.tab);
  };
  switchTab(tabs.some(tab => tab.id === currentTab) ? currentTab : tabs[0]?.id || 'runs');
}

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-content').forEach(panel => {
    const active = panel.id === `${tab}Tab`;
    panel.classList.toggle('hidden', !active); panel.hidden = !active;
    panel.setAttribute('aria-labelledby', panel.id.replace(/Tab$/, 'TabButton'));
  });
  document.querySelectorAll('.tab').forEach(button => {
    const active = button.dataset.tab === tab;
    button.classList.toggle('active', active); button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1;
  });
  if (tab === 'performance') renderPerformance();
}

function renderSummary() {
  el('totalRuns').textContent = DATA.runs.length;
  el('totalTasks').textContent = Object.values(DATA.tasks || {}).reduce((total, items) => total + (Array.isArray(items) ? items.length : 0), 0);
  el('completeRuns').textContent = DATA.runs.filter(run => run.status === 'complete').length;
  el('totalFigures').textContent = DATA.figures?.length || 0;
}

function tableColumns() { return model.columns(DATA).filter(column => column.visible !== false); }
function renderRuns() {
  const statuses = ['All', ...new Set(DATA.runs.map(run => run.status))];
  el('filterStatus').replaceChildren(...statuses.map(status => new Option(status, status)));
  filterRuns();
}

function filterRuns() {
  const status = el('filterStatus').value, search = el('filterSearch').value.toLowerCase();
  const columns = tableColumns();
  filteredRuns = DATA.runs.filter(run => (status === 'All' || run.status === status) && (!search || JSON.stringify(run).toLowerCase().includes(search)));
  if (sortCol) filteredRuns.sort((a, b) => {
    const x = model.get(a, sortCol), y = model.get(b, sortCol);
    if (x == null) return y == null ? 0 : 1;
    if (y == null) return -1;
    return (x < y ? -1 : x > y ? 1 : 0) * (sortAsc ? 1 : -1);
  });
  el('runsTableHead').innerHTML = columns.map((column, index) => `<th scope="col" aria-sort="${sortCol === column.key ? sortAsc ? 'ascending' : 'descending' : 'none'}" title="${escapeHTML(column.description || '')}"><button class="sort-button" data-column="${index}">${escapeHTML(model.label(column))}<span aria-hidden="true" class="sort-arrow"> ${sortCol === column.key ? sortAsc ? '▲' : '▼' : '↕'}</span></button></th>`).join('');
  el('runsTableHead').querySelectorAll('button').forEach(button => button.onclick = () => sortRuns(columns[Number(button.dataset.column)].key));
  el('runsTableBody').innerHTML = filteredRuns.map((run, index) => `<tr class="${selectedRun === run.runId ? 'selected' : ''}" data-run="${index}">${columns.map((column, i) => {
    const value = model.get(run, column.key), text = escapeHTML(model.display(value, column));
    return `<td class="${typeof value === 'number' ? 'mono' : ''}">${i === 0 ? `<button class="run-button" aria-label="Details for ${escapeHTML(run.runId)}">${text}</button>` : text}</td>`;
  }).join('')}</tr>`).join('') || `<tr><td colspan="${Math.max(columns.length, 1)}" class="loading">No matching runs</td></tr>`;
  el('runsTableBody').querySelectorAll('tr[data-run]').forEach(row => row.onclick = () => selectRun(Number(row.dataset.run)));
  if (selectedRun) {
    const run = DATA.runs.find(item => item.runId === selectedRun);
    if (run) renderRunDetail(run);
  }
}

function sortRuns(key) { sortAsc = sortCol === key ? !sortAsc : true; sortCol = key; filterRuns(); }
function resetFilters() { el('filterStatus').value = 'All'; el('filterSearch').value = ''; filterRuns(); }
function selectRun(index) { selectedRun = filteredRuns[index]?.runId; filterRuns(); }
function closeDetail() { selectedRun = null; el('runDetailPanel')?.replaceChildren(); filterRuns(); }

function detailCard(title, value) {
  if (!value || !Object.keys(value).length) return '';
  return `<section class="detail-card"><h4>${escapeHTML(title)}</h4>${Object.entries(value).map(([key, item]) => item !== null && typeof item === 'object'
    ? `<details class="detail-data"><summary>${escapeHTML(key)} (${Object.keys(item).length} entries)</summary><pre>${escapeHTML(JSON.stringify(item, null, 2))}</pre></details>`
    : `<div class="param-row"><span class="param-key">${escapeHTML(key)}</span><span class="param-value">${escapeHTML(model.display(item))}</span></div>`).join('')}</section>`;
}

function renderRunDetail(run) {
  let panel = el('runDetailPanel');
  if (!panel) { panel = document.createElement('div'); panel.id = 'runDetailPanel'; el('runsTab').appendChild(panel); }
  const metadata = Object.fromEntries(Object.entries(run).filter(([key, value]) => !['params', 'parameters', 'results', 'provenance', 'verification', 'artifacts', 'figures'].includes(key) && typeof value !== 'object'));
  const artifacts = (run.artifacts || []).map(artifact => {
    const url = resourceURL(artifact.path);
    return url ? `<li><a href="${escapeHTML(url)}" target="_blank" rel="noopener">${escapeHTML(artifact.label)}</a>${artifact.sha256 ? `<div class="hint mono">SHA-256: ${escapeHTML(artifact.sha256)}</div>` : ''}</li>` : '';
  }).join('');
  panel.innerHTML = `<div class="detail-panel visible"><div class="detail-header"><h3>Run: ${escapeHTML(run.runId)}</h3><button class="btn" onclick="closeDetail()">Close</button></div><div class="detail-grid">${detailCard('Run', metadata)}${detailCard('Parameters', run.parameters)}${detailCard('Results', run.results)}${detailCard('Provenance', run.provenance)}${detailCard('Numerical checks', run.verification)}${detailCard('Study notes', run.assessment)}${artifacts ? `<section class="detail-card"><h4>Files</h4><ul>${artifacts}</ul></section>` : ''}</div>${run.figures?.length ? figureCards(run.figures) : ''}</div>`;
  bindFigures(panel);
}

function configureCharts() {
  const columns = model.columns(DATA), xColumns = columns.filter(column => column.chart !== false && ['number', 'integer', 'date', 'datetime'].includes(column.type)), yColumns = xColumns.filter(column => ['number', 'integer'].includes(column.type));
  el('perfXAxis').replaceChildren(...xColumns.map(column => new Option(model.label(column), column.key)));
  el('perfYAxis').replaceChildren(...yColumns.map(column => new Option(model.label(column), column.key)));
  el('perfGroup').replaceChildren(new Option('All runs', ''), ...columns.filter(column => column.type === 'string' || column.type === 'integer').map(column => new Option(column.label, column.key)));
  if (DATA.charts?.x) el('perfXAxis').value = DATA.charts.x;
  if (DATA.charts?.y) el('perfYAxis').value = DATA.charts.y;
  else if (yColumns.length > 1) el('perfYAxis').selectedIndex = 1;
  if (DATA.charts?.groupBy) {
    if (![...el('perfGroup').options].some(option => option.value === DATA.charts.groupBy)) el('perfGroup').add(new Option(DATA.charts.groupBy, DATA.charts.groupBy));
    el('perfGroup').value = DATA.charts.groupBy;
  }
  el('perfChartType').value = DATA.charts?.type || 'scatter';
}

function renderPerformance() {
  const container = el('perfChart'), xKey = el('perfXAxis').value, yKey = el('perfYAxis').value, groupKey = el('perfGroup').value;
  const columns = model.columns(DATA), points = model.chartPoints(DATA, xKey, yKey, groupKey);
  container.replaceChildren();
  if (!points.length) { container.textContent = 'No numeric data for these axes.'; return; }
  if (typeof Plot === 'undefined' || typeof Plot.plot !== 'function' || typeof Plot.dot !== 'function') { container.textContent = 'Chart library unavailable. The computed numbers are available in Runs & Results.'; return; }
  const labels = key => model.label(columns.find(column => column.key === key) || {label: key});
  points.sort((a, b) => String(a.group).localeCompare(String(b.group)) || Number(a.x) - Number(b.x));
  const grouped = Boolean(groupKey), color = grouped ? 'group' : 'var(--primary)', marks = [];
  if (el('perfChartType').value === 'line') marks.push(Plot.line(points, {x:'x', y:'y', z:'group', stroke:color, strokeWidth:2}));
  marks.push(Plot.dot(points, {x:'x', y:'y', fill:color, r:4, title: point => `${point.runId}\n${labels(xKey)}: ${point.x instanceof Date ? point.x.toISOString() : point.x}\n${labels(yKey)}: ${point.y}`}));
  const plot = Plot.plot({width: Math.max(240, Math.min(900, el('perfChartContainer').clientWidth - 32)), height:340, marginLeft:75, marginBottom:55, x:{label:labels(xKey)}, y:{label:labels(yKey)}, color:{legend:grouped, label: columns.find(column => column.key === groupKey)?.label || groupKey}, marks});
  plot.setAttribute('aria-label', `${labels(yKey)} versus ${labels(xKey)}`);
  container.appendChild(plot);
  el('perfHint').textContent = `${points.length} recorded points${grouped ? `; series by ${columns.find(column => column.key === groupKey)?.label || groupKey}` : ''}.`;
}

function figureCards(figures) {
  return '<div class="figure-grid">' + figures.map(figure => {
    const url = resourceURL(figure.path);
    return `<article class="figure-card"><div class="figure-img">${url ? `<button class="run-button" data-image="${escapeHTML(url)}" aria-label="Enlarge ${escapeHTML(figure.title)}"><img loading="lazy" src="${escapeHTML(url)}" alt="${escapeHTML(figure.title)}"></button>` : ''}</div><div class="figure-info"><div class="figure-title">${escapeHTML(figure.title)}</div><div class="figure-desc">${escapeHTML(figure.description || '')}</div>${(figure.tags || []).map(tag => `<span class="tag">${escapeHTML(tag)}</span>`).join('')}</div></article>`;
  }).join('') + '</div>';
}
function bindFigures(container) { container.querySelectorAll('[data-image]').forEach(button => button.onclick = () => openModal(button.dataset.image, button.getAttribute('aria-label'))); }
function renderFigures() { el('figuresContainer').innerHTML = DATA.figures?.length ? figureCards(DATA.figures) : '<p class="loading">No figures recorded.</p>'; bindFigures(el('figuresContainer')); }
function noteId(doc) { return String(doc.title || 'note').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'note'; }
function isMarkdownDoc(doc) { return /\.(?:md|txt)$/i.test(doc.path || ''); }
function markdownSlug(text) { return String(text || '').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9_ -]/g, '').trim().replace(/\s+/g, '-'); }
function packagedURL(url) {
  if (!url.pathname.includes('/study-assets/')) return url;
  if (url.pathname.includes('/study-assets/memory-bank/')) url.pathname = url.pathname.replace('/study-assets/memory-bank/', '/study-assets/study-records/');
  if (url.pathname.endsWith('.md')) url.pathname = url.pathname.slice(0, -3) + '.txt';
  return url;
}
function prepareMarkdownLinks(container, doc, sourceURL) {
  const docs = (DATA.docs || []).filter(isMarkdownDoc).map(item => ({item, id: noteId(item), url: new URL(resourceURL(item.path))}));
  const markdownTargets = new Map(docs.map(entry => [entry.url.pathname.replace(/\.txt$/i, '.md'), entry]));
  const headingTargets = new Map();
  const slugCounts = new Map();
  container.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(heading => {
    const slug = markdownSlug(heading.textContent) || 'section';
    const count = slugCounts.get(slug) || 0;
    slugCounts.set(slug, count + 1);
    const unique = count ? `${slug}-${count}` : slug;
    heading.id = `${noteId(doc)}--${unique}`;
    if (!headingTargets.has(`#${slug}`)) headingTargets.set(`#${slug}`, heading.id);
  });
  container.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#')) {
      if (href && headingTargets.has(href)) link.setAttribute('href', `#${headingTargets.get(href)}`);
      return;
    }
    try {
      const target = packagedURL(new URL(href, sourceURL));
      if (!['http:', 'https:', 'mailto:'].includes(target.protocol)) { link.removeAttribute('href'); return; }
      const linkedDoc = markdownTargets.get(target.pathname.replace(/\.txt$/i, '.md'));
      if (linkedDoc && target.pathname.endsWith('.txt')) {
        link.href = `#note-${linkedDoc.id}`;
        link.dataset.noteTarget = linkedDoc.id;
        link.title = `Open ${linkedDoc.item.title}`;
      } else {
        link.href = target.href;
      }
      if (target.origin !== location.origin) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
    } catch { link.removeAttribute('href'); }
  });
  container.querySelectorAll('img[src]').forEach(image => {
    try {
      const target = packagedURL(new URL(image.getAttribute('src'), sourceURL));
      if (['http:', 'https:'].includes(target.protocol)) image.src = target.href;
      else image.removeAttribute('src');
      image.loading = 'lazy';
    } catch { image.removeAttribute('src'); }
  });
  container.querySelectorAll('table').forEach(table => {
    const wrapper = document.createElement('div'); wrapper.className = 'note-table-wrap';
    table.parentNode.insertBefore(wrapper, table); wrapper.appendChild(table);
  });
}
async function loadNote(container, doc) {
  const body = container.querySelector('[data-markdown-body]');
  const id = noteId(doc);
  if (!body || container.dataset.loadedNote === id || container.dataset.loadingNote === id) return;
  container.dataset.loadingNote = id;
  body.textContent = 'Loading note…'; body.classList.add('loading');
  try {
    const url = resourceURL(doc.path);
    if (!url) throw new Error('Note link is unavailable.');
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Could not load note (${response.status}).`);
    const markdown = await response.text();
    if (container.dataset.loadingNote !== id) return;
    body.innerHTML = InfoDashMarkdown.parse(markdown);
    prepareMarkdownLinks(body, doc, url);
    if (typeof renderMathInElement === 'function') renderMathInElement(body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '\\[', right: '\\]', display: true},
        {left: '\\(', right: '\\)', display: false},
        {left: '$', right: '$', display: false}
      ],
      throwOnError: false, trust: false, strict: 'ignore'
    });
    body.classList.remove('loading');
    container.dataset.loadedNote = id;
  } catch (error) {
    if (container.dataset.loadingNote !== id) return;
    body.classList.remove('loading'); body.replaceChildren();
    const message = document.createElement('p'); message.className = 'error'; message.textContent = error.message;
    const retry = document.createElement('button'); retry.className = 'btn'; retry.textContent = 'Try again';
    retry.onclick = () => { container.dataset.loadedNote = ''; container.dataset.loadingNote = ''; loadNote(container, doc); };
    body.append(message, retry);
  } finally {
    if (container.dataset.loadingNote === id) container.dataset.loadingNote = '';
  }
}
function showDesktopNote(doc) {
  const reader = el('noteDesktopReader');
  if (!reader) return;
  const id = noteId(doc);
  const card = el(`note-${id}`);
  reader.hidden = false;
  el('noteReaderTitle').textContent = doc.title || 'Numerical note';
  const download = el('noteReaderDownload');
  const url = resourceURL(doc.path);
  download.hidden = !url;
  if (url) {
    download.href = url;
    download.download = new URL(url).pathname.split('/').pop().replace(/\.txt$/i, '.md');
  }
  el('theoryContent').querySelectorAll('.note-card').forEach(item => {
    item.classList.toggle('selected', item === card);
    const details = item.querySelector('details');
    if (details) details.open = item === card;
  });
  if (reader.dataset.loadedNote !== id) {
    reader.dataset.loadedNote = '';
    reader.dataset.loadingNote = '';
    reader.querySelector('[data-markdown-body]').replaceChildren();
    loadNote(reader, doc);
  }
  reader.scrollIntoView({behavior:'smooth', block:'start'});
}
function renderTheory() {
  let taskHtml = '';
  const docs = DATA.docs || [];
  const docsHtml = docs.map(doc => {
    const id = noteId(doc), sourceURL = resourceURL(doc.path);
    if (!isMarkdownDoc(doc)) return `<article class="note-card"><div style="padding:14px"><div class="note-title"><a href="${escapeHTML(sourceURL)}">${escapeHTML(doc.title)}</a></div><p class="note-description">${escapeHTML(doc.description || '')}</p></div></article>`;
    const sourceName = sourceURL ? new URL(sourceURL).pathname.split('/').pop().replace(/\.txt$/i, '.md') : `${id}.md`;
    return `<article class="note-card" id="note-${escapeHTML(id)}"><details data-note-id="${escapeHTML(id)}"><summary><span class="note-title">${escapeHTML(doc.title)}</span><span class="note-description">${escapeHTML(doc.description || '')}</span><span class="note-open-label">Open note</span></summary><div class="markdown-body" data-markdown-body><p class="loading">Open the note to read it.</p></div></details>${sourceURL ? `<a class="note-download" href="${escapeHTML(sourceURL)}" download="${escapeHTML(sourceName)}">Download Markdown</a>` : ''}</article>`;
  }).join('');
  const readerHtml = `<section class="note-desktop-reader" id="noteDesktopReader" aria-label="Selected numerical note" hidden><div class="note-reader-header"><button class="btn" type="button" id="noteReaderBack">All documents</button><h4 id="noteReaderTitle"></h4><a class="note-download" id="noteReaderDownload">Download Markdown</a></div><div class="markdown-body" data-markdown-body><p class="loading">Choose a document above to read it.</p></div></section>`;
  for (const [category, title] of [['active','Active'], ['completed','Completed'], ['pending','Pending']]) {
    const tasks = DATA.tasks?.[category] || [];
    if (tasks.length) taskHtml += `<h3>${title}</h3><div class="figure-grid">${tasks.map(task => `<article class="figure-card" style="padding:12px"><div class="figure-title">${escapeHTML(task.id)} — ${escapeHTML(task.title)}</div><div class="figure-desc">${escapeHTML(task.description || '')}</div></article>`).join('')}</div>`;
  }
  const content = `${docs.length ? `<section aria-labelledby="documentationHeading"><h3 id="documentationHeading">Documentation</h3><div class="note-grid">${docsHtml}</div>${readerHtml}</section>` : ''}${taskHtml ? `<section aria-labelledby="tasksHeading"><h3 id="tasksHeading">Tasks and Numerical Notes</h3>${taskHtml}</section>` : ''}`;
  el('theoryContent').innerHTML = content || '<p class="loading">No notes recorded.</p>';
  docs.filter(isMarkdownDoc).forEach(doc => {
    const details = el(`note-${noteId(doc)}`)?.querySelector('details');
    details?.querySelector('summary')?.addEventListener('click', event => {
      if (!window.matchMedia('(min-width: 769px)').matches) return;
      event.preventDefault();
      showDesktopNote(doc);
    });
    details?.addEventListener('toggle', () => {
      if (details.open && !window.matchMedia('(min-width: 769px)').matches) loadNote(details, doc);
    });
  });
  el('noteReaderBack')?.addEventListener('click', () => {
    el('noteDesktopReader').hidden = true;
    el('theoryContent').querySelectorAll('.note-card').forEach(card => {
      card.classList.remove('selected');
      const details = card.querySelector('details');
      if (details) details.open = false;
    });
    el('documentationHeading')?.scrollIntoView({behavior:'smooth', block:'start'});
  });
  el('theoryContent').addEventListener('click', event => {
    const link = event.target.closest('a[data-note-target]');
    if (!link) return;
    event.preventDefault();
    const doc = docs.find(item => noteId(item) === link.dataset.noteTarget);
    const target = el(`note-${link.dataset.noteTarget}`);
    if (window.matchMedia('(min-width: 769px)').matches && doc) {
      showDesktopNote(doc);
    } else if (target) {
      target.querySelector('details').open = true;
      target.scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
}
let modalTrigger;
function openModal(src, title) { modalTrigger = document.activeElement; el('modalImg').src = src; el('modalImg').alt = title || 'Figure'; el('imageModal').classList.add('visible'); document.querySelector('.modal-close').focus(); }
function closeModal() { el('imageModal').classList.remove('visible'); modalTrigger?.focus(); }
document.addEventListener('keydown', event => {
  if (!el('imageModal').classList.contains('visible')) return;
  if (event.key === 'Escape') closeModal();
  if (event.key === 'Tab') { event.preventDefault(); document.querySelector('.modal-close').focus(); }
});
let resizeTimer;
window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { if (currentTab === 'performance') renderPerformance(); }, 120); });
loadData();

/* Catalogue of saved calculations; values and plots are supplied by the build script. */
let RESEARCH = null;
const studyEscape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function studyNumber(value) {
  if (value === null || value === undefined || value === '') return '—';
  const n = Number(value);
  return Number.isFinite(n) ? (Number.isInteger(n) ? String(n) : n.toPrecision(7)) : studyEscape(value);
}
function studyTable(table) {
  if (!table) return '';
  return `<details><summary>Numerical summary (${table.rows.length} rows)</summary><div class="table-wrap"><table><thead><tr>${table.columns.map(k => `<th>${studyEscape(k.replaceAll('_',' '))}</th>`).join('')}</tr></thead><tbody>${table.rows.map(row => `<tr>${table.columns.map(k => `<td>${studyNumber(row[k])}</td>`).join('')}</tr>`).join('')}</tbody></table></div></details>`;
}
function renderStudyCards() {
  if (!RESEARCH) return;
  const query = document.getElementById('studySearch').value.trim().toLowerCase();
  const task = document.getElementById('studyTask').value;
  const studies = RESEARCH.studies.filter(s => (task === 'All' || s.task === task) && `${s.task} ${s.title} ${s.description} ${s.limits}`.toLowerCase().includes(query));
  document.getElementById('studyCount').textContent = `${studies.length} of ${RESEARCH.studies.length} studies`;
  document.getElementById('studyCards').innerHTML = studies.map(s => `
    <article class="research-study" id="study-${studyEscape(s.id)}">
      <h3>${studyEscape(s.task)} — ${studyEscape(s.title)}</h3>
      <p class="study-status">${studyEscape(s.status)}</p>
      <p>${studyEscape(s.description)}</p><p class="study-limits">${studyEscape(s.limits)}</p>
      ${studyTable(s.table)}
      <div class="research-figures">${s.figures.map(f => `<figure class="${f.wide ? 'wide' : ''}"><a href="${studyEscape(f.path)}" target="_blank" rel="noopener"><img loading="lazy" width="${f.width}" height="${f.height}" src="${studyEscape(f.path)}" alt="${studyEscape(s.title + ': ' + f.title)}"></a><figcaption>${studyEscape(f.title)}${f.pdf ? ` · <a href="${studyEscape(f.pdf)}">PDF</a>` : ''} · <a href="${studyEscape(f.path)}">PNG</a></figcaption></figure>`).join('')}</div>
      <details><summary>Data, operators and write-ups (${s.files.length} files)</summary><p class="hint">Source paths and SHA-256 hashes identify the original saved artifacts. Nonfinite numbers are represented as null in dashboard JSON exports.</p><ul class="study-downloads">${s.files.map(f => `<li><a href="${studyEscape(f.path)}" download>${studyEscape(f.name)}</a><small>${studyEscape(f.source)}</small><details><summary>Source SHA-256</summary><code>${studyEscape(f.sourceSha256)}</code></details></li>`).join('')}</ul></details>
    </article>`).join('') || '<p>No studies match these filters.</p>';
}
async function renderResearchStudies() {
  try {
    const response = await fetch('studies.json');
    if (!response.ok) throw new Error(`Study catalogue returned HTTP ${response.status}`);
    RESEARCH = await response.json();
    document.getElementById('studyTask').innerHTML = '<option>All</option>' + [...new Set(RESEARCH.studies.map(s => s.task))].sort().map(t => `<option>${studyEscape(t)}</option>`).join('');
    renderStudyCards();
    if (location.hash.startsWith('#study-')) showStudy(location.hash.slice(7));
  } catch(error) {
    document.getElementById('studyCards').innerHTML = `<p role="alert">Unable to load study catalogue: ${studyEscape(error.message)}</p>`;
  }
}
function showStudy(id) {
  document.getElementById('studySearch').value = '';
  document.getElementById('studyTask').value = 'All';
  renderStudyCards();
  switchTab('studies');
  const target = document.getElementById(`study-${id}`);
  if (target) { location.hash = `study-${id}`; target.scrollIntoView({block:'start'}); }
}

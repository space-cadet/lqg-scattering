/* Local project navigation; the InfoDash renderer remains the upstream renderer. */
(async function () {
  const select = document.getElementById('datasetSelect');
  try {
    const response = await fetch('datasets.json');
    if (!response.ok) throw new Error(`Dataset list returned HTTP ${response.status}`);
    const {datasets} = await response.json();
    const active = new URLSearchParams(location.search).get('data') || 'data.json';
    select.replaceChildren(new Option('All studies — overview', 'data.json'),
      ...datasets.map(dataset => new Option(`${dataset.title} (${dataset.cases} rows)`, dataset.path)));
    select.value = active;
    select.addEventListener('change', () => {
      const url = new URL('index.html', location.href);
      if (select.value !== 'data.json') url.searchParams.set('data', select.value);
      location.assign(url);
    });
  } catch (error) {
    select.replaceChildren(new Option('Study list unavailable', ''));
    select.disabled = true;
    select.title = error.message;
  }
})();

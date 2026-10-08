'use strict';

const $ = id => document.getElementById(id);
const state = { images: [], groups: [], selected: null, imageIndex: 0, threshold: 0.5, candidatesOnly: false, config: {}, map: null, markers: [], running: false };
const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));
const percent = value => `${(value * 100).toFixed(1)}%`;
const mapsURL = site => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${site.latitude},${site.longitude}`)}`;
const locationName = site => site.id.startsWith('orcutt_') ? `Orcutt · ${site.id.split('_')[1]}` : `Added site · ${site.id.slice(-8)}`;
const coordinates = site => `${site.latitude.toFixed(6)}, ${site.longitude.toFixed(6)}`;

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status}).`);
  return body;
}
function notice(message, error = false) {
  $('notice').textContent = message;
  $('notice').classList.toggle('error', error);
  $('notice').hidden = !message;
}
function isPositive(image) {
  return image.source === 'model' ? image.probability >= state.threshold : image.diagonal === true;
}
function groupImages() {
  const sites = new Map();
  state.images.forEach(image => {
    if (!sites.has(image.location_id)) sites.set(image.location_id, { id: image.location_id, latitude: image.latitude, longitude: image.longitude, images: [] });
    sites.get(image.location_id).images.push(image);
  });
  state.groups = [...sites.values()].map(site => {
    site.images.sort((a, b) => (a.heading ?? 360) - (b.heading ?? 360));
    site.positiveCount = site.images.filter(isPositive).length;
    site.candidate = site.positiveCount > 0;
    const probabilities = site.images.filter(image => image.source === 'model').map(image => image.probability);
    site.probability = probabilities.length ? Math.max(...probabilities) : null;
    site.unreviewed = site.images.every(image => image.source === 'unreviewed');
    return site;
  }).sort((a, b) => Number(b.candidate) - Number(a.candidate) || (b.probability ?? -1) - (a.probability ?? -1) || b.positiveCount - a.positiveCount || a.id.localeCompare(b.id));
}
function bestImageIndex(site) {
  const positive = site.images.findIndex(isPositive);
  if (positive !== -1) return positive;
  let best = 0;
  site.images.forEach((image, index) => { if ((image.probability ?? -1) > (site.images[best].probability ?? -1)) best = index; });
  return best;
}
function selectedSite() { return state.groups.find(site => site.id === state.selected); }
function selectSite(id, imageIndex = null, pan = true) {
  state.selected = id;
  const site = selectedSite();
  if (!site) return;
  state.imageIndex = imageIndex ?? bestImageIndex(site);
  renderDetail();
  renderTable();
  renderMap();
  if (state.map && pan) state.map.panTo({ lat: site.latitude, lng: site.longitude });
}
function render() {
  groupImages();
  if (!selectedSite() && state.groups.length) { state.selected = state.groups[0].id; state.imageIndex = bestImageIndex(state.groups[0]); }
  $('image-count').textContent = state.images.length.toLocaleString();
  $('location-count').textContent = state.groups.length.toLocaleString();
  $('candidate-count').textContent = state.groups.filter(site => site.candidate).length.toLocaleString();
  const modelCount = state.images.filter(image => image.source === 'model').length;
  const labelCount = state.images.filter(image => image.source === 'label').length;
  $('mode-label').textContent = modelCount === state.images.length && modelCount > 0 ? 'Model results' : modelCount > 0 ? 'Labels + model results' : labelCount > 0 ? 'Labeled-data preview' : 'Images awaiting analysis';
  $('candidate-caption').textContent = modelCount ? 'Based on evidence & active threshold' : 'With diagonal-parking labels';
  renderDetail(); renderTable(); renderMap();
}
function filteredSites() {
  const query = $('search').value.trim().toLowerCase();
  const filter = $('status-filter').value;
  return state.groups.filter(site => {
    const matches = `${site.id} ${locationName(site)} ${coordinates(site)}`.toLowerCase().includes(query);
    return matches && (filter === 'all' || (filter === 'candidate' && site.candidate) || (filter === 'other' && !site.candidate && !site.unreviewed) || (filter === 'unreviewed' && site.unreviewed));
  });
}
function renderTable() {
  const sites = filteredSites();
  $('results-count').textContent = sites.length;
  $('results-summary').textContent = `${sites.length} of ${state.groups.length} locations shown · sorted by parking evidence`;
  $('empty-state').hidden = sites.length > 0;
  $('results-body').innerHTML = sites.map(site => `<tr data-site="${escapeHTML(site.id)}" class="${site.id === state.selected ? 'selected' : ''}" tabindex="0" aria-label="Review ${escapeHTML(locationName(site))}"><td>${escapeHTML(locationName(site))}<small>${coordinates(site)}</small></td><td><span class="parking-tag ${site.candidate ? '' : 'other'}"><i></i>${site.candidate ? `${site.positiveCount} positive ${site.positiveCount === 1 ? 'image' : 'images'}` : site.unreviewed ? 'Awaiting analysis' : 'No positive evidence'}</span></td><td>${site.probability === null ? (site.unreviewed ? 'Not analyzed' : '<span title="Labels have no model probability">Label only</span>') : percent(site.probability)}</td><td>${site.images.length} ${site.images.length === 1 ? 'image' : 'images'}</td><td><span class="review-link">View evidence <span>↗</span></span></td></tr>`).join('');
  $('results-body').querySelectorAll('tr').forEach(row => {
    row.addEventListener('click', () => selectSite(row.dataset.site));
    row.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectSite(row.dataset.site); } });
  });
}
function renderDetail() {
  const site = selectedSite();
  if (!site) return;
  state.imageIndex = Math.max(0, Math.min(state.imageIndex, site.images.length - 1));
  const image = site.images[state.imageIndex];
  $('detail-title').textContent = locationName(site);
  $('detail-rank').textContent = site.candidate ? 'ϟ' : '◉';
  $('evidence-image').src = image.image_url;
  $('evidence-image').alt = `Street View image for ${locationName(site)}, ${image.heading === null ? 'uploaded view' : `heading ${image.heading} degrees`}`;
  $('evidence-image').hidden = false;
  $('image-heading').textContent = image.heading === null ? 'UPLOADED IMAGE' : `STREET VIEW · ${image.heading}°`;
  $('image-counter').textContent = `${state.imageIndex + 1} / ${site.images.length}`;
  const positive = isPositive(image);
  $('evidence-badge').textContent = positive ? '✓ Diagonal parking evidence' : image.source === 'unreviewed' ? 'Awaiting model analysis' : 'No diagonal parking identified';
  $('evidence-badge').classList.toggle('neutral', !positive);
  $('source-tag').textContent = image.source === 'label' ? 'DATASET LABEL' : image.source === 'model' ? 'MODEL PREDICTION' : 'UNREVIEWED';
  $('evidence-description').textContent = image.source === 'label' ? 'This view uses its existing dataset label. Run the model to compare its prediction with the image evidence.' : image.source === 'model' ? `The model ${positive ? 'identifies diagonal parking' : 'does not identify diagonal parking'} in this view at the current ${Math.round(state.threshold * 100)}% threshold. Check the image before shortlisting.` : 'This image has coordinates but no parking classification yet. Run model analysis to evaluate it.';
  $('probability-section').hidden = image.probability === null;
  if (image.probability !== null) { $('probability-value').textContent = percent(image.probability); $('probability-fill').style.width = percent(image.probability); }
  $('detail-coordinates').textContent = coordinates(site);
  $('detail-evidence').textContent = `${site.positiveCount} positive / ${site.images.length} ${site.images.length === 1 ? 'view' : 'views'}`;
  $('google-link').href = mapsURL(site);
  $('google-link').hidden = false;
  $('previous-image').hidden = $('next-image').hidden = site.images.length < 2;
}
function mapSites() { return state.groups.filter(site => !state.candidatesOnly || site.candidate); }
function renderMap() {
  const sites = mapSites();
  $('map-count').textContent = `${sites.length} locations · ${sites.filter(site => site.candidate).length} candidates`;
  if (state.map) { renderGoogleMarkers(sites); return; }
  if (!state.groups.length) return;
  const lats = state.groups.map(site => site.latitude), lons = state.groups.map(site => site.longitude);
  const minLat = Math.min(...lats), maxLat = Math.max(...lats), minLon = Math.min(...lons), maxLon = Math.max(...lons);
  const latSpan = Math.max(maxLat - minLat, 0.002), lonSpan = Math.max(maxLon - minLon, 0.002);
  // An equirectangular coordinate plot: no fabricated roads or place labels.
  const midLat = (minLat + maxLat) / 2, midLon = (minLon + maxLon) / 2;
  const ratio = Math.max(0.0001, lonSpan * Math.cos(midLat * Math.PI / 180) / latSpan);
  const plotWidth = Math.min(650, 330 * ratio), plotHeight = Math.min(330, 650 / ratio);
  const x = lon => 450 + ((lon - midLon) / lonSpan) * plotWidth;
  const y = lat => 265 - ((lat - midLat) / latSpan) * plotHeight;
  const ticks = [0, 0.25, 0.5, 0.75, 1];
  let svg = `<svg viewBox="0 0 900 520" preserveAspectRatio="xMidYMid meet" role="group" aria-label="Geographic coordinate overview"><defs><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M 30 0 L 0 0 0 30" fill="none" stroke="#d6e1ce" stroke-width=".7"/></pattern><radialGradient id="terrain"><stop stop-color="#dce8cf"/><stop offset="1" stop-color="#eef3e8"/></radialGradient></defs><rect width="900" height="520" fill="url(#terrain)"/><rect width="900" height="520" fill="url(#grid)"/><g fill="none" stroke="#d1dec6" opacity=".6"><ellipse cx="460" cy="265" rx="260" ry="220"/><ellipse cx="460" cy="265" rx="310" ry="265"/><ellipse cx="460" cy="265" rx="360" ry="310"/></g><text x="450" y="486" text-anchor="middle" class="map-label" style="font-size:9px;letter-spacing:1.5px">ORCUTT · COLLECTION COORDINATES</text>`;
  ticks.forEach(tick => {
    const lat = minLat + tick * (maxLat - minLat), lon = minLon + tick * (maxLon - minLon);
    svg += `<text x="25" y="${y(lat) + 4}" class="map-label" style="font-size:9px">${lat.toFixed(3)}° N</text><text x="${x(lon)}" y="462" text-anchor="middle" class="map-label" style="font-size:9px">${Math.abs(lon).toFixed(3)}° W</text>`;
  });
  const ordered = [...sites].sort((a, b) => Number(a.candidate) - Number(b.candidate) || Number(a.id === state.selected) - Number(b.id === state.selected));
  ordered.forEach(site => {
    const active = site.id === state.selected;
    if (active) svg += `<circle cx="${x(site.longitude)}" cy="${y(site.latitude)}" r="19" fill="#237857" opacity=".12"/><circle cx="${x(site.longitude)}" cy="${y(site.latitude)}" r="12" fill="none" stroke="#628d4b" stroke-width="1"/>`;
    svg += `<circle class="map-point" tabindex="0" role="button" aria-label="${escapeHTML(locationName(site))}${site.candidate ? ', candidate location' : ''}" data-site="${escapeHTML(site.id)}" cx="${x(site.longitude)}" cy="${y(site.latitude)}" r="${active ? 7 : site.candidate ? 6 : 3.5}" fill="${active ? '#d5e096' : site.candidate ? '#26785a' : '#a7b99b'}" stroke="${active ? '#457342' : site.candidate ? '#f6faee' : '#eaf0e4'}" stroke-width="${site.candidate ? 2 : 1}"><title>${escapeHTML(locationName(site))} · ${coordinates(site)}</title></circle>`;
  });
  $('coordinate-map').innerHTML = svg + '</svg>';
  $('coordinate-map').querySelectorAll('[data-site]').forEach(point => {
    point.addEventListener('click', () => selectSite(point.dataset.site));
    point.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectSite(point.dataset.site); } });
  });
}
function renderGoogleMarkers(sites) {
  state.markers.forEach(marker => { marker.map = null; });
  state.markers = sites.map(site => {
    const active = site.id === state.selected;
    const content = document.createElement('div');
    content.style.cssText = `width:${active ? 20 : site.candidate ? 16 : 9}px;height:${active ? 20 : site.candidate ? 16 : 9}px;background:${active ? '#d5e096' : site.candidate ? '#26785a' : '#a7b99b'};border:2px solid white;border-radius:50%;box-shadow:0 1px 5px #193d3244;cursor:pointer;`;
    const marker = new google.maps.marker.AdvancedMarkerElement({ map: state.map, position: { lat: site.latitude, lng: site.longitude }, title: `${locationName(site)}${site.candidate ? ' · Candidate' : ''}`, content, zIndex: active ? 3 : site.candidate ? 2 : 1 });
    marker.addListener('click', () => selectSite(site.id));
    return marker;
  });
}
function fitMap() {
  if (!state.map) { renderMap(); return; }
  const sites = mapSites();
  if (!sites.length) return;
  const bounds = new google.maps.LatLngBounds();
  sites.forEach(site => bounds.extend({ lat: site.latitude, lng: site.longitude }));
  state.map.fitBounds(bounds, 65);
}
function googleMapFailed() {
  state.map = null;
  state.markers = [];
  $('google-map').hidden = true;
  $('coordinate-map').hidden = false;
  $('map-mode').textContent = 'Coordinate preview';
  $('map-subtitle').textContent = 'Geographic preview · collected GPS coordinates';
  notice('Google Maps could not load. The coordinate preview and links to Google Maps are still available. Check the browser key, API access, and referrer settings.', true);
  renderMap();
}
async function loadGoogleMap() {
  if (!state.config.maps_key) return;
  window.gm_authFailure = googleMapFailed;
  window.initChargeAtlasMap = async () => {
    try {
      const { Map } = await google.maps.importLibrary('maps');
      await google.maps.importLibrary('marker');
      $('google-map').hidden = false;
      state.map = new Map($('google-map'), { center: state.config.center, zoom: 15, mapId: 'DEMO_MAP_ID', disableDefaultUI: true, zoomControl: true, mapTypeControl: true, streetViewControl: true, gestureHandling: 'cooperative' });
      $('coordinate-map').hidden = true;
      $('map-mode').textContent = 'Google Maps';
      $('map-subtitle').textContent = 'Google Maps · collected GPS coordinates';
      renderMap(); fitMap();
    } catch (_error) { googleMapFailed(); }
  };
  const script = document.createElement('script');
  script.src = `https://maps.googleapis.com/maps/api/js?${new URLSearchParams({ key: state.config.maps_key, v: 'weekly', loading: 'async', callback: 'initChargeAtlasMap' })}`;
  script.async = true;
  script.onerror = googleMapFailed;
  document.head.append(script);
}
async function analyze(ids = null) {
  if (state.running) throw new Error('Wait for the current analysis to finish.');
  state.running = true;
  $('analyze-button').disabled = true;
  $('upload-button').disabled = true;
  const originalText = $('analyze-button').innerHTML;
  $('analyze-button').textContent = 'Analyzing images…';
  try {
    const start = await api('/api/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(ids ? { ids } : {}) });
    let job;
    do {
      await new Promise(resolve => setTimeout(resolve, 1000));
      job = await api(`/api/jobs/${start.job_id}`);
      notice(`Reading image evidence… ${job.completed} of ${job.total} images analyzed. The model runs locally on the CPU.`);
    } while (job.status === 'running');
    if (job.status === 'error') throw new Error(job.error);
    const results = new Map(job.images.map(image => [image.id, image]));
    state.images = state.images.map(image => results.get(image.id) || image);
    render();
    const site = selectedSite();
    if (site) selectSite(site.id);
    notice(`Analysis complete. ${job.total} images processed; ${state.groups.filter(site => site.candidate).length} candidate locations at the current threshold. Review the image evidence before shortlisting.`);
  } finally {
    state.running = false;
    $('analyze-button').disabled = !state.config.model_available;
    $('upload-button').disabled = false;
    $('analyze-button').innerHTML = originalText;
  }
}
function exportCSV() {
  const headers = ['location_id', 'latitude', 'longitude', 'candidate', 'positive_images', 'total_images', 'max_diagonal_probability', 'threshold', 'evidence_sources', 'image_filenames', 'google_maps_url'];
  const rows = filteredSites().map(site => [site.id, site.latitude, site.longitude, site.candidate, site.positiveCount, site.images.length, site.probability ?? '', state.threshold, [...new Set(site.images.map(image => image.source))].join(';'), site.images.map(image => image.filename).join(';'), mapsURL(site)]);
  const cell = value => `"${(typeof value === 'string' ? value.replace(/^[=+\-@]/, "'$&") : String(value)).replace(/"/g, '""')}"`;
  const csv = [headers, ...rows].map(row => row.map(cell).join(',')).join('\r\n');
  const url = URL.createObjectURL(new Blob(['\ufeff', csv], { type: 'text/csv;charset=utf-8;' }));
  const anchor = document.createElement('a');
  anchor.href = url; anchor.download = 'charge-atlas-locations.csv'; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function library() {
  const site = selectedSite();
  $('library-grid').innerHTML = site ? site.images.map((image, index) => `<button class="library-card" data-image="${index}"><img src="${escapeHTML(image.image_url)}" alt="${escapeHTML(image.filename)}" loading="lazy"><span>${image.heading === null ? 'Uploaded image' : `Heading ${image.heading}°`} · ${image.source === 'model' ? percent(image.probability) + ' diagonal probability' : image.source === 'label' ? (image.diagonal ? 'Diagonal parking label' : 'No diagonal parking label') : 'Unreviewed'}</span></button>`).join('') : '<p>No location is selected.</p>';
  $('library-grid').querySelectorAll('[data-image]').forEach(card => card.addEventListener('click', () => { selectSite(state.selected, Number(card.dataset.image)); $('library-dialog').close(); }));
  $('library-dialog').showModal();
}
function fileBase64(file) {
  return new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(',')[1]); reader.onerror = () => reject(new Error('Could not read the selected image.')); reader.readAsDataURL(file); });
}
$('analyze-button').addEventListener('click', () => analyze().catch(error => notice(error.message, true)));
$('upload-button').addEventListener('click', () => { $('upload-error').textContent = ''; $('upload-dialog').showModal(); });
$('upload-form').addEventListener('submit', async event => {
  event.preventDefault();
  $('upload-error').textContent = '';
  const file = $('upload-file').files[0];
  if (!file || file.size > 8 * 1024 * 1024) { $('upload-error').textContent = 'Choose an image no larger than 8 MB.'; return; }
  $('upload-submit').disabled = true;
  try {
    const form = new FormData(event.target);
    const result = await api('/api/uploads', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: file.name, data: await fileBase64(file), latitude: Number(form.get('latitude')), longitude: Number(form.get('longitude')) }) });
    state.images.push(result.image);
    render(); selectSite(result.image.location_id);
    $('status-filter').value = 'all'; renderTable();
    $('upload-dialog').close(); event.target.reset();
    if (state.config.model_available) await analyze([result.image.id]);
    else notice('Image added with its coordinates. Install the model dependencies to analyze its parking evidence.');
  } catch (error) { $('upload-error').textContent = error.message; notice(error.message, true); }
  finally { $('upload-submit').disabled = false; }
});
$('threshold').addEventListener('input', event => { state.threshold = Number(event.target.value) / 100; $('threshold-stat').innerHTML = `${event.target.value}<span>%</span>`; $('threshold-output').value = `${event.target.value}%`; render(); });
$('search').addEventListener('input', renderTable);
$('status-filter').addEventListener('change', renderTable);
$('show-all').addEventListener('click', () => { state.candidatesOnly = false; $('show-all').classList.add('selected'); $('show-candidates').classList.remove('selected'); renderMap(); });
$('show-candidates').addEventListener('click', () => { state.candidatesOnly = true; $('show-candidates').classList.add('selected'); $('show-all').classList.remove('selected'); renderMap(); });
$('fit-map').addEventListener('click', fitMap);
$('export-button').addEventListener('click', exportCSV);
['method-button', 'method-nav'].forEach(id => $(id).addEventListener('click', () => $('method-dialog').showModal()));
$('library-nav').addEventListener('click', library);
$('explorer-nav').addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
document.querySelectorAll('.close-dialog').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } }));
['previous-image', 'next-image'].forEach((id, direction) => $(id).addEventListener('click', () => { const site = selectedSite(); if (!site) return; state.imageIndex = (state.imageIndex + (direction ? 1 : -1) + site.images.length) % site.images.length; renderDetail(); }));
$('evidence-image').addEventListener('error', () => notice('The selected image could not be loaded. Try another view or check its local file.', true));

async function initialize() {
  try {
    const [config, dataset] = await Promise.all([api('/api/config'), api('/api/dataset')]);
    state.config = config; state.images = dataset.images;
    $('analyze-button').disabled = !config.model_available;
    if (!config.model_available) $('analyze-button').title = 'Install TensorFlow and provide the saved model to enable analysis.';
    render();
    if (!state.images.length) notice('No geolocated images were found. Add an image with coordinates to start exploring.');
    loadGoogleMap();
  } catch (error) { notice(`Could not load the dashboard: ${error.message}`, true); }
}
initialize();

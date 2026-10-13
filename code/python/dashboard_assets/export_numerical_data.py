"""Export saved catalogue summaries into the shared InfoDash interface.

Standalone: python code/python/dashboard_assets/export_numerical_data.py
The catalogue builder also calls this after packaging study sources.
"""
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DASH = ROOT / 'code/dashboard'
OUT = DASH
JSON_SOURCES = {
    'excited-spin': ('results/thermal-j1-spin/j1_spin_method_summary.json', 'temperature_results'),
    'high-j': ('results/t5c_degenerate_limits_highJ_results.json', None),
    'magnetization': ('results/t5a_mag_results.json', 'results'),
    'chirality': ('results/t5a_prime_results.json', 'runs'),
    'perturbation': ('results/t5b_results.json', 'n'),
    'phase': ('results/t5d_phase_scan_results.json', 'points'),
    'large-k': ('results/t5e_results.json', 'families'),
    't7a': ('results/t7a_results.json', 'n'),
    't7b': ('results/t7b_results.json', 'n'),
    't7e': ('results/t7e_results.json', 'n'),
    'geometry-audit': ('results/t7_geometry_thermal_results.json', 'cases'),
    'volume-controls': ('results/volume_prescription_results.json', 'results'),
    'covariance-pilot': ('results/t5c_covariance_probe_results.json', 'records'),
}
CSV_SOURCES = {
    'vacuum-area': 'figures/thermal-area-sectors/thermal_coefficients_vacuum.csv',
    'vacuum-spin': 'figures/thermal-spin-sectors/thermal_vacuum_spin.csv',
    't11-candidate-hamiltonians': 'results/t11-candidate-hamiltonians/model_summary.csv',
}
PARAMETERS = {'n', 'N', 'K', 'J', 'L', 'graph', 'case', 'candidate', 'U_over_t', 'alpha',
              'beta', 'beta_hbar_omega', 'state', 'seed', 'eps', 'epsilon', 'phiRadians',
              'q_bosons_per_copy', 'bosons_per_copy', 'total_spin_S', 'family', 'channel', 'M'}
NUMBER = re.compile(r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$')


def clean(value):
    if isinstance(value, float) and not math.isfinite(value): return None
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list): return [clean(v) for v in value]
    return value


def scalar(value):
    if not isinstance(value, str): return value
    if value == '': return None
    if NUMBER.fullmatch(value):
        n = float(value)
        return (int(value) if re.fullmatch(r'[+-]?\d+', value) else n) if math.isfinite(n) else None
    return value


def csv_rows(source):
    with (ROOT / source).open(newline='', encoding='utf-8-sig') as stream:
        return [{k: scalar(v) for k, v in row.items()} for row in csv.DictReader(stream)]


def records(value, context=None, selector='$'):
    """Unpack explicit record containers, preserving source selectors and group labels."""
    context = context or {}
    if isinstance(value, list):
        for i, row in enumerate(value):
            if isinstance(row, dict):
                yield selector + f'[{i}]', {**context, **row}
        return
    if not isinstance(value, dict): return
    metadata = {k: v for k, v in value.items() if not isinstance(v, (dict, list))}
    for key in ('rows', 'points'):
        if isinstance(value.get(key), list):
            yield from records(value[key], {**context, **metadata}, selector + '.' + key)
            return
    # The perturbation output stores aligned eps/V/q arrays instead of row objects.
    if isinstance(value.get('eps'), list) and isinstance(value.get('V'), list):
        count = len(value['eps'])
        aligned = {k: v for k, v in value.items() if isinstance(v, list) and len(v) == count and all(not isinstance(x, (dict, list)) for x in v)}
        for i in range(count):
            yield selector + f'[{i}]', {**context, **metadata, **{k: v[i] for k, v in aligned.items()}}
        return
    if all(not isinstance(v, dict) and not (isinstance(v, list) and any(isinstance(x, dict) for x in v)) for v in value.values()):
        yield selector, {**context, **value}
        return
    for key, child in value.items():
        if isinstance(child, (dict, list)):
            group = {'sourceGroup': key}
            if key.isdigit(): group['n'] = int(key)
            yield from records(child, {**context, **metadata, **group}, selector + '.' + key)


def leaves(value, prefix=''):
    for key, item in value.items():
        if '.' in key: continue  # Keep literal dotted keys in details, not path-based columns.
        path = prefix + key
        if isinstance(item, dict): yield from leaves(item, path + '.')
        elif not isinstance(item, list): yield path, item


def columns(runs):
    fields = {}
    for run in runs:
        for section in ('parameters', 'results'):
            for key, value in leaves(run[section], section + '.'):
                fields.setdefault(key, []).append(value)
    result = [{'key': 'runId', 'label': 'Case', 'type': 'string'}]
    for key, values in fields.items():
        present = [v for v in values if v is not None]
        kind = ('boolean' if present and all(isinstance(v, bool) for v in present)
                else 'number' if present and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in present)
                else 'string')
        # Mixed scalar fields are presented as text consistently across cases.
        if kind == 'string':
            for run in runs:
                target = run
                parts = key.split('.')
                for part in parts[:-1]: target = target.get(part, {})
                if parts[-1] in target and target[parts[-1]] is not None:
                    target[parts[-1]] = str(target[parts[-1]])
        label = key.split('.', 1)[1].replace('_', ' ')
        column = {'key': key, 'label': label, 'type': kind, 'precision': 8}
        if key.endswith(('ground_energy', 'groundEnergy', 'first_distinct_gap', 'gap')): column['unit'] = 't'
        if key.endswith(('ground_volume_mean_project_units', 'ground_mean_volume', 'ground_volume', 'volume_mean')): column['unit'] = 'project units'
        result.append(column)
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, allow_nan=False) + '\n')


def export_numerical_data(catalogue=None):
    catalogue = catalogue or json.loads((DASH / 'studies.json').read_text())
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    now = datetime.now(timezone.utc).isoformat()
    datasets, overview = [], []
    supplemental = [
        ('t11-fl-sampling', 'T11', 'Prepared FL evolution sampling', 'results/t11-candidate-hamiltonians/dynamics_schedule.csv', None),
        ('t1b-real-plane', 'T1b', 'Positive volumes on two real-plane states', 'results/t1b_real_plane_volume_results.json', None),
        ('t5c-shape-recovery', 'T5c', 'FL covariance shape recovery', 'results/t5c_shape_recovery_results.json', 'records'),
        ('t5c-weighted-input', 'T5c', 'Weighted FL input geometry and volumes', 'results/t5c_input_geometry_results.json', 'cases'),
        ('fl-regular-area', 'T1a', 'Regular FL volume versus area', 'results/fl_volume_area_results.json', None),
        ('fl-shape-scan', 'T1a', 'Equal-area FL shape scan at J=2', 'code/dashboard/fl-volume-shape-j2.json', 'records'),
        ('binding-energy', 'T11', 'Same-number detachment energies', 'results/binding-energy/summary.json', 'records'),
        ('state-space-probes', 'T11', 'Closed and open state evolution probes', 'results/state-space-probes/summary.json', 'records'),
        ('sewing-probes', 'Unassigned', 'Constructive edge sewing probes', 'results/sewing-probes/summary.json', None),
    ]
    extra_studies = []
    for identifier, task, title, source, selection in supplemental:
        package_path = 'study-assets/' + source
        package = DASH / package_path
        package.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, package)
        if source.endswith('.csv'): CSV_SOURCES[identifier] = source
        else: JSON_SOURCES[identifier] = (source, selection)
        extra_studies.append({'id': identifier, 'task': task, 'title': title,
            'description': 'Saved numerical records from ' + source, 'status': 'Saved calculation',
            'files': [{'name': Path(source).name, 'path': package_path, 'source': source,
                       'sourceSha256': hashlib.sha256((ROOT / source).read_bytes()).hexdigest()}], 'figures': []})
    catalogue_ids = {study['id'] for study in catalogue['studies']}
    for study in [*catalogue['studies'], *extra_studies]:
        identifier = study['id']
        source_metadata = {}
        if identifier in CSV_SOURCES:
            source = CSV_SOURCES[identifier]
            rows = [(f'{source}:row-{i+1}', row) for i, row in enumerate(csv_rows(source))]
        elif study.get('table'):
            source = 'code/dashboard/studies.json'
            rows = [(f'studies.{identifier}.table.rows[{i}]', {k: scalar(v) for k, v in row.items()}) for i, row in enumerate(study['table']['rows'])]
        else:
            source, selection = JSON_SOURCES[identifier]
            source_metadata = json.loads((ROOT / source).read_text())
            selected = source_metadata[selection] if selection else ({k: source_metadata[k] for k in ('pythonResults', 'rustResults')} if identifier == 'high-j' else source_metadata)
            if identifier == 't5c-weighted-input':
                rows = [(f'cases[{i}].results[{j}]', {'shape': case['name'], **row}) for i, case in enumerate(selected) for j, row in enumerate(case['results'])]
            else:
                rows = list(records(selected, selector=selection or '$'))
        if not rows: raise ValueError(f'No numerical rows for {identifier}')
        artifacts = []
        hashes = {}
        for file in study['files']:
            package = DASH / file['path']
            package_hash = hashlib.sha256(package.read_bytes()).hexdigest()
            hashes[file['source']] = file['sourceSha256']
            artifacts.append({'label': file['name'], 'path': '../' + file['path'],
                              'kind': 'operators' if file['name'].endswith('.npz') else 'data',
                              'sha256': package_hash, 'sourcePath': file['source'], 'sourceSha256': file['sourceSha256']})
        figures = [{'title': f['title'], 'path': '../' + f['path'], 'tags': [study['task']]} for f in study['figures']]
        checks = {}
        for file in study['files']:
            if Path(file['source']).name in ('independent_checks.json', 'validation.json'):
                saved = json.loads((ROOT / file['source']).read_text())
                checks[Path(file['source']).name] = {k: v for k, v in saved.items() if not isinstance(v, (dict, list))}
        provenance = {'sourceHashes': hashes, 'presentationSource': source,
                      'exportRevision': revision, 'exportDirtySource': dirty, 'importedAt': now,
                      'exportCommand': 'python code/python/dashboard_assets/export_numerical_data.py',
                      'exporterSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        for source_key, target_key in [('source_commit', 'sourceRevision'), ('created_utc', 'startedAt')]:
            if isinstance(source_metadata, dict) and source_metadata.get(source_key): provenance[target_key] = source_metadata[source_key]
        software = {k: source_metadata[k] for k in ('python', 'numpy', 'scipy', 'matplotlib') if isinstance(source_metadata, dict) and isinstance(source_metadata.get(k), str)}
        if software: provenance['software'] = software
        runs = []
        for i, (selector, row) in enumerate(rows):
            case_id = row.get('model_id') or row.get('state') or f'case-{i+1:04d}'
            run = {'runId': f'{identifier}:{case_id}:{i+1}', 'task': study['task'], 'status': 'complete',
                   'description': study['title'], **({'catalogueDate': study['catalogueDate']} if study.get('catalogueDate') else {}),
                   'parameters': {k: v for k, v in row.items() if k in PARAMETERS or k == 'shape'},
                   'results': {k: v for k, v in row.items() if k not in PARAMETERS and k != 'shape'},
                   'provenance': {**provenance, 'sourceSelector': selector},
                   'assessment': {'summary': study['description'], 'recordedStudyStatus': study['status']}}
            # Large download lists are shown once, in the first case; all cases keep hashes/selectors.
            if i == 0:
                run['artifacts'], run['figures'] = artifacts, figures
                if checks: run['verification'] = {'checks': checks}
            runs.append(clean(run))
        cols = columns(runs)
        numerics = [c['key'] for c in cols if c['type'] == 'number']
        preferred_x = next((k for k in ('parameters.alpha', 'parameters.K', 'parameters.J', 'parameters.beta', 'parameters.beta_hbar_omega', 'parameters.eps', 'parameters.bosons_per_copy', 'parameters.q_bosons_per_copy') if k in numerics), None)
        preferred_y = next((k for k in ('results.ground_volume_mean_project_units', 'results.ground_mean_volume', 'results.ground_volume', 'results.volume_mean', 'results.equal_weight_mean', 'results.equal_weight_closed_rs_mean', 'results.sector_probability', 'results.P_q_S', 'results.V', 'results.corr', 'results.gibbs.q2') if k in numerics), None)
        chart = {'type': 'scatter'}
        if len(numerics) >= 2:
            chart.update(x=preferred_x or numerics[0], y=preferred_y or next((k for k in numerics if k.startswith('results.')), numerics[1]))
            # A series must include every varying model control to avoid connecting unrelated systems.
            grouping = [k for k in ('graph', 'candidate', 'U_over_t', 'n', 'sourceGroup', 'family', 'case', 'beta_hbar_omega') if any(k in run['parameters'] or k in run['results'] for run in runs) and 'parameters.' + k != chart['x']]
            if grouping:
                for run in runs:
                    run['series'] = ', '.join(f'{k}={run["parameters"].get(k, run["results"].get(k))}' for k in grouping)
                cols.append({'key': 'series', 'label': 'Series', 'type': 'string', 'visible': False})
                chart['groupBy'] = 'series'
        data = {'schemaVersion': '1.0.0', 'project': {'name': study['title'], 'subtitle': study['description']},
                'columns': cols, 'charts': chart, 'runs': runs, 'figures': figures,
                'docs': [{'title': 'Numerical studies overview', 'path': '../index.html'}]}
        path = f'datasets/{identifier}.json'
        write(OUT / path, data)
        datasets.append({'id': identifier, 'title': study['title'], 'path': path, 'cases': len(runs)})
        overview.append({'runId': identifier, 'task': study['task'], 'status': 'complete', 'description': study['title'],
                         **({'catalogueDate': study['catalogueDate']} if study.get('catalogueDate') else {}), 'parameters': {},
                         'results': {'caseCount': len(runs), 'fileCount': len(artifacts)},
                         'artifacts': [{'label': 'Open numerical cases and charts', 'path': 'index.html?data=' + path}],
                         'provenance': {'exportRevision': revision, 'exportDirtySource': dirty, 'importedAt': now},
                         'assessment': {'summary': study['description'], 'limits': study.get('limits'),
                                        'recordedStudyStatus': study['status']}})
    write(OUT / 'datasets.json', {'datasets': datasets})
    # Serve the chronology under the deployment's supported .txt extension.
    chronology = DASH / 'study-assets/notes/numerical-studies.txt'
    chronology.parent.mkdir(parents=True, exist_ok=True)
    chronology.write_bytes((ROOT / 'notes/numerical-studies.md').read_bytes())

    # Keep the project's existing saved records and figures as InfoDash's overview.
    # The per-study datasets add the nine supplemental studies and give all 30
    # datasets a direct route from the same root interface.
    overview_data = json.loads((DASH / 'data.json').read_text())
    overview_data['schemaVersion'] = '1.0.0'
    overview_data['project']['name'] = 'Scattering in LQG'
    overview_data['project']['subtitle'] = 'Numerical study records, saved cases, figures, provenance and calculation limits.'
    overview_data['tabs'] = [
        {'id': 'runs', 'label': 'Runs & Studies'},
        {'id': 'figures', 'label': 'Figure Archive'},
        {'id': 'performance', 'label': 'Charts'},
        {'id': 'theory', 'label': 'Tasks & Numerical Notes'},
    ]
    overview_data['columns'] = [
        {'key': 'runId', 'label': 'Study / Run', 'type': 'string'},
        {'key': 'task', 'label': 'Task', 'type': 'string'},
        {'key': 'description', 'label': 'Calculation', 'type': 'string'},
        {'key': 'status', 'label': 'Status', 'type': 'string'},
        {'key': 'date', 'label': 'Run date', 'type': 'date'},
        {'key': 'catalogueDate', 'label': 'Catalogue date', 'type': 'date'},
        {'key': 'n', 'label': 'n', 'type': 'integer'},
        {'key': 'dim', 'label': 'Dimension', 'type': 'integer'},
        {'key': 'results.caseCount', 'label': 'Saved numerical rows', 'type': 'integer'},
        {'key': 'results.fileCount', 'label': 'Downloads', 'type': 'integer'},
    ]
    overview_by_id = {run['runId']: run for run in overview_data['runs']}
    for item in overview:
        run = overview_by_id.get(item['runId'])
        if run is None:
            run = {'runId': item['runId'], 'task': item['task'], 'status': item['status']}
            overview_data['runs'].append(run)
            overview_by_id[item['runId']] = run
        run.update({key: value for key, value in item.items() if key not in ('runId', 'artifacts')})
        run['artifacts'] = item['artifacts']
        run['assessment'] = item['assessment']
    overview_data['docs'] = [
        {'title': 'Chronological numerical studies', 'path': 'study-assets/notes/numerical-studies.txt',
         'description': 'Indexed record of the numerical studies in chronological order.'},
        {'title': 'Hamiltonian studies', 'path': 'study-assets/notes/hamiltonian-studies.txt',
         'description': 'Saved Hamiltonian calculations, comparisons and interpretation limits.'},
        {'title': 'Volume studies', 'path': 'study-assets/notes/volume-studies.txt',
         'description': 'Saved volume calculations, validation and open normalization questions.'},
        {'title': 'Thermal area sectors', 'path': 'study-assets/notes/thermal-area-sectors.txt',
         'description': 'Thermal area and spin-sector numerical records.'},
        {'title': 'T11 geometric interpretation', 'path': 'study-assets/notes/t11-geometric-interpretation.txt',
         'description': 'Prepared-state data and the limits of the geometric interpretation.'},
    ]
    write(DASH / 'data.json', overview_data)
    return datasets


if __name__ == '__main__':
    datasets = export_numerical_data()
    print(f'Exported {len(datasets)} InfoDash datasets, {sum(d["cases"] for d in datasets)} numerical rows')

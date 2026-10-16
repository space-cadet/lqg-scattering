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
    'fl-face-activation': 'results/fl-face-activation/summary.csv',
    'thermal-closed-entanglement': 'results/thermal-closed-entanglement/temperature_summary.csv',
    'thermal-closure-temperature': 'results/thermal-closure-temperature/closure_temperature.csv',
    'thermal-closed-projection': 'results/thermal-closed-projection/temperature_summary.csv',
    't9a-singlet-exchange': 'results/t9a-singlet-exchange/thermal.csv',
    'vacuum-area': 'figures/thermal-area-sectors/thermal_coefficients_vacuum.csv',
    'vacuum-spin': 'figures/thermal-spin-sectors/thermal_vacuum_spin.csv',
    't11-candidate-hamiltonians': 'results/t11-candidate-hamiltonians/model_summary.csv',
    't11-geometric-redistribution': 'results/t11-geometric-redistribution/summary.csv',
}
PARAMETERS = {'n', 'N', 'K', 'J', 'L', 'graph', 'case', 'candidate', 'U_over_t', 'alpha',
              'beta', 'beta_hbar_omega', 'state', 'seed', 'eps', 'epsilon', 'phiRadians',
              'q_bosons_per_copy', 'bosons_per_copy', 'total_spin_S', 'family', 'channel', 'M',
              'temperature', 'temperature_kBT_over_hbar_omega', 'channels', 'phase_case',
              'rotor_count', 'energy_coupling_ratio', 'coupling', 'control_type',
              'preparation', 'packet_scale_at_N8', 'seed_count', 'phase', 'window_end', 'U',
              'm', 'packet_energy', 'mean_total_energy', 'accepted_cutoff', 'sector_dimension',
              'source_class', 'source_spin', 'transition', 'from_active_channels',
              'to_active_channels', 'operator', 'operator_order'}
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
            if identifier == 't11-geometric-redistribution':
                rows = [(selector, {**row, 'display_id': row['run'], 'series':
                    f"L={row['L']}; {row['graph']}; {row['preparation'].replace('_', ' ')}"})
                    for selector, row in rows]
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
        hashes = dict(study.get('sourceHashes', {}))
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
            case_id = row.get('display_id') or row.get('model_id') or row.get('state') or f'case-{i+1:04d}'
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
        column_views = {
            't11-quantum-planar-rotors': {
                'visible': {'runId', 'parameters.m', 'parameters.packet_energy', 'parameters.mean_total_energy',
                    'results.late_quantum_cold_pair_fraction', 'results.late_classical_cold_pair_fraction',
                    'results.late_quantum_entropy_hot_pair_nats', 'results.late_quantum_entropy_cold_pair_nats',
                    'results.late_quantum_entropy_per_rotor_nats'},
                'labels': {'runId': 'Case', 'parameters.m': 'Initial momentum m',
                    'parameters.packet_energy': 'Initial pair energy', 'parameters.mean_total_energy': 'Mean total energy',
                    'results.late_quantum_cold_pair_fraction': 'Quantum cold-pair fraction',
                    'results.late_classical_cold_pair_fraction': 'Classical cold-pair fraction',
                    'results.late_quantum_entropy_hot_pair_nats': 'Entropy, initially energetic pair (nats)',
                    'results.late_quantum_entropy_cold_pair_nats': 'Entropy, initially cold pair (nats)',
                    'results.late_quantum_entropy_per_rotor_nats': 'Mean single-rotor entropy (nats)',
                    'series': 'Initial momentum'},
            },
            't11-face-connectivity': {
                'visible': {'runId', 'parameters.L', 'parameters.K', 'parameters.graph',
                    'parameters.source_class', 'parameters.transition', 'parameters.from_active_channels',
                    'parameters.to_active_channels', 'parameters.operator', 'results.matrix_element',
                    'results.source_counts_label', 'results.target5_counts_label', 'results.target6_counts_label',
                    'results.singlet_4_to_5_rank', 'results.singlet_4_to_5_source_nullity',
                    'results.direct_4_to_6_block_norm', 'results.singlet_4_to_5_block_frobenius_norm'},
                'labels': {'runId': 'Witness / transition', 'parameters.L': 'Available channels L',
                    'parameters.K': 'Fixed area K', 'parameters.graph': 'Hopping graph',
                    'parameters.source_class': 'Source sector', 'parameters.transition': 'Occupation transition',
                    'parameters.from_active_channels': 'From active channels',
                    'parameters.to_active_channels': 'To active channels', 'parameters.operator': 'Operator',
                    'results.matrix_element': 'Signed matrix element (H or H²)',
                    'results.source_counts_label': 'Source counts', 'results.target5_counts_label': 'Five-channel witness',
                    'results.target6_counts_label': 'Six-channel witness',
                    'results.singlet_4_to_5_rank': 'Singlet rank, 4→5',
                    'results.singlet_4_to_5_source_nullity': 'Singlet source nullity, 4→5',
                    'results.direct_4_to_6_block_norm': 'Direct 4→6 block norm',
                    'results.singlet_4_to_5_block_frobenius_norm': 'Control singlet block norm',
                    'series': 'Graph and source sector'},
            },
            't11-geometric-redistribution': {
                'visible': {'runId', 'parameters.L', 'parameters.K', 'parameters.graph', 'parameters.alpha',
                    'parameters.preparation', 'results.projection_probability', 'results.late_mean_active',
                    'results.late_receiver_area_fraction', 'results.late_receiver_casimir_fraction',
                    'results.late_probability_at_least5', 'results.late_probability_all_channels'},
                'labels': {'runId': 'Trajectory summary', 'parameters.L': 'Available channels L',
                    'parameters.K': 'Fixed area K', 'parameters.graph': 'Hopping graph',
                    'parameters.alpha': 'Casimir coupling α', 'parameters.preparation': 'Input preparation',
                    'results.projection_probability': 'Sharp-state preparation probability',
                    'results.late_mean_active': 'Late mean active channels',
                    'results.late_receiver_area_fraction': 'Late area in receivers / K',
                    'results.late_receiver_casimir_fraction': 'Late receiver Casimir fraction',
                    'results.late_probability_at_least5': 'Late probability of ≥5 active channels',
                    'results.late_probability_all_channels': 'Late probability all channels are active',
                    'results.series': 'Size, graph and preparation'},
            },
        }
        if identifier in column_views:
            view = column_views[identifier]
            for col in cols:
                col['visible'] = col['key'] in view['visible']
                if col['key'] in view['labels']:
                    col['label'] = view['labels'][col['key']]
        if identifier == 'thermal-closed-entanglement':
            visible = {'runId', 'parameters.temperature', 'results.projection_probability',
                'results.entropy_nats', 'results.area_entropy_nats', 'results.within_area_entropy_nats',
                'results.renyi2_nats', 'results.mean_area', 'results.joint_F12_creation_real'}
            labels = {'parameters.temperature': 'Temperature T*',
                'results.projection_probability': 'Closed fraction',
                'results.entropy_nats': 'Entanglement entropy (nats)',
                'results.area_entropy_nats': 'Area-distribution entropy (nats)',
                'results.within_area_entropy_nats': 'Within-area entropy (nats)',
                'results.renyi2_nats': 'Rényi-2 entropy (nats)',
                'results.mean_area': 'Mean area per copy',
                'results.joint_F12_creation_real': 'Joint singlet coherence'}
            for col in cols:
                col['visible'] = col['key'] in visible
                col['label'] = labels.get(col['key'],col['label'])
        numerics = [c['key'] for c in cols if c['type'] == 'number']
        if study.get('chart'):
            chart_spec = study['chart']
            chart = {key: value for key, value in chart_spec.items() if key != 'labels'}
            for col in cols:
                col['label'] = chart_spec.get('labels', {}).get(col['key'], col['label'])
        else:
            preferred_x = next((k for k in ('parameters.temperature', 'parameters.temperature_kBT_over_hbar_omega', 'parameters.alpha', 'parameters.K', 'parameters.J', 'parameters.beta', 'parameters.beta_hbar_omega', 'parameters.eps', 'parameters.bosons_per_copy', 'parameters.q_bosons_per_copy') if k in numerics), None)
            preferred_y = next((k for k in ('results.maximum_sampled_active_faces', 'results.entropy_nats', 'results.conditional_mean_area', 'results.ground_volume_mean_project_units', 'results.ground_mean_volume', 'results.ground_volume', 'results.volume_mean', 'results.equal_weight_mean', 'results.equal_weight_closed_rs_mean', 'results.sector_probability', 'results.P_q_S', 'results.V', 'results.corr', 'results.gibbs.q2') if k in numerics), None)
            chart = {'type': 'scatter'}
            if len(numerics) >= 2:
                chart.update(x=preferred_x or numerics[0], y=preferred_y or next((k for k in numerics if k.startswith('results.')), numerics[1]))
                # A series must include every varying model control to avoid connecting unrelated systems.
                grouping = [k for k in ('graph', 'candidate', 'U_over_t', 'channels', 'phase_case', 'n', 'sourceGroup', 'family', 'case', 'beta_hbar_omega') if any(k in run['parameters'] or k in run['results'] for run in runs) and 'parameters.' + k != chart['x'] and not (k=='beta_hbar_omega' and chart['x'] in ('parameters.temperature','parameters.temperature_kBT_over_hbar_omega'))]
                if grouping:
                    for run in runs:
                        run['series'] = ', '.join(f'{k}={run["parameters"].get(k, run["results"].get(k))}' for k in grouping)
                    cols.append({'key': 'series', 'label': 'Series', 'type': 'string', 'visible': False})
                    chart['groupBy'] = 'series'
        note_files = {f['source']: f for f in study['files']
                      if f['source'].startswith('notes/') and f['source'].endswith('.md')}
        selected_notes = study.get('documentNotes', list(note_files))
        study_docs = [{'title': Path(source).stem.replace('-', ' ').capitalize(),
                       'path': '../'+note_files[source]['path'], 'sourcePath': source,
                       'description': 'Explanation and calculation record for this study.'}
                      for source in selected_notes if source in note_files]
        data = {'schemaVersion': '1.0.0', 'project': {'name': study['title'], 'subtitle': study['description']},
                'columns': cols, 'charts': chart, 'runs': runs, 'figures': figures,
                'docs': [*study_docs, {'title': 'Numerical studies overview', 'path': '../index.html'}]}
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
    # The supplemental datasets and each catalogue study share one root index.
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
        {'title': 'Face growth and energy sharing', 'path': 'study-assets/notes/face-energy-equipartition.txt',
         'description': 'Verified large-area free-hopping controls and proposed neighbouring-face F/J interactions.'},
        {'title': 'Entanglement of closed thermal polyhedra', 'path': 'study-assets/notes/thermal-entanglement.txt',
         'description': 'Schmidt spectra, area-sector entropy, joint singlet coherence and convergence.'},
        {'title': 'Heating, equilibrium and singlet exchange', 'path': 'study-assets/notes/thermal-geometry-and-singlet-exchange.txt',
         'description': 'Temperature-dependent closure and geometry, Gibbs test and finite exchange model.'},
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
        {'title': 'Classical rotor energy transfer and equilibration', 'path': 'study-assets/notes/classical-rotor-equilibration.txt',
         'description': 'Finite-area face-channel pilot, grouped rotor summaries and equilibrium comparisons.'},
        {'title': 'Why fast rotors exchange little energy', 'path': 'study-assets/notes/few-rotor-energy-transfer.txt',
         'description': 'Exact planar-pair transfer bound and separate three-dimensional controls.'},
        {'title': 'Coupling strength and the apparent transfer cutoff', 'path': 'study-assets/notes/rotor-coupling-crossover.txt',
         'description': 'Finite-time coupling scan, direct controls and delayed transfer.'},
        {'title': 'Quantum and geometric T11 results', 'path': 'study-assets/notes/quantum-geometry-research.txt',
         'description': 'NS37–NS40: planar-rotor transfer, occupation connectivity, exact-singlet area redistribution, and its post-run permutation rule.'},
        {'title': 'Four quantum planar rotors at zero total momentum', 'path': 'study-assets/notes/quantum-planar-rotor-energy-transfer.txt',
         'description': 'Two matched quantum/classical energy-transfer cases and quantum single-rotor entropies.'},
        {'title': 'Four-to-five-to-six face-channel connectivity', 'path': 'study-assets/notes/face-activation-connectivity.txt',
         'description': 'Exact closed and open occupation transitions, including direct and two-hop matrix elements.'},
        {'title': 'Exact-singlet geometric area redistribution', 'path': 'study-assets/notes/geometric-area-redistribution.txt',
         'description': 'Fifty-four exact-singlet trajectories, selected geometry samples and a post-run symmetry diagnostic.'},
    ]
    write(DASH / 'data.json', overview_data)
    return datasets


if __name__ == '__main__':
    datasets = export_numerical_data()
    print(f'Exported {len(datasets)} InfoDash datasets, {sum(d["cases"] for d in datasets)} numerical rows')

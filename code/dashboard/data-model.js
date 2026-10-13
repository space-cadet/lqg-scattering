/* Shared browser/CLI data handling. No package installation is required. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.InfoDashData = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const blockedKeys = new Set(['__proto__', 'prototype', 'constructor']);
  const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  function get(object, path) {
    return String(path).split('.').reduce((value, key) =>
      value != null && !blockedKeys.has(key) && Object.hasOwn(Object(value), key) ? value[key] : undefined, object);
  }
  function set(object, path, value) {
    const keys = String(path).split('.');
    if (keys.some(key => !key || blockedKeys.has(key))) throw new Error(`Invalid field path: ${path}`);
    let target = object;
    for (const key of keys.slice(0, -1)) {
      if (!isObject(target[key])) target[key] = {};
      target = target[key];
    }
    target[keys.at(-1)] = value;
  }
  function validDate(value, datetime = false) {
    if (typeof value !== 'string') return false;
    const date = value.slice(0, 10);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return false;
    const time = Date.parse(`${date}T00:00:00Z`);
    if (!Number.isFinite(time) || new Date(time).toISOString().slice(0, 10) !== date) return false;
    return datetime ? /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/i.test(value) && Number.isFinite(Date.parse(value)) : value === date;
  }
  function checkSchema(value, schema, rootSchema, path = '$', errors = []) {
    if (schema.$ref) {
      const ref = schema.$ref.slice(2).split('/').reduce((node, key) => node[key], rootSchema);
      return checkSchema(value, ref, rootSchema, path, errors);
    }
    if (Object.hasOwn(schema, 'const') && value !== schema.const) errors.push(`${path}: expected ${JSON.stringify(schema.const)}`);
    if (schema.enum && !schema.enum.includes(value)) errors.push(`${path}: expected one of ${schema.enum.join(', ')}`);
    if (schema.type) {
      const types = [].concat(schema.type);
      const matches = types.some(type => type === 'object' ? isObject(value)
        : type === 'array' ? Array.isArray(value)
        : type === 'integer' ? Number.isInteger(value)
        : type === 'number' ? typeof value === 'number' && Number.isFinite(value)
        : typeof value === type);
      if (!matches) { errors.push(`${path}: expected ${types.join(' or ')}`); return errors; }
    }
    if (typeof value === 'string') {
      if (schema.minLength && value.length < schema.minLength) errors.push(`${path}: must not be empty`);
      if (schema.pattern && !new RegExp(schema.pattern).test(value)) errors.push(`${path}: invalid format`);
      if (schema.format === 'date' && !validDate(value)) errors.push(`${path}: expected YYYY-MM-DD`);
      if (schema.format === 'date-time' && !validDate(value, true)) errors.push(`${path}: expected an ISO timestamp with timezone`);
    }
    if (typeof value === 'number') {
      if (!Number.isFinite(value)) errors.push(`${path}: expected a finite number`);
      if (schema.minimum !== undefined && value < schema.minimum) errors.push(`${path}: below ${schema.minimum}`);
      if (schema.maximum !== undefined && value > schema.maximum) errors.push(`${path}: above ${schema.maximum}`);
    }
    if (isObject(value)) {
      for (const key of schema.required || []) if (!Object.hasOwn(value, key)) errors.push(`${path}.${key}: required`);
      for (const [key, child] of Object.entries(value)) {
        if (blockedKeys.has(key)) { errors.push(`${path}.${key}: reserved field name`); continue; }
        const childSchema = schema.properties?.[key] || (isObject(schema.additionalProperties) ? schema.additionalProperties : null);
        if (childSchema) checkSchema(child, childSchema, rootSchema, `${path}.${key}`, errors);
        else if (schema.additionalProperties === false) errors.push(`${path}.${key}: unknown field`);
      }
    }
    if (Array.isArray(value) && schema.items) value.forEach((item, i) => checkSchema(item, schema.items, rootSchema, `${path}[${i}]`, errors));
    return errors;
  }
  function normalize(input) {
    if (!isObject(input)) return input;
    const data = JSON.parse(JSON.stringify(input));
    // Existing InfoDash data files remain readable. Explicit versions are checked.
    data.schemaVersion ??= '1.0.0';
    data.runs = Array.isArray(data.runs) ? data.runs.map(run => {
      if (!isObject(run)) return run;
      if (isObject(run.params) && run.parameters === undefined) run.parameters = run.params;
      return run;
    }) : data.runs;
    if (Array.isArray(data.docs)) data.docs = data.docs.map(doc => isObject(doc) ? {...doc, path: doc.path ?? doc.file} : doc);
    return data;
  }
  function leaves(object, prefix = '') {
    return Object.entries(object).flatMap(([key, value]) => {
      if (blockedKeys.has(key)) return [];
      const path = prefix ? `${prefix}.${key}` : key;
      return isObject(value) ? leaves(value, path) : Array.isArray(value) ? [] : [path];
    });
  }
  function columns(data) {
    if (Array.isArray(data.columns) && data.columns.length) return data.columns;
    const fields = [...new Set((data.runs || []).flatMap(run => leaves(run)))].filter(key =>
      !/^(params|provenance|verification|assessment)(\.|$)/.test(key));
    return fields.map(key => {
      const values = data.runs.map(run => get(run, key)).filter(value => value != null);
      const type = values.length && values.every(value => typeof value === 'number') ? 'number'
        : values.length && values.every(value => typeof value === 'boolean') ? 'boolean'
        : values.length && values.every(value => validDate(value)) ? 'date'
        : values.length && values.every(value => validDate(value, true)) ? 'datetime' : 'string';
      return {key, label: key.replace(/^(parameters|results)\./, ''), type};
    });
  }
  function validate(data, schema) {
    const errors = checkSchema(data, schema, schema);
    if (errors.length) return errors;
    if (!Array.isArray(data.runs)) return errors;
    const ids = new Set();
    data.runs.forEach((run, i) => {
      if (ids.has(run.runId)) errors.push(`$.runs[${i}].runId: duplicate ${run.runId}`);
      ids.add(run.runId);
    });
    const fields = columns(data), keys = new Set();
    fields.forEach(column => {
      if (typeof column.key !== 'string') return;
      if (keys.has(column.key)) errors.push(`$.columns: duplicate ${column.key}`);
      keys.add(column.key);
      if (column.key.split('.').some(key => blockedKeys.has(key) || !key)) errors.push(`$.columns: invalid key ${column.key}`);
      data.runs.forEach((run, i) => {
        if (!data.columns?.length) return;
        const value = get(run, column.key);
        if (value == null) return;
        const okay = column.type === 'number' ? typeof value === 'number' && Number.isFinite(value)
          : column.type === 'integer' ? Number.isInteger(value)
          : column.type === 'date' ? validDate(value)
          : column.type === 'datetime' ? validDate(value, true)
          : typeof value === column.type;
        if (!okay) errors.push(`$.runs[${i}].${column.key}: expected ${column.type}`);
      });
    });
    for (const axis of ['x', 'y']) {
      const key = data.charts?.[axis];
      if (!key) continue;
      const column = fields.find(item => item.key === key);
      const allowed = axis === 'x' ? ['number', 'integer', 'date', 'datetime'] : ['number', 'integer'];
      if (!column || column.chart === false || !allowed.includes(column.type)) errors.push(`$.charts.${axis}: select a chartable ${axis === 'y' ? 'numeric ' : ''}column`);
    }
    if (data.charts?.groupBy && !keys.has(data.charts.groupBy) && !data.runs.some(run => get(run, data.charts.groupBy) !== undefined)) errors.push('$.charts.groupBy: select a recorded field');
    return errors;
  }
  const label = column => column.unit ? `${column.label} (${column.unit})` : column.label;
  function display(value, column = {}) {
    if (value == null) return '—';
    if (typeof value === 'number') return column.precision ? Number(value.toPrecision(column.precision)).toString() : String(value);
    return typeof value === 'object' ? JSON.stringify(value) : String(value);
  }
  function chartPoints(data, xKey, yKey, groupKey) {
    const xColumn = columns(data).find(column => column.key === xKey);
    return data.runs.flatMap(run => {
      const rawX = get(run, xKey), y = get(run, yKey);
      if (rawX == null || y == null) return [];
      const x = ['date', 'datetime'].includes(xColumn?.type) ? new Date(rawX) : rawX;
      if ((x instanceof Date ? !Number.isFinite(x.getTime()) : typeof x !== 'number' || !Number.isFinite(x)) || typeof y !== 'number' || !Number.isFinite(y)) return [];
      return [{x, y, runId: run.runId, group: groupKey ? display(get(run, groupKey)) : 'All runs'}];
    });
  }
  return {get, set, normalize, columns, validate, checkSchema, validDate, label, display, chartPoints};
});

/* Accessible inline-SVG plots for the weighted-input T5c volume pilot. */
(function () {
  const COLORS = {
    regular: "#0072B2",
    unequal: "#D55E00",
    j2: "#0072B2",
    j4: "#E69F00",
    j6: "#009E73",
    j7: "#CC79A7",
    classical: "#343a40",
  };
  const J_SERIES = [
    { J: 2, color: COLORS.j2, marker: "circle", dash: "" },
    { J: 4, color: COLORS.j4, marker: "square", dash: "7 4" },
    { J: 6, color: COLORS.j6, marker: "triangle", dash: "3 3" },
    { J: 7, color: COLORS.j7, marker: "diamond", dash: "9 3 2 3" },
  ];

  const esc = (value) => String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[ch]);
  const fixed = (value, digits = 2) => Number(value).toFixed(digits);
  const complexText = (z) => `${fixed(z.real, 3)} ${z.imag < 0 ? "−" : "+"} ${fixed(Math.abs(z.imag), 3)}i`;

  function marker(shape, x, y, color, size = 5) {
    if (shape === "square") {
      return `<rect x="${x - size}" y="${y - size}" width="${2 * size}" height="${2 * size}" fill="${color}" stroke="white" stroke-width="1.5"/>`;
    }
    if (shape === "diamond") {
      return `<polygon points="${x},${y - size - 1} ${x + size + 1},${y} ${x},${y + size + 1} ${x - size - 1},${y}" fill="${color}" stroke="white" stroke-width="1.5"/>`;
    }
    if (shape === "triangle") {
      return `<polygon points="${x},${y - size - 1} ${x + size + 1},${y + size} ${x - size - 1},${y + size}" fill="${color}" stroke="white" stroke-width="1.5"/>`;
    }
    return `<circle cx="${x}" cy="${y}" r="${size}" fill="${color}" stroke="white" stroke-width="1.5"/>`;
  }

  function axes({ x, y, w, h, yMax, yStep, xLabels, yDigits = 1, yPrefix = "" }) {
    let svg = "";
    for (let value = 0; value <= yMax + 1e-10; value += yStep) {
      const py = y + h - (value / yMax) * h;
      svg += `<line x1="${x}" y1="${py}" x2="${x + w}" y2="${py}" stroke="var(--border)"/><text x="${x - 9}" y="${py + 4}" text-anchor="end" fill="currentColor" font-size="11">${yPrefix}${value.toFixed(yDigits)}</text>`;
    }
    svg += `<line x1="${x}" y1="${y}" x2="${x}" y2="${y + h}" stroke="currentColor"/><line x1="${x}" y1="${y + h}" x2="${x + w}" y2="${y + h}" stroke="currentColor"/>`;
    xLabels.forEach((label, index) => {
      const px = x + (index / Math.max(1, xLabels.length - 1)) * w;
      svg += `<line x1="${px}" y1="${y + h}" x2="${px}" y2="${y + h + 5}" stroke="currentColor"/><text x="${px}" y="${y + h + 22}" text-anchor="middle" fill="currentColor" font-size="11">${esc(label)}</text>`;
    });
    return svg;
  }

  function convergencePlot(geometries) {
    const width = 940, height = 385;
    const panels = [
      { key: "meanRatio", title: "Mean / classical target", yMax: 1.2, yStep: 0.3, desc: "Geometry-matched quantum mean divided by the unit-area classical target, with a reference at one." },
      { key: "spreadRatio", title: "Intrinsic spread / classical target", yMax: 0.9, yStep: 0.3, desc: "The standard deviation of positive volume divided by the same classical target. This is state spread, not uncertainty of a sample mean." },
    ];
    let svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="t5c-convergence-title t5c-convergence-desc"><title id="t5c-convergence-title">Weighted FL positive-volume comparison versus J</title><desc id="t5c-convergence-desc">${panels.map((p) => p.desc).join(" ")} Two input tetrahedra are shown; the selected four-valent RS and AL curves coincide after geometric normalization.</desc>`;
    panels.forEach((panel, panelIndex) => {
      const originX = 18 + panelIndex * 466;
      const plot = { x: originX + 58, y: 58, w: 375, h: 230 };
      const xAt = (j) => plot.x + ((j - 1) / 6) * plot.w;
      const yAt = (value) => plot.y + plot.h - (value / panel.yMax) * plot.h;
      svg += `<text x="${originX + 245}" y="26" text-anchor="middle" fill="currentColor" font-size="15" font-weight="600">${panel.title}</text>`;
      svg += axes({ ...plot, yMax: panel.yMax, yStep: panel.yStep, xLabels: [1, 2, 3, 4, 5, 6, 7], yDigits: 1 });
      svg += `<text x="${plot.x + plot.w / 2}" y="${plot.y + plot.h + 47}" text-anchor="middle" fill="currentColor" font-size="12">Area label J</text><text transform="translate(${originX + 15} ${plot.y + plot.h / 2}) rotate(-90)" text-anchor="middle" fill="currentColor" font-size="12">${panel.key === "meanRatio" ? "mean ratio" : "σV / Vclassical"}</text>`;
      if (panel.key === "meanRatio") {
        const referenceY = yAt(1);
        svg += `<line x1="${plot.x}" y1="${referenceY}" x2="${plot.x + plot.w}" y2="${referenceY}" stroke="var(--text)" stroke-dasharray="5 4" opacity="0.8"/><text x="${plot.x + plot.w - 3}" y="${referenceY - 6}" text-anchor="end" fill="currentColor" font-size="10">classical = 1</text>`;
      }
      geometries.forEach((geometry, seriesIndex) => {
        const rows = geometry.results;
        const color = seriesIndex === 0 ? COLORS.regular : COLORS.unequal;
        const dash = seriesIndex === 0 ? "" : "7 4";
        const markerShape = seriesIndex === 0 ? "circle" : "square";
        const points = rows.map((row) => `${xAt(row.J)},${yAt(row[panel.key])}`).join(" ");
        svg += `<polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.5" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
        rows.forEach((row) => {
          const px = xAt(row.J), py = yAt(row[panel.key]);
          const label = `${geometry.label}; J=${row.J}; ${panel.key === "meanRatio" ? `mean ratio ${fixed(row.meanRatio, 4)}` : `intrinsic spread ratio ${fixed(row.spreadRatio, 4)}`}`;
          svg += `<g tabindex="0" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>${marker(markerShape, px, py, color, 5)}</g>`;
        });
      });
      const legendY = 365;
      geometries.forEach((geometry, index) => {
        const color = index === 0 ? COLORS.regular : COLORS.unequal;
        const dash = index === 0 ? "" : "7 4";
        const markerShape = index === 0 ? "circle" : "square";
        const lx = originX + 112 + index * 190;
        svg += `<line x1="${lx}" y1="${legendY}" x2="${lx + 26}" y2="${legendY}" stroke="${color}" stroke-width="2.5" ${dash ? `stroke-dasharray="${dash}"` : ""}/>${marker(markerShape, lx + 13, legendY, color, 4)}<text x="${lx + 33}" y="${legendY + 4}" fill="currentColor" font-size="11">${esc(geometry.label)}</text>`;
      });
    });
    return svg + "</svg>";
  }

  function ratioColor(value) {
    const stops = [
      { x: 0.3, rgb: [246, 189, 96] },
      { x: 0.7, rgb: [246, 229, 157] },
      { x: 1.05, rgb: [120, 184, 147] },
    ];
    const v = Math.max(stops[0].x, Math.min(stops[2].x, value));
    let left = stops[0], right = stops[1];
    if (v > stops[1].x) [left, right] = [stops[1], stops[2]];
    const t = (v - left.x) / (right.x - left.x);
    const rgb = left.rgb.map((channel, index) => Math.round(channel + t * (right.rgb[index] - channel)));
    return `rgb(${rgb.join(",")})`;
  }

  function shapeGridPlot(grid) {
    const width = 960, height = 350;
    const diagonals = grid.diagonals;
    const angles = grid.bendAnglesDegrees;
    const panels = [
      { J: 2, x: 14 }, { J: 4, x: 330 }, { J: 6, x: 646 },
    ];
    let svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="t5c-grid-title t5c-grid-desc"><title id="t5c-grid-title">Unequal-area tetrahedron volume-ratio grid</title><desc id="t5c-grid-desc">Tile maps show geometry-matched positive-volume mean divided by the classical target for area fractions ${esc(grid.areaFractions.join(", "))}. Nine shapes are sampled at J=2 and J=4; four selected shapes at J=6.</desc>`;
    const allShapes = grid.shapes.concat(grid.selectedJ6);
    panels.forEach((panel) => {
      const cellW = 72, cellH = 52, gap = 4, gridX = panel.x + 52, gridY = 70;
      svg += `<text x="${panel.x + 145}" y="28" text-anchor="middle" fill="currentColor" font-size="15" font-weight="600">J = ${panel.J}${panel.J === 6 ? " (selected)" : ""}</text>`;
      angles.forEach((angle, rowIndex) => {
        const y = gridY + rowIndex * (cellH + gap);
        svg += `<text x="${gridX - 8}" y="${y + cellH / 2 + 4}" text-anchor="end" fill="currentColor" font-size="11">${fixed(angle, 0)}°</text>`;
        diagonals.forEach((diagonal, colIndex) => {
          const x = gridX + colIndex * (cellW + gap);
          const shape = allShapes.find((item) =>
            Math.abs(item.pairDiagonal - diagonal) < 1e-9
            && Math.abs(item.bendAngleDegrees - angle) < 1e-7
            && item.results.some((result) => result.J === panel.J)
          );
          const result = shape?.results.find((item) => item.J === panel.J);
          if (!result) {
            svg += `<rect x="${x}" y="${y}" width="${cellW}" height="${cellH}" rx="4" fill="var(--bg)" stroke="var(--border)" stroke-dasharray="4 3"/><text x="${x + cellW / 2}" y="${y + cellH / 2 + 4}" text-anchor="middle" fill="var(--muted)" font-size="12">—</text>`;
            return;
          }
          const label = `J=${panel.J}, pair diagonal d=${fixed(diagonal, 2)}, bend angle ${fixed(angle, 0)} degrees, ratio ${fixed(result.meanRatio, 4)}, vertex cross-ratio ${complexText(shape.vertexCrossRatio)}, face-normal cross-ratio ${complexText(shape.faceNormalCrossRatio)}`;
          const fill = ratioColor(result.meanRatio);
          svg += `<g tabindex="0" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title><rect x="${x}" y="${y}" width="${cellW}" height="${cellH}" rx="4" fill="${fill}" stroke="var(--border)"/><text x="${x + cellW / 2}" y="${y + cellH / 2 + 5}" text-anchor="middle" fill="#212529" font-size="13" font-weight="600">${fixed(result.meanRatio, 2)}</text></g>`;
        });
      });
      diagonals.forEach((diagonal, colIndex) => {
        const x = gridX + colIndex * (cellW + gap) + cellW / 2;
        svg += `<text x="${x}" y="${gridY + 3 * (cellH + gap) + 18}" text-anchor="middle" fill="currentColor" font-size="11">${fixed(diagonal, 2)}</text>`;
      });
      svg += `<text x="${gridX + (3 * cellW + 2 * gap) / 2}" y="${height - 50}" text-anchor="middle" fill="currentColor" font-size="12">Pair diagonal d</text>`;
    });
    svg += `<text x="19" y="${height - 52}" fill="currentColor" font-size="11">Bend φ</text><defs><linearGradient id="t5c-ratio-legend"><stop offset="0%" stop-color="${ratioColor(0.3)}"/><stop offset="53%" stop-color="${ratioColor(0.7)}"/><stop offset="100%" stop-color="${ratioColor(1.05)}"/></linearGradient></defs><rect x="785" y="${height - 28}" width="126" height="10" rx="3" fill="url(#t5c-ratio-legend)"/><text x="785" y="${height - 7}" fill="currentColor" font-size="10">0.3</text><text x="911" y="${height - 7}" text-anchor="end" fill="currentColor" font-size="10">1.05</text><text x="848" y="${height - 33}" text-anchor="middle" fill="currentColor" font-size="10">ratio to classical</text>`;
    return svg + "</svg>";
  }

  function crossRatioPlot(grid) {
    const width = 960, height = 395;
    const fields = [
      { key: "vertexCrossRatio", title: "Vertex cross-ratio on unit circumsphere" },
      { key: "faceNormalCrossRatio", title: "Face-normal spinor cross-ratio" },
    ];
    const diagonalColors = ["#0072B2", "#D55E00", "#009E73"];
    const angleMarkers = { 45: "circle", 90: "square", 135: "diamond" };
    let svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="t5c-cross-title t5c-cross-desc"><title id="t5c-cross-title">Complex cross-ratio coordinates for unequal-area tetrahedron shapes</title><desc id="t5c-cross-desc">The nine fixed-area shape samples are plotted in two complex planes. Color distinguishes pair diagonals and marker shape distinguishes bend angle. Cross-ratios are coordinates; six unit-sphere chord lengths remain necessary metric data.</desc>`;
    fields.forEach((field, panelIndex) => {
      const originX = 12 + panelIndex * 478;
      const plot = { x: originX + 64, y: 60, w: 365, h: 245 };
      const values = grid.shapes.map((shape) => shape[field.key]);
      const minRe = Math.min(...values.map((z) => z.real)), maxRe = Math.max(...values.map((z) => z.real));
      const minIm = Math.min(...values.map((z) => z.imag)), maxIm = Math.max(...values.map((z) => z.imag));
      const xSpan = Math.max(maxRe - minRe, 0.1), ySpan = Math.max(maxIm - minIm, 0.1);
      const xMin = minRe - xSpan * 0.12, xMax = maxRe + xSpan * 0.12;
      const yMin = minIm - ySpan * 0.12, yMax = maxIm + ySpan * 0.12;
      const xAt = (v) => plot.x + ((v - xMin) / (xMax - xMin)) * plot.w;
      const yAt = (v) => plot.y + plot.h - ((v - yMin) / (yMax - yMin)) * plot.h;
      svg += `<text x="${originX + 240}" y="25" text-anchor="middle" fill="currentColor" font-size="14" font-weight="600">${field.title}</text>`;
      for (let tick = 0; tick <= 4; tick++) {
        const xv = xMin + (tick / 4) * (xMax - xMin), px = xAt(xv);
        const yv = yMin + (tick / 4) * (yMax - yMin), py = yAt(yv);
        svg += `<line x1="${px}" y1="${plot.y}" x2="${px}" y2="${plot.y + plot.h}" stroke="var(--border)"/><text x="${px}" y="${plot.y + plot.h + 18}" text-anchor="middle" fill="currentColor" font-size="10">${xv.toFixed(2)}</text><line x1="${plot.x}" y1="${py}" x2="${plot.x + plot.w}" y2="${py}" stroke="var(--border)"/><text x="${plot.x - 7}" y="${py + 3}" text-anchor="end" fill="currentColor" font-size="10">${yv.toFixed(2)}</text>`;
      }
      svg += `<line x1="${plot.x}" y1="${plot.y + plot.h}" x2="${plot.x + plot.w}" y2="${plot.y + plot.h}" stroke="currentColor"/><line x1="${plot.x}" y1="${plot.y}" x2="${plot.x}" y2="${plot.y + plot.h}" stroke="currentColor"/><text x="${plot.x + plot.w / 2}" y="${plot.y + plot.h + 39}" text-anchor="middle" fill="currentColor" font-size="11">Re(λ)</text><text transform="translate(${originX + 15} ${plot.y + plot.h / 2}) rotate(-90)" text-anchor="middle" fill="currentColor" font-size="11">Im(λ)</text>`;
      grid.shapes.forEach((shape) => {
        const diagonalIndex = grid.diagonals.findIndex((d) => Math.abs(d - shape.pairDiagonal) < 1e-9);
        const z = shape[field.key], px = xAt(z.real), py = yAt(z.imag);
        const label = `d=${fixed(shape.pairDiagonal, 2)}, φ=${fixed(shape.bendAngleDegrees, 0)}°; λvertex=${complexText(shape.vertexCrossRatio)}; λnormal=${complexText(shape.faceNormalCrossRatio)}; unit-sphere chords ${Object.entries(shape.unitSphereChordDistances).map(([edge, length]) => `${edge}:${fixed(length, 3)}`).join(", ")}`;
        svg += `<g tabindex="0" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>${marker(angleMarkers[Math.round(shape.bendAngleDegrees)], px, py, diagonalColors[diagonalIndex], 5)}</g>`;
      });
    });
    const legendY = 378;
    const diagonals = grid.diagonals;
    diagonals.forEach((d, index) => {
      const x = 150 + index * 145;
      svg += `<circle cx="${x}" cy="${legendY}" r="5" fill="${diagonalColors[index]}"/><text x="${x + 9}" y="${legendY + 4}" fill="currentColor" font-size="10">d=${fixed(d, 2)}</text>`;
    });
    [45, 90, 135].forEach((angle, index) => {
      const x = 640 + index * 92;
      svg += `${marker(angleMarkers[angle], x, legendY, "#59636e", 4)}<text x="${x + 9}" y="${legendY + 4}" fill="currentColor" font-size="10">φ=${angle}°</text>`;
    });
    return svg + "</svg>";
  }

  function categoricalPlot(samples, kind) {
    const width = 940, height = 350;
    const isMean = kind === "mean";
    const title = isMean ? "Positive-volume means and classical target" : "Intrinsic positive-volume spread";
    const field = isMean ? "meanProjectUnitsOverJ32" : "sdProjectUnitsOverJ32";
    const yMax = isMean ? 0.007 : 0.006;
    const yStep = isMean ? 0.001 : 0.001;
    const cats = [
      { phi: 0, label: "0° flat" },
      { phi: 0.05, label: "0.05 rad" },
      { phi: Math.PI / 2, label: "90° regular" },
    ];
    const xLabels = cats.map((item) => item.label);
    const plot = { x: 82, y: 52, w: 800, h: 200 };
    const xAt = (index) => plot.x + (index / (cats.length - 1)) * plot.w;
    const yAt = (value) => plot.y + plot.h - (value / yMax) * plot.h;
    let svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="t5c-flat-${kind}-title t5c-flat-${kind}-desc"><title id="t5c-flat-${kind}-title">${title} along the flat path</title><desc id="t5c-flat-${kind}-desc">Three categorical samples: the exact flat boundary, phi equals 0.05 radians, and the regular tetrahedron. ${isMean ? "The classical input target is zero at the flat boundary; the quantum positive mean remains finite in the sampled J range." : "The plotted values are intrinsic standard deviations of the positive volume operator, not errors on the mean."}</desc>`;
    svg += `<text x="${width / 2}" y="24" text-anchor="middle" fill="currentColor" font-size="14" font-weight="600">${title}</text>`;
    svg += axes({ ...plot, yMax, yStep, xLabels, yDigits: 3 });
    svg += `<text x="${plot.x + plot.w / 2}" y="${height - 13}" text-anchor="middle" fill="currentColor" font-size="11">Sampled flat-path geometry (categories, not linear angle spacing)</text><text transform="translate(19 ${plot.y + plot.h / 2}) rotate(-90)" text-anchor="middle" fill="currentColor" font-size="11">${isMean ? "volume mean / J³⁄² (project units)" : "σV / J³⁄² (project units)"}</text>`;
    if (isMean) {
      const classical = cats.map((category) => {
        const row = samples.find((item) => Math.abs(item.phiRadians - category.phi) < 1e-10);
        return row?.classicalVolumeProjectUnits ?? 0;
      });
      const points = classical.map((value, index) => `${xAt(index)},${yAt(value)}`).join(" ");
      svg += `<polyline points="${points}" fill="none" stroke="${COLORS.classical}" stroke-width="2.5" stroke-dasharray="3 4"/>`;
      classical.forEach((value, index) => {
        const label = `classical input volume at ${cats[index].label}: ${value.toPrecision(5)} project units`;
        svg += `<g tabindex="0" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>${marker("diamond", xAt(index), yAt(value), COLORS.classical, 5)}</g>`;
      });
    }
    J_SERIES.forEach((series) => {
      const rows = cats.map((category) => samples.find((item) => item.J === series.J && Math.abs(item.phiRadians - category.phi) < 1e-10));
      if (rows.some((row) => !row)) return;
      const points = rows.map((row, index) => `${xAt(index)},${yAt(row[field])}`).join(" ");
      svg += `<polyline points="${points}" fill="none" stroke="${series.color}" stroke-width="2" stroke-dasharray="${series.dash}"/>`;
      rows.forEach((row, index) => {
        const value = row[field];
        const label = `J=${series.J}, ${kind === "mean" ? "mean" : "standard deviation"} ${value.toPrecision(5)} project units at ${cats[index].label}`;
        svg += `<g tabindex="0" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>${marker(series.marker, xAt(index), yAt(value), series.color, 5)}</g>`;
      });
    });
    const legendItems = J_SERIES.concat(isMean ? [{ label: "classical target", color: COLORS.classical, marker: "diamond", dash: "3 4" }] : []);
    legendItems.forEach((series, index) => {
      const x = 180 + index * (isMean ? 132 : 155), y = 300;
      const label = series.label || `J=${series.J}`;
      svg += `<line x1="${x}" y1="${y}" x2="${x + 22}" y2="${y}" stroke="${series.color}" stroke-width="2" stroke-dasharray="${series.dash}"/>${marker(series.marker, x + 11, y, series.color, 4)}<text x="${x + 28}" y="${y + 4}" fill="currentColor" font-size="10">${label}</text>`;
    });
    return svg + "</svg>";
  }

  window.renderT5cInputVolumeSection = function (bundle, resultsFile) {
    const geometries = bundle.inputGeometries;
    const grid = bundle.unequalShapeGrid;
    const samples = bundle.flatPath.samples;
    const regular = geometries.find((item) => item.id === "regular");
    const unequal = geometries.find((item) => item.id === "unequal_skew");
    const regJ7 = regular.results.find((row) => row.J === 7).meanRatio;
    const unequalJ7 = unequal.results.find((row) => row.J === 7).meanRatio;
    const boundary = samples.find((row) => row.J === 7 && Math.abs(row.phiRadians) < 1e-12);
    const boundary05 = samples.find((row) => row.J === 7 && Math.abs(row.phiRadians - 0.05) < 1e-12);
    const maxClosure = Math.max(
      ...geometries.map((item) => item.spinorClosureError),
      ...grid.shapes.map((item) => item.spinorClosureError),
    );
    const maxAreaError = Math.max(
      ...geometries.flatMap((item) => item.results.map((row) => row.areaMeanError)),
      ...grid.shapes.flatMap((item) => item.results.map((row) => row.areaMeanError)),
      ...grid.selectedJ6.flatMap((item) => item.results.map((row) => row.areaMeanError)),
    );
    const ratioFile = esc(resultsFile || "t5c-input-volume.json");
    return String.raw`
      <section class="volume-study input-volume-study">
        <h3>T5c — Weighted input-geometry volume comparison</h3>
        <p>The new scans start from closed tetrahedral face data, form weighted FL spinors, and compare the positive volume with the classical volume of that same input tetrahedron. The fixed geometric factors are applied once across shapes and J. Individual quantum flux-vector means vanish by gauge invariance; the normals are input labels, while shape recovery is tested through inter-face correlations.</p>
        <div class="math-model">
          <h4>State family and normalization</h4>
          <p>At unit total area, the four input face-area fractions \(a_i\) and outward unit normals \(\mathbf n_i\) obey closure. The weighted spinors are built from normalized spinors \(\xi_i\) for those normals:</p>
          <div class="math-equation">\[\sum_{i=0}^{3}a_i=1,\qquad \sum_{i=0}^{3}a_i\mathbf n_i=0,\qquad \mathbf F_i=a_i\mathbf n_i.\]</div>
          <div class="math-equation">\[z_i=\sqrt{2a_i}\,\xi_i,\qquad \sum_{i=0}^{3}|z_i\rangle\langle z_i|=\mathbb I_2.\]</div>
          <p>The fixed-area Freidel–Livine state used in the scan is</p>
          <div class="math-equation">\[F_z^\dagger=\sum_{i&lt;j}[z_j|z_i\rangle F_{ij}^\dagger,\qquad |\Psi_{J,z}\rangle=\frac{(F_z^\dagger)^J|0\rangle}{\left\|(F_z^\dagger)^J|0\rangle\right\|},\qquad \langle\hat j_i\rangle_{\Psi_{J,z}}=J a_i.\]</div>
          <p>Here \([z_j|z_i\rangle=z_j^0z_i^1-z_j^1z_i^0\). The classical target at unit total area and at area label \(J\) is</p>
          <div class="math-equation">\[V_{\mathrm{cl}}^{(1)}=(\gamma\hbar)^{3/2}\sqrt{\frac{2}{9}\left|\det(\mathbf F_1,\mathbf F_2,\mathbf F_3)\right|},\qquad V_{\mathrm{cl}}(J)=J^{3/2}V_{\mathrm{cl}}^{(1)},\qquad \hbar=1.\]</div>
          <p>For \(X\in\{\mathrm{RS},\mathrm{AL}\}\), fixed factors \(\kappa_{\mathrm{RS}}=\sqrt{2/9}/4\) and \(\kappa_{\mathrm{AL}}=\sqrt{2/9}/2\) put each positive-volume operator on the same classical scale. The plotted mean ratio and intrinsic spread are</p>
          <div class="math-equation">\[R_X(J)=\frac{\kappa_X\langle\hat V_X^+\rangle_{\Psi_{J,z}}}{J^{3/2}V_{\mathrm{cl}}^{(1)}},\qquad S_X(J)=\frac{\kappa_X\sqrt{\langle(\hat V_X^+)^2\rangle_{\Psi_{J,z}}-\langle\hat V_X^+\rangle_{\Psi_{J,z}}^2}}{J^{3/2}V_{\mathrm{cl}}^{(1)}}.\]</div>
          <p>Thus \(R_X=1\) is the classical mean target, while \(S_X\) is the state’s volume spread, not an error bar on the mean. At zero classical volume the ratios are undefined, so the flat-path plots show absolute values scaled by \(J^{3/2}\).</p>
          <h4>Shape coordinates</h4>
          <p>The ordered vertex cross-ratio uses stereographic coordinates \(w_i\) on the unit circumsphere. The face-normal spinor cross-ratio uses \([z_i z_j]=z_i^0z_j^1-z_i^1z_j^0\):</p>
          <div class="math-equation">\[\lambda_{\mathrm{vertex}}=\frac{(w_0-w_2)(w_1-w_3)}{(w_0-w_3)(w_1-w_2)},\qquad \lambda_{\mathrm{normal}}=\frac{[z_0z_2][z_1z_3]}{[z_0z_3][z_1z_2]}.\]</div>
          <p>These are conformal coordinates. The records also retain all six normalized vertex chord lengths, which carry the Euclidean similarity-shape data needed for the classical volume.</p>
        </div>
        <div class="study-metrics">
          <div class="study-metric"><strong>${regJ7.toFixed(3)}</strong><span>regular mean / classical at J=7</span></div>
          <div class="study-metric"><strong>${unequalJ7.toFixed(3)}</strong><span>unequal-skew mean / classical at J=7</span></div>
          <div class="study-metric"><strong>${Number(maxClosure).toExponential(2)}</strong><span>max weighted-spinor closure residual</span></div>
          <div class="study-metric"><strong>${Number(maxAreaError).toExponential(2)}</strong><span>max mean-face-spin error</span></div>
          <div class="study-metric"><strong>${Number(boundary.meanProjectUnitsOverJ32).toFixed(5)}</strong><span>flat-boundary positive mean / \(J^{3/2}\) at \(J=7\)</span></div>
        </div>
        <h4>Convergence and fluctuations</h4>
        <div class="chart-container study-chart t5c-input-chart">${convergencePlot(geometries)}</div>
        <p class="hint">Left: \(\kappa\langle V\rangle_{\mathrm{project}}/(J^{3/2}V_{\mathrm{classical,project}})\), with one marking the classical target. Right: the intrinsic standard deviation divided by that target; it is not a standard error. The four-valent signs make calibrated RS and AL curves coincide by closure, so one curve per geometry is shown.</p>
        <h4>Unequal-area shape grid</h4>
        <p class="hint">Area fractions are \((a_i)=(${grid.areaFractions.map((value) => Number(value).toFixed(2)).join(", ")})\). Tile values are geometry-matched positive mean divided by the classical target. Rows vary bend angle \(\phi\); columns vary the pair diagonal \(d\) at unit total area. \(J=6\) includes four selected shapes only. Focus or hover on a tile to see both cross-ratios.</p>
        <div class="chart-container study-chart t5c-input-chart">${shapeGridPlot(grid)}</div>
        <h4>Cross-ratio coordinates for the sampled shapes</h4>
        <div class="chart-container study-chart t5c-input-chart">${crossRatioPlot(grid)}</div>
        <p class="hint">Color marks \(d\) and marker shape marks \(\phi\). The vertex cross-ratio is evaluated after projection from the unit circumsphere; the face-normal spinor cross-ratio is shown separately. A cross-ratio is a conformal coordinate, so the full record also retains all six normalized vertex chord lengths.</p>
        <h4>Approach to the flat boundary</h4>
        <div class="flat-plot-grid">
          <div class="chart-container study-chart t5c-input-chart">${categoricalPlot(samples, "mean")}</div>
          <div class="chart-container study-chart t5c-input-chart">${categoricalPlot(samples, "spread")}</div>
        </div>
        <p class="hint">At \(\phi=0\) the classical volume is zero while the positive quantum mean remains finite in this \(J\) range. At \(\phi=0.05\,\mathrm{rad}\), the \(J=7\) quantum/classical ratio is ${boundary05.meanRatio.toFixed(2)}. These are three sampled geometries, not a limit fit; neither order of the flat-shape and large-\(J\) limits is established.</p>
        <p class="hint">All volume values use project units with \(\gamma=${bundle.normalization.gamma},\ \hbar=${bundle.normalization.hbar}\). The physical regularization prefactor and graph embedding behind the AL signs remain open. <a href="${ratioFile}">Download dashboard result data</a>.</p>
      </section>`;
  };
})();

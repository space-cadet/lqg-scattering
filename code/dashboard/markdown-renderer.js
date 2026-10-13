/* Protect TeX expressions from Markdown emphasis before KaTeX renders them. */
(function (global) {
  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));

  function isEscaped(source, index) {
    let slashes = 0;
    for (let cursor = index - 1; cursor >= 0 && source[cursor] === '\\'; cursor--) slashes++;
    return slashes % 2 === 1;
  }

  function readDelimited(source, left, right, allowNewlines) {
    if (!source.startsWith(left)) return null;
    let end = source.indexOf(right, left.length);
    while (end !== -1 && isEscaped(source, end)) end = source.indexOf(right, end + right.length);
    if (end < 0) return null;
    const body = source.slice(left.length, end);
    if (!body.trim() || (!allowNewlines && body.includes('\n'))) return null;
    return { raw: source.slice(0, end + right.length), body };
  }

  const displayMath = {
    name: 'displayMath',
    level: 'block',
    start(source) {
      const match = /(?:^|\n)[ \t]{0,3}(?:\$\$|\\\[)/.exec(source);
      return match ? match.index + (match[0].startsWith('\n') ? 1 : 0) : -1;
    },
    tokenizer(source) {
      const prefix = /^[ \t]{0,3}/.exec(source)[0];
      const rest = source.slice(prefix.length);
      let match = readDelimited(rest, '$$', '$$', true);
      let delimiter = '$$';
      if (!match) { match = readDelimited(rest, '\\[', '\\]', true); delimiter = '\\['; }
      if (!match) return;
      const raw = prefix + match.raw;
      return { type: 'displayMath', raw, body: match.body, delimiter };
    },
    renderer(token) {
      const expression = token.delimiter === '$$'
        ? `$$${token.body}$$`
        : `\\[${token.body}\\]`;
      return `<div class="math-source math-source-display">${escapeHTML(expression)}</div>\n`;
    }
  };

  const inlineMath = {
    name: 'inlineMath',
    level: 'inline',
    start(source) {
      const match = /\\\(|\$(?!\$)/.exec(source);
      return match ? match.index : -1;
    },
    tokenizer(source) {
      for (const [left, right, allowNewlines] of [
        ['\\(', '\\)', false],
        ['$', '$', false]
      ]) {
        const match = readDelimited(source, left, right, allowNewlines);
        if (match && (left !== '$' || !match.raw.startsWith('$$'))) {
          return { type: 'inlineMath', raw: match.raw, expression: match.raw };
        }
      }
    },
    renderer(token) {
      return `<span class="math-source">${escapeHTML(token.expression)}</span>`;
    }
  };

  const renderer = new global.marked.Renderer();
  renderer.html = token => {
    const source = String(typeof token === 'string' ? token : token.text ?? '');
    const anchor = source.trim().match(/^<a\s+id=(['"])([A-Za-z0-9_-]+)\1\s*>\s*<\/a>$/i);
    return anchor ? `<span id="${anchor[2]}"></span>` : escapeHTML(source);
  };
  global.marked.use({
    gfm: true,
    breaks: false,
    renderer,
    extensions: [displayMath, inlineMath]
  });

  global.InfoDashMarkdown = {
    parse(source) {
      const anchors = [];
      const protectedSource = String(source).replace(/^[ \t]*<a\s+id=(['"])([A-Za-z0-9_-]+)\1\s*>\s*<\/a>[ \t]*$/gim, (_match, _quote, id) => {
        const marker = `INFODASHANCHOR${anchors.length}TOKEN`;
        anchors.push({marker, id});
        return marker;
      });
      let html = global.marked.parse(protectedSource);
      for (const {marker, id} of anchors) html = html.split(marker).join(`<span id="${id}"></span>`);
      return html;
    },
    escapeHTML
  };
})(window);

/* Prüft die Sprachpakete in src/lang gegen die englische Vorlage: gleiche Schlüssel, Platzhalter und HTML-Tags. */
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const base = fs.readFileSync(path.join(root, 'src/strings.js'), 'utf8');
const dir = path.join(root, 'src/lang');
let bad = 0;
const ph = s => (s.match(/\{\{?[A-Za-z_]+\}?\}/g) || []).sort().join(' ');
const tags = s => (s.match(/<\/?[a-z]+[^>]*>/g) || []).map(t => t.replace(/\s+/g, ' ')).filter(t => !/lbl-more/.test(t)).sort().join(' ');
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.js')).sort()) {
  const code = f.replace('.js', '');
  const r = (new Function(base + '\n' + fs.readFileSync(path.join(dir, f), 'utf8') + '\nreturn {I18N, CHAT};'))();
  for (const [name, T] of [['I18N', r.I18N], ['CHAT', r.CHAT]]) {
    const en = T.en, x = T[code];
    if (!x) { console.log(code, name, 'fehlt'); bad++; continue; }
    const miss = Object.keys(en).filter(k => !(k in x)), extra = Object.keys(x).filter(k => !(k in en));
    if (miss.length || extra.length) { console.log(code, name, 'fehlend:', miss.join(', '), '| zu viel:', extra.join(', ')); bad++; }
    for (const k of Object.keys(en)) {
      if (!(k in x)) continue;
      if (ph(en[k]) !== ph(x[k])) { console.log(code, name, k, 'Platzhalter:', ph(en[k]), '<>', ph(x[k])); bad++; }
      let te = tags(en[k]), tx = tags(x[k]);
      if (k === 'cta.chat') { te = tx = ''; }
      if (te !== tx) { console.log(code, name, k, 'Tags:', te, '<>', tx); bad++; }
      if (!x[k].trim()) { console.log(code, name, k, 'leer'); bad++; }
    }
    console.log(code, name, Object.keys(x).length, 'Schlüssel, Zeichen:', Object.values(x).join('').length);
  }
}
console.log(bad ? bad + ' FEHLER' : 'Sprachpakete in Ordnung');
process.exit(bad ? 1 : 0);

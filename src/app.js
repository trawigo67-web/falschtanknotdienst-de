(function () {
  'use strict';

  var CFG = /*CFG*/;
  var doc = document;
  var root = doc.documentElement;

  function $(s, r) { return (r || doc).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); }
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* Speichern nicht möglich: Seite läuft trotzdem */ } }
  };
  var reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  function isWide() { return !!(window.matchMedia && window.matchMedia('(min-width: 760px)').matches); }

  /* ---------- Sprache ---------- */
  var lang = 'de';
  var orig = { html: new Map(), aria: new Map(), ph: new Map(), title: doc.title };
  var metaDesc = $('meta[name="description"]');
  orig.desc = metaDesc ? metaDesc.getAttribute('content') : '';
  $$('[data-i18n]').forEach(function (el) { orig.html.set(el, el.innerHTML); });
  $$('[data-i18n-aria]').forEach(function (el) { orig.aria.set(el, el.getAttribute('aria-label')); });
  $$('[data-i18n-ph]').forEach(function (el) { orig.ph.set(el, el.getAttribute('placeholder')); });

  function t(key) {
    var d = I18N[lang];
    if (d && d[key] != null) { return d[key]; }
    return I18N.de[key] != null ? I18N.de[key] : '';
  }

  function setLang(l, persist) {
    if (l !== 'de' && !I18N[l]) { l = 'de'; }
    lang = l;
    root.lang = l;
    var d = I18N[l] || {};
    $$('[data-i18n]').forEach(function (el) {
      var v = l === 'de' ? orig.html.get(el) : d[el.getAttribute('data-i18n')];
      if (v != null) { el.innerHTML = v; }
    });
    $$('[data-i18n-aria]').forEach(function (el) {
      var v = l === 'de' ? orig.aria.get(el) : d[el.getAttribute('data-i18n-aria')];
      if (v != null) { el.setAttribute('aria-label', v); }
    });
    $$('[data-i18n-ph]').forEach(function (el) {
      var v = l === 'de' ? orig.ph.get(el) : d[el.getAttribute('data-i18n-ph')];
      if (v != null) { el.setAttribute('placeholder', v); }
    });
    doc.title = l === 'de' ? orig.title : (d['meta.title'] || orig.title);
    if (metaDesc) { metaDesc.setAttribute('content', l === 'de' ? orig.desc : (d['meta.desc'] || orig.desc)); }
    $$('.lang-list button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === l)); });
    var cur = $('[data-lang-current]');
    if (cur) { cur.textContent = l.toUpperCase(); }
    $$('.legal-lang').forEach(function (p) { p.hidden = (l === 'de'); });
    if (persist) { store.set('lang', l); }
    renderLocator();
    if (chatStarted) { restart(false); }
  }

  /* ---------- Standort: Bundesland aus Koordinaten (Grenzen stehen in geo.js) ---------- */
  var GEO = null;
  function geoRings() {
    if (GEO) { return GEO; }
    GEO = {};
    Object.keys(GEO_STATES).forEach(function (code) {
      GEO[code] = GEO_STATES[code].map(function (str) {
        var pts = [], i = 0, x = 0, y = 0;
        function num() {
          var r = 0, sh = 0, b;
          do { b = str.charCodeAt(i++) - 63; r |= (b & 31) << sh; sh += 5; } while (b >= 32);
          return (r & 1) ? ~(r >> 1) : (r >> 1);
        }
        while (i < str.length) { x += num(); y += num(); pts.push([x / 1000, y / 1000]); }
        return pts;
      });
    });
    return GEO;
  }
  function inRings(rings, lon, lat) {
    var inside = false;
    for (var k = 0; k < rings.length; k++) {
      var r = rings[k];
      for (var i = 0, j = r.length - 1; i < r.length; j = i++) {
        var xi = r[i][0], yi = r[i][1], xj = r[j][0], yj = r[j][1];
        if ((yi > lat) !== (yj > lat) && lon < (xj - xi) * (lat - yi) / (yj - yi) + xi) { inside = !inside; }
      }
    }
    return inside;
  }
  function stateAt(lat, lon) {
    if (!(lat > 47 && lat < 55.2 && lon > 5.5 && lon < 15.3)) { return null; }
    var g = geoRings(), codes = Object.keys(g), k;
    for (k = 0; k < codes.length; k++) { if (inRings(g[codes[k]], lon, lat)) { return codes[k]; } }
    /* knapp neben der vereinfachten Außengrenze: das nächste Land, höchstens 3 km entfernt */
    var best = null, bd = 3, kx = 111.32 * Math.cos(lat * Math.PI / 180), ky = 111.2;
    codes.forEach(function (c) {
      g[c].forEach(function (r) {
        for (var i = 0, j = r.length - 1; i < r.length; j = i++) {
          var ax = (r[j][0] - lon) * kx, ay = (r[j][1] - lat) * ky, bx = (r[i][0] - lon) * kx, by = (r[i][1] - lat) * ky;
          var dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy;
          var u = L ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / L)) : 0;
          var d = Math.sqrt(Math.pow(ax + u * dx, 2) + Math.pow(ay + u * dy, 2));
          if (d < bd) { bd = d; best = c; }
        }
      });
    });
    return best;
  }
  function kmBetween(aLat, aLon, bLat, bLon) {
    var q = Math.PI / 180, dLat = (bLat - aLat) * q, dLon = (bLon - aLon) * q;
    var h = Math.pow(Math.sin(dLat / 2), 2) + Math.cos(aLat * q) * Math.cos(bLat * q) * Math.pow(Math.sin(dLon / 2), 2);
    return 12742 * Math.asin(Math.sqrt(h));
  }

  /* ---------- Gebiet, Standort-Weiche, Anruf und WhatsApp ---------- */
  var STATE_KEY = { NW: 'nrw', HE: 'he', RP: 'rp', BY: 'by' };
  var region = null;      /* gilt nur für diesen Besuch */
  var fix = null;         /* freigegebener Standort: { lat, lon, acc, code, region, soon } */
  var locState = 'idle';  /* idle | busy | ok | denied | fail */
  var locBusy = false;
  var locCbs = [];
  function setRegion(r) { if (r === 'west' || r === 'by') { region = r; } }
  function soonAt(lat, lon) {
    var hit = null;
    Object.keys(CFG.soon || {}).forEach(function (k) {
      var z = CFG.soon[k];
      if (!hit && kmBetween(lat, lon, z.center[0], z.center[1]) <= z.radiusKm) { hit = k; }
    });
    return hit;
  }
  function resolveFix(lat, lon, acc) {
    var code = stateAt(lat, lon);
    var r = code === 'BY' ? 'by' : (STATE_KEY[code] ? 'west' : null);
    var soon = (code && code !== 'BY') ? soonAt(lat, lon) : null;
    if (soon && !r) { r = CFG.soon[soon].fallback || 'west'; }
    return { lat: lat, lon: lon, acc: acc, code: code, region: r, soon: soon };
  }
  function waDefault() {
    var text = CFG.waText;
    if (fix && locState === 'ok') { text += 'https://maps.google.com/?q=' + fix.lat.toFixed(5) + ',' + fix.lon.toFixed(5); }
    return text;
  }
  function waHref(r, text) {
    return 'https://wa.me/' + CFG.regions[r].wa + '?text=' + encodeURIComponent(text || waDefault());
  }
  function defaultText(node) { return lang === 'de' ? orig.html.get(node) : t(node.getAttribute('data-i18n')); }

  var sheet = $('#sheet');
  var sheetFocus = null;
  var sheetMode = 'call';
  function syncSheet() {
    var mine = (locState === 'ok' && fix) ? fix.region : null;
    $$('[data-sheet-region]', sheet).forEach(function (a) {
      var key = a.getAttribute('data-sheet-region');
      var r = key === 'by' ? 'by' : 'west';
      if (sheetMode === 'wa') { a.href = waHref(r); a.rel = 'noopener'; } else { a.href = 'tel:' + CFG.regions[r].tel; a.removeAttribute('rel'); }
      a.classList.toggle('is-hidden', !!mine && key !== mine);
    });
  }
  function renderLocator() {
    var ok = locState === 'ok' && !!fix;
    var mine = ok ? fix.region : null;
    var status = '';
    root.setAttribute('data-loc', locState);
    $$('[data-locate]').forEach(function (b) {
      var title = $('.loc-title', b), sub = $('.loc-sub', b), use = $('.loc-ico use', b);
      if (locState === 'busy') { title.textContent = t('loc.busy'); sub.textContent = t('loc.busy.sub'); }
      else if (ok) { title.textContent = fix.code ? t('st.' + fix.code) : t('loc.abroad.t'); sub.textContent = t('loc.ok.sub'); }
      else { title.innerHTML = defaultText(title); sub.innerHTML = defaultText(sub); }
      if (use) { use.setAttribute('href', ok ? '#i-check' : '#i-target'); }
      b.setAttribute('aria-busy', String(locState === 'busy'));
    });
    if (ok) {
      if (!fix.code) { status = t('loc.abroad'); }
      else if (fix.soon) { status = t('loc.soon'); }
      else if (!fix.region) { status = t('loc.other'); }
    } else if (locState === 'denied') { status = t('loc.denied'); }
    else if (locState === 'fail') { status = t('loc.fail'); }
    $$('.loc-status').forEach(function (p) { p.textContent = status; p.hidden = !status; });
    $$('.callpanel .btn-call').forEach(function (a) {
      var r = a.getAttribute('data-region'), where = $('.where', a);
      a.classList.toggle('is-other', !!mine && r !== mine);
      if (where) { where.innerHTML = (mine && r === mine && STATE_KEY[fix.code]) ? t('loc.team').replace('{state}', t('st.' + fix.code)) : defaultText(where); }
    });
    if (region) {
      $$('a[data-open-sheet]').forEach(function (a) { a.href = a.getAttribute('data-open-sheet') === 'wa' ? waHref(region) : 'tel:' + CFG.regions[region].tel; });
    }
    syncSheet();
  }
  function locate(auto, done) {
    if (done) { locCbs.push(done); }
    if (locBusy) { return; }
    function finish(state, success) {
      locBusy = false;
      locState = (auto && !success) ? 'idle' : state;
      renderLocator();
      var cbs = locCbs; locCbs = [];
      cbs.forEach(function (cb) { cb(success); });
    }
    if (!navigator.geolocation) { finish('fail', false); return; }
    var fresh = locState === 'ok'; /* erneutes Antippen: Standort neu messen statt den letzten zu nehmen */
    locBusy = true;
    if (!auto) { locState = 'busy'; renderLocator(); }
    try {
      navigator.geolocation.getCurrentPosition(function (pos) {
        fix = resolveFix(pos.coords.latitude, pos.coords.longitude, Math.max(1, Math.round(pos.coords.accuracy || 0)));
        if (fix.region) { setRegion(fix.region); }
        finish('ok', true);
      }, function (err) { finish(err && err.code === 1 ? 'denied' : 'fail', false); }, { enableHighAccuracy: true, timeout: 12000, maximumAge: fresh ? 0 : 120000 });
    } catch (e) { finish('fail', false); }
  }

  function openSheet(mode) {
    sheetMode = mode === 'wa' ? 'wa' : 'call';
    sheet.classList.toggle('is-wa', sheetMode === 'wa');
    syncSheet();
    $('.sheet-note', sheet).innerHTML = t(sheetMode === 'wa' ? 'sheet.note.wa' : 'sheet.note.call');
    sheetFocus = doc.activeElement;
    sheet.hidden = false;
    var first = $('.sheet-row:not(.is-hidden)', sheet);
    if (first) { first.focus(); }
  }
  function closeSheet() {
    if (sheet.hidden) { return; }
    sheet.hidden = true;
    if (sheetFocus && sheetFocus.focus) { sheetFocus.focus(); }
  }

  /* ---------- Soforthilfe-Check ---------- */
  var tabs = $$('.case-tab');
  var panels = $$('.case-panel');
  function selectCase(id, focus) {
    tabs.forEach(function (tb) {
      var on = tb.getAttribute('data-case') === id;
      tb.setAttribute('aria-selected', String(on));
      tb.tabIndex = on ? 0 : -1;
      if (on && focus) { tb.focus(); }
    });
    panels.forEach(function (p) { p.hidden = p.getAttribute('data-case') !== id; });
  }
  tabs.forEach(function (tb, i) {
    tb.addEventListener('click', function () { selectCase(tb.getAttribute('data-case')); });
    tb.addEventListener('keydown', function (e) {
      var j = -1;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { j = (i + 1) % tabs.length; }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { j = (i - 1 + tabs.length) % tabs.length; }
      else if (e.key === 'Home') { j = 0; }
      else if (e.key === 'End') { j = tabs.length - 1; }
      if (j >= 0) { e.preventDefault(); selectCase(tabs[j].getAttribute('data-case'), true); }
    });
  });

  /* ---------- feste Leiste auf dem Telefon ---------- */
  var bar = $('#stickybar');
  var heroPanel = $('#callpanel');
  var closingPanel = $('.sign-closing .callpanel');
  var heroSeen = true;
  var closingSeen = false;
  function updateBar() {
    var on = !heroSeen && !closingSeen;
    bar.classList.toggle('is-on', on);
    bar.setAttribute('aria-hidden', String(!on));
    $$('a,button', bar).forEach(function (el) { el.tabIndex = on ? 0 : -1; });
  }
  if ('IntersectionObserver' in window && heroPanel && closingPanel) {
    new IntersectionObserver(function (es) { heroSeen = es[es.length - 1].isIntersecting; updateBar(); }).observe(heroPanel);
    new IntersectionObserver(function (es) { closingSeen = es[es.length - 1].isIntersecting; updateBar(); }).observe(closingPanel);
  } else {
    heroSeen = false; updateBar();
  }

  /* ---------- Impressum und Datenschutz als eigene Ansicht ---------- */
  function route() {
    var h = (window.location.hash || '').slice(1);
    var legal = h === 'impressum' || h === 'datenschutz';
    doc.body.classList.toggle('view-legal', legal);
    $$('.legal').forEach(function (a) { a.hidden = a.id !== h; });
    if (legal) { window.scrollTo(0, 0); window.setTimeout(function () { window.scrollTo(0, 0); }, 60); }
  }
  window.addEventListener('hashchange', route);
  window.addEventListener('resize', function () { if (chatOpen) { syncViewport(); } });

  /* ---------- Chat ---------- */
  var chatEl = $('#chat');
  var logEl = $('#chat-log');
  var form = $('#chat-form');
  var input = $('#chat-input');
  var chatOpen = false;
  var chatStarted = false;
  var chatFocus = null;
  var S = null;
  var queue = Promise.resolve();
  var token = 0;
  var currentChips = [];
  var CASES = ['p_in_d', 'd_in_p', 'adblue', 'inadblue', 'grade'];
  var PHONE = '<span class="call-ico" aria-hidden="true"><svg class="ico"><use href="#i-phone"/></svg></span>';
  var BUBBLE = '<svg class="ico" aria-hidden="true"><use href="#i-bubble"/></svg>';

  function T(k, vars) {
    var s = CHAT[lang] && CHAT[lang][k];
    if (s == null) { s = CHAT.de[k]; }
    if (s == null) { return k; }
    if (vars) { Object.keys(vars).forEach(function (a) { s = s.split('{' + a + '}').join(vars[a]); }); }
    return s;
  }
  function priceVars() { return { car: CFG.price.car, camper: CFG.price.camper }; }

  function resetState() {
    S = { kase: null, engine: null, vehicle: null, state: null, region: null, code: null, soon: null, place: '', geo: null, placeDone: false, gradeDone: false, asked: null, finished: false };
    if (fix && locState === 'ok' && fix.code) {
      /* Standort wurde schon auf der Seite freigegeben: Gebiet und Ort sind bekannt */
      S.geo = { lat: fix.lat, lon: fix.lon, acc: fix.acc };
      S.placeDone = true;
      S.code = fix.code;
      S.soon = fix.soon;
      S.state = STATE_KEY[fix.code] || 'other';
      S.region = fix.region || 'west';
    }
  }
  function callBtn(r, cls) {
    var a = el('a', cls || 'btn-call', PHONE + '<span class="btn-call-text"><span class="call-label">' + T('call.now') + '</span><span class="num">' + CFG.regions[r].num + '</span><span class="where">' + T('call.' + r) + '</span></span>');
    a.href = 'tel:' + CFG.regions[r].tel;
    a.setAttribute('data-region', r);
    return a;
  }
  function el(tag, cls, html) {
    var e = doc.createElement(tag);
    if (cls) { e.className = cls; }
    if (html != null) { e.innerHTML = html; }
    return e;
  }
  function scrollLog() { logEl.scrollTop = logEl.scrollHeight; }
  function clearChips() { $$('.chips', logEl).forEach(function (c) { c.remove(); }); currentChips = []; }
  function addUser(text) {
    clearChips();
    var m = el('div', 'msg msg-user');
    m.textContent = text;
    logEl.appendChild(m);
    scrollLog();
  }
  function enqueue(fn, delay) {
    var my = token;
    var wait = (delay && !reduced) ? delay : 0;
    queue = queue.then(function () {
      return new Promise(function (res) {
        if (my !== token) { res(); return; }
        var dots = null;
        if (wait) {
          dots = el('div', 'msg msg-bot', '<span class="typing"><i></i><i></i><i></i></span>');
          logEl.appendChild(dots); scrollLog();
        }
        window.setTimeout(function () {
          if (dots) { dots.remove(); }
          if (my === token) { fn(); scrollLog(); }
          res();
        }, wait);
      });
    });
  }
  function say(html) { enqueue(function () { logEl.appendChild(el('div', 'msg msg-bot', html)); }, 430); }
  function note(html) { enqueue(function () { logEl.appendChild(el('div', 'msg msg-note', html)); }, 0); }
  function chips(list) {
    enqueue(function () {
      var w = el('div', 'chips');
      list.forEach(function (c) {
        var b = el('button', c.cls ? 'chip ' + c.cls : 'chip');
        b.type = 'button';
        b.textContent = c.label;
        b.addEventListener('click', function () { addUser(c.label); c.go(); });
        w.appendChild(b);
      });
      logEl.appendChild(w);
      currentChips = list;
    }, 0);
  }
  function callCard() {
    enqueue(function () {
      var card = el('div', 'result');
      (region ? [region] : ['west', 'by']).forEach(function (r) { card.appendChild(callBtn(r)); });
      logEl.appendChild(card);
    }, 250);
  }

  function askCase() {
    S.asked = 'case';
    say(T('askCase'));
    chips(CASES.map(function (c) { return { label: T('c.' + c), go: function () { S.kase = c; next(); } }; })
      .concat([{ label: T('c.other'), go: askFaq }]));
  }
  function askAdblue() {
    S.asked = 'adblue';
    say(T('askAdblue'));
    chips([
      { label: T('c.adblue'), go: function () { S.kase = 'adblue'; next(); } },
      { label: T('c.inadblue'), go: function () { S.kase = 'inadblue'; next(); } }
    ]);
  }
  function tellGrade() {
    S.asked = 'grade';
    say(T('grade.info'));
    say(T('grade.q'));
    chips([
      { label: T('grade.ok'), go: function () { S.gradeDone = true; S.finished = true; say(T('grade.bye')); offerMore(); } },
      { label: T('grade.help'), go: function () { S.gradeDone = true; say(T('grade.go')); next(); } }
    ]);
  }
  function advise() {
    say(T('adv.' + S.engine));
    if (S.kase && S.kase !== 'grade') { say(T('why.' + S.kase)); }
  }
  function askEngine() {
    S.asked = 'engine';
    say(T('askEngine'));
    chips(['no', 'ign', 'yes'].map(function (e) {
      return { label: T('e.' + e), go: function () { S.engine = e; advise(); next(); } };
    }));
  }
  function askVehicle() {
    S.asked = 'vehicle';
    say(T('askVehicle'));
    chips(['car', 'van', 'camper', 'moto', 'other'].map(function (v) {
      return { label: T('v.' + v), go: function () { S.vehicle = v; next(); } };
    }));
  }
  function setState(s) {
    S.state = s;
    S.code = null;
    S.region = s === 'by' ? 'by' : 'west';
    if (s !== 'other') { setRegion(S.region); }
  }
  function askRegion() {
    S.asked = 'region';
    say(T('askRegion'));
    chips([{ label: T('p.share'), cls: 'chip-loc', go: locateChat }].concat(['nrw', 'he', 'rp', 'by', 'other'].map(function (s) {
      return { label: T('r.' + s), go: function () { setState(s); next(); } };
    })));
  }
  function askPlace() {
    S.asked = 'place';
    say(T('askPlace'));
    chips([
      { label: T('p.geo'), go: locateChat },
      { label: T('p.skip'), go: function () { S.placeDone = true; next(); } }
    ]);
  }
  function geoFail() { S.asked = 'place'; say(T('geo.fail')); }
  function locateChat() {
    var my = token;
    say(T('geo.wait'));
    enqueue(function () {
      locate(false, function (success) {
        if (my !== token) { return; }
        if (!success) { geoFail(); return; }
        S.geo = { lat: fix.lat, lon: fix.lon, acc: fix.acc };
        S.placeDone = true;
        S.soon = fix.soon;
        S.code = fix.code;
        if (fix.code) {
          setState(STATE_KEY[fix.code] || 'other');
          S.code = fix.code;
          say(T('geo.ok', { m: String(fix.acc) }) + ' ' + T('geo.in', { state: t('st.' + fix.code) }));
        } else {
          if (!S.state) { setState('other'); }
          say(T('geo.ok', { m: String(fix.acc) }) + ' ' + T('geo.abroad'));
        }
        next();
      });
    }, 0);
  }
  function placeLabel() {
    if (S.geo) { return (S.place ? S.place + ', ' : '') + T('place.geo'); }
    return S.place || T('place.phone');
  }
  function waMessage() {
    var D = CHAT.de;
    var lines = [
      'Hallo, ich habe falsch getankt und brauche Hilfe.',
      'Fall: ' + D['c.' + S.kase],
      'Motor: ' + D['es.' + S.engine],
      'Fahrzeug: ' + D['v.' + S.vehicle],
      'Bundesland: ' + (S.code ? I18N.de['st.' + S.code] : D['r.' + S.state])
    ];
    var place = S.place || '';
    if (S.geo) { place = (place ? place + ', ' : '') + 'https://maps.google.com/?q=' + S.geo.lat.toFixed(5) + ',' + S.geo.lon.toFixed(5); }
    lines.push('Standort: ' + (place || 'nenne ich am Telefon'));
    if (lang === 'en') { lines.push('Sprache: Englisch'); }
    if (lang === 'tr') { lines.push('Sprache: Türkisch'); }
    return lines.join('\n');
  }
  function showResult() {
    S.asked = null;
    S.finished = true;
    var r = S.region || 'west';
    enqueue(function () {
      var card = el('div', 'result');
      card.appendChild(el('h3', '', T('res.title')));
      var dl = el('dl');
      [['f.case', T('c.' + S.kase)], ['f.engine', T('es.' + S.engine)], ['f.vehicle', T('v.' + S.vehicle)], ['f.region', S.code ? t('st.' + S.code) : T('r.' + S.state)], ['f.place', placeLabel()]].forEach(function (row) {
        dl.appendChild(el('dt', '', T(row[0])));
        var dd = el('dd');
        dd.textContent = row[1];
        dl.appendChild(dd);
      });
      card.appendChild(dl);
      card.appendChild(el('p', '', T(S.state === 'other' ? 'res.other' : 'res.lead')));
      if (S.soon && S.state !== 'other') { card.appendChild(el('p', 'result-soon', T('res.soon'))); }
      card.appendChild(callBtn(r));
      var wa = el('a', 'btn btn-wa', BUBBLE + '<span>' + T('res.wa') + '</span>');
      wa.href = waHref(r, waMessage());
      wa.rel = 'noopener';
      card.appendChild(wa);
      var pk = S.vehicle === 'car' ? 'res.price.car' : (S.vehicle === 'camper' ? 'res.price.camper' : 'res.price.other');
      card.appendChild(el('p', 'result-note', T(pk, priceVars())));
      logEl.appendChild(card);
    }, 520);
    offerMore();
  }
  function offerMore() {
    S.asked = 'more';
    say(T('after'));
    chips([
      { label: T('a.more'), go: askFaq },
      { label: T('a.restart'), go: function () { restart(true); } }
    ]);
  }
  function faqChips() {
    var list = ['price', 'time', 'ins', 'drive', 'pay', 'area'].map(function (q) {
      return { label: T('q.' + q), go: function () { answer(q); } };
    });
    list.push({ label: T('q.back'), go: function () { if (S.finished) { resetState(); } next(); } });
    chips(list);
  }
  function askFaq() { S.asked = 'faq'; say(T('askFaq')); faqChips(); }
  function answer(q) {
    say(T('ans.' + q, priceVars()));
    if (q === 'human') { callCard(); }
    if (S.kase && !S.finished) { next(); } else { S.asked = 'faq'; faqChips(); }
  }
  function next() {
    if (S.finished) { return; }
    if (!S.kase) { askCase(); return; }
    if (S.kase === 'grade' && !S.gradeDone) { tellGrade(); return; }
    if (!S.engine) { askEngine(); return; }
    if (!S.vehicle) { askVehicle(); return; }
    if (!S.state) { askRegion(); return; }
    if (!S.placeDone) { askPlace(); return; }
    showResult();
  }

  /* ---------- Freitext verstehen (Deutsch, Englisch, Türkisch) ---------- */
  function fold(s) {
    return s.toLowerCase().replace(/ß/g, 'ss').replace(/ı/g, 'i').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ').trim();
  }
  var PET = '(?:benzin|super|e10|e5|otto\\w*|petrol|gasoline|unleaded)';
  var DSL = '(?:diesel|dizel|mazot|motorin)';
  var INTO = '(?:in|im|ins|into|in the|in a|in my|in den|in meinen)';
  var STATT = '(?:statt|anstatt|anstelle von|anstelle|instead of)';
  var RX = {
    inadblue: [
      new RegExp('(?:' + DSL + '|benzin|super|wasser|water|sprit|kraftstoff|fuel)\\w*\\s+' + INTO + '\\s+(?:den\\s+|dem\\s+|the\\s+|my\\s+)?ad\\s?blue'),
      /ad\s?blue\s?-?\s?(?:tank|depo\w*)\s.{0,24}(?:diesel|dizel|mazot|benzin|yakit|wasser|water)/
    ],
    adblue: [
      new RegExp('ad\\s?blue\\s+' + INTO + '\\s+(?:den\\s+|dem\\s+|the\\s+|my\\s+)?(?:diesel|tank|kraftstoff|fuel)'),
      /(?:dizel|mazot|yakit)\s+depo\w*\s.{0,14}ad\s?blue/
    ],
    anyAdblue: /ad\s?blue|harnstoff|\burea\b/,
    p_in_d: [
      new RegExp('\\b' + PET + '\\b.{0,30}\\b' + INTO + '\\b.{0,25}\\b' + DSL),
      new RegExp('\\b' + PET + '\\b.{0,14}\\b' + STATT + '\\b.{0,14}\\b' + DSL),
      new RegExp('\\b(?:in|im)\\s+(?:den\\s+|meinen\\s+|unseren\\s+|einen\\s+|dem\\s+|meinem\\s+)?' + DSL + '\\w*\\b.{0,30}\\b' + PET),
      /\b(?:dizel|mazot|motorin)\w*\s+(?:(?:arac|araba|depo|motor)\w*\s+)?.{0,18}\bbenzin\b/,
      /\b(?:dizel|mazot|motorin)\w*\s+yerine\s+benzin/
    ],
    d_in_p: [
      new RegExp('\\b' + DSL + '\\b.{0,30}\\b' + INTO + '\\b.{0,25}\\b(?:benzin\\w*|otto\\w*|petrol|gasoline|super)'),
      new RegExp('\\b' + DSL + '\\b.{0,14}\\b' + STATT + '\\b.{0,14}\\b' + PET),
      new RegExp('\\b(?:in|im)\\s+(?:den\\s+|meinen\\s+|unseren\\s+|einen\\s+|dem\\s+|meinem\\s+)?benzin\\w*\\b.{0,30}\\b' + DSL),
      /\bbenzinli\w*\s+(?:(?:arac|araba|depo|motor)\w*\s+)?.{0,18}\b(?:dizel|mazot|motorin)/,
      /\bbenzin\s+yerine\s+(?:dizel|mazot|motorin)/
    ],
    grade: /e10.{0,25}(?:statt|anstatt|instead|yerine).{0,25}(?:e5|super)|e5.{0,25}(?:statt|instead|yerine).{0,25}e10|super\s?plus|falsche\s+(?:benzin)?sorte|wrong\s+(?:petrol\s+)?grade|yanlis\s+benzin\s+tur/,
    engNo: /(?:nicht|noch nicht|nie)\s+(?:gestartet|gefahren|angelassen|losgefahren|angemacht)|motor\s+(?:ist\s+|war\s+|bleibt\s+|blieb\s+)?aus\b|not\s+started|haven'?t\s+started|didn'?t\s+start|did not start|engine\s+(?:is\s+|was\s+)?off|calistirmadim|mars\s?a?\s+basmadim|motor\s+kapali|kontak\s+kapali/,
    engIgn: /nur\s+(?:die\s+)?zundung|zundung\s+(?:war\s+|ist\s+)?(?:an|ein)|ignition\s+(?:was\s+|is\s+)?on|only\s+(?:the\s+)?ignition|sadece\s+konta|kontak\s+acik|kontagi\s+act/,
    engYes: /gefahren|losgefahren|gestartet|angelassen|motor\s+(?:lauft|lief|an\b|ging aus)|ruckelt|stottert|ausgegangen|liegen\s?geblieben|qualmt|\bkm\b|kilometer|drove|driven|started|running|stalled|broke down|calistirdim|surdum|gittim|yolda\s+kaldim|stop\s+etti|motor\s+calis/,
    camper: /wohnmobil|camper|womo|motorhome|karavan/,
    van: /transporter|sprinter|lieferwagen|kastenwagen|\bvan\b|panelvan|minibus/,
    moto: /motorrad|\broller\b|moped|motorbike|motorcycle|motosiklet/,
    car: /\bpkw\b|\bauto\b|\bwagen\b|\bcar\b|otomobil|\baraba/,
    plz: /\b(\d{5})\b/
  };
  var INTENTS = [
    ['drive', /weiter\s?fahren|trotzdem fahren|noch fahren|kann ich fahren|darf ich fahren|keep driving|drive on|can i drive|still drive|devam ede|surebilir|yola devam/],
    ['price', /kost|preis|teuer|wie\s?viel|euro|€|price|cost|how much|expensive|fiyat|ucret|kac para|ne kadar tut|pahali/],
    ['ins', /versicher|schutzbrief|adac|kasko|insurance|breakdown cover|sigorta/],
    ['pay', /bezahl|zahlen|zahlung|\bkarte\b|\bbar\b|paypal|uberweis|rechnung|\bpay\b|payment|\bcard\b|\bcash\b|invoice|odeme|odeye|oderim|nakit|\bkart\b|fatura/],
    ['time', /wie lange|wie schnell|wann seid|wann sind|wann kom|dauer|wartezeit|anfahrt|how long|how fast|how soon|when can|ne kadar sur|ne zaman gel|kac dakika/],
    ['hours', /nachts|sonntag|feiertag|uhrzeit|geoffnet|offnungszeit|rund um die uhr|at night|sunday|open now|opening hours|\bgece\b|pazar gun|acik mi|7\/24/],
    ['vehicles', /\blkw\b|welche fahrzeuge|which vehicles|\btruck\b|lorry|kamyon|hangi arac/],
    ['area', /einsatzgebiet|kommt ihr|kommen sie|auch in|wo seid|wo sind sie|where do you|do you come|service area|nerelerde|hangi bolge|geliyor musunuz|gelir misiniz/],
    ['human', /mensch|mitarbeiter|echte person|jemanden sprechen|telefonnummer|\bnummer\b|anrufen|human|real person|talk to someone|phone number|call you|\binsan\b|yetkili|numara|\btelefon\b/]
  ];
  var CITIES = [
    ['nrw', 'nrw|nordrhein|westfalen|ruhrgebiet', ''],
    ['nrw', 'koln|koeln|cologne', 'Köln'], ['nrw', 'dusseldorf|duesseldorf', 'Düsseldorf'], ['nrw', 'dortmund', 'Dortmund'], ['nrw', 'essen', 'Essen'],
    ['nrw', 'duisburg', 'Duisburg'], ['nrw', 'bochum', 'Bochum'], ['nrw', 'wuppertal', 'Wuppertal'], ['nrw', 'bonn', 'Bonn'], ['nrw', 'gelsenkirchen', 'Gelsenkirchen'],
    ['nrw', 'monchengladbach|moenchengladbach', 'Mönchengladbach'], ['nrw', 'aachen', 'Aachen'], ['nrw', 'krefeld', 'Krefeld'], ['nrw', 'oberhausen', 'Oberhausen'],
    ['nrw', 'hagen', 'Hagen'], ['nrw', 'mulheim|muelheim', 'Mülheim'], ['nrw', 'leverkusen', 'Leverkusen'], ['nrw', 'solingen', 'Solingen'], ['nrw', 'neuss', 'Neuss'],
    ['nrw', 'bottrop', 'Bottrop'], ['nrw', 'recklinghausen', 'Recklinghausen'], ['nrw', 'remscheid', 'Remscheid'], ['nrw', 'moers', 'Moers'], ['nrw', 'haan', 'Haan'],
    ['nrw', 'munster|muenster', 'Münster'], ['nrw', 'bielefeld', 'Bielefeld'], ['nrw', 'paderborn', 'Paderborn'], ['nrw', 'siegen', 'Siegen'], ['nrw', 'hilden', 'Hilden'],
    ['nrw', 'ratingen', 'Ratingen'], ['nrw', 'dormagen', 'Dormagen'], ['nrw', 'duren|dueren', 'Düren'], ['nrw', 'kerpen', 'Kerpen'],
    ['he', 'hessen|hesse', ''], ['he', 'frankfurt', 'Frankfurt'], ['he', 'wiesbaden', 'Wiesbaden'], ['he', 'kassel', 'Kassel'], ['he', 'darmstadt', 'Darmstadt'],
    ['he', 'offenbach', 'Offenbach'], ['he', 'giessen', 'Gießen'], ['he', 'fulda', 'Fulda'], ['he', 'hanau', 'Hanau'], ['he', 'marburg', 'Marburg'], ['he', 'wetzlar', 'Wetzlar'],
    ['he', 'russelsheim|ruesselsheim', 'Rüsselsheim'], ['he', 'bad homburg', 'Bad Homburg'], ['he', 'oberursel', 'Oberursel'], ['he', 'eschborn', 'Eschborn'], ['he', 'neu-isenburg|neu isenburg', 'Neu-Isenburg'],
    ['he', 'dreieich', 'Dreieich'], ['he', 'rodgau', 'Rodgau'], ['he', 'bad vilbel', 'Bad Vilbel'], ['he', 'maintal', 'Maintal'], ['he', 'bad nauheim', 'Bad Nauheim'], ['he', 'dietzenbach', 'Dietzenbach'],
    ['he', 'limburg', 'Limburg'], ['he', 'bensheim', 'Bensheim'], ['he', 'rhein-main|rhein main|rhine-main', ''],
    ['rp', 'rheinland-pfalz|rheinland pfalz|rhineland', ''], ['rp', 'mainz', 'Mainz'], ['rp', 'koblenz', 'Koblenz'], ['rp', 'trier', 'Trier'], ['rp', 'ludwigshafen', 'Ludwigshafen'],
    ['rp', 'kaiserslautern', 'Kaiserslautern'], ['rp', 'worms', 'Worms'], ['rp', 'neuwied', 'Neuwied'], ['rp', 'speyer', 'Speyer'],
    ['by', 'bayern|bavaria|bavyera', ''], ['by', 'munchen|muenchen|munich|munih', 'München'], ['by', 'nurnberg|nuernberg|nuremberg', 'Nürnberg'], ['by', 'augsburg', 'Augsburg'],
    ['by', 'regensburg', 'Regensburg'], ['by', 'ingolstadt', 'Ingolstadt'], ['by', 'wurzburg|wuerzburg', 'Würzburg'], ['by', 'furth|fuerth', 'Fürth'], ['by', 'erlangen', 'Erlangen'],
    ['by', 'bamberg', 'Bamberg'], ['by', 'bayreuth', 'Bayreuth'], ['by', 'landshut', 'Landshut'], ['by', 'rosenheim', 'Rosenheim'], ['by', 'kempten', 'Kempten'],
    ['by', 'aschaffenburg', 'Aschaffenburg'], ['by', 'passau', 'Passau'], ['by', 'schweinfurt', 'Schweinfurt'], ['by', 'straubing', 'Straubing'], ['by', 'freising', 'Freising']
  ].map(function (c) { return { state: c[0], rx: new RegExp('\\b(?:' + c[1] + ')\\b'), name: c[2] }; });
  /* Orte, für die bald das eigene Team Rhein-Main zuständig ist */
  var SOON_RX = /\b(?:frankfurt|offenbach|darmstadt|wiesbaden|mainz|hanau|russelsheim|ruesselsheim|bad homburg|oberursel|eschborn|neu-isenburg|neu isenburg|dreieich|rodgau|bad vilbel|maintal|bad nauheim|dietzenbach|giessen|wetzlar|limburg|bensheim|worms|rhein-main|rhein main|rhine-main)\b/;
  function plzSoon(p) {
    var a = parseInt(p.slice(0, 2), 10);
    var b = parseInt(p.slice(0, 3), 10);
    if (b >= 637 && b <= 639) { return null; }
    if (a === 60 || a === 61 || a === 63 || a === 64 || a === 65 || (b >= 550 && b <= 552) || (b >= 353 && b <= 355)) { return 'rm'; }
    return null;
  }

  function plzState(p) {
    var a = parseInt(p.slice(0, 2), 10);
    var b = parseInt(p.slice(0, 3), 10);
    if (b >= 637 && b <= 639) { return 'by'; }
    if ((a >= 40 && a <= 48) || (a >= 50 && a <= 53) || a === 32 || a === 33 || a === 57 || a === 58 || a === 59) { return 'nrw'; }
    if (a === 34 || a === 35 || a === 36 || a === 60 || a === 61 || a === 63 || a === 64 || a === 65) { return 'he'; }
    if (a === 54 || a === 55 || a === 56 || a === 67) { return 'rp'; }
    if ((a >= 80 && a <= 87) || (a >= 90 && a <= 97)) { return 'by'; }
    return null;
  }
  function firstIndex(list, f) {
    var best = -1;
    list.forEach(function (rx) { var m = rx.exec(f); if (m && (best < 0 || m.index < best)) { best = m.index; } });
    return best;
  }
  function understand(text) {
    var f = fold(text);
    var u = { kase: null, ambig: false, engine: null, vehicle: null, state: null, soon: null, place: '', intent: null, greet: false, thanks: false };
    if (firstIndex(RX.inadblue, f) >= 0) { u.kase = 'inadblue'; }
    else if (firstIndex(RX.adblue, f) >= 0) { u.kase = 'adblue'; }
    else if (RX.anyAdblue.test(f)) { u.ambig = true; }
    else {
      var a = firstIndex(RX.p_in_d, f);
      var b = firstIndex(RX.d_in_p, f);
      if (a >= 0 && (b < 0 || a <= b)) { u.kase = 'p_in_d'; }
      else if (b >= 0) { u.kase = 'd_in_p'; }
      else if (RX.grade.test(f)) { u.kase = 'grade'; }
    }
    if (RX.engNo.test(f)) { u.engine = 'no'; }
    else if (RX.engIgn.test(f)) { u.engine = 'ign'; }
    else if (RX.engYes.test(f)) { u.engine = 'yes'; }
    if (RX.camper.test(f)) { u.vehicle = 'camper'; }
    else if (RX.van.test(f)) { u.vehicle = 'van'; }
    else if (RX.moto.test(f)) { u.vehicle = 'moto'; }
    else if (RX.car.test(f)) { u.vehicle = 'car'; }
    for (var i = 0; i < CITIES.length; i++) {
      if (CITIES[i].rx.test(f)) { u.state = CITIES[i].state; u.place = CITIES[i].name; if (u.place) { break; } }
    }
    var plz = RX.plz.exec(f);
    if (plz) {
      var st = plzState(plz[1]);
      if (st && !u.state) { u.state = st; }
      u.place = (u.place ? u.place + ' ' : 'PLZ ') + plz[1];
      if (plzSoon(plz[1])) { u.soon = 'rm'; }
    }
    if (!u.soon && SOON_RX.test(f)) { u.soon = 'rm'; }
    for (var k = 0; k < INTENTS.length; k++) {
      if (INTENTS[k][1].test(f)) { u.intent = INTENTS[k][0]; break; }
    }
    u.greet = /^(?:hallo|hi|hey|guten\s|moin|servus|merhaba|selam|hello|good (?:morning|evening|afternoon))/.test(f);
    u.thanks = /danke|vielen dank|\bthx\b|thank|tesekkur|sag ?ol/.test(f);
    return u;
  }
  function matchChip(text) {
    var n = fold(text).replace(/[.!?,;:]/g, '').trim();
    if (!currentChips.length || n.length < 2) { return null; }
    for (var i = 0; i < currentChips.length; i++) {
      if (fold(currentChips[i].label).replace(/[.!?,;:]/g, '').trim() === n) { return currentChips[i]; }
    }
    if (S.asked === 'engine' && currentChips.length === 3) {
      if (/^(?:nein|ne|noe|no|nope|hayir|yok)\b/.test(n)) { return currentChips[0]; }
      if (/^(?:ja|jo|yes|yep|evet)\b/.test(n)) { return currentChips[2]; }
    }
    return null;
  }
  function onText(text) {
    var hit = matchChip(text);
    addUser(text);
    if (hit) { hit.go(); return; }
    var u = understand(text);
    if (S.finished && (u.kase || u.ambig)) { resetState(); }
    if (S.asked === 'place' && !u.intent && !u.kase && !u.ambig) {
      S.place = text.slice(0, 160);
      S.placeDone = true;
      if (u.state && !S.state) { setState(u.state); }
      if (u.soon) { S.soon = u.soon; }
      next();
      return;
    }
    var got = [];
    var engineNew = false;
    if (u.kase && !S.kase) { S.kase = u.kase; got.push(T('c.' + u.kase)); }
    if (u.engine && !S.engine) { S.engine = u.engine; engineNew = true; got.push(T('es.' + u.engine)); }
    if (u.vehicle && !S.vehicle) { S.vehicle = u.vehicle; got.push(T('v.' + u.vehicle)); }
    if (u.state && !S.state) { setState(u.state); got.push((u.place ? u.place + ', ' : '') + T('r.' + u.state)); }
    if (u.place && !S.place) { S.place = u.place; }
    if (u.soon) { S.soon = u.soon; }
    if (got.length) { say(T('understood', { list: got.join(', ') })); }
    if (engineNew) { advise(); }
    if (u.intent) {
      say(T('ans.' + u.intent, priceVars()));
      if (u.intent === 'human') { callCard(); }
    }
    if (!got.length && !u.intent) {
      if (u.ambig && !S.kase) { askAdblue(); return; }
      if (u.thanks) { say(T('thanks')); if (S.kase && !S.finished) { next(); } return; }
      if (u.greet) { say(T('hi')); if (!S.finished) { next(); } else { offerMore(); } return; }
      say(T('fallback'));
      callCard();
      if (S.kase && !S.finished) { next(); } else if (S.finished) { faqChips(); } else { askCase(); }
      return;
    }
    if (S.kase && !S.finished) { next(); }
    else if (S.finished) { offerMore(); }
    else { S.asked = 'faq'; faqChips(); }
  }

  /* ---------- Chat öffnen und schließen ---------- */
  function begin() {
    token++;
    queue = Promise.resolve();
    logEl.innerHTML = '';
    currentChips = [];
    resetState();
    chatStarted = true;
    say(T('hello'));
    note(T('privacy'));
  }
  function restart(announce) {
    begin();
    if (announce) { say(T('restart')); }
    askCase();
  }
  function syncViewport() {
    if (!chatOpen) { return; }
    var vv = window.visualViewport;
    if (!isWide()) {
      chatEl.style.setProperty('--vvh', (vv ? vv.height : window.innerHeight) + 'px');
      chatEl.style.setProperty('--vvt', (vv ? vv.offsetTop : 0) + 'px');
    } else {
      chatEl.style.removeProperty('--vvh');
      chatEl.style.removeProperty('--vvt');
    }
    scrollLog();
  }
  function openChat(kase) {
    if (!chatOpen) {
      chatFocus = doc.activeElement;
      chatOpen = true;
      chatEl.hidden = false;
      root.classList.add('chat-open');
      syncViewport();
    }
    if (!chatStarted) {
      begin();
      if (kase) { S.kase = kase; enqueue(function () { var m = el('div', 'msg msg-user'); m.textContent = T('c.' + kase); logEl.appendChild(m); }, 0); next(); }
      else { askCase(); }
    } else if (kase && (S.finished || S.kase !== kase)) {
      begin();
      S.kase = kase;
      enqueue(function () { var m = el('div', 'msg msg-user'); m.textContent = T('c.' + kase); logEl.appendChild(m); }, 0);
      next();
    }
    if (isWide()) { input.focus(); }
  }
  function closeChat() {
    if (!chatOpen) { return; }
    chatOpen = false;
    chatEl.hidden = true;
    root.classList.remove('chat-open');
    if (chatFocus && chatFocus.focus) { chatFocus.focus(); }
  }
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', syncViewport);
    window.visualViewport.addEventListener('scroll', syncViewport);
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text) { return; }
    input.value = '';
    onText(text);
  });

  /* ---------- Klicks und Tasten ---------- */
  doc.addEventListener('click', function (e) {
    var target = e.target;
    if (!target.closest) { return; }
    var langBox = $('.lang');
    var langToggle = target.closest('.lang-current');
    if (langToggle) {
      var open = !langBox.classList.contains('is-open');
      langBox.classList.toggle('is-open', open);
      langToggle.setAttribute('aria-expanded', String(open));
      return;
    }
    var langBtn = target.closest('.lang-list button');
    if (langBtn) { setLang(langBtn.getAttribute('data-lang'), true); }
    if (langBox && langBox.classList.contains('is-open')) {
      langBox.classList.remove('is-open');
      $('.lang-current').setAttribute('aria-expanded', 'false');
    }
    if (langBtn) { return; }
    if (target.closest('[data-locate]')) { locate(false); return; }
    var row = target.closest('[data-sheet-region]');
    if (row) { setRegion(row.getAttribute('data-sheet-region')); window.setTimeout(closeSheet, 350); return; }
    var opener = target.closest('[data-open-sheet]');
    if (opener) {
      var mode = opener.getAttribute('data-open-sheet');
      if (region) { opener.href = mode === 'wa' ? waHref(region) : 'tel:' + CFG.regions[region].tel; return; }
      e.preventDefault();
      openSheet(mode);
      return;
    }
    if (target.closest('[data-close-sheet]')) { closeSheet(); return; }
    var chatBtn = target.closest('[data-open-chat]');
    if (chatBtn) { openChat(chatBtn.getAttribute('data-chat-case')); return; }
    if (target.closest('[data-close-chat]')) { closeChat(); return; }
    var regionLink = target.closest('a[data-region]');
    if (regionLink) { setRegion(regionLink.getAttribute('data-region')); }
  });
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') { return; }
    var lb = $('.lang');
    if (lb && lb.classList.contains('is-open')) { lb.classList.remove('is-open'); $('.lang-current').setAttribute('aria-expanded', 'false'); return; }
    if (!sheet.hidden) { closeSheet(); } else if (chatOpen) { closeChat(); }
  });

  /* ---------- Start ---------- */
  route();
  (function () {
    var saved = store.get('lang');
    var l = 'de';
    if (saved === 'de' || saved === 'en' || saved === 'tr') { l = saved; }
    else if (!/bot|crawl|spider|lighthouse|headless/i.test(navigator.userAgent || '')) {
      var nav = String(navigator.language || 'de').slice(0, 2).toLowerCase();
      if (nav === 'tr' || nav === 'en') { l = nav; }
    }
    if (l !== 'de') { setLang(l, false); }
  })();
  renderLocator();
  /* Wurde die Standortfreigabe für diese Seite schon früher erteilt, gleich die passende Nummer zeigen */
  if (navigator.geolocation && navigator.permissions && navigator.permissions.query) {
    try {
      navigator.permissions.query({ name: 'geolocation' }).then(function (st) { if (st && st.state === 'granted') { locate(true); } }, function () { /* Abfrage nicht möglich */ });
    } catch (e) { /* ältere Browser */ }
  }

  window.__tank = { understand: understand, setLang: setLang, openChat: openChat, stateAt: stateAt, resolveFix: resolveFix, kmBetween: kmBetween, setFix: function (lat, lon) { fix = resolveFix(lat, lon, 12); if (fix.region) { setRegion(fix.region); } locState = 'ok'; renderLocator(); return fix; } };
})();

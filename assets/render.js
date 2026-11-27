/* Rendert een nieuwsbriefeditie uit data.json in de vaste template.
   Gebruik: <main id="nieuwsbrief" data-src="data.json"></main> + dit script. */
(function () {
  const DAGEN = ["zo", "ma", "di", "wo", "do", "vr", "za"];
  const MAANDEN = ["jan", "feb", "maa", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"];
  const MAANDEN_LANG = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"];

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  // eenvoudige opmaak in teksten: **vet**, lege regel = nieuwe alinea, links klikbaar
  const tekst = (s) => esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
    .replace(/([\w.+-]+@[\w-]+\.[\w.]+[a-z])/gi, '<a href="mailto:$1">$1</a>')
    .split(/\n\s*\n/).map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");

  const parseDatum = (iso) => {
    if (!iso) return null;
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(y, m - 1, d);
  };
  const fmt = (d, metJaar) => `${DAGEN[d.getDay()]} ${d.getDate()} ${MAANDEN[d.getMonth()]}${metJaar ? " " + d.getFullYear() : ""}`;
  function periode(van, tot, metJaar) {
    const a = parseDatum(van), b = parseDatum(tot);
    if (!a) return "datum nog te bepalen";
    if (!b || +a === +b) return fmt(a, metJaar);
    return `${fmt(a)} – ${fmt(b, metJaar)}`;
  }

  const id = (s) => String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

  function naamChip(s) {
    const m = String(s).match(/^(.*?)\s*\((.*)\)\s*$/);
    return m ? `<span class="naam">${esc(m[1])} <small>${esc(m[2])}</small></span>` : `<span class="naam">${esc(s)}</span>`;
  }

  function fotos(lijst) {
    if (!lijst || !lijst.length) return "";
    const items = lijst.map((f) => {
      const src = typeof f === "string" ? f : f.src;
      const alt = typeof f === "string" ? "" : f.alt || "";
      return `<img src="${esc(src)}" alt="${esc(alt)}" loading="lazy">`;
    }).join("");
    const hint = lijst.length > 1 ? `<div class="fotos-hint">← swipe voor meer foto's · tik om te vergroten</div>` : "";
    return `<div class="fotos${lijst.length === 1 ? " een" : ""}">${items}</div>${hint}`;
  }

  const todo = (t) => (t ? `<div class="todo">✏️ Nog te doen: ${esc(t)}</div>` : "");

  function wedstrijdKaart(w) {
    if (w.tussentitel) return `<div class="tussentitel">${esc(w.tussentitel)}</div>`;
    let html = `<article class="kaart" id="${id(w.naam + "-" + (w.van || ""))}">
      <div class="kaart-kop"><div><h3>${esc(w.naam)}</h3><div class="plaats">${esc(w.plaats || "")}</div></div>
      <span class="datum-chip">${periode(w.van, w.tot)}</span></div>`;
    if (w.tekst) html += tekst(w.tekst);
    (w.records || []).forEach((r) => {
      html += `<div class="record"><div class="label">${esc(r.label || "Record")}</div>
        <div class="wie">${esc(r.wie)} — ${esc(r.wat)} <span class="tijd">${esc(r.tijd || "")}</span></div>
        ${r.extra ? `<div>${esc(r.extra)}</div>` : ""}</div>`;
    });
    const rijen = [["goud", "1", w.goud], ["zilver", "2", w.zilver], ["brons", "3", w.brons]].filter((r) => r[2] && r[2].length);
    if (rijen.length) {
      html += `<div class="medailles">` + rijen.map(([k, n, namen]) =>
        `<div class="medaille-rij"><span class="medaille ${k}" title="${k}">${n}</span><div class="namen">${namen.map(naamChip).join("")}</div></div>`).join("") + `</div>`;
    }
    if (w.finales && Object.keys(w.finales).length) {
      html += `<div class="finales">` + Object.entries(w.finales).map(([titel, lijst]) =>
        `<div class="finale"><h4>${esc(titel)}</h4><ul>${lijst.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`).join("") + `</div>`;
    }
    html += fotos(w.fotos) + todo(w.todo) + `</article>`;
    return html;
  }

  function render(d) {
    const el = document.getElementById("nieuwsbrief");
    document.title = `${d.titel} ${d.periode} – Competitiezwemmen Neptunus Aalst`;
    const nav = [];
    let body = "";

    const w = d.wedstrijden;
    if (w && w.items && w.items.length) {
      nav.push(["wedstrijden", "Wedstrijden"]);
      body += `<section class="blok" id="wedstrijden"><h2 class="sectietitel">${esc(w.titel || "Wedstrijdnieuws")}</h2>
        ${w.intro ? `<div class="sectie-intro">${tekst(w.intro)}</div>` : ""}
        ${w.voetnoot ? `<p class="voetnoot">${esc(w.voetnoot)}</p>` : ""}
        ${w.items.map(wedstrijdKaart).join("")}</section>`;
    }

    const s = d.stages;
    if (s && s.items && s.items.length) {
      nav.push(["stages", "Stages"]);
      body += `<section class="blok" id="stages"><h2 class="sectietitel">${esc(s.titel || "Stages")}</h2>` +
        s.items.map((x) => `<article class="kaart"><div class="kaart-kop"><div><h3>${esc(x.titel)}</h3>
          <div class="plaats">${esc(x.groep || "")}</div></div>${x.van ? `<span class="datum-chip">${periode(x.van, x.tot)}</span>` : ""}</div>
          ${x.tekst ? tekst(x.tekst) : ""}${fotos(x.fotos)}${todo(x.todo)}</article>`).join("") + `</section>`;
    }

    const k = d.kalender;
    if (k && k.items && k.items.length) {
      nav.push(["kalender", "Kalender"]);
      // wedstrijden vóór de publicatiedatum van de editie worden grijs (oude edities: niets grijs)
      const vandaag = parseDatum(d.gepubliceerd);
      body += `<section class="blok" id="kalender"><h2 class="sectietitel">${esc(k.titel || "Wedstrijdkalender")}</h2>
        ${k.intro ? `<div class="sectie-intro">${tekst(k.intro)}</div>` : ""}
        <ul class="kalender">` + k.items.map((x) => {
          const eind = parseDatum(x.tot || x.van);
          const voorbij = vandaag && eind && eind < vandaag ? " voorbij" : "";
          return `<li class="${voorbij}"><div class="wanneer">${periode(x.van, x.tot)}</div>
            <div class="wat">${esc(x.naam)}${x.gewijzigd ? ' <span class="gewijzigd">Gewijzigd</span>' : ""}</div><div class="details">${esc([x.plaats, x.details].filter(Boolean).join(" · "))}</div></li>`;
        }).join("") + `</ul>${todo(k.todo)}</section>`;
    }

    const e = d.extra;
    if (e && e.items && e.items.length) {
      nav.push(["extra", "Extra"]);
      body += `<section class="blok" id="extra"><h2 class="sectietitel">${esc(e.titel || "Extra")}</h2><div class="extra-grid">` +
        e.items.map((x) => `<article class="kaart${x.tag === "Save the date" ? " save-the-date" : ""}${(x.fotos && x.fotos.length) || (x.tekst || "").length > 450 ? " breed" : ""}">
          ${x.tag ? `<span class="tag">${esc(x.tag)}</span>` : ""}<h3>${esc(x.titel)}</h3>
          ${x.van ? `<div class="plaats">${periode(x.van, x.tot, true)}${x.plaats ? " · " + esc(x.plaats) : ""}</div>` : ""}
          ${x.tekst ? tekst(x.tekst) : ""}
          ${fotos(x.fotos)}
          ${x.link ? `<a class="knop" href="${esc(x.link)}" target="_blank" rel="noopener">${esc(x.linktekst || "Meer info")}</a>` : ""}
          ${todo(x.todo)}</article>`).join("") + `</div></section>`;
    }

    const sp = d.sponsors;
    if (sp && sp.items && sp.items.length) {
      nav.push(["sponsors", "Sponsors"]);
      body += `<section class="blok" id="sponsors"><h2 class="sectietitel">${esc(sp.titel || "Dank aan onze sponsors")}</h2><div class="sponsors">` +
        sp.items.map((x) => {
          const inhoud = x.logo ? `<img src="${esc(x.logo)}" alt="${esc(x.naam)}">` : esc(x.naam);
          return x.url ? `<a class="sponsor" href="${esc(x.url)}" target="_blank" rel="noopener">${inhoud}</a>` : `<div class="sponsor">${inhoud}</div>`;
        }).join("") +
        (sp.vrij ? `<div class="sponsor vrij">${tekst(sp.vrij)}</div>` : "") + `</div></section>`;
    }

    const gepubliceerd = parseDatum(d.gepubliceerd);
    el.outerHTML = `
      ${d.concept ? `<div class="concept-banner">CONCEPT – deze editie is nog niet af. Gele blokken tonen wat nog ontbreekt.</div>` : ""}
      <header class="hero"><div class="hero-inner">
        <div class="club">Competitiezwemmen Neptunus Aalst</div>
        <h1>${esc(d.titel)} <span class="accent">${esc(d.periode)}</span></h1>
        ${d.ondertitel ? `<p class="ondertitel">${esc(d.ondertitel)}</p>` : ""}
        <div class="meta">${[d.redactie ? "Redactie: " + esc(d.redactie) : "", gepubliceerd ? gepubliceerd.getDate() + " " + MAANDEN_LANG[gepubliceerd.getMonth()] + " " + gepubliceerd.getFullYear() : ""].filter(Boolean).join(" · ")}</div>
      </div>
      <svg class="drietand" viewBox="0 0 64 96" aria-hidden="true"><g fill="none" stroke="#f2b62b" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M32 92V20"/><path d="M12 8v20a20 20 0 0 0 40 0V8"/><path d="M32 4l-6 12h12z" fill="#f2b62b"/><path d="M12 4l-5 10h10zM52 4l-5 10h10z" fill="#f2b62b"/><path d="M24 70h16"/></g></svg>
      </header>
      <nav class="inhoud"><ul>${nav.map(([a, t]) => `<li><a href="#${a}">${t}</a></li>`).join("")}
        <li><a href="../../">Alle edities</a></li></ul></nav>
      <main>${d.intro ? `<section class="blok"><div class="kaart">${tekst(d.intro)}</div></section>` : ""}${body}</main>
      <footer>Competitiezwemmen Neptunus Aalst · <a href="https://www.neptunusaalst.be" target="_blank" rel="noopener">neptunusaalst.be</a><br>
        <a href="#" class="geen-print" onclick="window.print();return false;">Afdrukken / opslaan als PDF</a></footer>`;
  }

  // Lightbox: tik op een foto om ze groot te bekijken, swipe of pijltjes voor de volgende
  function lightbox() {
    const lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML = `<img alt=""><button class="sluit" aria-label="Sluiten">×</button>
      <button class="vorige" aria-label="Vorige">‹</button><button class="volgende" aria-label="Volgende">›</button><div class="teller"></div>`;
    document.body.appendChild(lb);
    const img = lb.querySelector("img");
    let reeks = [], i = 0, startX = null;
    const toon = () => {
      img.src = reeks[i].src; img.alt = reeks[i].alt;
      lb.querySelector(".teller").textContent = reeks.length > 1 ? `${i + 1} / ${reeks.length}` : "";
      lb.querySelectorAll(".vorige,.volgende").forEach((b) => (b.style.display = reeks.length > 1 ? "" : "none"));
    };
    const stap = (n) => { i = (i + n + reeks.length) % reeks.length; toon(); };
    const sluit = () => { lb.classList.remove("open"); document.body.style.overflow = ""; };
    document.addEventListener("click", (e) => {
      const f = e.target.closest(".fotos img");
      if (!f) return;
      reeks = [...f.parentElement.querySelectorAll("img")];
      i = reeks.indexOf(f); toon();
      lb.classList.add("open"); document.body.style.overflow = "hidden";
    });
    lb.querySelector(".sluit").onclick = sluit;
    lb.querySelector(".vorige").onclick = (e) => { e.stopPropagation(); stap(-1); };
    lb.querySelector(".volgende").onclick = (e) => { e.stopPropagation(); stap(1); };
    lb.addEventListener("click", (e) => { if (e.target === lb) sluit(); });
    document.addEventListener("keydown", (e) => {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") sluit(); if (e.key === "ArrowLeft") stap(-1); if (e.key === "ArrowRight") stap(1);
    });
    lb.addEventListener("touchstart", (e) => (startX = e.touches[0].clientX), { passive: true });
    lb.addEventListener("touchend", (e) => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50 && reeks.length > 1) stap(dx < 0 ? 1 : -1);
      startX = null;
    });
  }

  const main = document.getElementById("nieuwsbrief");
  fetch(main.dataset.src || "data.json", { cache: "no-cache" })
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => { render(d); lightbox(); })
    .catch((err) => { main.innerHTML = `<p style="padding:24px">Deze nieuwsbrief kon niet geladen worden (${esc(err.message)}).</p>`; });
})();

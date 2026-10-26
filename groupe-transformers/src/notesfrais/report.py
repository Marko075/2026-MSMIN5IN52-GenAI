"""Rapport HTML statique (results/report.html) : aucune dépendance, graphiques SVG inline."""
from __future__ import annotations

import html
import json
from pathlib import Path

from .config import RESULTS_DIR

MODE_LABEL = {"naive": "Naïf (baseline)", "protected": "Protégé"}
MODE_VAR = {"naive": "--series-naive", "protected": "--series-protected"}

CSS = """
:root { color-scheme: light;
  --surface: #fcfcfb; --surface-2: #f3f2ef; --text-primary: #0b0b0b; --text-secondary: #52514e;
  --text-muted: #77756f; --grid: #e4e2dd; --series-protected: #2a78d6; --series-naive: #eb6834;
  --good: #0a7d32; --critical: #c62828; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { color-scheme: dark;
  --surface: #1a1a19; --surface-2: #242423; --text-primary: #f0efec; --text-secondary: #c3c2b7;
  --text-muted: #9a988f; --grid: #34332f; --series-protected: #3987e5; --series-naive: #d95926;
  --good: #4cc272; --critical: #ef6b6b; } }
:root[data-theme="dark"] { color-scheme: dark;
  --surface: #1a1a19; --surface-2: #242423; --text-primary: #f0efec; --text-secondary: #c3c2b7;
  --text-muted: #9a988f; --grid: #34332f; --series-protected: #3987e5; --series-naive: #d95926;
  --good: #4cc272; --critical: #ef6b6b; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--surface); color: var(--text-primary);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1040px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 26px; margin: 0 0 4px; } h2 { font-size: 19px; margin: 40px 0 8px; }
p.lead, .muted { color: var(--text-secondary); }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 24px 0; }
.tile { background: var(--surface-2); border-radius: 10px; padding: 14px 16px; }
.tile .label { color: var(--text-secondary); font-size: 13px; }
.tile .value { font-size: 28px; font-weight: 650; font-variant-numeric: tabular-nums; }
.tile .sub { color: var(--text-muted); font-size: 13px; }
.legend { display: flex; gap: 18px; color: var(--text-secondary); font-size: 13px; margin: 4px 0 8px; }
.legend i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }
.chart { width: 100%; overflow-x: auto; }
svg text { fill: var(--text-secondary); font-size: 12px; }
svg .value { fill: var(--text-primary); font-weight: 600; }
table { border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--grid); }
th { color: var(--text-secondary); font-weight: 600; }
td.num, th.num { text-align: right; }
.ok { color: var(--good); font-weight: 600; } .ko { color: var(--critical); font-weight: 600; }
.wrap { overflow-x: auto; }
code { background: var(--surface-2); padding: 1px 5px; border-radius: 4px; }
"""


def _fmt(x, digits=2, suffix=""):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{digits}f}{suffix}"
    return f"{x}{suffix}"


def grouped_bars(runs: list[dict], metric: str, title: str, unit: str = "") -> str:
    """Barres groupées par seed (naïf vs protégé), extrémités arrondies, étiquettes directes."""
    seeds = sorted({r["seed"] for r in runs})
    modes = ["naive", "protected"]
    values = {(r["mode"], r["seed"]): r[metric] for r in runs}
    vmax = max([v for v in values.values()] + [1])
    w, h, left, bottom, top = 760, 230, 44, 30, 16
    group_w = (w - left - 10) / len(seeds)
    bar_w = min(34, group_w / 3)
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{html.escape(title)}">']
    for i in range(5):
        y = top + (h - top - bottom) * i / 4
        val = vmax * (1 - i / 4)
        parts.append(f'<line x1="{left}" x2="{w - 10}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end">{val:.0f}</text>')
    base = h - bottom
    for gi, seed in enumerate(seeds):
        cx = left + group_w * gi + group_w / 2
        parts.append(f'<text x="{cx:.1f}" y="{h - 8}" text-anchor="middle">seed {seed}</text>')
        for mi, mode in enumerate(modes):
            v = values.get((mode, seed))
            if v is None:
                continue
            bh = (base - top) * v / vmax
            x = cx + (mi - 1) * (bar_w + 2) + 1
            r = min(4, bh / 2)
            path = (f"M{x:.1f},{base} V{base - bh + r:.1f} Q{x:.1f},{base - bh:.1f} {x + r:.1f},{base - bh:.1f} "
                    f"H{x + bar_w - r:.1f} Q{x + bar_w:.1f},{base - bh:.1f} {x + bar_w:.1f},{base - bh + r:.1f} V{base} Z")
            label = f"{MODE_LABEL[mode]} — seed {seed} : {v}{unit}"
            parts.append(f'<path d="{path}" fill="var({MODE_VAR[mode]})"><title>{html.escape(label)}</title></path>')
            parts.append(f'<text class="value" x="{x + bar_w / 2:.1f}" y="{base - bh - 5:.1f}" '
                         f'text-anchor="middle">{v}</text>')
    parts.append(f'<line x1="{left}" x2="{w - 10}" y1="{base}" y2="{base}" stroke="var(--text-muted)"/>')
    parts.append("</svg>")
    return "".join(parts)


def recovery_strip(runs: list[dict]) -> str:
    """Distribution des temps de reprise : un point par crash, p50 et p95 marqués."""
    from .metrics import percentile
    modes = ["naive", "protected"]
    samples = {m: [x for r in runs if r["mode"] == m for x in r["recovery_samples"]] for m in modes}
    vmax = max([x for xs in samples.values() for x in xs] + [1.0])
    w, row_h, left, right = 760, 64, 130, 20
    h = row_h * len(modes) + 36
    scale = (w - left - right) / vmax
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Temps de reprise après crash">']
    ticks = [vmax * i / 5 for i in range(6)]
    for t in ticks:
        x = left + t * scale
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="8" y2="{h - 26}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{x:.1f}" y="{h - 8}" text-anchor="middle">{t:.2f} s</text>')
    for i, mode in enumerate(modes):
        y = 8 + row_h * i + row_h / 2
        parts.append(f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end">{MODE_LABEL[mode]}</text>')
        xs = sorted(samples[mode])
        for j, s in enumerate(xs):
            jitter = ((j * 7919) % 17 - 8) * 1.4
            parts.append(f'<circle cx="{left + s * scale:.1f}" cy="{y + jitter:.1f}" r="4" fill="var({MODE_VAR[mode]})"'
                         f' fill-opacity="0.75" stroke="var(--surface)" stroke-width="1"><title>{s:.3f} s</title></circle>')
        for q in (50, 95):
            p = percentile(xs, q)
            if p is not None:
                x = left + p * scale
                parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y - 22:.1f}" y2="{y + 22:.1f}" '
                             f'stroke="var(--text-primary)" stroke-width="2"/>')
                parts.append(f'<text class="value" x="{x + 4:.1f}" y="{y - 14:.1f}">p{q} {p:.2f} s</text>')
    parts.append("</svg>")
    return "".join(parts)


def legend() -> str:
    return ('<div class="legend"><span><i style="background:var(--series-naive)"></i>Naïf (baseline)</span>'
            '<span><i style="background:var(--series-protected)"></i>Protégé</span></div>')


def build_report(results_dir: Path = RESULTS_DIR) -> Path:
    summary = json.loads((results_dir / "summary.json").read_text(encoding="utf-8"))
    runs = json.loads((results_dir / "runs.json").read_text(encoding="utf-8"))
    real_path = results_dir / "real_llm.json"
    real = json.loads(real_path.read_text(encoding="utf-8")) if real_path.exists() else None
    by = summary["by_mode"]
    nv, pr = by.get("naive", {}), by.get("protected", {})

    def tile(label, value, sub=""):
        return (f'<div class="tile"><div class="label">{label}</div><div class="value">{value}</div>'
                f'<div class="sub">{sub}</div></div>')

    tiles = "".join([
        tile("Effets en double — naïf", f'<span class="ko">{nv.get("duplicate_effects", "—")}</span>',
             f'{nv.get("requests_with_duplicates", 0)} demandes touchées'),
        tile("Effets en double — protégé", f'<span class="ok">{pr.get("duplicate_effects", "—")}</span>',
             f'{pr.get("inconsistent_requests", 0)} demande incohérente'),
        tile("Crashs injectés (par mode)", f'{nv.get("crashes", 0)} / {pr.get("crashes", 0)}',
             "naïf / protégé — kills psutil + points de crash"),
        tile("Reprise p50 / p95 (protégé)",
             f'{_fmt(pr.get("recovery_p50_s"))} s', f'p95 {_fmt(pr.get("recovery_p95_s"))} s — {pr.get("recovery_n", 0)} reprises'),
    ])

    rows = []
    keys = [("Demandes traitées", "requests"), ("Taux de complétion", "completion_rate"),
            ("Effets en double", "duplicate_effects"), ("Demandes avec doublon", "requests_with_duplicates"),
            ("Demandes incohérentes (effets ≠ statut)", "inconsistent_requests"),
            ("Compensations", "compensations"), ("Crashs du worker", "crashes"),
            ("Pannes injectées (toutes)", "faults_total"), ("Appels LLM", "llm_calls"),
            ("Appels LLM évités (cache)", "llm_cache_hits"), ("Étapes ré-exécutées", "steps_replayed"),
            ("Rejeux idempotents (service)", "idempotent_replays"), ("Reprise p50 (s)", "recovery_p50_s"),
            ("Reprise p95 (s)", "recovery_p95_s")]
    for label, key in keys:
        a, b = nv.get(key), pr.get(key)
        if key == "completion_rate":
            a, b = (f"{a:.0%}" if a is not None else "—"), (f"{b:.0%}" if b is not None else "—")
        rows.append(f"<tr><td>{label}</td><td class='num'>{_fmt(a, 3)}</td><td class='num'>{_fmt(b, 3)}</td></tr>")
    faults_rows = "".join(
        f"<tr><td>{k}</td><td class='num'>{nv.get('faults', {}).get(k, 0)}</td>"
        f"<td class='num'>{pr.get('faults', {}).get(k, 0)}</td></tr>" for k in pr.get("faults", {}))
    run_rows = "".join(
        f"<tr><td>{MODE_LABEL[r['mode']]}</td><td class='num'>{r['seed']}</td><td class='num'>{r['completion_rate']:.0%}</td>"
        f"<td class='num'>{r['duplicate_effects']}</td><td class='num'>{r['inconsistent_requests']}</td>"
        f"<td class='num'>{r['crashes']}</td><td class='num'>{r['faults_total']}</td>"
        f"<td class='num'>{_fmt(r['recovery_s']['p50'])}</td><td class='num'>{r['duration_s']:.1f}</td></tr>"
        for r in runs)

    real_html = "<p class='muted'>Pas encore d'exécution réelle (<code>python -m notesfrais real-run</code>).</p>"
    if real:
        s = real["summary"]
        rr = "".join(
            f"<tr><td>{r['request_id']}</td><td>{html.escape(r['texte'])}</td>"
            f"<td>{html.escape(json.dumps({k: r['obtenu'].get(k) for k in ('montant', 'devise', 'categorie', 'date')}, ensure_ascii=False))}</td>"
            f"<td class='{'ok' if all(r['champs_corrects'].values()) else 'ko'}'>{'oui' if all(r['champs_corrects'].values()) else 'non'}</td>"
            f"<td>{r['statut']}</td></tr>" for r in real["rows"])
        real_html = (
            f"<p>Modèle <code>{s['model']}</code> via OpenRouter et Semantic Kernel : {s['requests']} demandes, "
            f"<b>{s['real_llm_calls']} appels réels</b>, {s['llm_cache_hits']} appel évité par le cache après un crash forcé "
            f"juste après l'appel LLM, {s['duplicate_effects']} effet en double. Exactitude des champs : "
            f"{', '.join(f'{k} {v:.0%}' for k, v in s['field_accuracy'].items())}. "
            f"Budget du projet : {s['budget_used_total']} / {s['budget_max']} appels.</p>"
            f"<div class='wrap'><table><tr><th>Demande</th><th>Texte</th><th>Extraction</th><th>Correct</th><th>Statut</th></tr>{rr}</table></div>")

    doc = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Rapport B5 — campagne de pannes</title>
<style>{CSS}</style></head><body><main>
<h1>Workflow résilient et idempotent — rapport de campagne</h1>
<p class="lead">Notes de frais en 5 étapes (réception, extraction LLM, contrôle, virement, notification).
Campagne du {summary['generated_at']} : {summary['n_requests']} demandes synthétiques × {len(summary['seeds'])} seeds
par mode, kills aléatoires du worker toutes les {summary['kill_interval_s'][0]}–{summary['kill_interval_s'][1]} s,
points de crash aléatoires (p = {summary['crash_prob']}), pannes transitoires des services, doublons de livraison.
LLM simulé et déterministe pour la campagne.</p>
<div class="tiles">{tiles}</div>

<h2>Effets externes en double, par seed</h2>
<p class="muted">Paiements, remboursements et e-mails exécutés plus d'une fois pour une même demande (registre des services).</p>
{legend()}<div class="chart">{grouped_bars(runs, "duplicate_effects", "Effets en double par seed")}</div>

<h2>Crashs injectés, par seed</h2>
{legend()}<div class="chart">{grouped_bars(runs, "crashes", "Crashs du worker par seed")}</div>

<h2>Temps de reprise après crash</h2>
<p class="muted">Du kill jusqu'à la première étape terminée par le worker relancé (redémarrage du processus Python inclus).</p>
<div class="chart">{recovery_strip(runs)}</div>

<h2>Synthèse par mode</h2>
<div class="wrap"><table><tr><th>Mesure</th><th class="num">Naïf</th><th class="num">Protégé</th></tr>{''.join(rows)}</table></div>

<h2>Pannes injectées par type</h2>
<div class="wrap"><table><tr><th>Type</th><th class="num">Naïf</th><th class="num">Protégé</th></tr>{faults_rows}</table></div>

<h2>Détail des runs</h2>
<div class="wrap"><table><tr><th>Mode</th><th class="num">Seed</th><th class="num">Complétion</th><th class="num">Doublons</th>
<th class="num">Incohérentes</th><th class="num">Crashs</th><th class="num">Pannes</th><th class="num">Reprise p50 (s)</th>
<th class="num">Durée (s)</th></tr>{run_rows}</table></div>

<h2>Preuve avec le vrai LLM</h2>
{real_html}
</main></body></html>"""
    out = results_dir / "report.html"
    out.write_text(doc, encoding="utf-8")
    return out

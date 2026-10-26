"""Tableau de bord Streamlit : campagne en direct, kill manuel, ou replay d'une campagne enregistrée.

Lancement : `python -m notesfrais dashboard` (direct) ou `python -m notesfrais replay` (sans rien exécuter).
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from notesfrais import STEPS
from notesfrais.chaos import kill_worker
from notesfrais.config import GROUP_DIR, RESULTS_DIR, RUNS_DIR
from notesfrais.journal import Journal
from notesfrais.snapshot import snapshot
from notesfrais.supervisor import worker_env

MODE_LABEL = {"protected": "Protégé (persistance + idempotence)", "naive": "Naïf (baseline)"}
SEGMENTS = STEPS + ["compensation"]
SEG_LABEL = ["Réception", "Extraction", "Contrôle", "Virement", "Notification", "Compensation"]
CELL = {"d": ("#1f9d55", "terminée"), "r": ("#e0a100", "en cours"), "f": ("#d93838", "échec"),
        ".": ("rgba(128,128,128,0.18)", "à venir")}
STATUS_BADGE = {"DONE": ("#1f9d55", "Payée"), "REJECTED": ("#6b6b6b", "Refusée"),
                "COMPENSATED": ("#7b5cd6", "Compensée"), "FAILED": ("#d93838", "Échec"),
                None: ("#e0a100", "En cours")}

CSS = """
<style>
.req-table { width: 100%; border-collapse: separate; border-spacing: 0 3px; font-size: 13px; }
.req-table td { padding: 2px 6px; white-space: nowrap; }
.seg { display: inline-block; width: 15%; height: 12px; margin-right: 2px; border-radius: 3px; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 10px; color: #fff; font-size: 12px; }
.dup { color: #fff; background: #d93838; border-radius: 10px; padding: 1px 8px; font-size: 12px; font-weight: 600; }
.legend-cell { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin: 0 4px 0 12px; vertical-align: -1px; }
.bignum { font-size: 34px; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1.1; }
.bignum.red { color: #d93838; } .bignum.green { color: #1f9d55; }
.biglabel { font-size: 13px; opacity: 0.75; }
.logline { font-family: ui-monospace, Consolas, monospace; font-size: 12px; margin: 0; }
</style>
"""


def parse_args() -> dict:
    args = sys.argv[1:]
    out = {"replay": "--replay" in args, "recording": None}
    if out["replay"]:
        rest = [a for a in args if a != "--replay"]
        out["recording"] = rest[0] if rest else None
    return out


def counter(col, label: str, value, tone: str = "") -> None:
    col.markdown(f'<div class="biglabel">{label}</div><div class="bignum {tone}">{value}</div>',
                 unsafe_allow_html=True)


def render(snap: dict, total: int | None = None) -> None:
    c = snap["counters"]
    cols = st.columns(7)
    counter(cols[0], "Terminées", f"{c['terminees']}" + (f" / {total}" if total else ""))
    counter(cols[1], "En cours", c["en_cours"])
    counter(cols[2], "Pannes injectées", c["pannes_injectees"])
    counter(cols[3], "Crashs du worker", c["kills"])
    dup = c["effets_en_double"]
    counter(cols[4], "Effets en double", dup, "red" if dup else "green")
    counter(cols[5], "Compensations", c["compensations"])
    p50 = c.get("reprise_p50_s")
    counter(cols[6], "Reprise p50", f"{p50:.2f} s" if p50 is not None else "—")

    alive = "🟢 worker en vie" if snap.get("worker_alive") else ("⏹️ terminé" if snap.get("finished") else "🔴 worker arrêté / redémarrage")
    st.caption(f"{alive} · mode : {MODE_LABEL.get(snap.get('mode'), snap.get('mode'))} · "
               f"{c.get('paiements', 0)} paiements dans le registre")

    left, right = st.columns([3, 2])
    with left:
        legend = "".join(f'<span class="legend-cell" style="background:{col}"></span>{lab}' for col, lab in CELL.values())
        st.markdown(f"**Demandes et étapes** {legend}", unsafe_allow_html=True)
        rows = []
        for rid, r in snap["requests"].items():
            segs = "".join(f'<span class="seg" title="{SEG_LABEL[i]} : {CELL.get(code, CELL["."])[1]}" '
                           f'style="background:{CELL.get(code, CELL["."])[0]}"></span>'
                           for i, code in enumerate(r["s"]))
            color, label = STATUS_BADGE.get(r["st"], ("#6b6b6b", r["st"]))
            extra = ""
            if r.get("dup"):
                extra += ' <span class="dup">effet en double</span>'
            if r.get("n", 0) > 1:
                extra += f' <span title="traitements complets">×{r["n"]}</span>'
            if r.get("rs"):
                extra += f' <span title="reprises après crash">↻{r["rs"]}</span>'
            rows.append(f"<tr><td><b>{html.escape(rid)}</b></td><td style='width:55%'>{segs}</td>"
                        f"<td><span class='badge' style='background:{color}'>{label}</span>{extra}</td></tr>")
        st.markdown(f"<table class='req-table'>{''.join(rows)}</table>", unsafe_allow_html=True)
    with right:
        st.markdown("**Journal en direct**")
        lines = []
        for e in reversed(snap["log"][-30:]):
            t = datetime.fromtimestamp(e["ts"]).strftime("%H:%M:%S.%f")[:-3]
            ev = e["event"]
            icon = {"chaos_kill": "💥", "manual_kill": "💥", "crash_point": "💥", "worker_spawned": "🔄",
                    "worker_crashed": "⚠️", "request_resumed": "↻", "duplicate_ignored": "🛡️",
                    "idempotent_replay": "🛡️", "effect_applied": "💶", "fault_injected": "⚡", "retry": "⏳",
                    "llm_cache_hit": "📦", "request_final": "✅", "permanent_error": "⛔", "step_failed": "⛔"}.get(ev, "·")
            detail = " ".join(str(e[k]) for k in ("request_id", "step", "kind", "fault", "status", "point",
                                                   "worker_pid") if e.get(k) is not None)
            lines.append(f'<p class="logline">{t} {icon} <b>{ev}</b> {html.escape(detail)}</p>')
        st.markdown("".join(lines) or "_(vide)_", unsafe_allow_html=True)


def live_page() -> None:
    st.sidebar.header("Campagne en direct")
    mode = st.sidebar.radio("Mode", ["protected", "naive"], format_func=lambda m: MODE_LABEL[m])
    n = st.sidebar.slider("Nombre de demandes", 5, 40, 40)
    seed = st.sidebar.number_input("Seed", 0, 999, 0)
    chaos = st.sidebar.checkbox("Chaos automatique (kills aléatoires)", value=True)
    interval = st.sidebar.slider("Délai avant kill (s)", 0.2, 4.0, (0.5, 1.5), 0.1, disabled=not chaos)
    run_dir = RUNS_DIR / "live" / mode
    if st.sidebar.button("▶ Lancer la campagne", type="primary", use_container_width=True):
        cmd = [sys.executable, "-m", "notesfrais", "run-live", "--run-dir", str(run_dir), "--mode", mode,
               "--n", str(n), "--seed", str(seed), "--kill-interval", str(interval[0]), str(interval[1])]
        if not chaos:
            cmd.append("--no-chaos")
        st.session_state["proc"] = subprocess.Popen(cmd, cwd=str(GROUP_DIR), env=worker_env(),
                                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        st.session_state["run_dir"] = str(run_dir)
        st.session_state["total"] = n
        time.sleep(0.8)
    if st.sidebar.button("💥 Tuer le worker maintenant", use_container_width=True):
        target = Path(st.session_state.get("run_dir", run_dir))
        pid = kill_worker(target, Journal(target, "dashboard"), "manual_kill")
        st.sidebar.success(f"worker {pid} tué") if pid else st.sidebar.info("aucun worker en cours")
    st.sidebar.caption("Le superviseur relance le worker ; en mode protégé il reprend à la première étape non terminée.")

    @st.fragment(run_every=1.0)
    def live() -> None:
        target = Path(st.session_state.get("run_dir", run_dir))
        if not (target / "config.json").exists():
            st.info("Choisissez un mode puis « Lancer la campagne ».")
            return
        render(snapshot(target), st.session_state.get("total"))

    live()


def replay_page(default: str | None) -> None:
    st.sidebar.header("Replay (aucune exécution)")
    recordings = sorted((RESULTS_DIR / "recordings").glob("*.snapshots.jsonl"))
    if default:
        recordings = [Path(default)] + [r for r in recordings if r != Path(default)]
    if not recordings:
        st.warning("Aucun enregistrement dans results/recordings : lancez d'abord `python -m notesfrais campaign`.")
        return
    choice = st.sidebar.selectbox("Enregistrement", recordings, format_func=lambda p: p.name.replace(".snapshots.jsonl", ""))
    speed = st.sidebar.slider("Vitesse", 0.5, 10.0, 2.0, 0.5)
    frames = [json.loads(line) for line in Path(choice).read_text(encoding="utf-8").splitlines() if line.strip()]
    if st.sidebar.button("▶ Rejouer depuis le début", type="primary", use_container_width=True):
        st.session_state["replay_start"] = time.time()
        st.session_state["replay_file"] = str(choice)
    st.sidebar.caption(f"{len(frames)} instantanés enregistrés pendant la campagne.")

    @st.fragment(run_every=0.5)
    def play() -> None:
        if st.session_state.get("replay_file") != str(choice):
            render(frames[-1])
            st.caption("État final — cliquez « Rejouer » pour voir le déroulé.")
            return
        elapsed = (time.time() - st.session_state["replay_start"]) * speed
        t0 = frames[0]["t"]
        frame = frames[0]
        for f in frames:
            if f["t"] - t0 <= elapsed:
                frame = f
            else:
                break
        render(frame)
        st.caption(f"Replay ×{speed} — t = {frame['t'] - t0:.1f} s / {frames[-1]['t'] - t0:.1f} s")

    play()


def main() -> None:
    st.set_page_config(page_title="B5 — Workflow résilient", page_icon="🛡️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    opts = parse_args()
    st.title("Notes de frais — workflow résilient et idempotent")
    if opts["replay"]:
        replay_page(opts["recording"])
    else:
        live_page()


main()

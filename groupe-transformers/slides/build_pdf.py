"""Convertit slides.md (format Marp) en slides.pdf avec matplotlib, sans outil externe.

Gère les titres, sous-titres, listes, paragraphes, tableaux Markdown et blocs de code ;
ajoute le graphique des effets en double après la diapositive « Résultats ».
"""
import json
import re
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).parent
RESULTS = HERE.parent / "results"
INK, MUTED, ACCENT, NAIVE, PROTECTED = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834", "#2a78d6"
W, H = 13.33, 7.5


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    return text.replace("`", "")


def is_bold(text: str) -> bool:
    return text.strip().startswith("**")


def parse(md: str) -> list[list[str]]:
    body = md.split("---", 2)[2]  # retire l'en-tête YAML
    return [s.strip().splitlines() for s in re.split(r"\n---\n", body) if s.strip()]


def draw_table(fig, rows: list[list[str]], top: float) -> float:
    n = len(rows)
    height = min(0.075 * n, 0.62)
    ax = fig.add_axes([0.07, top - height, 0.86, height])
    ax.axis("off")
    cells = [[strip_md(c) for c in r] for r in rows[1:]]
    table = ax.table(cellText=cells, colLabels=[strip_md(c) for c in rows[0]], loc="upper left", cellLoc="left",
                     colLoc="left", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(13)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#e4e2dd")
        cell.set_linewidth(0.8)
        if r == 0:
            cell.set_text_props(color=MUTED, weight="bold")
        elif is_bold(rows[r][c] if c < len(rows[r]) else ""):
            cell.set_text_props(weight="bold", color=INK)
    return top - height - 0.04


def render_slide(pdf: PdfPages, lines: list[str], number: int) -> None:
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor("white")
    y = 0.88
    in_code, table = False, []

    def flush_table():
        nonlocal y, table
        if table:
            y = draw_table(fig, table, y)
            table = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            fig.text(0.09, y, line, fontsize=15, family="monospace", color=INK, va="top")
            y -= 0.055
            continue
        if line.startswith("|"):
            if set(line.replace("|", "").strip()) <= set("-: "):
                continue
            table.append([c.strip() for c in line.strip("|").split("|")])
            continue
        flush_table()
        if not line.strip():
            y -= 0.02
        elif line.startswith("# "):
            fig.text(0.07, y, strip_md(line[2:]), fontsize=30, weight="bold", color=INK)
            fig.add_artist(plt.Line2D([0.07, 0.17], [y - 0.03, y - 0.03], color=ACCENT, linewidth=4))
            y -= 0.09
        elif line.startswith("## "):
            fig.text(0.07, y, strip_md(line[3:]), fontsize=20, color=MUTED, va="top")
            y -= 0.08
        elif re.match(r"^(\d+\.|-|\+) ", line):
            marker, text = line.split(" ", 1)
            bullet = "•" if marker in ("-", "+") else marker
            wrapped = textwrap.wrap(strip_md(text), 72 if is_bold(text) else 82)
            fig.text(0.08, y, bullet, fontsize=17, color=ACCENT, weight="bold", va="top", linespacing=1.35)
            fig.text(0.11, y, "\n".join(wrapped), fontsize=17, color=INK, va="top", linespacing=1.35,
                     weight="bold" if is_bold(text) else "normal")
            y -= 0.052 * len(wrapped) + 0.014
        else:
            wrapped = textwrap.wrap(strip_md(line), 74 if is_bold(line) else 86)
            y -= 0.012
            fig.text(0.07, y, "\n".join(wrapped), fontsize=17, color=INK, va="top", linespacing=1.35,
                     weight="bold" if is_bold(line) else "normal",
                     style="italic" if line.startswith("*") and not line.startswith("**") else "normal")
            y -= 0.052 * len(wrapped) + 0.016
    flush_table()
    fig.text(0.93, 0.04, str(number), fontsize=11, color=MUTED, ha="right")
    fig.text(0.07, 0.04, "B5 — groupe transformers", fontsize=11, color=MUTED)
    pdf.savefig(fig)
    plt.close(fig)


def chart_slide(pdf: PdfPages, number: int) -> None:
    runs = json.loads((RESULTS / "runs.json").read_text(encoding="utf-8"))
    seeds = sorted({r["seed"] for r in runs})
    fig = plt.figure(figsize=(W, H))
    fig.text(0.07, 0.88, "Effets en double, par seed", fontsize=30, weight="bold", color=INK)
    ax = fig.add_axes([0.08, 0.14, 0.86, 0.62])
    for i, (mode, color, label) in enumerate([("naive", NAIVE, "Naïf (baseline)"), ("protected", PROTECTED, "Protégé")]):
        vals = [next(r["duplicate_effects"] for r in runs if r["mode"] == mode and r["seed"] == s) for s in seeds]
        xs = [k + (i - 0.5) * 0.38 for k in range(len(seeds))]
        bars = ax.bar(xs, vals, 0.35, color=color, label=label)
        ax.bar_label(bars, padding=3, fontsize=14)
    ax.set_xticks(range(len(seeds)), [f"seed {s}" for s in seeds], fontsize=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e4e2dd")
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(r["duplicate_effects"] for r in runs) * 1.2 + 1)
    ax.legend(frameon=False, fontsize=14)
    ax.set_ylabel("effets exécutés plus d'une fois", fontsize=13)
    fig.text(0.93, 0.04, str(number), fontsize=11, color=MUTED, ha="right")
    fig.text(0.07, 0.04, "B5 — groupe transformers", fontsize=11, color=MUTED)
    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    slides = parse((HERE / "slides.md").read_text(encoding="utf-8"))
    number = 0
    with PdfPages(HERE / "slides.pdf") as pdf:
        for lines in slides:
            number += 1
            render_slide(pdf, lines, number)
            if lines and lines[0].startswith("# Résultats") and (RESULTS / "runs.json").exists():
                number += 1
                chart_slide(pdf, number)
    print(f"{number} diapositives -> {HERE / 'slides.pdf'}")


if __name__ == "__main__":
    main()

"""
Generate all five figures for the Hermes Bytecode paper at 300 DPI
with a cohesive academic design system.

Design tokens
-------------
Palette:
  primary_*   blues  — informational
  success_*   greens — patched/correct
  warning_*   oranges — bug/caution
  error_*     reds   — original bug
Typography: serif body, monospace for code.
Radius: 0.08–0.12, Linewidth: 1.0–1.5.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

OUTDIR = os.path.abspath('figs_new')
os.makedirs(OUTDIR, exist_ok=True)
DPI = 300

# --- Design tokens ---
C = {
    'primary_50':   '#E3F2FD',
    'primary_100':  '#BBDEFB',
    'primary_200':  '#90CAF9',
    'primary_300':  '#64B5F6',
    'primary_400':  '#42A5F5',
    'primary_500':  '#2196F3',
    'primary_600':  '#1E88E5',
    'primary_700':  '#1565C0',
    'primary_900':  '#0D47A1',
    'success_50':   '#E8F5E9',
    'success_100':  '#C8E6C9',
    'success_300':  '#66BB6A',
    'success_700':  '#2E7D32',
    'warning_50':   '#FFF3E0',
    'warning_100':  '#FFE0B2',
    'warning_200':  '#FFCC80',
    'warning_700':  '#E65100',
    'error_100':    '#FFCDD2',
    'error_700':    '#C62828',
    'caution_50':   '#FFF9C4',
    'caution_700':  '#F57F17',
    'indigo_50':    '#E8EAF6',
    'indigo_100':   '#C5CAE9',
    'indigo_200':   '#9FA8DA',
    'indigo_300':   '#7986CB',
    'indigo_400':   '#5C6BC0',
    'indigo_500':   '#3F51B5',
    'indigo_700':   '#303F9F',
    'indigo_900':   '#1A237E',
    'purple_50':    '#F3E5F5',
    'purple_700':   '#4527A0',
    'pink_50':      '#FCE4EC',
    'pink_700':     '#AD1457',
    'neutral_800':  '#37474F',
    'neutral_600':  '#546E7A',
    'white':        '#FFFFFF',
}

# ------------------------------------------------------------
#  FIGURE 1 — Reverse engineering methodology workflow
# ------------------------------------------------------------
def make_fig1():
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-1.3, 2.3)
    ax.axis('off')

    steps = [
        ("1", "Network\nTraffic\nCapture\n(HAR)"),
        ("2", "API\nResponse\nAnalysis"),
        ("3", "APK\nDecompile\n(JADX +\nhbc-dec)"),
        ("4", "Function\nID &\nBytecode\nDisasm."),
        ("5", "Root\nCause\nAnalysis"),
        ("6", "Bytecode\nPatch\nDesign"),
        ("7", "APK\nRebuild\n& Sign"),
        ("8", "Validation\n& Test"),
    ]
    fills = [C['primary_50'], C['primary_100'], C['primary_200'], C['primary_300'],
             C['primary_400'], C['primary_500'], C['primary_600'], C['primary_700']]
    # Label color depends on box darkness; number circles always dark navy for visibility
    label_colors = [C['primary_900']] * 5 + [C['white']] * 3

    for i, (num, label) in enumerate(steps):
        box = FancyBboxPatch((i - 0.42, -0.55), 0.84, 1.75,
                             boxstyle="round,pad=0.08",
                             facecolor=fills[i], edgecolor=C['primary_900'],
                             linewidth=1.2)
        ax.add_patch(box)
        # Circled number above box (always dark navy on white, readable)
        num_circle = plt.Circle((i, 1.55), 0.20,
                                facecolor=C['primary_900'],
                                edgecolor=C['primary_900'])
        ax.add_patch(num_circle)
        ax.text(i, 1.55, num, ha='center', va='center',
                fontsize=11, fontweight='bold', color=C['white'],
                fontfamily='serif')
        ax.text(i, 0.33, label, ha='center', va='center',
                fontsize=7.5, color=label_colors[i], fontfamily='serif',
                linespacing=1.15)
        if i < len(steps) - 1:
            ax.annotate('', xy=(i + 0.52, 0.42), xytext=(i + 0.48, 0.42),
                        arrowprops=dict(arrowstyle='->',
                                        color=C['primary_900'],
                                        lw=1.8, mutation_scale=14))

    fig.tight_layout(pad=0.3)
    out = os.path.join(OUTDIR, 'fig1_methodology.png')
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return out


# ------------------------------------------------------------
#  FIGURE 2 — HBC v96 file structure overview
# ------------------------------------------------------------
def make_fig2():
    fig, ax = plt.subplots(figsize=(5.5, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 9.2)
    ax.axis('off')

    sections = [
        ("File Header",                        "0x00",    "128 B",      C['indigo_50']),
        ("Function Headers\n(31,361 × 16 B)",  "0x80",    "501,776 B",  C['indigo_100']),
        ("String Kind Table",                  "0x7A890", "Variable",   C['indigo_200']),
        ("Small String Table",                 "0x91BB0", "200,868 B",  C['indigo_300']),
        ("Overflow String Table",              "0xC2C54", "3,144 B",    C['indigo_400']),
        ("String Storage",                     "0xC389C", "977,152 B",  C['indigo_500']),
        ("Bytecode Section",                   "…",       "~4.9 MB",    C['indigo_900']),
    ]

    y = 8.6
    box_w = 6.4
    x0 = 2.0
    for i, (name, offset, size, color) in enumerate(sections):
        h = 0.85 if i < 5 else 1.2
        tc = C['white'] if i >= 4 else C['indigo_900']

        rect = FancyBboxPatch((x0, y - h), box_w, h,
                              boxstyle="round,pad=0.04",
                              facecolor=color, edgecolor=C['indigo_900'],
                              linewidth=1.0)
        ax.add_patch(rect)
        ax.text(x0 + box_w / 2, y - h / 2, name,
                ha='center', va='center', fontsize=9,
                fontweight='bold', color=tc, fontfamily='serif',
                linespacing=1.15)

        ax.text(x0 - 0.2, y - h / 2, offset,
                ha='right', va='center', fontsize=8,
                fontfamily='monospace', color=C['neutral_800'])
        ax.text(x0 + box_w + 0.2, y - h / 2, size,
                ha='left', va='center', fontsize=8,
                fontfamily='serif', color=C['neutral_800'])

        y -= h + 0.18

    ax.text(0.9, 8.6, "Offset", ha='center', fontsize=8.5, fontweight='bold',
            fontfamily='serif', color=C['neutral_800'])
    ax.text(9.1, 8.6, "Size",   ha='center', fontsize=8.5, fontweight='bold',
            fontfamily='serif', color=C['neutral_800'])

    fig.tight_layout(pad=0.3)
    out = os.path.join(OUTDIR, 'fig2_hbc_structure.png')
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return out


# ------------------------------------------------------------
#  FIGURE 3 — Login generator control flow + Patch #1
# ------------------------------------------------------------
def make_fig3():
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-1.0, 10.3)
    ax.axis('off')

    nodes = {
        'case31':  (5.0, 9.3,  "Case 31\nloginFn(loginData)"),
        'case46':  (5.0, 7.8,  "Case 46\nr1 ← login response"),
        'case55':  (5.0, 6.2,  "Cases 55–119\nPush-token processing\n(r1 unchanged)"),
        'case128': (5.0, 4.35, "Case 128\nsetLoading(false)\nif (!r1) — JmpFalse"),
        'case142': (2.5, 2.45, "Case 142\nnavigation.replace\n(STUDENT_TABS_ROOT)"),
        'case216': (7.5, 2.45, "Case 216\nAcademic-role\ncheck"),
    }
    colors = {
        'case142': (C['success_50'],  C['success_700']),
        'case128': (C['warning_50'],  C['warning_700']),
    }
    for key, (x, y, label) in nodes.items():
        fc, ec = colors.get(key, (C['primary_50'], C['primary_700']))
        w, h = 3.0, 1.25
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.1",
                              facecolor=fc, edgecolor=ec, linewidth=1.4)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center',
                fontsize=8, fontfamily='serif', linespacing=1.25,
                color=ec)

    # Vertical arrows main flow
    arrow_main = dict(arrowstyle='->', color=C['primary_700'], lw=1.6,
                      mutation_scale=14)
    for (x1, y1), (x2, y2) in [
        ((5, 8.68), (5, 8.43)),
        ((5, 7.18), (5, 6.83)),
        ((5, 5.58), (5, 4.98)),
    ]:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=arrow_main)

    # Green arrow: r1 truthy → Case 142 (PATCHED)
    ax.annotate('', xy=(2.85, 3.05), xytext=(3.85, 3.85),
                arrowprops=dict(arrowstyle='->', color=C['success_700'],
                                lw=2.2, mutation_scale=16))
    ax.text(2.2, 4.0, "r1 truthy\n(after patch)", ha='center',
            fontsize=8, color=C['success_700'], fontweight='bold',
            fontfamily='serif')

    # Red dashed arrow: r1 falsy → Case 216 (ORIGINAL BUG)
    ax.annotate('', xy=(7.15, 3.05), xytext=(6.15, 3.85),
                arrowprops=dict(arrowstyle='->', color=C['error_700'],
                                lw=1.8, mutation_scale=16, linestyle='dashed'))
    ax.text(7.85, 4.0, "r1 falsy\n(original bug)", ha='center',
            fontsize=8, color=C['error_700'], fontweight='bold',
            fontfamily='serif')

    # Patch callout
    ax.text(5, 0.9,
            "Patch #1 — Offset 0x4FF3BB :  JmpFalse 0x4D → 0x03  (1 byte)\n"
            "Effect: conditional branch converted to fall-through;\n"
            "navigation always executed when Case 128 is reached.",
            ha='center', va='center', fontsize=8.5, fontfamily='serif',
            bbox=dict(boxstyle='round,pad=0.45',
                      facecolor=C['caution_50'],
                      edgecolor=C['caution_700'], linewidth=1.3))

    fig.tight_layout(pad=0.3)
    out = os.path.join(OUTDIR, 'fig3_login_flow.png')
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return out


# ------------------------------------------------------------
#  Helper — render one bytecode cell, wrapping long labels
# ------------------------------------------------------------
def _draw_op_cell(ax, x, w, bytes_len, name, bytecode, effect,
                  face, edge):
    """Draw a single opcode cell.
    Long labels are split onto two lines, font size shrinks for narrow cells."""
    # Two-line name if it's too long relative to cell width
    if len(name) > 10:
        display_name = name.replace("LoadConstUndefined", "LoadConst\nUndefined")
        name_fs = 8.0
        name_ls = 1.05
    else:
        display_name = name
        name_fs = 9.0
        name_ls = 1.0

    rect = FancyBboxPatch((x, 0.3), w - 0.12, 2.8,
                          boxstyle="round,pad=0.06",
                          facecolor=face, edgecolor=edge, linewidth=1.2)
    ax.add_patch(rect)
    cx = x + (w - 0.12) / 2

    ax.text(cx, 2.60, display_name, ha='center', va='center',
            fontsize=name_fs, fontweight='bold',
            fontfamily='serif', color=edge, linespacing=name_ls)
    ax.text(cx, 1.80, bytecode, ha='center', va='center',
            fontsize=8, fontfamily='monospace',
            color=C['neutral_800'])
    ax.text(cx, 1.20, effect, ha='center', va='center',
            fontsize=7.5, fontfamily='serif',
            color=C['neutral_800'], style='italic')
    ax.text(cx, 0.55, f"{bytes_len} B", ha='center',
            fontsize=7.5, fontfamily='monospace',
            color=C['neutral_600'])


# ------------------------------------------------------------
#  FIGURE 4a — Original bytecode sequence (nested, 15 B)
# ------------------------------------------------------------
def make_fig4a():
    fig, ax = plt.subplots(figsize=(8.5, 2.4))
    ax.set_xlim(-0.3, 12.3)
    ax.set_ylim(-0.2, 3.9)
    ax.axis('off')

    ax.text(6.0, 3.55, "(a) Original 15-byte sequence — fails on flat response",
            ha='center', fontsize=10.5, fontweight='bold',
            fontfamily='serif', color=C['error_700'])

    ops = [
        ("GetById",            "37 09 00 0C 0F 65",  "r9 ← r0.yoklamaGunler",  6),
        ("Eq",                 "0E 07 09 06",        "r7 = (r9 == null)",      4),
        ("LoadConstUndefined", "76 06",              "r6 ← undefined",         2),
        ("JmpTrue +20",        "90 14 07",           "skip → empty render",    3),
    ]
    x = 0.0
    total_w = 12.0
    unit = total_w / sum(b for _, _, _, b in ops)
    for name, bytecode, effect, bytes_len in ops:
        w = unit * bytes_len
        _draw_op_cell(ax, x, w, bytes_len, name, bytecode, effect,
                      C['error_100'], C['error_700'])
        x += w

    fig.tight_layout(pad=0.2)
    out = os.path.join(OUTDIR, 'fig4a_array_wrap_original.png')
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return out


# ------------------------------------------------------------
#  FIGURE 4b — Patched bytecode sequence (array-wrap, 15 B)
# ------------------------------------------------------------
def make_fig4b():
    fig, ax = plt.subplots(figsize=(8.5, 2.4))
    ax.set_xlim(-0.3, 12.3)
    ax.set_ylim(-0.2, 3.9)
    ax.axis('off')

    ax.text(6.0, 3.55, "(b) Patched 15-byte sequence — wraps flat item into single-element array",
            ha='center', fontsize=10.5, fontweight='bold',
            fontfamily='serif', color=C['success_700'])

    ops = [
        ("NewArray",           "07 09 01 00",        "r9 ← new Array(size=1)", 4),
        ("PutByIndex",         "44 09 00 00",        "r9[0] ← r0 (item)",      4),
        ("LoadConstUndefined", "76 06",              "r6 ← undefined",         2),
        ("LoadConstUndefined", "76 07",              "r7 ← undefined",         2),
        ("JmpTrue +3",         "90 03 07",           "fall through → .map",    3),
    ]
    x = 0.0
    total_w = 12.0
    unit = total_w / sum(b for _, _, _, b in ops)
    for name, bytecode, effect, bytes_len in ops:
        w = unit * bytes_len
        _draw_op_cell(ax, x, w, bytes_len, name, bytecode, effect,
                      C['success_100'], C['success_700'])
        x += w

    fig.tight_layout(pad=0.2)
    out = os.path.join(OUTDIR, 'fig4b_array_wrap_patched.png')
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return out


# ------------------------------------------------------------
#  FIGURE 5 — Hierarchical render chain
# ------------------------------------------------------------
def make_fig5():
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.set_xlim(-0.5, 11.2)
    ax.set_ylim(-0.6, 4.2)
    ax.axis('off')

    funcs = [
        ("_fun26882\n(Data Loader)",
         "API → response\nyoklamaHaftalar\n→ component state",
         C['primary_50'], C['primary_700']),
        ("_fun26884\n(Week Render)",
         "H_NO header\nyoklamaGunler\n.map()",
         C['indigo_50'], C['purple_700']),
        ("_fun26885\n(Day Render)",
         "TARIH + GUN\nyoklamaSaatList\n.map()",
         C['pink_50'], C['pink_700']),
        ("_fun26886\n(Slot Render)",
         "SAAT\nGIRME_TIP\n(leaf display)",
         C['success_50'], C['success_700']),
    ]

    W, H = 2.45, 2.8
    GAP = 0.25
    for i, (title, desc, fc, ec) in enumerate(funcs):
        x = i * (W + GAP)
        rect = FancyBboxPatch((x, 0.5), W, H, boxstyle="round,pad=0.12",
                              facecolor=fc, edgecolor=ec, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(x + W/2, 2.85, title, ha='center', va='center',
                fontsize=9, fontweight='bold', fontfamily='serif', color=ec)
        ax.text(x + W/2, 1.55, desc, ha='center', va='center',
                fontsize=8, fontfamily='serif', color=C['neutral_800'],
                linespacing=1.30)

        if i < len(funcs) - 1:
            ax.annotate('', xy=(x + W + GAP - 0.02, 1.9),
                        xytext=(x + W + 0.02, 1.9),
                        arrowprops=dict(arrowstyle='->',
                                        color=C['neutral_600'],
                                        lw=2.2, mutation_scale=18))

    fig.tight_layout(pad=0.3)
    out = os.path.join(OUTDIR, 'fig5_render_chain.png')
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return out


# ------------------------------------------------------------
if __name__ == '__main__':
    from PIL import Image
    paths = [make_fig1(), make_fig2(), make_fig3(),
             make_fig4a(), make_fig4b(), make_fig5()]
    print("\nGenerated figures:")
    for p in paths:
        img = Image.open(p)
        print(f"  {os.path.basename(p):<35} {img.size[0]}x{img.size[1]}  DPI {img.info.get('dpi')}")

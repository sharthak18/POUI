"""
Generate the paper's parameter-size, checklist, and architecture figures.
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from pathlib import Path

BG    = "#0d1117"
PANEL = "#161b22"
EDGE  = "#30363d"
TXT   = "#c9d1d9"
TXT_H = "#e6edf3"
GRID  = "#21262d"

C_HONEST   = "#3fb950"
C_MAL      = "#f85149"
C_ACCENT   = "#58a6ff"
C_AMBER    = "#d29922"
C_PURPLE   = "#bc8cff"
C_TEAL     = "#39d353"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL,
    "axes.edgecolor": EDGE, "axes.labelcolor": TXT,
    "axes.titlecolor": TXT_H, "xtick.color": "#8b949e",
    "ytick.color": "#8b949e", "text.color": TXT,
    "grid.color": GRID, "grid.linestyle": "--", "grid.alpha": 0.6,
    "font.family": "sans-serif", "legend.facecolor": PANEL,
    "legend.edgecolor": EDGE,
})

out_dir = Path(__file__).parent / "figures"
out_dir.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# FIGURE 1: PQC Parameter-Size and Payload Dashboard
# ═══════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 9), facecolor=BG)
fig.suptitle("PQC Parameter Sizing — FIPS Byte Sizes and Scenario Payloads\n"
             "Illustrative model only; no local ML-DSA/ML-KEM benchmark (RQ3)",
             fontsize=13, fontweight="bold", color=TXT_H, y=0.98)
gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38,
              left=0.07, right=0.97, top=0.90, bottom=0.09)

pqc_results_path = Path(__file__).parent.parent / "pqc-benchmarks" / "results" / "pqc_benchmark_results.json"
with open(pqc_results_path, encoding="utf-8") as f:
    pqc_results = json.load(f)
profiles = pqc_results["signature_schemes"]
kem_profiles = pqc_results["kem_schemes"]
scheme_keys = ["ECDSA-P256", "Ed25519", "ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
sig_bytes = [profiles[name]["signature_bytes"] for name in scheme_keys]
pk_bytes = [profiles[name]["public_key_bytes"] for name in scheme_keys]
colors_bar = [C_ACCENT, C_ACCENT, C_MAL, C_AMBER, C_PURPLE]

# ── Plot 1: Signature sizes ──────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(scheme_keys, sig_bytes, color=colors_bar, alpha=0.85, edgecolor=EDGE, linewidth=0.8)
ax1.set_title("Signature Size Comparison", fontweight="bold", fontsize=10)
ax1.set_ylabel("Bytes")
ax1.set_yscale("log")
ax1.tick_params(axis='x', rotation=30, labelsize=7.5)
ax1.grid(True, axis='y')
for bar, val in zip(bars, sig_bytes):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.1,
             f"{val:,}", ha='center', va='bottom', fontsize=7, color=TXT)
ax1.axhline(64, color=C_ACCENT, linestyle=':', alpha=0.5, linewidth=1, label="Ed25519 baseline")
ax1.legend(fontsize=7)

# ── Plot 2: Public-key parameter sizes ────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
bars2 = ax2.bar(scheme_keys, pk_bytes, color=colors_bar, alpha=0.85, edgecolor=EDGE, linewidth=0.8)
ax2.set_title("Public-Key Parameter Size", fontweight="bold", fontsize=10)
ax2.set_ylabel("Bytes")
ax2.tick_params(axis='x', rotation=30, labelsize=7.5)
ax2.grid(True, axis='y')
for bar, val in zip(bars2, pk_bytes):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 35,
             f"{val:,}", ha='center', va='bottom', fontsize=7, color=TXT)
ax2.text(0.97, 0.92, "Encoding conventions are scheme-specific;\nP-256 uses raw x||y coordinates.",
         transform=ax2.transAxes, ha='right', va='top', fontsize=7,
         color=TXT, bbox=dict(boxstyle='round,pad=0.3', fc=PANEL, ec=EDGE, alpha=0.9))

# ── Plot 3: raw signature payload by TPS scenario ─────────────────
ax3 = fig.add_subplot(gs[0, 2])
payload_rows = [
    row for row in pqc_results["signature_payload_scenarios"]
    if row["scheme_key"] == "ML-DSA-44" and row["validator_count"] == 100
]
tps_levels = [f"{row['tps_context_only']:,} TPS" for row in payload_rows]
payload = [row["total_signature_bytes_per_block"] / 1000.0 for row in payload_rows]
x = np.arange(len(tps_levels))
ax3.bar(x, payload, 0.58, color=C_MAL, alpha=0.82, edgecolor=EDGE)
ax3.set_title("Raw ML-DSA-44 Signature Payload\n(100 validators; one signature each/block)", fontweight="bold", fontsize=9)
ax3.set_ylabel("Decimal kB/block")
ax3.set_xticks(x); ax3.set_xticklabels(tps_levels, fontsize=8)
ax3.grid(True, axis='y')
ax3.text(0.5, 0.94,
         "Same per block under this model; public keys are registered.\nProofs and framing excluded; no aggregation evaluated.",
         transform=ax3.transAxes, ha='center', va='top', fontsize=7,
         color=TXT, bbox=dict(boxstyle='round,pad=0.3', fc=PANEL, ec=EDGE, alpha=0.95))

# ── Plot 4: ML-KEM parameter sizes ────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
kem_names = list(kem_profiles)
kem_public_keys = [kem_profiles[name]["public_key_bytes"] for name in kem_names]
kem_ciphertexts = [kem_profiles[name]["ciphertext_bytes"] for name in kem_names]
x2 = np.arange(len(kem_names))
ax4.bar(x2 - 0.2, kem_public_keys, 0.4, label="Public key", color=C_ACCENT, alpha=0.8, edgecolor=EDGE)
ax4.bar(x2 + 0.2, kem_ciphertexts, 0.4, label="Ciphertext", color=C_PURPLE, alpha=0.8, edgecolor=EDGE)
ax4.set_title("ML-KEM Public-Key and Ciphertext Sizes", fontweight="bold", fontsize=9)
ax4.set_ylabel("Bytes")
ax4.set_xticks(x2); ax4.set_xticklabels(kem_names, fontsize=8, rotation=15)
ax4.legend(fontsize=7)
ax4.grid(True, axis='y')

# ── Plot 5: Signature size amplification radar-style bar ─────────
ax5 = fig.add_subplot(gs[1, 1])
dsa_names = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
amp_sig = [profiles[name]["signature_bytes"] / profiles["Ed25519"]["signature_bytes"]
            for name in ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]]
amp_pk = [profiles[name]["public_key_bytes"] / profiles["Ed25519"]["public_key_bytes"]
          for name in ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]]
x3 = np.arange(len(dsa_names))
ax5.bar(x3 - 0.2, amp_sig, 0.4, label="Sig Amplification×", color=C_MAL, alpha=0.8, edgecolor=EDGE)
ax5.bar(x3 + 0.2, amp_pk,  0.4, label="PK Amplification×",  color=C_AMBER, alpha=0.8, edgecolor=EDGE)
ax5.set_title("Size Amplification vs Ed25519", fontweight="bold", fontsize=10)
ax5.set_ylabel("× Ed25519")
ax5.set_xticks(x3); ax5.set_xticklabels(dsa_names, fontsize=8)
ax5.legend(fontsize=7)
ax5.grid(True, axis='y')
ax5.axhline(1, color=C_ACCENT, linestyle=':', alpha=0.5, linewidth=1)

# ── Plot 6: Mitigation comparison ───────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis("off")
mit_data = [
    ["ID", "Option", "Sizing", "Status"],
    ["M1", "Aggregate sigs", "Not measured", "Research"],
    ["M2", "Hybrid rollout", "Not quantified", "Design-specific"],
    ["M3", "Merkle batch", "Not computed", "Format open"],
    ["M4", "Hardware", "Not measured", "Not evaluated"],
]
tbl = ax6.table(cellText=mit_data[1:], colLabels=mit_data[0],
                cellLoc="center", loc="center", bbox=[0, 0, 1, 1],
                colWidths=[0.10, 0.30, 0.28, 0.32])
tbl.auto_set_font_size(False); tbl.set_fontsize(7)
for (r, c), cell in tbl.get_celld().items():
    cell.set_facecolor(PANEL); cell.set_edgecolor(EDGE)
    cell.set_text_props(color=TXT)
    if r == 0:
        cell.set_facecolor("#21262d")
        cell.set_text_props(color=TXT_H, fontweight="bold")
ax6.set_title("Architecture Options (Not Evaluated)", fontweight="bold", fontsize=9)

fig.savefig(out_dir / "fig_pqc_benchmarks.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out_dir}/fig_pqc_benchmarks.png")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 2: ZKML Design Checklist Visual
# ═══════════════════════════════════════════════════════════════════
fig2, ax = plt.subplots(figsize=(14, 7), facecolor=BG)
ax.set_facecolor(BG)
ax.axis("off")
fig2.suptitle("ZKML Circuit-Soundness Review Checklist for PoUI\n"
              "Analytical Feasibility Study",
              fontsize=13, fontweight="bold", color=TXT_H)

checklist_data = [
    ("V-I",   "Range &\nrepresentation", "Bounded integer wires", C_MAL),
    ("V-II",  "Tie-breaking\nsemantics", "ArgMax/TopK outputs", C_AMBER),
    ("V-III", "Layer-relation\ncoverage", "Intermediate values", C_PURPLE),
    ("V-IV",  "Quantization\nconfiguration", "Scale, rounding, overflow", "#79c0ff"),
    ("V-V",   "Model/version\nbinding", "Weights and commitment", C_MAL),
]

for i, (vid, name, layers, color) in enumerate(checklist_data):
    x0 = 0.05 + i * 0.19
    # Main box
    rect = mpatches.FancyBboxPatch((x0, 0.35), 0.16, 0.50,
                                    boxstyle="round,pad=0.02",
                                    facecolor=color, alpha=0.15,
                                    edgecolor=color, linewidth=2,
                                    transform=ax.transAxes)
    ax.add_patch(rect)
    # Class ID
    ax.text(x0 + 0.08, 0.81, vid, ha='center', va='center',
            fontsize=16, fontweight='bold', color=color, transform=ax.transAxes)
    # Name
    ax.text(x0 + 0.08, 0.72, name, ha='center', va='center',
            fontsize=8.5, color=TXT_H, transform=ax.transAxes)
    # Requirement badge
    badge_color = C_ACCENT
    badge = mpatches.FancyBboxPatch((x0 + 0.02, 0.57), 0.12, 0.07,
                                     boxstyle="round,pad=0.01",
                                     facecolor=badge_color, alpha=0.3,
                                     edgecolor=badge_color, linewidth=1,
                                     transform=ax.transAxes)
    ax.add_patch(badge)
    ax.text(x0 + 0.08, 0.605, "Review focus", ha='center', va='center',
            fontsize=7, color=badge_color, fontweight='bold', transform=ax.transAxes)
    # Affected layers
    ax.text(x0 + 0.08, 0.46, f"Layers:\n{layers}", ha='center', va='center',
            fontsize=7, color=TXT, transform=ax.transAxes)
    ax.text(x0 + 0.08, 0.38, "Audit question", ha='center', va='center',
            fontsize=7, color=C_ACCENT, fontweight='bold', transform=ax.transAxes)

# Soundness condition box
ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.08), 0.90, 0.20,
             boxstyle="round,pad=0.02", facecolor="#161b22",
             edgecolor=C_ACCENT, linewidth=1.5, transform=ax.transAxes))
ax.text(0.50, 0.24, "Soundness target: accepted outputs satisfy the intended, bound model/input relation.",
        ha='center', va='center', fontsize=9.5, color=C_ACCENT,
        fontweight='bold', transform=ax.transAxes)
ax.text(0.50, 0.14, "Design checklist only — not a compiler-specific audit or exploit study.",
        ha='center', va='center', fontsize=8.5, color=TXT, transform=ax.transAxes)

fig2.savefig(out_dir / "fig_zkml_taxonomy.jpg", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out_dir}/fig_zkml_taxonomy.jpg")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 3: Architecture Co-Design Diagram
# ═══════════════════════════════════════════════════════════════════
fig3, ax3 = plt.subplots(figsize=(14, 8), facecolor=BG)
ax3.set_facecolor(BG)
ax3.axis("off")
fig3.suptitle("PoUI Challenge--Proof--Score Requirements\n"
              "Analytical Feasibility Study",
              fontsize=13, fontweight="bold", color=TXT_H)

layers = [
    {"label": "L1: PoUI Consensus Layer",
     "desc": "Epoch nonce and challenge commitment\nScore update and slash decision\nUnderlying consensus supplies finality",
     "color": C_HONEST, "y": 0.68},
    {"label": "L2: ZKML Proof Layer",
     "desc": "Committed model inference\nProof binds challenge, model, and output\nVerifier accepts or rejects proof",
     "color": C_ACCENT, "y": 0.42},
    {"label": "L3: PQC Key and Signature Interfaces",
     "desc": "ML-DSA signature binds the transcript\nML-KEM can protect probe delivery\nKey-to-identity binding is required",
     "color": C_PURPLE, "y": 0.16},
]

for layer in layers:
    rect = mpatches.FancyBboxPatch((0.05, layer["y"]), 0.55, 0.20,
                                    boxstyle="round,pad=0.02",
                                    facecolor=layer["color"], alpha=0.12,
                                    edgecolor=layer["color"], linewidth=2,
                                    transform=ax3.transAxes)
    ax3.add_patch(rect)
    ax3.text(0.325, layer["y"] + 0.135, layer["label"],
             ha='center', va='center', fontsize=11,
             fontweight='bold', color=layer["color"], transform=ax3.transAxes)
    ax3.text(0.325, layer["y"] + 0.065, layer["desc"],
             ha='center', va='center', fontsize=8.5, color=TXT, transform=ax3.transAxes)

# Arrows between layers
for y_start, label_ic in [(0.68, "IC-01: RequestInferenceProof\nIC-02: SubmitVerifiedOutput"),
                           (0.42, "IC-03: RegisterValidatorKey\nIC-04: SignProofHash")]:
    ax3.annotate("", xy=(0.325, y_start - 0.005), xytext=(0.325, y_start - 0.048),
                 xycoords='axes fraction', textcoords='axes fraction',
                 arrowprops=dict(arrowstyle='<->', color="#8b949e", lw=2))
    ax3.text(0.37, y_start - 0.027, label_ic, ha='left', va='center',
             fontsize=7.5, color="#8b949e", transform=ax3.transAxes)

# Required bindings panel
props = [
    ("B-1", "Epoch + challenge", C_TEAL),
    ("B-2", "Model + inference config", C_ACCENT),
    ("B-3", "Output + proof hash + signature", C_AMBER),
]
ax3.text(0.72, 0.88, "Fields to Bind\n(before score update)",
         ha='center', fontsize=10, fontweight='bold', color=TXT_H, transform=ax3.transAxes)
for i, (pid, name, col) in enumerate(props):
    y_p = 0.72 - i * 0.13
    badge = mpatches.FancyBboxPatch((0.63, y_p - 0.03), 0.33, 0.09,
                                     boxstyle="round,pad=0.01",
                                     facecolor=col, alpha=0.15,
                                     edgecolor=col, linewidth=1.5,
                                     transform=ax3.transAxes)
    ax3.add_patch(badge)
    ax3.text(0.795, y_p + 0.015, f"[{pid}] {name}",
             ha='center', va='center', fontsize=8, color=col,
             fontweight='bold', transform=ax3.transAxes)

# Design-scenario panel (no unsupported severity ranking)
scenarios = [
    ("FM-CD-1", "Proof deadline mismatch", C_MAL),
    ("FM-CD-2", "Key-version mismatch", C_AMBER),
    ("FM-CD-3", "Enrollment authentication", C_TEAL),
    ("FM-CD-4", "Payload budget unspecified", C_PURPLE),
]
ax3.text(0.72, 0.30, "Design Scenarios to Resolve",
         ha='center', fontsize=10, fontweight='bold', color=TXT_H, transform=ax3.transAxes)
for i, (fid, name, col) in enumerate(scenarios):
    y_f = 0.23 - i * 0.05
    ax3.text(0.65, y_f, f"[{fid}]", ha='left', va='center',
             fontsize=7.5, color=col, fontweight='bold', transform=ax3.transAxes)
    ax3.text(0.73, y_f, name, ha='left', va='center',
             fontsize=7.5, color=TXT, transform=ax3.transAxes)

fig3.savefig(out_dir / "fig_architecture.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out_dir}/fig_architecture.png")
print("\nAll paper figures generated ✓")

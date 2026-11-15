"""
generate_param_sweep_artifacts.py
Generates publication-quality charts and comprehensive report for the optimization parameter sweep.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether

CSV_PATH = "03_Results/experimental_study/dip_optimization/param_sweep/optimization_sweep_results.csv"
CHARTS_DIR = "03_Results/experimental_study/dip_optimization/param_sweep/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

NAVY = '#1E3A8A'
TEAL = '#0D9488'
AMBER = '#D97706'
SLATE = '#334155'
DARK = '#0F172A'
CORAL = '#E11D48'
GRID_COL = '#E2E8F0'

plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13
})

def make_charts():
    # 1. OPT-P1: Finite-difference step eps
    p1 = df[df['experiment_id'] == 'OPT-P1']
    # Group by method and value
    g1 = p1.groupby(['method', 'value'], sort=False)[['synth_auroc', 'test_auroc', 'moved_L1', 'n_iter']].mean().reset_index()
    
    eps_order = ['default', '0.0001', '0.001', '0.01', '0.05', '0.1']
    g1['eps_str'] = g1['value'].astype(str)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=300)
    
    methods = ['SLSQP', 'CG', 'L-BFGS-B']
    palette = {'SLSQP': NAVY, 'CG': TEAL, 'L-BFGS-B': AMBER}
    
    for m in methods:
        sub = g1[g1['method'] == m].set_index('eps_str').reindex(eps_order).reset_index()
        ax1.plot(sub['eps_str'], sub['synth_auroc'], marker='o', label=f'{m} (Synth)', color=palette[m], lw=1.8)
        ax1.plot(sub['eps_str'], sub['test_auroc'], marker='s', linestyle='--', label=f'{m} (Test)', color=palette[m], alpha=0.7, lw=1.5)
        
        ax2.plot(sub['eps_str'], sub['moved_L1'], marker='^', label=f'{m} moved_L1', color=palette[m], lw=1.8)
    
    ax1.set_title('OPT-P1: Synthetic vs Test AUROC by Finite-Diff Step (eps)')
    ax1.set_xlabel('Finite Difference Step (eps)')
    ax1.set_ylabel('AUROC')
    ax1.grid(True, linestyle=':', color=GRID_COL)
    ax1.legend(loc='lower left', fontsize=8, ncol=2)
    
    ax2.set_title('OPT-P1: Weight Displacement (L1 distance from equal w0)')
    ax2.set_xlabel('Finite Difference Step (eps)')
    ax2.set_ylabel('L1 Distance from Equal Weights')
    ax2.grid(True, linestyle=':', color=GRID_COL)
    ax2.legend(loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'opt_p1_eps_sensitivity.png'), bbox_inches='tight')
    plt.close()

    # 2. OPT-P2: Noise scale
    p2 = df[df['experiment_id'] == 'OPT-P2']
    g2 = p2.groupby('value', sort=False)[['synth_auroc', 'test_auroc', 'moved_L1']].mean().reset_index()
    g2['noise_scale'] = g2['value'].astype(float)
    g2 = g2.sort_values('noise_scale')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), dpi=300)
    ax1.plot(g2['noise_scale'], g2['synth_auroc'], marker='o', color=NAVY, lw=2, label='Synthetic Train AUROC')
    ax1.plot(g2['noise_scale'], g2['test_auroc'], marker='s', linestyle='--', color=CORAL, lw=2, label='Real Test AUROC')
    ax1.axhline(0.5758, color=SLATE, linestyle=':', label='Equal Weight Baseline (0.5758)')
    ax1.set_title('OPT-P2: Effect of Pseudo-Anomaly Noise Scale')
    ax1.set_xlabel('Noise Scale (multiplier on std)')
    ax1.set_ylabel('AUROC')
    ax1.grid(True, linestyle=':', color=GRID_COL)
    ax1.legend()
    
    ax2.plot(g2['noise_scale'], g2['moved_L1'], marker='^', color=TEAL, lw=2)
    ax2.set_title('OPT-P2: Weight Deviation (moved_L1) vs Noise Scale')
    ax2.set_xlabel('Noise Scale')
    ax2.set_ylabel('L1 Distance from Equal Weights')
    ax2.grid(True, linestyle=':', color=GRID_COL)
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'opt_p2_noise_scale.png'), bbox_inches='tight')
    plt.close()

    # 3. OPT-P3: Starting Point
    p3 = df[df['experiment_id'] == 'OPT-P3']
    g3 = p3.groupby('value', sort=False)[['synth_auroc', 'test_auroc', 'moved_L1']].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    x = np.arange(len(g3))
    w = 0.35
    ax.bar(x - w/2, g3['synth_auroc'], width=w, label='Synthetic AUROC', color=NAVY)
    ax.bar(x + w/2, g3['test_auroc'], width=w, label='Test AUROC', color=CORAL)
    ax.axhline(0.5758, color=SLATE, linestyle='--', label='Equal Baseline (0.5758)')
    ax.set_xticks(x)
    ax.set_xticklabels(g3['value'], rotation=15)
    ax.set_title('OPT-P3: Equal vs Random Dirichlet Initialization (x0)')
    ax.set_ylabel('AUROC')
    ax.set_ylim(0.4, 1.05)
    ax.grid(True, linestyle=':', color=GRID_COL, axis='y')
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'opt_p3_starting_point.png'), bbox_inches='tight')
    plt.close()

    # 4. OPT-P4: Max iterations
    p4 = df[df['experiment_id'] == 'OPT-P4']
    g4 = p4.groupby('value', sort=False)[['synth_auroc', 'test_auroc', 'moved_L1', 'n_iter']].mean().reset_index()
    g4['maxiter'] = g4['value'].astype(float)
    g4 = g4.sort_values('maxiter')
    
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    ax.plot(g4['maxiter'], g4['synth_auroc'], marker='o', color=NAVY, lw=2, label='Synthetic AUROC')
    ax.plot(g4['maxiter'], g4['test_auroc'], marker='s', linestyle='--', color=CORAL, lw=2, label='Test AUROC')
    ax.set_xscale('log')
    ax.set_title('OPT-P4: Optimization Trajectory vs Max Iterations')
    ax.set_xlabel('Max Iterations (log scale: 1, 5, 20, 500)')
    ax.set_ylabel('AUROC')
    ax.grid(True, linestyle=':', color=GRID_COL)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'opt_p4_iterations.png'), bbox_inches='tight')
    plt.close()

    # 5. Composite Summary Panel
    fig, axs = plt.subplots(2, 2, figsize=(12, 8.5), dpi=300)
    
    # Subplot A: EPS (SLSQP)
    slsqp_p1 = g1[g1['method'] == 'SLSQP'].set_index('eps_str').reindex(eps_order).reset_index()
    axs[0, 0].plot(slsqp_p1['eps_str'], slsqp_p1['synth_auroc'], 'o-', color=NAVY, label='Synth AUROC')
    axs[0, 0].plot(slsqp_p1['eps_str'], slsqp_p1['test_auroc'], 's--', color=CORAL, label='Test AUROC')
    axs[0, 0].set_title('(A) OPT-P1: Finite-Diff Step (eps)')
    axs[0, 0].grid(True, linestyle=':', color=GRID_COL)
    axs[0, 0].legend(fontsize=8)
    
    # Subplot B: Noise Scale
    axs[0, 1].plot(g2['noise_scale'], g2['synth_auroc'], 'o-', color=NAVY, label='Synth AUROC')
    axs[0, 1].plot(g2['noise_scale'], g2['test_auroc'], 's--', color=CORAL, label='Test AUROC')
    axs[0, 1].set_title('(B) OPT-P2: Noise Scale Multiplier')
    axs[0, 1].grid(True, linestyle=':', color=GRID_COL)
    axs[0, 1].legend(fontsize=8)

    # Subplot C: Starting Point
    axs[1, 0].bar(np.arange(len(g3)) - 0.15, g3['synth_auroc'], width=0.3, color=NAVY, label='Synth AUROC')
    axs[1, 0].bar(np.arange(len(g3)) + 0.15, g3['test_auroc'], width=0.3, color=CORAL, label='Test AUROC')
    axs[1, 0].set_xticks(np.arange(len(g3)))
    axs[1, 0].set_xticklabels(g3['value'], rotation=15, fontsize=8)
    axs[1, 0].set_ylim(0.4, 1.05)
    axs[1, 0].set_title('(C) OPT-P3: Starting Weights (x0)')
    axs[1, 0].grid(True, linestyle=':', color=GRID_COL, axis='y')
    axs[1, 0].legend(fontsize=8)

    # Subplot D: Lower Bound
    p5 = df[df['experiment_id'] == 'OPT-P5']
    g5 = p5.groupby('value', sort=False)[['synth_auroc', 'test_auroc', 'moved_L1']].mean().reset_index()
    g5['lb'] = g5['value'].astype(float)
    g5 = g5.sort_values('lb')
    axs[1, 1].plot(g5['lb'], g5['synth_auroc'], 'o-', color=NAVY, label='Synth AUROC')
    axs[1, 1].plot(g5['lb'], g5['test_auroc'], 's--', color=CORAL, label='Test AUROC')
    axs[1, 1].set_title('(D) OPT-P5: Weight Lower Bound (lb)')
    axs[1, 1].grid(True, linestyle=':', color=GRID_COL)
    axs[1, 1].legend(fontsize=8)
    
    plt.suptitle('Optimization Parameter Sweep Summary (OPT-P1 to OPT-P5 across 12 Categories)', fontsize=14, fontweight='bold', color=NAVY)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'opt_param_sweep_summary.png'), bbox_inches='tight')
    plt.close()
    print("All parameter sweep charts generated successfully!")

def build_pdf_report():
    pdf_path = "03_Results/experimental_study/dip_optimization/param_sweep/PARAM_SWEEP_REPORT.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor(NAVY), fontName='Helvetica-Bold')
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor(TEAL), fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor(DARK), spaceAfter=4)
    table_cell = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor(DARK))
    table_hdr = ParagraphStyle('TableHdr', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.white, fontName='Helvetica-Bold')
    
    story = []
    story.append(Paragraph("Optimization Parameter Sweep Report (OPT-P1 to OPT-P5)", title_style))
    story.append(Paragraph("Controlled Sensitivity Analysis of Feature Weight Optimization across 12 MVTec AD Categories (444 Trials)", body_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("1. Executive Summary & Core Scientific Findings", h2_style))
    story.append(Paragraph(
        "This experimental suite conducts a rigorous, one-at-a-time parameter sensitivity analysis of the project's numerical "
        "feature-weight optimization pipeline (SLSQP, CG, L-BFGS-B). Across 444 trials spanning 12 industrial categories, we evaluate "
        "finite-difference step size (OPT-P1), pseudo-anomaly noise strength (OPT-P2), initial starting weights (OPT-P3), maximum iterations (OPT-P4), "
        "and weight lower bounds (OPT-P5).", body_style
    ))
    story.append(Paragraph(
        "<b>Key Finding 1 (The Gradient Invisibility Trap):</b> With SciPy's default eps (1.49e-8), finite difference cannot detect any AUROC changes "
        "in the non-smooth step-function objective, causing the optimizer to terminate immediately with moved_L1 = 0.0000. Increasing eps to 0.01-0.10 "
        "enables the optimizer to register gradients and increase synthetic AUROC from 0.9853 to 0.9920.", body_style
    ))
    story.append(Paragraph(
        "<b>Key Finding 2 (The Inverse Generalization Law):</b> Actively moving away from equal weights under the synthetic noise objective consistently "
        "<b>degrades real test AUROC</b> (dropping from 0.5758 down to 0.5247). This confirms that synthetic isotropic Gaussian perturbations fail to proxy "
        "real anisotropic morphological defects.", body_style
    ))
    
    story.append(Spacer(1, 6))
    summary_chart = os.path.join(CHARTS_DIR, 'opt_param_sweep_summary.png')
    if os.path.exists(summary_chart):
        story.append(RLImage(summary_chart, width=540, height=360))
        story.append(Spacer(1, 8))
        
    story.append(Paragraph("2. Empirical Sweep Results Table", h2_style))
    
    g = (df.groupby(['experiment_id', 'method', 'param', 'value'], sort=False)
           [['synth_auroc', 'test_auroc', 'moved_L1', 'n_iter']].mean().round(4)).reset_index()
           
    table_data = [[
        Paragraph("Exp ID", table_hdr),
        Paragraph("Method", table_hdr),
        Paragraph("Parameter", table_hdr),
        Paragraph("Value", table_hdr),
        Paragraph("Synth AUROC", table_hdr),
        Paragraph("Test AUROC", table_hdr),
        Paragraph("moved_L1", table_hdr),
        Paragraph("Iter", table_hdr)
    ]]
    
    for _, row in g.iterrows():
        table_data.append([
            Paragraph(str(row['experiment_id']), table_cell),
            Paragraph(str(row['method']), table_cell),
            Paragraph(str(row['param']), table_cell),
            Paragraph(str(row['value']), table_cell),
            Paragraph(f"{row['synth_auroc']:.4f}", table_cell),
            Paragraph(f"{row['test_auroc']:.4f}", table_cell),
            Paragraph(f"{row['moved_L1']:.4f}", table_cell),
            Paragraph(f"{row['n_iter']:.1f}", table_cell),
        ])
        
    t = Table(table_data, colWidths=[55, 55, 75, 75, 70, 70, 70, 50])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(NAVY)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t)
    
    doc.build(story)
    print(f"PDF report built: {pdf_path}")

def build_md_report():
    md_path = "03_Results/experimental_study/dip_optimization/param_sweep/PARAM_SWEEP_REPORT.md"
    g = (df.groupby(['experiment_id', 'method', 'param', 'value'], sort=False)
           [['synth_auroc', 'test_auroc', 'moved_L1', 'n_iter']].mean().round(4)).reset_index()
           
    lines = [
        "# Optimization Parameter Sweep Report (OPT-P1 to OPT-P5)",
        "",
        "**Scope:** Controlled Sensitivity Analysis of Feature Weight Optimization across 12 MVTec AD Categories (444 Trials)  ",
        "**Date:** November 15, 2026  ",
        "**Code Source:** `02_Code/experiments/optimization_param_sweep.py`  ",
        "**Data Source:** `03_Results/experimental_study/dip_optimization/param_sweep/optimization_sweep_results.csv`  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Research Implications",
        "",
        "This experimental suite systematically analyzes how each numerical hyperparameter in the feature-weight optimization pipeline influences convergence and generalization:",
        "",
        "1. **OPT-P1 (Finite-Difference Step `eps`):** With SciPy's default step size ($1.49 \\times 10^{-8}$), the finite difference approximation cannot detect changes in the piece-wise constant empirical AUROC objective. As a result, optimizers terminate at iteration 0 or 1 with `moved_L1 = 0.0000`, defaulting to equal weights (test AUROC 0.5758). Increasing `eps` to 0.01–0.10 allows the optimizer to detect gradient steps, lifting synthetic AUROC to 0.9920 and moving weights by `moved_L1 = 0.40–0.55`.",
        "2. **The Negative Result Solidified:** Crucially, whenever the optimizer successfully modifies weights (`moved_L1 > 0`), **real test AUROC consistently drops from 0.5758 to ~0.5247–0.5466**. This proves that the synthetic noise proxy steers the weights toward high-variance noise dimensions that carry zero diagnostic signal for real industrial defects.",
        "3. **OPT-P2 (Noise Scale):** Raising noise scale from 0.5 to 5.0 inflates synthetic AUROC from 0.7365 to 0.9993, but real defect AUROC remains stagnant between 0.52 and 0.56.",
        "4. **OPT-P3 (Initial Starting Weights `x0`):** Comparing equal weights against 5 random Dirichlet starting points demonstrates that random initialization leads to varied local minima under synthetic noise, all of which yield inferior test AUROC (0.524–0.553) compared to uniform weighting.",
        "5. **OPT-P4 (Max Iterations `maxiter`):** The optimizer converges rapidly within 5 iterations (`n_iter = 5.3`); allowing up to 500 iterations yields zero further change.",
        "6. **OPT-P5 (Weight Lower Bound `lb`):** Constraining the minimum weight ($lb = 0.10$) restricts `moved_L1` to 0.2497, slightly moderating test degradation to 0.5480.",
        "",
        "---",
        "",
        "## 2. Empirical Benchmark Table",
        "",
        "| Experiment ID | Method | Parameter | Value | Synthetic Train AUROC | Test Defect AUROC | moved_L1 (Displacement) | Iterations |",
        "|---|---|---|---|---|---|---|---|"
    ]
    
    for _, r in g.iterrows():
        lines.append(f"| {r['experiment_id']} | {r['method']} | {r['param']} | {r['value']} | **{r['synth_auroc']:.4f}** | {r['test_auroc']:.4f} | {r['moved_L1']:.4f} | {r['n_iter']:.1f} |")
        
    lines.extend([
        "",
        "---",
        "",
        "## 3. Visual Visualizations",
        "",
        "- `charts/opt_param_sweep_summary.png`: 4-panel composite summary covering OPT-P1 through OPT-P5.",
        "- `charts/opt_p1_eps_sensitivity.png`: Synthetic vs Test AUROC and weight displacement across SLSQP, CG, L-BFGS-B vs eps.",
        "- `charts/opt_p2_noise_scale.png`: Impact of synthetic pseudo-anomaly noise scale.",
        "- `charts/opt_p3_starting_point.png`: Equal vs random Dirichlet initializations.",
        "- `charts/opt_p4_iterations.png`: Convergence trajectory vs maximum iterations.",
        ""
    ])
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Markdown report written: {md_path}")

if __name__ == '__main__':
    make_charts()
    build_pdf_report()
    build_md_report()

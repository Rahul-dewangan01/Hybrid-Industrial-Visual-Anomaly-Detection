"""
Script: generate_architecture_figures.py
Generates Figures 1 to 7 for the research paper and presentation with 300 DPI publication quality.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('06_FINAL_RESEARCH/Figures/Architecture', exist_ok=True)
os.makedirs('06_FINAL_RESEARCH/Figures/Methodology', exist_ok=True)

# Common styling
NAVY = '#1E3A8A'
TEAL = '#0D9488'
AMBER = '#D97706'
SLATE = '#334155'
LIGHT_BG = '#F1F5F9'
BORDER_COL = '#94A3B8'
WHITE = '#FFFFFF'
PURPLE = '#7C3AED'
CORAL = '#E11D48'

def draw_box(ax, x, y, w, h, text, title='', bg_col=WHITE, border_col=SLATE, text_col=SLATE, title_col=NAVY, lw=1.5, fontsize=9):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
                                  facecolor=bg_col, edgecolor=border_col, linewidth=lw, zorder=2)
    ax.add_patch(rect)
    if title:
        ax.text(x + w/2, y + h - 0.18, title, ha='center', va='center', fontsize=fontsize+1, fontweight='bold', color=title_col, zorder=3)
        ax.text(x + w/2, y + (h - 0.22)/2, text, ha='center', va='center', fontsize=fontsize, color=text_col, zorder=3, multialignment='center')
    else:
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, color=text_col, zorder=3, multialignment='center')

def draw_arrow(ax, x1, y1, x2, y2, label='', color=SLATE, lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=5, shrinkB=5, mutation_scale=15), zorder=4)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.08, label, ha='center', va='center', fontsize=8, color=color, fontweight='semibold')

# -------------------------------------------------------------
# Figure 1: Overall Proposed System Architecture
# -------------------------------------------------------------
def make_fig1():
    fig, ax = plt.subplots(figsize=(12, 4.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    # Title
    ax.text(6, 4.7, 'Figure 1: Overall Proposed Industrial Anomaly Detection System Architecture', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    # Stages
    draw_box(ax, 0.5, 2.0, 1.6, 1.8, 'MVTec AD Dataset\n12 Categories\n(Normal Train,\nDefect/Good Test)', '1. Data Input', LIGHT_BG, NAVY, SLATE)
    draw_arrow(ax, 2.1, 2.9, 2.7, 2.9)
    
    draw_box(ax, 2.7, 2.0, 1.8, 1.8, 'Resolution 256x256\nCLAHE Enhancement\nGaussian Denoising\nReference Synthesis', '2. Preprocessing', LIGHT_BG, TEAL, SLATE)
    draw_arrow(ax, 4.5, 2.9, 5.1, 2.9)
    
    # Branching into DIP and DL
    draw_box(ax, 5.1, 2.9, 2.2, 1.4, '11 Texture/Shape/Diff\nScipy SLSQP/CG/BFGS\nMahalanobis Distance', '3A. DIP & ACOMA', '#FEF3C7', AMBER, SLATE)
    draw_box(ax, 5.1, 1.2, 2.2, 1.4, 'Conv-AE (MSE+SSIM)\nPatchCore (Coreset)\nPaDiM (Patch Gaussian)', '3B. Deep Learning', '#EDE9FE', PURPLE, SLATE)
    
    draw_arrow(ax, 7.3, 3.6, 7.9, 2.9)
    draw_arrow(ax, 7.3, 1.9, 7.9, 2.9)
    
    draw_box(ax, 7.9, 2.0, 1.8, 1.8, 'Min-Max Normalization\nScore Fusion:\nMean, Max, Weighted\nDL-Heavy (HY-03)', '4. Hybrid Fusion', LIGHT_BG, CORAL, SLATE)
    draw_arrow(ax, 9.7, 2.9, 10.3, 2.9)
    
    draw_box(ax, 10.3, 2.0, 1.4, 1.8, 'Image AUROC\nPixel AUROC\nF1-Score / Latency\nNetwork Q95/Q75', '5. Evaluation', LIGHT_BG, NAVY, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Architecture/fig1_overall_system_architecture.png', bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------
# Figure 2: Dataset Organization and Experimental Workflow
# -------------------------------------------------------------
def make_fig2():
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    ax.text(5.5, 4.7, 'Figure 2: Dataset Organization and Zero-Leakage Experimental Workflow', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    draw_box(ax, 0.5, 2.2, 2.2, 1.8, '12 MVTec AD Classes\n(bottle, cable, capsule,\ncarpet, grid, hazelnut,\nleather, metal_nut, etc.)', 'Industrial Categories', LIGHT_BG, NAVY, SLATE)
    draw_arrow(ax, 2.7, 3.1, 3.4, 3.8, 'Normal Only')
    draw_arrow(ax, 2.7, 3.1, 3.4, 2.0, 'Defects + Normal')
    
    draw_box(ax, 3.4, 3.0, 2.5, 1.6, 'Train Set (Good Only)\nFit Normal Statistics\nBuild Memory Bank / Fit Gauss', 'Training Split', '#DCFCE7', TEAL, SLATE)
    draw_box(ax, 3.4, 1.1, 2.5, 1.6, 'Test Set (Good & Defect)\nGround Truth Masks\nNo Leakage into Fit/Weights', 'Evaluation Split', '#FEE2E2', CORAL, SLATE)
    
    draw_arrow(ax, 5.9, 3.8, 6.7, 3.1)
    draw_arrow(ax, 5.9, 1.9, 6.7, 3.1)
    
    draw_box(ax, 6.7, 2.0, 2.0, 2.0, 'One-Class Model Fitting\nFrozen Feature Extractor\nThreshold via Normal 95th\nSynthetic Noise Validation', 'Zero-Leakage Protocol', LIGHT_BG, PURPLE, SLATE)
    draw_arrow(ax, 8.7, 3.0, 9.3, 3.0)
    
    draw_box(ax, 9.3, 2.0, 1.4, 2.0, '292 Experiments\nMetrics: AUROC,\nPixel AUROC, F1,\nLatency, FPS', 'Validated Runs', LIGHT_BG, NAVY, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Methodology/fig2_dataset_workflow.png', bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------
# Figure 3: Digital Image Processing Pipeline
# -------------------------------------------------------------
def make_fig3():
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    
    ax.text(5.5, 4.2, 'Figure 3: Digital Image Processing & Feature Extraction Pipeline', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    draw_box(ax, 0.4, 1.5, 1.8, 2.2, 'Test Image & Reference\nCLAHE Enhancement\nGaussian Smoothing\nDiff Image: |I - R|', 'Preprocessing', LIGHT_BG, TEAL, SLATE)
    draw_arrow(ax, 2.2, 2.6, 2.8, 2.6)
    
    draw_box(ax, 2.8, 1.5, 2.5, 2.2, '1. Mean Abs Diff (MAD)\n2. SSIM Structural Sim\n3. LBP Texture Hist χ²\n4. Hu Moments (1-7)\n5. Contour Count & Area\n6. High-Pass Gradient Energy', '11 Feature Vectors', '#FEF3C7', AMBER, SLATE)
    draw_arrow(ax, 5.3, 2.6, 5.9, 2.6)
    
    draw_box(ax, 5.9, 1.5, 2.4, 2.2, 'SLSQP, CG, L-BFGS-B\nObjective: Max Separability\nConstraint: Σ w_i = 1, w_i >= 0\nSynthetic Noise Regularizer', 'Weight Optimization', '#EDE9FE', PURPLE, SLATE)
    draw_arrow(ax, 8.3, 2.6, 8.9, 2.6)
    
    draw_box(ax, 8.9, 1.5, 1.8, 2.2, 'D_M = sqrt((f-μ)^T Σ^-1 (f-μ))\nEqual-Weight Baseline\nFast CPU: 38.5 FPS\nDeterministic Scoring', 'Anomaly Scoring', LIGHT_BG, NAVY, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Methodology/fig3_dip_pipeline.png', bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------
# Figure 4: Autoencoder Architecture
# -------------------------------------------------------------
def make_fig4():
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    
    ax.text(5.5, 4.2, 'Figure 4: Convolutional Autoencoder Architecture with Dual MSE+SSIM Loss', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    draw_box(ax, 0.4, 1.4, 1.8, 2.2, 'Input (3 x 256 x 256)\nConv2D + BatchNorm + ReLU\nDownsampling (Stride 2)\nChannels: 32 -> 64 -> 128', 'Encoder (5-Layer)', LIGHT_BG, TEAL, SLATE)
    draw_arrow(ax, 2.2, 2.5, 2.8, 2.5)
    
    draw_box(ax, 2.8, 1.7, 1.6, 1.6, 'Latent Bottleneck\nDim = 64\n(Prevents Identity\nReconstruction)', 'Bottleneck', '#FEF3C7', AMBER, SLATE)
    draw_arrow(ax, 4.4, 2.5, 5.0, 2.5)
    
    draw_box(ax, 5.0, 1.4, 1.8, 2.2, 'ConvTranspose2D + ReLU\nUpsampling (Stride 2)\nChannels: 128 -> 64 -> 32\nOutput: 3 x 256 x 256', 'Decoder', LIGHT_BG, PURPLE, SLATE)
    draw_arrow(ax, 6.8, 2.5, 7.4, 2.5)
    
    draw_box(ax, 7.4, 1.4, 1.6, 2.2, 'L = MSE(I, I_rec)\n  + λ (1 - SSIM(I, I_rec))\nCaptures fine textures\n& structural defects', 'Dual Loss (AE-04)', '#DCFCE7', TEAL, SLATE)
    draw_arrow(ax, 9.0, 2.5, 9.4, 2.5)
    
    draw_box(ax, 9.4, 1.4, 1.3, 2.2, 'Residual Map\nPixel AUROC 0.805\n100% Precision\nat calibrated τ', 'Anomaly Map', LIGHT_BG, CORAL, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Architecture/fig4_autoencoder_architecture.png', bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------
# Figure 5: PatchCore Architecture
# -------------------------------------------------------------
def make_fig5():
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    
    ax.text(5.5, 4.2, 'Figure 5: PatchCore Architecture with Coreset Memory Bank Subsampling', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    draw_box(ax, 0.4, 1.4, 1.8, 2.2, 'Input (256 x 256)\nResNet-50 / 34 / 18\nExtract Layer2 & Layer3\nMid-level features', 'Backbone Extractor', LIGHT_BG, TEAL, SLATE)
    draw_arrow(ax, 2.2, 2.5, 2.8, 2.5)
    
    draw_box(ax, 2.8, 1.4, 2.0, 2.2, 'Locally Aware Patches\nAdaptive Avg Pooling\nAggregated Features\nFull Memory M (100%)', 'Patch Embedding', LIGHT_BG, PURPLE, SLATE)
    draw_arrow(ax, 4.8, 2.5, 5.4, 2.5)
    
    draw_box(ax, 5.4, 1.4, 2.2, 2.2, 'Greedy k-Center Search\n1% to 10% Subsampling\nReduces memory 90-99%\nPreserves coverage bound', 'Coreset Reduction', '#FEF3C7', AMBER, SLATE)
    draw_arrow(ax, 7.6, 2.5, 8.2, 2.5)
    
    draw_box(ax, 8.2, 1.4, 2.4, 2.2, 'k-NN Distance to Coreset\nSoftmax Reweighting\nImage AUROC: 0.9837 (RN50)\nPixel AUROC: 0.9680', 'Nearest-Neighbor Score', '#DCFCE7', CORAL, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Architecture/fig5_patchcore_architecture.png', bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------
# Figure 6: PaDiM Architecture
# -------------------------------------------------------------
def make_fig6():
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    
    ax.text(5.5, 4.2, 'Figure 6: PaDiM Architecture: Spatial Patch Distribution Modeling', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    draw_box(ax, 0.4, 1.4, 2.0, 2.2, 'Pretrained CNN\nResNet-18 Layers 1, 2, 3\nConcatenate embeddings\nat each spatial grid (i, j)', 'Feature Extraction', LIGHT_BG, TEAL, SLATE)
    draw_arrow(ax, 2.4, 2.5, 3.0, 2.5)
    
    draw_box(ax, 3.0, 1.4, 2.2, 2.2, 'Random Dimension Red.\nSelect d = 100 or 200 dims\nRetains inter-layer correlation\nEfficient computation', 'Dimensionality Reduction', '#EDE9FE', PURPLE, SLATE)
    draw_arrow(ax, 5.2, 2.5, 5.8, 2.5)
    
    draw_box(ax, 5.8, 1.4, 2.2, 2.2, 'Fit Gaussian N(μ_ij, Σ_ij)\nFor each grid position (i, j)\nRegularized Covariance:\nΣ_ij + ϵ I (ϵ = 1e-4..1e-2)', 'Gaussian Modeling', '#FEF3C7', AMBER, SLATE)
    draw_arrow(ax, 8.0, 2.5, 8.6, 2.5)
    
    draw_box(ax, 8.6, 1.4, 2.0, 2.2, 'Mahalanobis Dist Map\nGaussian Smoothing\nPixel AUROC: 0.9515\nImage AUROC: 0.9654', 'Anomaly Localization', '#DCFCE7', CORAL, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Architecture/fig6_padim_architecture.png', bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------
# Figure 7: Hybrid Anomaly Detection Architecture
# -------------------------------------------------------------
def make_fig7():
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    ax.text(5.5, 4.7, 'Figure 7: Multi-Paradigm Hybrid Score Fusion Framework', 
            ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY)
    
    # 4 Input Models
    draw_box(ax, 0.4, 3.5, 2.2, 0.9, 'PatchCore (w = 0.40)', 'DL Patch (PC)', LIGHT_BG, TEAL, SLATE, fontsize=8)
    draw_box(ax, 0.4, 2.4, 2.2, 0.9, 'PaDiM (w = 0.40)', 'DL Gaussian (PaDiM)', LIGHT_BG, PURPLE, SLATE, fontsize=8)
    draw_box(ax, 0.4, 1.3, 2.2, 0.9, 'Autoencoder (w = 0.10)', 'Reconstruction (AE)', LIGHT_BG, AMBER, SLATE, fontsize=8)
    draw_box(ax, 0.4, 0.2, 2.2, 0.9, 'DIP Mahalanobis (w = 0.10)', 'Classical DIP', LIGHT_BG, SLATE, SLATE, fontsize=8)
    
    draw_arrow(ax, 2.6, 3.95, 3.4, 2.5)
    draw_arrow(ax, 2.6, 2.85, 3.4, 2.5)
    draw_arrow(ax, 2.6, 1.75, 3.4, 2.5)
    draw_arrow(ax, 2.6, 0.65, 3.4, 2.5)
    
    draw_box(ax, 3.4, 1.4, 2.2, 2.2, 'Min-Max Normalization\ns_norm = (s - μ) / σ\nZero-Leakage bounds\nfrom normal validation', 'Score Normalization', '#FEF3C7', AMBER, SLATE)
    draw_arrow(ax, 5.6, 2.5, 6.4, 2.5)
    
    draw_box(ax, 6.4, 1.4, 2.2, 2.2, 'Fusion Strategies:\n- HY-01: Equal Mean\n- HY-02: Extreme Max\n- HY-03: DL-Heavy (Top F1)\n- HY-04: Balanced w\n- HY-05: Top-2 Deep', 'Fusion Engine', '#EDE9FE', PURPLE, SLATE)
    draw_arrow(ax, 8.6, 2.5, 9.4, 2.5)
    
    draw_box(ax, 9.4, 1.4, 1.4, 2.2, 'Hybrid Score S\nF1: 0.8876\nAUROC: 0.9765\nEnhanced Robustness', 'Final Decision', '#DCFCE7', CORAL, SLATE)
    
    plt.tight_layout()
    plt.savefig('06_FINAL_RESEARCH/Figures/Architecture/fig7_hybrid_architecture.png', bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    print("Generating Figure 1...")
    make_fig1()
    print("Generating Figure 2...")
    make_fig2()
    print("Generating Figure 3...")
    make_fig3()
    print("Generating Figure 4...")
    make_fig4()
    print("Generating Figure 5...")
    make_fig5()
    print("Generating Figure 6...")
    make_fig6()
    print("Generating Figure 7...")
    make_fig7()
    print("All architecture and methodology figures generated successfully!")

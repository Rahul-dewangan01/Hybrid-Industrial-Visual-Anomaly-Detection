"""
generate_new_figures.py
Generates the 3 new figures required for the restructured 12-slide presentation:
  1. slide06_model_architecture.png  — Combined AE + PatchCore + PaDiM + Hybrid fusion architecture diagram
  2. slide07_dataset_samples.png     — MVTec AD categories overview with normal vs defective + GT masks
  3. slide11_ablation.png            — AE loss ablation + AE architecture depth ablation bar charts
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import pandas as pd

# Try to load images for dataset samples
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

OUTPUT_DIR = os.path.abspath('06_FINAL_RESEARCH/Presentation/PPT_Figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATASET_DIR = os.path.abspath('01_Dataset/MVTec_AD')
TABLES_DIR = os.path.abspath('06_FINAL_RESEARCH/Research_Paper/Research_Tables')

# Color palette
NAVY = '#0F172A'
BLUE_600 = '#2563EB'
BLUE_100 = '#DBEAFE'
TEAL_600 = '#0D9488'
TEAL_100 = '#CCFBF1'
AMBER_600 = '#D97706'
AMBER_100 = '#FEF3C7'
PURPLE_600 = '#7C3AED'
PURPLE_100 = '#EDE9FE'
CORAL_600 = '#E11D48'
SLATE_50 = '#F8FAFC'
SLATE_200 = '#E2E8F0'
SLATE_500 = '#64748B'
SLATE_700 = '#334155'
SLATE_900 = '#0F172A'
WHITE = '#FFFFFF'


def generate_model_architecture():
    """Generate slide06_model_architecture.png — Combined architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 9), dpi=150)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(SLATE_50)

    def draw_box(x, y, w, h, color, label, fontsize=9, text_color='white', alpha=1.0):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='none', alpha=alpha, zorder=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=3,
                wrap=True)

    def draw_arrow(x1, y1, x2, y2, color=SLATE_500):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5), zorder=1)

    # Title
    ax.text(8, 8.5, 'Multi-Paradigm Anomaly Detection Architecture', ha='center', va='center',
            fontsize=16, fontweight='bold', color=SLATE_900)
    ax.text(8, 8.1, 'ConvAE (Reconstruction) + PatchCore (Memory Bank) + PaDiM (Gaussian) → Hybrid Fusion',
            ha='center', va='center', fontsize=10, color=SLATE_500)

    # Input
    draw_box(0.3, 4.8, 2.0, 1.2, SLATE_700, 'Input Image\n(256×256×3)', 9, WHITE)

    # Preprocessing
    draw_box(3.0, 4.8, 2.0, 1.2, SLATE_500, 'Preprocessing\nResize, Normalize\nImageNet Stats', 8, WHITE)
    draw_arrow(2.3, 5.4, 3.0, 5.4)

    # Three parallel branches
    # Branch 1: ConvAE (top)
    draw_box(5.8, 7.0, 2.4, 1.0, BLUE_600, 'Conv Autoencoder\n5-Level Encoder/Decoder', 8, WHITE)
    draw_box(8.8, 7.0, 2.0, 1.0, '#3B82F6', 'Reconstruction\nError Map', 8, WHITE)
    draw_arrow(5.0, 5.8, 5.8, 7.5, BLUE_600)
    draw_arrow(8.2, 7.5, 8.8, 7.5, BLUE_600)

    # Branch 2: PatchCore (middle)
    draw_box(5.8, 4.8, 2.4, 1.2, NAVY, 'PatchCore\nResNet-18 Backbone\n5% Coreset', 8, WHITE)
    draw_box(8.8, 4.8, 2.0, 1.2, '#1E3A5F', 'k-NN Distance\nAnomaly Score', 8, WHITE)
    draw_arrow(5.0, 5.4, 5.8, 5.4, NAVY)
    draw_arrow(8.2, 5.4, 8.8, 5.4, NAVY)

    # Branch 3: PaDiM (bottom)
    draw_box(5.8, 2.6, 2.4, 1.0, TEAL_600, 'PaDiM\nResNet-18 + 100d\nGaussian Modeling', 8, WHITE)
    draw_box(8.8, 2.6, 2.0, 1.0, '#0F766E', 'Mahalanobis\nDistance Map', 8, WHITE)
    draw_arrow(5.0, 5.0, 5.8, 3.1, TEAL_600)
    draw_arrow(8.2, 3.1, 8.8, 3.1, TEAL_600)

    # Min-Max Normalization
    draw_box(11.5, 4.5, 1.6, 1.8, AMBER_600, 'Min-Max\nScore\nNormalization', 9, WHITE)
    draw_arrow(10.8, 7.5, 11.5, 5.8, AMBER_600)
    draw_arrow(10.8, 5.4, 11.5, 5.4, AMBER_600)
    draw_arrow(10.8, 3.1, 11.5, 5.0, AMBER_600)

    # Hybrid Fusion
    draw_box(13.6, 4.5, 2.0, 1.8, PURPLE_600, 'Hybrid Fusion\nMean (HY-01)\nMax (HY-02)\nWeighted (HY-03)\n0.2/0.4/0.4', 7.5, WHITE)
    draw_arrow(13.1, 5.4, 13.6, 5.4, PURPLE_600)

    # Output
    draw_box(13.6, 2.0, 2.0, 1.2, CORAL_600, 'Final Decision\nAnomaly / Normal\n+ Heatmap', 8, WHITE)
    draw_arrow(14.6, 4.5, 14.6, 3.2, CORAL_600)

    # Legend boxes
    legend_items = [
        (BLUE_600, 'ConvAE (Reconstruction)'),
        (NAVY, 'PatchCore (Memory Bank)'),
        (TEAL_600, 'PaDiM (Gaussian)'),
        (PURPLE_600, 'Hybrid Fusion'),
    ]
    for i, (color, label) in enumerate(legend_items):
        y_pos = 1.5 - i * 0.35
        rect = FancyBboxPatch((0.3, y_pos - 0.1), 0.4, 0.25,
                              boxstyle="round,pad=0.02", facecolor=color, edgecolor='none')
        ax.add_patch(rect)
        ax.text(0.9, y_pos + 0.02, label, va='center', fontsize=8, color=SLATE_700)

    # Training data note
    ax.text(0.3, 0.3, 'Training: Normal-only images (no defect exposure)',
            fontsize=8, color=SLATE_500, style='italic')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'slide06_model_architecture.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=SLATE_50)
    plt.close()
    print(f"Saved: {out_path}")


def generate_dataset_samples():
    """Generate slide07_dataset_samples.png — MVTec AD categories with sample images."""
    # Categories we used (12)
    categories = ['bottle', 'cable', 'capsule', 'carpet', 'grid', 'hazelnut',
                  'leather', 'metal_nut', 'screw', 'tile', 'toothbrush', 'transistor']

    if HAS_CV2:
        # Try to load actual sample images
        fig, axes = plt.subplots(3, 8, figsize=(16, 7), dpi=150)
        fig.patch.set_facecolor(SLATE_50)

        # Row 0: Normal samples from first 8 categories
        # Row 1: Normal samples from last 4 categories + defective from first 4
        # Row 2: Defective + GT masks

        # Simpler: 2 rows x 12 columns (normal + defective per category)
        plt.close()
        fig, axes = plt.subplots(2, 12, figsize=(18, 4), dpi=150)
        fig.patch.set_facecolor(SLATE_50)

        for i, cat in enumerate(categories):
            # Normal image
            train_dir = os.path.join(DATASET_DIR, cat, 'train', 'good')
            if os.path.exists(train_dir):
                imgs = sorted([f for f in os.listdir(train_dir) if f.endswith('.png')])
                if imgs:
                    img = cv2.imread(os.path.join(train_dir, imgs[0]))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, (128, 128))
                        axes[0, i].imshow(img)
            axes[0, i].set_title(cat, fontsize=6, fontweight='bold', color=SLATE_700)
            axes[0, i].axis('off')
            if i == 0:
                axes[0, i].set_ylabel('Normal', fontsize=8, fontweight='bold', color='green', rotation=90, labelpad=10)

            # Defective image
            test_dir = os.path.join(DATASET_DIR, cat, 'test')
            if os.path.exists(test_dir):
                defect_dirs = [d for d in os.listdir(test_dir) if d != 'good' and os.path.isdir(os.path.join(test_dir, d))]
                if defect_dirs:
                    defect_dir = os.path.join(test_dir, defect_dirs[0])
                    imgs_d = sorted([f for f in os.listdir(defect_dir) if f.endswith('.png')])
                    if imgs_d:
                        img_d = cv2.imread(os.path.join(defect_dir, imgs_d[0]))
                        if img_d is not None:
                            img_d = cv2.cvtColor(img_d, cv2.COLOR_BGR2RGB)
                            img_d = cv2.resize(img_d, (128, 128))
                            axes[1, i].imshow(img_d)
            axes[1, i].axis('off')
            if i == 0:
                axes[1, i].set_ylabel('Defective', fontsize=8, fontweight='bold', color='red', rotation=90, labelpad=10)

        fig.suptitle('MVTec AD Dataset: 12 Evaluated Categories — Normal vs. Defective Samples',
                     fontsize=12, fontweight='bold', color=SLATE_900, y=1.02)

        # Add dataset stats text below
        fig.text(0.5, -0.04,
                 '12 Categories  |  5,354 Total Images  |  1,389 Training (Normal-Only)  |  679 Test (200 Normal + 479 Defective)  |  65 Defect Types  |  256×256 Resized',
                 ha='center', fontsize=9, color=SLATE_500, style='italic')

    else:
        # Fallback: create a text-based overview figure
        fig, ax = plt.subplots(1, 1, figsize=(16, 7), dpi=150)
        fig.patch.set_facecolor(SLATE_50)
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 7)
        ax.axis('off')

        ax.text(8, 6.5, 'MVTec AD Dataset: 12 Evaluated Categories', ha='center',
                fontsize=14, fontweight='bold', color=SLATE_900)

        for i, cat in enumerate(categories):
            col = i % 6
            row = i // 6
            x = 1 + col * 2.5
            y = 4.5 - row * 2.5
            box = FancyBboxPatch((x, y), 2.0, 1.8, boxstyle="round,pad=0.1",
                                 facecolor=BLUE_100, edgecolor=BLUE_600, linewidth=1)
            ax.add_patch(box)
            ax.text(x + 1.0, y + 0.9, cat, ha='center', va='center',
                    fontsize=9, fontweight='bold', color=SLATE_900)

        ax.text(8, 0.3,
                '1,389 Training (Normal-Only)  |  679 Test (200 Normal + 479 Defective)  |  65 Defect Types',
                ha='center', fontsize=10, color=SLATE_500, style='italic')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'slide07_dataset_samples.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=SLATE_50)
    plt.close()
    print(f"Saved: {out_path}")


def generate_ablation_charts():
    """Generate slide11_ablation.png — AE loss ablation + AE architecture ablation bar charts."""
    df4 = pd.read_csv(os.path.join(TABLES_DIR, 'Table4_Autoencoder_Loss_Ablation.csv'))
    df5 = pd.read_csv(os.path.join(TABLES_DIR, 'Table5_Autoencoder_Architecture_Ablation.csv'))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)
    fig.patch.set_facecolor(SLATE_50)

    # --- Left: Loss Ablation (Table 4) ---
    loss_labels = ['MSE', 'MAE', 'SSIM', 'MSE+SSIM', 'MSE+Grad']
    img_auroc = df4['Image_AUROC'].values
    pix_auroc = df4['Pixel_AUROC'].values
    f1_scores = df4['F1_Score'].values

    x = np.arange(len(loss_labels))
    width = 0.25

    bars1 = ax1.bar(x - width, img_auroc, width, label='Image AUROC', color=BLUE_600, alpha=0.9)
    bars2 = ax1.bar(x, pix_auroc, width, label='Pixel AUROC', color=TEAL_600, alpha=0.9)
    bars3 = ax1.bar(x + width, f1_scores, width, label='F1-Score', color=AMBER_600, alpha=0.9)

    ax1.set_xlabel('Loss Function', fontsize=10, fontweight='bold', color=SLATE_700)
    ax1.set_ylabel('Score', fontsize=10, fontweight='bold', color=SLATE_700)
    ax1.set_title('Autoencoder Loss Function Ablation (Table 4)', fontsize=12, fontweight='bold', color=SLATE_900)
    ax1.set_xticks(x)
    ax1.set_xticklabels(loss_labels, fontsize=8, rotation=15)
    ax1.set_ylim(0, 1.05)
    ax1.legend(fontsize=8, loc='upper right')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_facecolor(WHITE)

    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, h + 0.01, f'{h:.2f}',
                     ha='center', va='bottom', fontsize=6.5, color=SLATE_700)

    # Highlight best MSE
    ax1.annotate('Best: MSE', xy=(0, img_auroc[0]), xytext=(0.5, 0.95),
                 fontsize=8, color=CORAL_600, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=CORAL_600, lw=1.2))

    # --- Right: Architecture Depth Ablation (Table 5, first 3 rows only) ---
    arch_df = df5[df5['Ablation_Type'] == 'Architecture Depth'].copy()
    arch_labels = ['3-Level', '4-Level', '5-Level']
    arch_img = arch_df['Image_AUROC'].values
    arch_pix = arch_df['Pixel_AUROC'].values
    arch_f1 = arch_df['F1_Score'].values

    x2 = np.arange(len(arch_labels))

    bars4 = ax2.bar(x2 - width, arch_img, width, label='Image AUROC', color=BLUE_600, alpha=0.9)
    bars5 = ax2.bar(x2, arch_pix, width, label='Pixel AUROC', color=TEAL_600, alpha=0.9)
    bars6 = ax2.bar(x2 + width, arch_f1, width, label='F1-Score', color=PURPLE_600, alpha=0.9)

    ax2.set_xlabel('Architecture Depth', fontsize=10, fontweight='bold', color=SLATE_700)
    ax2.set_ylabel('Score', fontsize=10, fontweight='bold', color=SLATE_700)
    ax2.set_title('Autoencoder Architecture Depth Ablation (Table 5)', fontsize=12, fontweight='bold', color=SLATE_900)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(arch_labels, fontsize=9)
    ax2.set_ylim(0, 1.05)
    ax2.legend(fontsize=8, loc='upper left')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_facecolor(WHITE)

    for bars in [bars4, bars5, bars6]:
        for bar in bars:
            h = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, h + 0.01, f'{h:.2f}',
                     ha='center', va='bottom', fontsize=7, color=SLATE_700)

    # Highlight 5-level as best
    ax2.annotate('Best: 5-Level\n(0.9333 Img AUROC)', xy=(2, arch_img[2]),
                 xytext=(1.0, 0.98),
                 fontsize=8, color=CORAL_600, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=CORAL_600, lw=1.2))

    plt.tight_layout(w_pad=3)
    out_path = os.path.join(OUTPUT_DIR, 'slide11_ablation.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=SLATE_50)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    print("Generating new figures for restructured 12-slide presentation...")
    generate_model_architecture()
    generate_dataset_samples()
    generate_ablation_charts()
    print("All 3 new figures generated successfully!")

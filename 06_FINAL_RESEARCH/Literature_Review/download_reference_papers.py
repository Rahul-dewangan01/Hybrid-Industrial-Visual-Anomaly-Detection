"""
Download all benchmark and reference research papers referenced and compared in this research.
Saves PDF files into 06_FINAL_RESEARCH/Literature_Review/Reference_Papers/
"""

import os
import sys
import time
import urllib.request
import urllib.error

PAPERS = [
    {
        "id": "01_Bergmann_2019_MVTec_AD",
        "title": "MVTec AD - A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection",
        "authors": "Bergmann et al.",
        "venue": "CVPR 2019",
        "urls": [
            "https://openaccess.thecvf.com/content_CVPR_2019/papers/Bergmann_MVTec_AD_--_A_Comprehensive_Real-World_Dataset_for_Unsupervised_Anomaly_CVPR_2019_paper.pdf",
            "https://www.mvtec.com/fileadmin/Redaktion/mvtec.com/company/research/datasets/mvtec_ad.pdf"
        ]
    },
    {
        "id": "02_Bergmann_2019_SSIM_Autoencoders",
        "title": "Improving Unsupervised Defect Segmentation by Applying Structural Similarity to Autoencoders",
        "authors": "Bergmann et al.",
        "venue": "VISIGRAPP 2019",
        "urls": [
            "https://arxiv.org/pdf/1811.01402.pdf"
        ]
    },
    {
        "id": "03_Defard_2021_PaDiM",
        "title": "PaDiM: a Patch Distribution Modeling Framework for Anomaly Detection and Localization",
        "authors": "Defard et al.",
        "venue": "ICPR 2021",
        "urls": [
            "https://arxiv.org/pdf/2011.08785.pdf"
        ]
    },
    {
        "id": "04_Roth_2022_PatchCore",
        "title": "Towards Total Recall in Industrial Anomaly Detection",
        "authors": "Roth et al.",
        "venue": "CVPR 2022",
        "urls": [
            "https://openaccess.thecvf.com/content/CVPR2022/papers/Roth_Towards_Total_Recall_in_Industrial_Anomaly_Detection_CVPR_2022_paper.pdf",
            "https://arxiv.org/pdf/2106.08265.pdf"
        ]
    },
    {
        "id": "05_Zavrtanik_2021_DRAEM",
        "title": "DRAEM - A Discriminatively Trained Reconstruction Embedding for Surface Anomaly Detection",
        "authors": "Zavrtanik et al.",
        "venue": "ICCV 2021",
        "urls": [
            "https://openaccess.thecvf.com/content/ICCV2021/papers/Zavrtanik_DRAEM_-_A_Discriminatively_Trained_Reconstruction_Embedding_for_Surface_Anomaly_ICCV_2021_paper.pdf",
            "https://arxiv.org/pdf/2108.07610.pdf"
        ]
    },
    {
        "id": "06_Deng_2022_Reverse_Distillation",
        "title": "Anomaly Detection via Reverse Distillation from One-Class Embedding",
        "authors": "Deng & Li",
        "venue": "CVPR 2022",
        "urls": [
            "https://openaccess.thecvf.com/content/CVPR2022/papers/Deng_Anomaly_Detection_via_Reverse_Distillation_From_One-Class_Embedding_CVPR_2022_paper.pdf",
            "https://arxiv.org/pdf/2201.10703.pdf"
        ]
    },
    {
        "id": "07_Yu_2021_FastFlow",
        "title": "FastFlow: Unsupervised Anomaly Detection and Localization via 2D Normalizing Flows",
        "authors": "Yu et al.",
        "venue": "arXiv 2021",
        "urls": [
            "https://arxiv.org/pdf/2111.07677.pdf"
        ]
    },
    {
        "id": "08_Batzner_2024_EfficientAD",
        "title": "EfficientAD: Accurate Visual Anomaly Detection at Millisecond-Level Latencies",
        "authors": "Batzner et al.",
        "venue": "WACV 2024",
        "urls": [
            "https://openaccess.thecvf.com/content/WACV2024/papers/Batzner_EfficientAD_Accurate_Visual_Anomaly_Detection_at_Millisecond-Level_Latencies_WACV_2024_paper.pdf",
            "https://arxiv.org/pdf/2303.14535.pdf"
        ]
    }
]

def main():
    dest_dir = os.path.join("06_FINAL_RESEARCH", "Literature_Review", "Reference_Papers")
    os.makedirs(dest_dir, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    print(f"Destination folder: {os.path.abspath(dest_dir)}")
    print(f"Total papers to download: {len(PAPERS)}\n" + "="*70)
    
    results = []
    
    for i, paper in enumerate(PAPERS, 1):
        filename = f"{paper['id']}.pdf"
        filepath = os.path.join(dest_dir, filename)
        
        # Check if already exists and valid
        if os.path.exists(filepath) and os.path.getsize(filepath) > 50 * 1024:
            with open(filepath, "rb") as f:
                header = f.read(4)
            if header == b"%PDF":
                size_kb = os.path.getsize(filepath) / 1024
                print(f"[{i}/{len(PAPERS)}] Already present: {filename} ({size_kb:.1f} KB)")
                results.append((paper, True, size_kb, "Cached"))
                continue
        
        print(f"[{i}/{len(PAPERS)}] Downloading: {paper['title']}")
        print(f"       Venue: {paper['venue']} | Target: {filename}")
        
        success = False
        final_size = 0
        error_msg = ""
        
        for url in paper["urls"]:
            print(f"       Trying: {url} ...")
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = resp.read()
                    if data[:4] == b"%PDF":
                        with open(filepath, "wb") as f:
                            f.write(data)
                        final_size = len(data) / 1024
                        print(f"       --> SUCCESS ({final_size:.1f} KB)")
                        success = True
                        break
                    else:
                        print(f"       --> Response was not a PDF (header: {data[:20]})")
            except Exception as e:
                print(f"       --> Failed: {e}")
                error_msg = str(e)
            time.sleep(1.5)
            
        results.append((paper, success, final_size, error_msg))
        print("-" * 70)
        time.sleep(1.0)
        
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY:")
    all_success = True
    for paper, success, size_kb, err in results:
        status = f"OK ({size_kb:.1f} KB)" if success else f"FAILED ({err})"
        if not success:
            all_success = False
        print(f" - {paper['id']}: {status}")
    print("="*70)
    
    if all_success:
        print("All 8 reference research papers have been successfully downloaded and verified!")
    else:
        print("Some papers could not be downloaded automatically.")

if __name__ == "__main__":
    main()

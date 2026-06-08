#!/usr/bin/env python3
"""
fix_map.py  –  Lab 7 Map Post-Processing Utility
-------------------------------------------------
Cleans up a noisy SLAM-generated PGM map by:
  1. Removing salt-and-pepper noise (median filter)
  2. Filling small isolated unknown regions (morphological closing)
  3. Sharpening wall/obstacle edges (dilation + erosion)
  4. Saving a cleaned copy: ~/maps/my_map_clean.pgm + my_map_clean.yaml

Run this BEFORE launching Nav2:
    python3 fix_map.py

Then launch Nav2 with the clean map:
    ros2 launch turtlebot3_navigation2 navigation2.launch.py \\
        use_sim_time:=True map:=$HOME/maps/my_map_clean.yaml
"""

import os
import sys
import shutil

# ── check dependencies ────────────────────────────────────────────────────────
try:
    import numpy as np
    from PIL import Image
    from scipy import ndimage
except ImportError:
    print("[fix_map] Installing required Python packages...")
    os.system("pip3 install numpy Pillow scipy --quiet")
    import numpy as np
    from PIL import Image
    from scipy import ndimage

# ── paths ─────────────────────────────────────────────────────────────────────
HOME       = os.path.expanduser("~")
SRC_PGM    = os.path.join(HOME, "maps", "my_map.pgm")
SRC_YAML   = os.path.join(HOME, "maps", "my_map.yaml")
DST_PGM    = os.path.join(HOME, "maps", "my_map_clean.pgm")
DST_YAML   = os.path.join(HOME, "maps", "my_map_clean.yaml")

def load_map(pgm_path):
    """Load PGM as numpy uint8 array."""
    img = Image.open(pgm_path).convert('L')
    return np.array(img, dtype=np.uint8)

def save_map(arr, pgm_path):
    """Save numpy uint8 array as PGM."""
    img = Image.fromarray(arr.astype(np.uint8), mode='L')
    img.save(pgm_path)
    print(f"  Saved: {pgm_path}  ({arr.shape[1]}×{arr.shape[0]} px)")

def classify(arr):
    """
    Return boolean masks for each occupancy class.
    Nav2 uses occupied_thresh=0.65 → pixel < (1-0.65)*255 = 89 → occupied
                  free_thresh=0.25  → pixel > (1-0.25)*255 = 191 → free
    """
    occupied = arr < 89
    free     = arr > 205
    unknown  = ~occupied & ~free
    return occupied, free, unknown

def fix_map(arr):
    """Apply a sequence of cleaning operations and return a clean array."""
    occupied, free, unknown = classify(arr)

    print(f"  Before  → free: {free.sum():,} px  "
          f"unknown: {unknown.sum():,} px  "
          f"occupied: {occupied.sum():,} px")

    # ── Step 1: Median filter to kill salt-and-pepper noise ──────────────────
    from scipy.ndimage import median_filter
    cleaned = median_filter(arr.astype(float), size=3)

    # ── Step 2: Re-classify after median filter ───────────────────────────────
    occ2 = cleaned < 89
    free2 = cleaned > 205
    unk2 = ~occ2 & ~free2

    # ── Step 3: Morphological closing on the UNKNOWN mask ────────────────────
    # Fills small unknown holes that are surrounded by free/occupied cells.
    struct = ndimage.generate_binary_structure(2, 1)
    # Dilate unknown, then erode — this closes small gaps
    unk_closed = ndimage.binary_closing(unk2, structure=ndimage.iterate_structure(struct, 4))

    # ── Step 4: Reconstruct the cleaned image ────────────────────────────────
    result = np.full_like(arr, 205, dtype=np.uint8)   # start: all unknown (205)
    result[free2]       = 254                           # free → white
    result[occ2]        = 0                             # occupied → black
    result[unk_closed & ~free2 & ~occ2] = 205          # keep unknown as gray

    # ── Step 5: Dilate obstacle pixels slightly for safer costmap inflation ───
    occ_final = result < 89
    occ_dilated = ndimage.binary_dilation(
        occ_final,
        structure=ndimage.iterate_structure(struct, 1))
    result[occ_dilated] = 0

    # ── Final classification report ───────────────────────────────────────────
    occ_f, free_f, unk_f = classify(result)
    print(f"  After   → free: {free_f.sum():,} px  "
          f"unknown: {unk_f.sum():,} px  "
          f"occupied: {occ_f.sum():,} px")

    return result

def patch_yaml(src_yaml, dst_yaml, new_pgm_name):
    """Copy the YAML, updating the image field to point to the new PGM."""
    with open(src_yaml, 'r') as f:
        lines = f.readlines()

    with open(dst_yaml, 'w') as f:
        for line in lines:
            if line.strip().startswith('image:'):
                # Write absolute path so Nav2 can always find it
                f.write(f"image: {os.path.join(HOME, 'maps', new_pgm_name)}\n")
            else:
                f.write(line)
    print(f"  Saved: {dst_yaml}")


def main():
    if not os.path.exists(SRC_PGM):
        print(f"[ERROR] Source map not found: {SRC_PGM}")
        print("  Run SLAM first and save your map to ~/maps/my_map.pgm")
        sys.exit(1)

    print(f"\n[fix_map] Loading:  {SRC_PGM}")
    arr = load_map(SRC_PGM)
    print(f"  Image size: {arr.shape[1]}×{arr.shape[0]} px")

    print("\n[fix_map] Cleaning map...")
    cleaned = fix_map(arr)

    print("\n[fix_map] Saving cleaned map...")
    save_map(cleaned, DST_PGM)
    patch_yaml(SRC_YAML, DST_YAML, 'my_map_clean.pgm')

    print("\n[fix_map] Done! Use the clean map with Nav2:")
    print(f"  ros2 launch turtlebot3_navigation2 navigation2.launch.py \\")
    print(f"      use_sim_time:=True map:={DST_YAML}")
    print()


if __name__ == '__main__':
    main()

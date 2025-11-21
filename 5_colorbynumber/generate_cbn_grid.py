import argparse 
import json 
from pathlib import Path 
import numpy as np 
from PIL import Image, ImageDraw, ImageFont 

def parse_xy(s: str):
    if "x" not in s.lower():
        raise argparse.ArgumentTypeError("grid must be like 32x32")
    a, b = s.lower().split("x", 1)
    try:
        w = int(a.strip())
        h = int(b.strip())
    except ValueError:
        raise argparse.ArgumentTypeError("grid must be like 32x32 with integers")
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("grid must be positive")
    return w, h 

# -------------- 1. image to grid --------------- #
def quantize_image_to_grid(image_path: Path, grid_w: int, grid_h: int, k_colors: int):
    """
    Returns:
        labels: (H, W) np.int32 in [1..K]
        palette: dict {1: (R,G,B), ...}
        preview_img: PIL.Image of the posterized grid (W X H)
    Steps:
        - load image (RGB)
        - resize to grid size (defines board dimensions)
        - quantize to k_colors (Pillow mediancut)
        - compact indices to 1...K and build palette
    """
    img = Image.open(image_path).convert("RGB")
    # resize to grid cells (board resolution)
    img_small = img.resize((grid_w, grid_h), Image.Resampling.BILINEAR)
    # quantize to k_colors
    img_q = img_small.quantize(colors=k_colors, method=Image.MEDIANCUT)
    # extract palette from the quantized image 
    raw_pal = img_q.getpalette() or []

    # build palette index -> RGB 
    pal_idx_to_rgb = {}
    for idx in range(256):
        base = 3 * idx 
        if base + 2 < len(raw_pal):
            pal_idx_to_rgb[idx] = (
                raw_pal[base+0],
                raw_pal[base+1],
                raw_pal[base+2],
            )
    
    # build labels from quantized indices, then remap to 1...K compact 
    idxs = np.array(img_q, dtype=np.uint8) # shape (H, W), values are palette indices 
    uniq = np.unique(idxs) # actual used indices 
    idx_to_label = {int(u): i+1 for i, u in enumerate(uniq)} # 1...K
    labels = np.vectorize(lambda v: idx_to_label[int(v)], otypes=[np.int32])(idxs)

    # build compact palette 1...K
    palette = {}
    for u in uniq:
        label = idx_to_label[int(u)]
        palette[label] = pal_idx_to_rgb.get(int(u), (0,0,0))
    
    # build a small posterized preview (exact grid size)
    preview = Image.new("RGB", (grid_w, grid_h))
    px = preview.load()
    for y in range(grid_h):
        for x in range(grid_w):
            px[x,y] = palette[int(labels[y,x])]

    return labels.astype(np.int32), palette, preview

# -------------- 2. draw grid board (optional) --------------- #
def draw_numbered_board(labels: np.ndarray, cell_px: int, palette: dict | None = None, show_grid: bool = True, numbers_alpha: int = 255) -> Image.Image:
    """
    Create a big image that shows each cell with its number in the center. 
    If a palette is provided, cells are left white (numbers only) so it's a clean hint sheet.
    """
    h, w = labels.shape
    W = w * cell_px 
    H = h * cell_px 

    img = Image.new("RGBA", (W, H), (255,255,255,255))
    draw = ImageDraw.Draw(img)

    # choose a readable font size based on cell size
    # try to use a default truetype if available; fall back to bitmap default
    font = None
    for size in (int(cell_px * 0.65), int(cell_px * 0.55), int(cell_px * 0.45)):
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size)
            break 
        except Exception:
            font = None 
    if font is None:
        font = ImageFont.load_default()

    text_color = (80,80,80, numbers_alpha)
    grid_color = (200,200,200,255)
    
    # cells & numbers
    for y in range(h):
        for x in range(w):
            cx0 = x * cell_px 
            cy0 = y * cell_px 
            rect = (cx0, cy0, cx0+cell_px, cy0+cell_px)

            # background remains white to keep numbers readable 
            # draw cell grid 
            if show_grid:
                draw.rectangle(rect, outline=grid_color)

            # center number 
            n = str(int(labels[y,x]))
            tb = draw.textbbox((0,0), n, font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            tx = cx0 + (cell_px - tw) // 2
            ty = cy0 + (cell_px - th) // 2
            # white patch behind text for clarity (light translucent)
            pad = max(2, cell_px // 12)
            draw.rectangle((tx - pad, ty - pad, tx + tw + pad, ty + th + pad), fill=(255, 255, 255, int(0.8 * numbers_alpha)))
            draw.text((tx, ty), n, font=font, fill=text_color)
    
    return img 

# -------------- 3. output --------------- #
def save_outputs(out_dir: Path, labels: np.ndarray, palette: dict, preview_small: Image.Image, cell_px: int):
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) labels array
    np.save(out_dir / "labels.npy", labels)

    # 2) palette json (convert tuples to lists)
    pal_json = {int(k): [int(v[0]), int(v[1]), int(v[2])] for k, v in palette.items()}
    with open(out_dir / "palette.json", "w") as f:
        json.dump(pal_json, f, indent=2)

    # 3) poster preview (optionally scaled up)
    scale = max(4, 512 // max(labels.shape[0], labels.shape[1]))
    poster_big = preview_small.resize(
        (preview_small.width * scale, preview_small.height * scale),
        Image.Resampling.NEAREST,
    )
    poster_big.save(out_dir / "poster_preview.png")

    # 4) numbers board (grid with numbers)
    board_img = draw_numbered_board(labels, cell_px=cell_px, palette=None, show_grid=True, numbers_alpha=255)
    board_img.convert("RGB").save(out_dir / "board_numbers.png")

# ----------------- main ------------------ #
def main():
    parser = argparse.ArgumentParser(description="Generate Color-by-Number grid, labels, palette, and numbered board.")
    parser.add_argument("image", help="input image path")
    parser.add_argument("--grid", type=parse_xy, default=(32,32), help="grid size, e.g. 32x32 or 48x36")
    parser.add_argument("--colors", type=int, default=8, help="number of colors K (2..32 is typical)")
    parser.add_argument("--cell", type=int, default=28, help="cell size (pixels) for board_numbers.png")
    parser.add_argument("--out", type=str, default="cbn_out", help="output folder")
    args = parser.parse_args()

    in_path = Path(args.image)
    out_dir = Path(args.out)

    labels, palette, preview_small = quantize_image_to_grid(
        in_path, grid_w=args.grid[0], grid_h=args.grid[1], k_colors=args.colors
    )
    save_outputs(out_dir, labels, palette, preview_small, cell_px=args.cell)

    print("Done. Wrote:")
    print(f"- {out_dir/'labels.npy'} (HxW int labels 1..K)")
    print(f"- {out_dir/'palette.json'} ({{label: [R,G,B]}})")
    print(f"- {out_dir/'board_numbers.png'} (grid with per-cell numbers)")
    print(f"- {out_dir/'poster_preview.png'} (K-color pixel preview)")

if __name__ in "__main__":
    main()



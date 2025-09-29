import argparse
import json
import os
from pathlib import Path 
import datetime 

import numpy as np 
import pygame
from PIL import Image

# ----------- utility IO ------------ #
def load_puzzle(pdir: Path):
    labels = np.load(pdir / "labels.npy")
    with open(pdir / "palette.json", "r") as f:
        palette = {int(k): tuple(v) for k, v in json.load(f).items()}
    preview_path = pdir / "browser_preview.jpg"
    if not preview_path.exists():
        # fallback preview from labels
        img = render_solved_pil(labels, palette, scale=8)
        preview_path = pdir / "_autogen_preview.png"
        img.save(preview_path)
    return labels, palette, preview_path

def render_solved_pil(labels: np.ndarray, palette: dict[int, tuple], scale=1):
    h, w = labels.shape
    img = Image.new("RGB", (w, h))
    pix = img.load()
    for y in range(h):
        for x in range(w):
            pix[x, y] = palette[int(labels[y, x])]
    if scale > 1:
        img = img.resize((w * scale, h * scale), Image.Resampling.NEAREST)
    return img 

# ------------------ basic UI primitives ----------------- #
class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, bg=(230,230,230), fg=(20,20,20), border=(0,0,0), hover=(210,210,210)):
        self.rect = rect 
        self.text = text 
        self.font = font 
        self.bg = bg
        self.fg = fg 
        self.border = border 
        self.hover = hover 

    def draw(self, surf):
        mx, my = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(mx, my)
        pygame.draw.rect(surf, self.hover if hovering else self.bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, self.border, self.rect, 2, border_radius=10)
        label = self.font.render(self.text, True, self.fg)
        surf.blit(label, label.get_rect(center=self.rect.center))
    
    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos))
    
# ------------ App States ------------- #
STATE_WELCOME = "WELCOME"
STATE_BROWSER = "BROWSER"
STATE_PLAY = "PLAY"
STATE_FINISHED = "FINISHED"

# ------------- Game App ------------------- #
class ColorByNumberApp:
    def __init__(self, puzzles_dir: Path, width=1100, height=800):
        pygame.init()
        pygame.display.set_caption("Color By Number")
        self.screen = pygame.display.set_mode((width, height))
        self.W, self.H = width, height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.slogan_font = pygame.font.Font("font/NotoSansSC-VariableFont_wght.ttf", 30)

        self.bg = (250,250,250)
        self.panel = (255,255,255)
        self.grid_c = (210,210,210)
        self.text_c = (40,40,40)

        # state
        self.state = STATE_WELCOME

        # load puzzles list
        self.puzzles = [] # list of dicts: {name, dir, labels, palette, preview_surf}
        for sub in sorted(p for p in Path(puzzles_dir).iterdir() if p.is_dir()):
            try:
                labels, palette, preview_img_path = load_puzzle(sub)
                complete_path = sub / "browser_complete.jpg"
                preview_surf = self._load_square_preview(preview_img_path, 360)
                if complete_path.exists():
                    complete_surf = self._load_square_preview(complete_path, 360)
                self.puzzles.append({
                    "name": sub.name, 
                    "dir": sub,
                    "labels": labels,
                    "palette": palette,
                    "preview": preview_surf,
                    "complete_preview": complete_surf
                })
            except Exception as e:
                print(f"Skipping {sub}: {e}")

        # welcome screen button
        bw, bh = 220, 60
        self.btn_start = Button(pygame.Rect((self.W-bw)//2, int(self.H//2+200), bw, bh), "START", self.font)
        self.welcome_img = None
        welcome_path = Path("assets/welcome.jpg")
        if welcome_path.exists():
            try:
                self.welcome_img = pygame.image.load(str(welcome_path)).convert_alpha()
            except Exception as e:
                print(f"[welcome image load failed] {e}")

        # browser layout
        self.browser_scroll = 0
        self.browser_cell = 420 # cell size (preview+label) per item vertically
        self.browser_cols = 2
        self.browser_card_max = 140
        self.browser_card_gap = 50

        # active puzzle (set in PLAY)
        self.active = None # dict like in self.puzzles
        self.selected_label = 1
        self.filled_ok = None # bool array HxW

        # drawing board offscreen
        self.BASE_CELL = 26 # logical cell size for offscreen drawing
        self.board_surface = None 
        self.min_zoom_fit = 0.5
        self.max_zoom = 6.0

        # camera
        self.zoom = 1.0
        self.pan = pygame.Vector2(30,30)
        self.dragging = False 
        self.drag_anchor = None 

        # palette bar geometry (bottom)
        self.palette_bar_h = 110
        self.palette_swatches = [] # (label, rect)
        self.palette_page = 0
        self._palette_pages = 1
        self._palette_left_btn = pygame.Rect(0,0,0,0)
        self._palette_right_btn = pygame.Rect(0,0,0,0)

        # back button in play window
        self.btn_play_back = Button(pygame.Rect(16, 12, 110, 40), "BACK", self.font)
        
        # finished buttons
        self.btn_save = Button(pygame.Rect(self.W - 160 - 30, self.H -60 - 20, 160, 60), "SAVE", self.font)
        self.btn_back = Button(pygame.Rect(30, self.H - 60 - 20, 160, 60), "RETURN", self.font)

    # --- helpers --- #
    def _fit_center(self, surf, max_w, max_h):
        """Scale surf to fit inside (max_w, max_h) while keeping aspect ratio."""
        if surf is None:
            return None 
        sw, sh = surf.get_size()
        scale = min(max_w/sw, max_h/sh)
        tw, th = int(sw*scale), int(sh*scale)
        return pygame.transform.smoothscale(surf, (tw, th))

    def _load_square_preview(self, img_path: Path, box: int) -> pygame.Surface:
        img = Image.open(img_path).convert("RGB")
        # make square letterbox with white background
        w, h = img.size 
        scale = box / max(w, h)
        img2 = img.resize((int(w * scale), int(h * scale)), Image.Resampling.NEAREST)
        canvas = Image.new("RGB", (box, box), (255,255,255))
        cx = (box - img2.size[0]) // 2
        cy = (box - img2.size[1]) // 2
        canvas.paste(img2, (cx, cy))
        mode = canvas.mode 
        data = canvas.tobytes()
        surf = pygame.image.fromstring(data, canvas.size, mode)
        return surf 
    
    def _compute_min_zoom_fit(self, labels):
        H, W = labels.shape 
        board_w = W * self.BASE_CELL
        board_h = H * self.BASE_CELL

        # view area above the palette bar (leave a small margin)
        margin = 20
        avail_w = self.W - margin * 2
        avail_h = self.H - self.palette_bar_h - margin * 2

        if board_w == 0 or board_h == 0:
            return 0.5
        
        # zoom that *just fits* the whole board into the available area 
        return min(avail_w/board_w, avail_h/board_h)
    
    def _clamp_pan(self, labels):
        """Keep the board within a reasonable border. Centers it if smaller than the viewport."""
        H, W = labels.shape
        bw = W*self.BASE_CELL*self.zoom
        bh = H*self.BASE_CELL*self.zoom

        # viewport where the board is visiable (above the palette bar)
        viewport_x = 0
        viewport_y = 0
        viewport_w = self.W 
        viewport_h = self.H-self.palette_bar_h

        # how much border you want at most when the board is larger than the view port
        margin = 80

        # horizontal clamp
        if bw+2*margin <= viewport_w:
            # board is narrower than viewport: keep it centered; no dragging outside
            self.pan.x = viewport_x+(viewport_w-bw)*0.5
        else:
            min_x = viewport_x+viewport_w-bw-margin # rightmost (board's right edge inside)
            max_x = viewport_x+margin 
            self.pan.x = max(min(self.pan.x, max_x), min_x)

        # vertical clamp
        if bh+2*margin <= viewport_h:
            # board is shorter than viewport: center vertically
            self.pan.y = viewport_y+(viewport_h-bh)*0.5
        else:
            min_y = viewport_y+viewport_h-bh-margin
            max_y = viewport_y+margin
            self.pan.y = max(min(self.pan.y, max_y), min_y)
    
    def _reset_camera(self, labels):
        self.min_zoom_fit = max(0.1, self._compute_min_zoom_fit(labels))
        # start at a pleasant zoom that shows whoe image
        self.zoom = max(self.min_zoom_fit, min(self.max_zoom, self.min_zoom_fit*1.0))
        # center the board
        H, W = labels.shape
        board_w = W*self.BASE_CELL*self.zoom
        board_h = H*self.BASE_CELL*self.zoom
        self.pan = pygame.Vector2((self.W-board_w)*0.5, (self.H-self.palette_bar_h-board_h)*0.5+20)
        self._clamp_pan(labels)

    def _screen_to_board(self, pos):
        sx, sy = pos
        bx = (sx - self.pan.x) / self.zoom
        by = (sy - self.pan.y) / self.zoom
        return bx, by 
    
    def _board_to_cell(self, labels, bx, by):
        H, W = labels.shape 
        if bx < 0 or by < 0:
            return None 
        cx = int(bx // self.BASE_CELL)
        cy = int(by // self.BASE_CELL)
        if 0 <= cx < W and 0 <= cy < H:
            return cx, cy 
        return None 
    
    def _prepare_board_surface(self, labels):
        H, W = labels.shape 
        self.board_surface = pygame.Surface((W * self.BASE_CELL, H * self.BASE_CELL))

    def _draw_board(self, labels, palette, filled_ok, show_numbers):
        s = self.board_surface 
        s.fill((255,255,255))
        font = pygame.font.SysFont(None, max(12, int(self.BASE_CELL * 0.55)))
        H, W = labels.shape

        # colors
        highlight_bg = (230,230,230)
        empty_bg = (250,250,250)
        for y in range(H):
            for x in range(W):
                rect = pygame.Rect(x * self.BASE_CELL, y * self.BASE_CELL, self.BASE_CELL, self.BASE_CELL)
                lab = int(labels[y, x])
                if filled_ok[y, x]:
                    pygame.draw.rect(s, palette[lab], rect)
                else:
                    if lab == self.selected_label:
                        pygame.draw.rect(s, highlight_bg, rect)
                    else:
                        pygame.draw.rect(s, empty_bg, rect)
                    if show_numbers:
                        n = str(int(labels[y, x]))
                        num_color = (90,90,90) if (lab == self.selected_label) else (120,120,120)
                        ts = font.render(n, True, num_color)
                        s.blit(ts, ts.get_rect(center=rect.center))

    def _draw_palette_bar(self, palette: dict[int, tuple]):
        mouse_pos = pygame.mouse.get_pos()
        y0 = self.H - self.palette_bar_h
        pygame.draw.rect(self.screen, self.panel, (0, y0, self.W, self.palette_bar_h))
        pygame.draw.line(self.screen, self.grid_c, (0, y0), (self.W, y0), 1)

        # ---- Layout: 1 row, squares, no gaps ----
        padding_x = 12
        padding_y = 10
        arrows_w = 40
        arrows_gap = 8

        usable_w = self.W - padding_x * 2 - arrows_w * 2 - arrows_gap * 2
        usable_h = self.palette_bar_h - padding_y * 2

        # Square size is limited by height (single row)
        sw = max(16, usable_h)
        sh = sw  # square

        # How many columns fit in the remaining width?
        cols = max(1, usable_w // sw)
        per_page = 10
        total_colors = len(palette)

        # Pagination
        self._palette_pages = max(1, (total_colors + per_page - 1) // per_page)
        self.palette_page = max(0, min(self.palette_page, self._palette_pages - 1))

        # ---- Arrow buttons ----
        left_x = padding_x
        right_x = self.W - padding_x - arrows_w
        btn_y = y0 + (self.palette_bar_h - sh) // 2
        self._palette_left_btn = pygame.Rect(left_x, btn_y, arrows_w, sh)
        self._palette_right_btn = pygame.Rect(right_x, btn_y, arrows_w, sh)

        def draw_arrow(rect, direction, enabled):
            hovered = rect.collidepoint(mouse_pos)
            if not enabled:
                bg = (245,245,245)
                border = (200,200,200)
            elif hovered:
                bg = (200,200,200)
                border = (0,0,0)
            else:
                bg = (235,235,235)
                border = (0,0,0)
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=6)
            cx, cy = rect.center
            if direction == "left":
                pts = [(cx + 6, cy - 10), (cx - 6, cy), (cx + 6, cy + 10)]
            else:
                pts = [(cx - 6, cy - 10), (cx + 6, cy), (cx - 6, cy + 10)]
            color = (50, 50, 50) if enabled else (170, 170, 170)
            pygame.draw.polygon(self.screen, color, pts)

        draw_arrow(self._palette_left_btn, "left", self.palette_page > 0)
        draw_arrow(self._palette_right_btn, "right", self.palette_page < self._palette_pages - 1)

        # ---- Visible labels for current page ----
        labels_sorted = list(range(1, total_colors + 1))
        start = self.palette_page * per_page
        end = min(total_colors, start + per_page)
        visible = labels_sorted[start:end]

        # Grid origin between arrows; no gaps between boxes
        grid_x0 = self._palette_left_btn.right + arrows_gap
        grid_y0 = y0 + (self.palette_bar_h - sh) // 2

        # Fonts: bigger for selected
        base_font = pygame.font.SysFont(None, max(12, int(sw * 0.45)))
        selected_font = pygame.font.SysFont(None, max(14, int(sw * 0.65)))

        def is_dark(rgb):
            r, g, b = rgb
            return (0.2126*r + 0.7152*g + 0.0722*b) < 140

        # Draw swatches left → right
        self.palette_swatches.clear()
        band_left = self._palette_left_btn.right+arrows_gap
        band_right = self._palette_right_btn.left-arrows_gap
        band_width = band_right-band_left 

        # fit exactly 10 square in a row
        sw = sh = band_width // per_page
        # center the row of visible swatches (no gaps)
        row_w = per_page*sw 
        start_x = band_left+(band_width-row_w)//2
        grid_y0 = y0+(self.palette_bar_h-sh)//2
        x = start_x
        for label in visible:
            rect = pygame.Rect(x, grid_y0, sw, sh)
            col_rgb = palette[label]

            # if this color is complete, grey it and (visually) disable
            done = self.color_filled.get(label, 0) >= self.color_total.get(label, 0)
            draw_rgb = (180,180,180) if done else col_rgb
            pygame.draw.rect(self.screen, draw_rgb, rect)

            # Centered number; auto-contrast; larger when selected
            font_for_label = selected_font if label == self.selected_label else base_font
            txt_color = (255, 255, 255) if is_dark(col_rgb) else (0, 0, 0)
            txt = font_for_label.render(str(label), True, txt_color)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

            # white progress bar under the number
            if (label == self.selected_label) and (not done):
                tot = max(1, self.color_total.get(label, 1))
                filled = min(tot, self.color_filled.get(label, 0))

                bar_margin = max(2, int(sw*0.1))
                bar_h = max(2, int(sw*0.05))
                bar_w = rect.w-bar_margin*2
                bar_x = rect.x+bar_margin
                bar_y = rect.bottom-int(sw*0.2)

                # bar color matches label contrast rule 
                bar_color = (255,255,255) if is_dark(draw_rgb) else (0,0,0)

                # background track (thin dar to frame the white)
                pygame.draw.rect(self.screen, bar_color, (bar_x-1, bar_y-1, bar_w+2, bar_h+2), 1)

                # progress fill (white)
                prog_w = int(bar_w*(filled/tot))
                if prog_w > 0:
                    pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, prog_w, bar_h))

            self.palette_swatches.append((label, rect))
            x += sw  # no gap

    # ---- progress I/O ---- #
    def _progress_paths(self, puzzle_dir: Path):
        """Return (npg_path, json_path) for a puzzle's progress."""
        pdir = Path(puzzle_dir)
        return (pdir/".progress_filled.npy", pdir/".progress_state.json")
    
    def _save_progress(self):
        """Save current play state for the active puzzle."""
        if not self.active or self.filled_ok is None:
            return 
        npy_path, json_path = self._progress_paths(self.active["dir"])
        try:
            # ensure dir exists
            npy_path.parent.mkdir(parents=True, exist_ok=True)
            # 1. filled mask
            np.save(npy_path, self.filled_ok.astype(np.bool_))
            # 2. simple state
            state = {
                "selected_label": int(self.selected_label),
                "palette_page": int(self.palette_page),
                "zoom": float(self.zoom), 
                "pan": [float(self.pan.x), float(self.pan.y)], 
            }
            with open(json_path, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"[progress save failed] {e}")

    def _load_progress(self, puzzle) -> bool:
        """Load progress is present; returns True if loaded."""
        npy_path, json_path = self._progress_paths(puzzle["dir"])
        loaded = False 

        # default fresh mask
        self.filled_ok = np.zeros_like(puzzle["labels"], dtype = bool)

        if npy_path.exists():
            try:
                filled = np.load(npy_path, allow_pickle=False)
                if filled.shape == puzzle["labels"].shape:
                    self.filled_ok = filled.astype(bool, copy=True)
                    loaded = True 
            except Exception as e:
                print(f"[progress load failed] {e}")
        
        # defaults if nothing loaded
        if self.filled_ok is None or self.filled_ok.shape != puzzle["labels"].shape:
            self.filled_ok = np.zeros_like(puzzle["labels"], dtype=bool)
        
        # optional UI state
        if json_path.exists():
            try:
                with open(json_path, "r") as f:
                    s = json.load(f)
                self.selected_label = int(s.get("selected_label", 1))
                self.palette_page = int(s.get("palette_page", 0))
                self.zoom = float(s.get("zoom", self.zoom))
                px, py = s.get("pan", [self.pan.x, self.pan.y])
                self.pan = pygame.Vector2(float(px), float(py))
            except Exception as e:
                print(f"[progress load failed] {e}")
        
        # recompute per-color counters from filled_ok
        labels = puzzle["labels"]
        K = len(puzzle["palette"])
        self.color_total = {k: int((labels == k).sum()) for k in range(1, K+1)}
        self.color_filled = {k: int((self.filled_ok & (labels == k)).sum()) for k in range(1, K+1)}

        # keep camera in bounds even if zoom/pan came from file 
        self._clamp_pan(labels)
        return loaded 
    
    def _puzzle_progress(self, puzzle) -> float:
        """
        Return complete fraction [0...1] for a puzzle by reading its saved mask if present.
        Uses .progress_filled.npy if it exists; otherwise 0.0
        """
        labels = puzzle["labels"]
        total = labels.size
        if total <= 0:
            return 0.0
        npy_path = puzzle["dir"] / ".progress_filled.npy"
        if npy_path.exists():
            try:
                filled = np.load(npy_path, allow_pickle=False)
                if filled.shape == labels.shape:
                    return float(filled.astype(bool).sum())/float(total)
            except Exception:
                pass
        return 0.0
    
    def _is_puzzle_complete(self, puzzle) -> bool:
        # small epsilon to be robust against rounding
        return self._puzzle_progress(puzzle) >= 0.999
    
    def _preview_surface_for_browser(self, puzzle) -> pygame.Surface:
        """Return completed preview if complete & avaialbe, else regular preview."""
        if self._is_puzzle_complete(puzzle) and puzzle.get("complete_preview") is not None:
            return puzzle["complete_preview"]
        return puzzle["preview"]

    # ---------------------- State screens -------------------------- #
    def draw_welcome(self):
        self.screen.fill(self.bg)
        if self.welcome_img:
            fitted = self._fit_center(self.welcome_img, int(self.W*0.5), int(self.H*0.5))
            rect = fitted.get_rect(center=(self.W//2, int(self.H*0.32)))
            self.screen.blit(fitted, rect)
            # --- subtitle below welcome image --- #
            tagline = self.slogan_font.render("长生不老 钓鱼爬山", True, (0,0,102))
            tagline_rect = tagline.get_rect(center=(self.W//2, rect.bottom+40))
            self.screen.blit(tagline, tagline_rect)
        self.btn_start.draw(self.screen)

    def draw_browser(self):
        self.screen.fill(self.bg)

        gap = self.browser_card_gap
        area_top = 20

        # compute square card size for current width
        avail_w = self.W-gap*(self.browser_cols+1) 
        size_by_w = avail_w//self.browser_cols
        item_w = item_h = size_by_w 

        # center the columns
        row_w = self.browser_cols*item_w+(self.browser_cols-1)*gap 
        left_x = (self.W-row_w)//2

        # scroll bounds
        total_rows = (len(self.puzzles)+self.browser_cols-1)//self.browser_cols 
        content_h = max(0, total_rows*(item_h+gap)-gap)
        viewport_h = self.H-area_top-20
        min_scroll = min(0, viewport_h-content_h)
        max_scroll = 0 
        self.browser_scroll = max(min(self.browser_scroll, max_scroll), min_scroll)
        self._browser_min_scroll = min_scroll
        self._browser_max_scroll = max_scroll

        # build rects
        self.browser_item_rects = []
        for i, p in enumerate(self.puzzles):
            col = i % self.browser_cols
            row = i // self.browser_cols
            x = left_x+col*(item_w+gap)
            y = area_top+self.browser_scroll+row*(item_h+gap)
            self.browser_item_rects.append(pygame.Rect(x, y, item_w, item_h))
        
        # draw each card: square, center-crop, plus progress bar
        for r, p in zip(self.browser_item_rects, self.puzzles):
            # card background+hariline border
            pygame.draw.rect(self.screen, self.panel, r)
            pygame.draw.rect(self.screen, (0,0,0), r, 1)

            # center-crop (cover) preview
            src = self._preview_surface_for_browser(p)
            sw, sh = src.get_width(), src.get_height()
            tw = th = r.w 
            scale = max(tw/sw, th/sh)
            scaled_w, scaled_h = int(sw*scale), int(sh*scale)
            scaled = pygame.transform.smoothscale(src, (scaled_w, scaled_h))
            ox = max(0, (scaled_w-tw)//2)
            oy = max(0, (scaled_h-th)//2)
            self.screen.blit(scaled, r, area=pygame.Rect(ox, oy, tw, th))

            # ---- progress bar at bottom of card ---- #
            if not self._is_puzzle_complete(p):
                frac = self._puzzle_progress(p)
                bar_h = max(3, r.h//24)
                bar_pad = max(8, r.w//18)
                bar_w = r.w-bar_pad*2
                bar_x = r.x+bar_pad
                bar_y = r.bottom-bar_pad-bar_h 

                # track (light gray) + fill (green)
                pygame.draw.rect(self.screen, (230,230,230), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
                fill_w = int(bar_w*frac)
                if fill_w > 0:
                    pygame.draw.rect(self.screen, (115, 145, 210), (bar_x, bar_y, fill_w, bar_h), border_radius=4)

    def draw_play(self):
        self.screen.fill(self.bg)
        labels = self.active["labels"]
        palette = self.active["palette"]

        # update board surface
        show_numbers = (self.zoom >= 1.25)
        self._draw_board(labels, palette, self.filled_ok, show_numbers)

        # scale and blit with camera
        scaled = pygame.transform.scale(self.board_surface, (int(self.board_surface.get_width() * self.zoom), int(self.board_surface.get_height() * self.zoom)))
        self.screen.blit(scaled, self.pan)
        # ---- 1px screen-space grid (stays thin at any zoom) ---- #
        H, W = labels.shape
        cell_screen_w = self.BASE_CELL*self.zoom 
        cell_screen_h = self.BASE_CELL*self.zoom
        gx0, gy0 = self.pan.x, self.pan.y 

        # only draw when zoomed in enough to be useful
        if cell_screen_w >= 12 and cell_screen_h >= 12:
            grid_color = (215,215,215)
            # vertical lines
            for x in range(W+1):
                xpix = int(gx0+x*cell_screen_w)
                pygame.draw.aaline(self.screen, grid_color, (xpix, gy0), (xpix, gy0+H*cell_screen_h))
            # horizontal lines
            for y in range(H+1):
                ypix = int(gy0+y*cell_screen_h)
                pygame.draw.aaline(self.screen, grid_color, (gx0, ypix), (gx0+W*cell_screen_w, ypix))
        
        # back button
        self.screen.set_clip(None)
        self.btn_play_back.draw(self.screen)
        # palette bar
        self._draw_palette_bar(palette)

    def draw_finished(self):
        self.screen.fill(self.bg)
        labels = self.active["labels"]
        palette = self.active["palette"]

        # render solved image (fit to view area)
        margin = 30
        area = pygame.Rect(margin, margin, self.W - margin * 2, self.H - margin * 2 - 90)
        # make a PIL image then to pygame 
        # choose scale to fit
        H, W = labels.shape
        solved = render_solved_pil(labels, palette, scale=1)
        sw, sh = solved.size
        scale = min(area.w / sw, area.h / sh)
        scale = max(1, int(scale)) # use integer to keep nearest crisp
        solved = solved.resize((sw * scale, sh * scale), Image.Resampling.NEAREST)
        mode = solved.mode 
        data = solved.tobytes()
        surf = pygame.image.fromstring(data, solved.size, mode)

        # draw card
        card = area.inflate(-20, -20)
        pygame.draw.rect(self.screen, self.panel, card, border_radius=12)
        pygame.draw.rect(self.screen, (0,0,0), card, 2, border_radius=12)
        self.screen.blit(surf, surf.get_rect(center=card.center))

        title = self.big_font.render("Finished!", True, (0,120,0))
        self.screen.blit(title, (card.x + 16, card.y + 12))

        # buttons
        self.btn_back.draw(self.screen)
        self.btn_save.draw(self.screen)

    # -------------------- Event handling ----------------------- #
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if self.state == STATE_PLAY:
                    self._save_progress()
                return False 
            if self.state == STATE_WELCOME:
                if self.btn_start.clicked(e):
                    self.state = STATE_BROWSER

            elif self.state == STATE_BROWSER:
                if e.type == pygame.MOUSEWHEEL:
                    # pygame: e.y > 0 = scroll up, e.y < 0 = scroll down
                    self.browser_scroll += e.y * 40
                    # clamp using limits computed in draw_browser()
                    if hasattr(self, "_browser_min_scroll"):
                        self.browser_scroll = max(min(self.browser_scroll, self._browser_max_scroll), self._browser_min_scroll)
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    for rect, puzzle in zip(self.browser_item_rects, self.puzzles):
                        if rect.collidepoint(e.pos):
                            self._enter_play(puzzle)
                            break 

            elif self.state == STATE_PLAY:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    # back to browser
                    self._save_progress()
                    self.state = STATE_BROWSER
                elif e.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    before = pygame.Vector2(self._screen_to_board((mx, my)))
                    # apply zoom delta
                    self.zoom *= (1.12 if e.y > 0 else 1/1.12)
                    # clamp: never smaller than "fit to view", never larger than max
                    self.zoom = max(self.min_zoom_fit, min(self.zoom, self.max_zoom))
                    after = pygame.Vector2(self._screen_to_board((mx, my)))
                    # keep cursor point anchored
                    self.pan += (after-before)*self.zoom 
                    self._clamp_pan(self.active["labels"])
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # back button
                    if self.btn_play_back.rect.collidepoint(e.pos):
                        try:
                            self._save_progress()
                        except Exception:
                            pass 
                        self.state = STATE_BROWSER
                        return True 
                    # first: arrow buttons
                    if self._palette_left_btn.collidepoint(e.pos) and self.palette_page > 0:
                        self.palette_page -= 1
                        # prevent starting a drag if clicked arrow
                        return True 
                    if self._palette_right_btn.collidepoint(e.pos) and self.palette_page < self._palette_pages-1:
                        self.palette_page += 1
                        return True
                    # next: swatches
                    self.dragging = True 
                    self.drag_anchor = pygame.Vector2(e.pos)
                    # check palette swatches first
                    for lab, r in self.palette_swatches:
                        if r.collidepoint(e.pos):
                            # ignore fully completed colors
                            if self.color_filled.get(lab, 0) >= self.color_total.get(lab, 0):
                                return True 
                            self.selected_label = lab 
                            self.dragging = False 
                            self.drag_anchor = None 
                            return True 
                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    if self.drag_anchor is not None:
                        moved = (pygame.Vector2(e.pos) - self.drag_anchor).length() >= 5
                    else:
                        moved = False 
                    if not moved:
                        # treat as click on board
                        bx, by = self._screen_to_board(e.pos)
                        cell = self._board_to_cell(self.active["labels"], bx, by)
                        if cell:
                            cx, cy = cell
                            lab = int(self.active["labels"][cy, cx])
                            if (not self.filled_ok[cy, cx]) and (self.selected_label == lab):
                                self.filled_ok[cy, cx] = True
                                # update per-color progress
                                self.color_filled[lab] += 1
                                # autosave right after each change
                                self._save_progress()
                                # if this color is now done, and it's the selected color, jump to nextselectable
                                if self.color_filled[lab] >= self.color_total[lab]:
                                    # auto-advance to next imcomplete color on this page
                                    for nxt in range(1, len(self.active["palette"])+1):
                                        if self.color_filled[nxt] < self.color_total[nxt]:
                                            self.selected_label = nxt
                                            break 
                                # puzzle finished
                                if self.filled_ok.all():
                                    self.state = STATE_FINISHED
                    self.dragging = False 
                    self.drag_anchor = None 
                elif e.type == pygame.MOUSEMOTION and self.dragging and self.drag_anchor is not None:
                    delta = pygame.Vector2(e.pos) - self.drag_anchor
                    self.pan += delta
                    self.drag_anchor = pygame.Vector2(e.pos)
                    self._clamp_pan(self.active["labels"])
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT and self.palette_page > 0:
                        self.palette_page -= 1
                    elif e.key == pygame.K_RIGHT and self.palette_page < self._palette_pages-1:
                        self.palette_page += 1
            
            elif self.state == STATE_FINISHED:
                try:
                    npy_path, json_path = self._progress_paths(self.active["dir"])
                    if npy_path.exists(): npy_path.unlink()
                    if json_path.exists(): json_path.unlink()
                except Exception:
                    pass

                if self.btn_back.clicked(e):
                    self.state = STATE_BROWSER
                elif self.btn_save.clicked(e):
                    self._save_finished_png()

        return True 

    # -------------------- transitions & actions ------------------------- #
    def _enter_play(self, puzzle):
        self.active = puzzle 
        self.board_surface = None 
        self._prepare_board_surface(self.active["labels"])

        # defaults (will be overwritten by _load_progress if files exists)
        self.selected_label = 1
        self.palette_page = 0
        self._reset_camera(self.active["labels"])

        # counters, may get replaced by _load_progress
        labels = self.active["labels"]
        K = len(self.active["palette"])
        self.filled_ok = np.zeros_like(labels, dtype=bool)
        self.color_total = {k: int((labels==k).sum()) for k in range(1, K+1)}
        self.color_filled = {k: 0 for k in range(1, K+1)}

        # try to load prior progress
        self._load_progress(self.active)
        self.state = STATE_PLAY

    def _save_finished_png(self):
        labels = self.active["labels"]
        palette = self.active["palette"]
        stem = self.active["dir"].name 
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = Path(f"{stem}_finished_{ts}.png")
        # render at a pleasant size 
        scale = max(4, 512 // max(labels.shape))
        img = render_solved_pil(labels, palette, scale)
        img.save(out)
        print(f"[Saved] {out.resolve()}")
    
    # ------------------------- Main loop ----------------------------- #
    def run(self):
        running = True
        while running:
            running = self.handle_events()

            if self.state == STATE_WELCOME:
                self.draw_welcome()
            elif self.state == STATE_BROWSER:
                self.draw_browser()
            elif self.state == STATE_PLAY:
                self.draw_play()
            elif self.state == STATE_FINISHED:
                self.draw_finished()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

# ---------------------- Entry ---------------------- #
def main():
    ap = argparse.ArgumentParser(description="Color-by-Number Game")
    ap.add_argument("--puzzles", type=str, default="./puzzles", help="directory containing puzzle folders")
    ap.add_argument("--width", type=int, default=1000)
    ap.add_argument("--height", type=int, default=800)
    args = ap.parse_args()

    app = ColorByNumberApp(Path(args.puzzles), width=args.width, height=args.height)
    app.run()

if __name__ == "__main__":
    main()
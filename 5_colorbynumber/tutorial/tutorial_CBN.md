# Make 100 games with Python: NO.5 Color By Number
## Generate cbn grid
### import modules
```
import argparse 
```
- Imports the `argparse` module, which helps you parse comand-line arguments easily. 

```
import json 
```
- Loads and saves data in JSON format (e.g. configuration files, results, or metadata)

```
from pathlib import Path 
```
- Imports the `Path` class from the `pathlib` module, a modern, object-oriented way to handle file and directory path. 

```
import numpy as np 
```
- Imports `NumPy`, a powerful library for numerical operations and array manipulation (often used for image data or calculations). 

```
from PIL import Image, ImageDraw, ImageFont 
```
- Imports classes from **Pillow** for working with images:
    - `Image`: open, manipulate, and save images.
    - `ImageDraw`: draw shapes, lines, or text on an image.
    - `ImageFont`: load and use custom fonts for drawing text. 

### Parse grid size argument
Parse a grid size argument (i.e. `32x32`) from the command line and return it as a tuple of two integers `(w, h)`. 
```
def parse_xy(s: str):
    if "x" not in s.lower():
    raise argparse.ArgumentTypeError("grid must be like 32x32")
```
- Ensures the input string contains an `"x"` (case-insensitive)
- If not, raises an error with a clear message. 

```
a, b = s.lower().split("x", 1)
```
- Splits the string into two parts around the first `"x"`. 

```
try:
    w = int(a.strip())
    h = int(b.strip())
except ValueError:
    raise argparse.ArgumentTypeError("grid must be like 32x32 with integers")
```
- Converts both parts to integers.
- `.strip()` removes any accidental spaces like `" 64 x 128 "`
- If conversion fails, raises a clear error. 

```
if w <= 0 or h <= 0:
    raise argparse.ArgumentTypeError("grid must be positive")
```
- Validates the both width and height are positive numbers. 

```
return w, h
```
- Returns the results as a tuple `(width, height)`. 

### Image to grid
```
def quantize_image_to_grid(image_path: Path, grid_w: int, grid_h: int, k_colors: int):
```
- Defines a function named `quantize_image_to_grid`.
- Parameters:
    - `image_path`: the path to your input image file
    - `grid_w`/`gird_h`: the width and height in grid cells, this sets the resolution of your board. 
    - `k_colors`: the number of distinct colors to keep when simplifying the image. 

1. Load and resize the image
```
img = Image.open(image_path).convert("RGB")
```
- Opens the image file using Pillow (PIL).
- Converts it to RGB mode to ensure it has 3 color channels. 

```
img_small = img.resize((grid_w, grid_h), Image.Resampling.BILINEAR)
```
- Shrinks the original image down to the specified grid size. 
- This means each pixel in this smaller image represents one cell in your final board. 
- Uses bilinear interpolation for smooth resizing. 

2. Quantize to limited colors
```
img_q = img_small.quantize(colors=k_colors, method=Image.MEDIANCUT)
```
- Reduces the image's color variety to only `k_colors` using the Median Cut algorithm. 
- The result `img_q` is a palette image, each pixel stores an index referring to a palette color. 

3. Extract palette data
```
raw_pal = img_q.getpalette() or []
```
- Retrieves the flat palette list, like `[R0,G0,B0,R1,G1,B1,...]`
- If no palette exists, returns an empty list. 

4. Build palette index to RGB dictionary
```
pal_idx_to_rgb = {}
for idx in range(256):
    base = 3 * idx
    if base+2 < len(raw_pal):
        pal_idx_to_rgb[idx] = (
            raw_pal[base+0],
            raw_pal[base+1],
            raw_pal[base+2],
        )
```
- There can be up to 256 colors in a Pillow palette. 
- For each possible palette index:
    - Compute the base offset `3*idx` in the flat palette list.
    - If valid, extract its 3 RGB values.
    - Store them as a tuple `(R,G,B)` in a dictionary, like `{0: (r,g,b), 1: (r,g,b), ...}`
- This makes color lookup easier later. 

5. Build "label map" 1...K
```
idxs = np.array(img_q, dtype=np.uint8)
```
- Converts the quantized image into a NumPy array of integers. 
- Each value is a palette index (0-255)

```
uniq = np.unique(idxs)
```
- Gets the set of unique palette indices actually used in this image (there might be fewer than 256). 

```
idx_to_label = {int(u): i+1 for i, u in enumerate(uniq)}
```
- Builds a compact mapping:
    - The smallest used palette index gets label `1`. 
    - The next gets label `2`. 
- So you end up with labels in a continuous range [1...K]

```
labels = np.vectorize(lambda v: idx_to_label[int(v)], otypes=[np.int32])(idxs)
```
- Applies the mapping to every pixel in `idxs`, producing a 2D `labels` array of the same shape. 
- Each pixel now holds a label number 1...K instead of a palette index. 

6. Build compact palette
```
palette = {}
for u in uniq:
    label = idx_to_label[int(u)]
    palette[label] = pal_idx_to_rgb.get(int(u), (0,0,0))
```
- Creates a new dictionary `palette` mapping label to RGB.
- For each used palette index `u`:
    - Get its label number (`idx_to_label[u]`)
    - Get its RGB fromthe earlier dictioanry `pal_idx_to_rgb`. 
    - Store it in `{label: (R,G,B)}` form. 

7. Build a small posterized preview
```
preview = Image.new("RGB", (grid_w, grid_h))
px = preview.load()
```
- Creates a new empty RGB image of the same grid size. 
- `px` is a pixel access object for setting pixel values. 

```
for y in range(grid_h):
    for x in range(grid_w):
        px[x,y] = palette[int(labels[y,x])]
```
- Loops through every pixel (grid cell).
- Looks up the label at that position (`labels[y,x]`). 
- Finds its corresponding RGB color. 
- Fills the pixel with that color. 
- The result is a posterized miniature preview showing the simplified color grid. 

8. Return everything
```
return labels.astype(np.int32), palette, preview
```
- Returns:
    - `labels`: 2D NumPy array of integer color labels (1...K).
    - `palette`: mapping of label to RGB color. 
    - `preview`: a tiny color image for visualization. 

### draw grid board
Draw the "numbered hint sheet". 
Takes the numeric `labels` array and renders each cell as a small square with a centered number. 
```
def draw_numbered_board(labels: np.ndarray, cell_px: int, palette: dict | None = None, show_grid: bool = True, numbers_alpha: int = 255) -> Image.Image:
```
- Purpose: Create a large image where each grid cell is drawn as a square with its label number in the middle.
- Parameters:
    - `labels`: a 2D NumPy array of integers (each is a color label).
    - `cell_px`: pixel size of each cell (the zoom factor). 
    - `palette`: optional dictionary `{label: (R,G,B)}`. If provided, the cells could be colored. 
    - `show_grid`: whether to draw faint borders around cells.
    - `numbers_alpha`: transparency (0-255) for text. 255=fully opaque. 

1. Compute image size
```
h, w = labels.shape
W = w * cell_px
H = h * cell_px
```
- Gets the height (`h`) and width (`w`) in grid cells.
- Each cell will occupy `cell_px * cell_px` pixels. 
- Compute final image size in pixels:
    - Width = `w * cell_px`, Height = `h * cell_px`. 

2. Create a blank RGBA image and drawing context
```
img = Image.new("RGBA", (W,H), (255,255,255,255))
draw = ImageDraw.Draw(img)
```
- Creates a new white backgound image with alpha channel (`RGBA`). 
- `ImageDraw.Draw(img)` gives a drawing surface for rectangles and text. 

3. Select font size
```
font = None
fo size in (int(cell_px * 0.65), int(cell_px * 0.55), int(cell_px * 0.45)):
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size)
        break
    except Exception:
        font = None
if font is None:
    font = ImageFont.load_default()
```
- Tries to find a readable font size relative to the cell:
    - Starts big (`65%` of cell size), then smaller (`55%`, `45%`) if the font file fails.
- Uses **DejaVuSans.ttf**, a common default system font. 
- If that is not found, falls back to Pillow's build-in font. 
- This ensures numbers always appear even if no font is available. 

4. Define colors
```
text_color = (80,80,80, numbers_alpha)
grid_color = (200,200,200,255)
```
- `text_color`: medium-dark gray text, transparent depending on `number_alpha`. 
- `grid_color`: light gray for grid outlines. 

5. Loop over all cells
```
for y in range(h):
    for x in range(w):
        cx0 = x * cell_px
        cy0 = y * cell_px
        rect = (cx0, cy0, cx0+cell_px, cy0+cell_px)
```
- Loops through each cell in the grid.
- Computes the top-left corner `(cx0, cy0)` of that cell in pixels.
- Defines a bounding box `(x0, y0, x1, y1)` for the rectangle. 

6. Draw grid lines
```
if show_grid:
draw.rectangle(rect, outline=grid_color)
```
- If `show_grid=True`, draws a light gray border rectangle.
- The inside remains white. 
- This makes cells distinct, forming the "grid" effect. 

7. Draw centered number in the cell
```
n = str(int(labels[y,x]))
```
- Reads the label number from the array and converts it to string for drawing. 

```
tb = draw.textbbox((0,0), n, font=font)
tw, th = tb[2]-tb[0], tb[3]-tb[1]
```
- Computes the text bounding box for that number using the chosen font. 
- `tw`,`th` = width and height of the rendered text. 

```
tx = cx0 + (cell_px - tw) // 2
ty = cy0 + (cell_px - th) // 2
```
- Centers the text in the cell:
    - Horizontal center = cell midpoint minus half text width
    - Vertical center = cell midpoint minus half text height

8. Add background patch under text
```
pad = max(2, cell_px // 2)
draw.rectangle((tx-pad, ty-pad, tx+tw+pad, ty+th+pad), fill=(255,255,255, int(0.8*numbers_alpha)))
```
- Draws a small white rectangle behind hte number to improve readability
- Slightly larger than the text
- It's partially transparent
- This is usefull if later overlay this sheet on top of colored cells. 

9. Draw the actual number
```
draw.text((tx,ty), n, font=font, fill=text_color)
```
- Draws the label number centered in the cell, using the selected font and gray color. 

10. Return the image
```
return img
```
- Returns the fully rendered RGBA image, a large numbered board image ready to save. 

### Save results to disk
```
def save_outputs(out_dir: Path, labels: np.ndarray, palette: dict, preview_small: Image.Image, cell_px: int):
```
- Purpose: Save all generated outputs of your color-by-number conversion
- Parameters: 
    - `out_dir`: target directory for saving files
    - `labels`: 2D NumPy array of color labels (1...K)
    - `palette`: dictionary mapping `{label: (R,G,B)}`
    - `preview_small`: a small, low-res image preview
    - `cell_px`: pixel size used for rendering the numbered board

1. Create output folder
```
out_dir.mkdir(parents=True, exist_ok=True)
```
- Ensures that the output directory exists:
    - Creates it if it doesn't
    - Doesn't raise an error if it already exists. 

2. Save labels array
```
np.save(out_dir/"labels.npy", labels)
```
- Saves your `labels` NumPy array in `.npy` format
- This preserves all shape and dtype information

3. Save palette as JSON
```
pal_json = {int(k): [int(v[0]), int(v[1]), int(v[2])] for k, v in palette.items()}
```
- Converts your palette dict into a JSON-friendly form:
    - JSON doesn't support tuples, so `(R,G,B)` -> `[R,G,B]`
    - Ensures all values are regular Python `int`

```
with open(out_dir/"palette.json", "w") as f:
    json.dump(pal_json, f, indent=2)
```
- Saves this dictionary to `palette.json` with nice indentation

4. Save enlarged "poster preview"
```
scale = max(4, 512//max(labels.shape[0], labels.shape[1]))
```
- Determines how much to upscale the small preview for better visibility
- The goal: make the largest dimension at least ~512 pixels.
- Mininum scale factor = 4

```
poster_big = preview_small.resize(
    (preview_small.width*scale, preview_small.height*scale),
    Image.Resampling.NEAREST
)
```
- Enlarges your small preview using nearest-neighbor scaling
- This keeps sharp pixel edges ferfect for grid-like poster art

```
poster_big.save(out_dir/"poster_preview.png")
```
- Saves the upscaled color poster to `.png` file. 
- This image is the colored final look. 

5. Save "numbered board" (hint sheet)
```
board_img = draw_numbered_board(labels, cell_px=cell_px, palette=None, show_grid=True, numbers_alpha=255)
```
- Calls your earlier function `draw_numbere_board()` to generate a board image:
    - Shows the grid numbers only, no colors (palette=None).
    - Draws light grid lines and fully opaque numbers (`alpha=255`).

```
board_img.convert("RGB").save(out_dir/"board_numbers.png")
```
- Converts from RGBA to plain RGB (drops transparency)
- Saves it as `board_numbers.png`. 
- This is the printable "paint-by-numbers" guide image. 

### Main
1. Define the main function
```
def main():
```
- Defines the main program logic
- This function will only run when the script is executed directly from the command line. 

2. Create an argument parser
```
parser = argparse.ArgumentParser(description="Generate Color-by-Bumber grid, labels, palette, and numbered board.")
```
- Creates an `ArgumentParser` instance from Python's build-in `argparse` module. 

3. Define command-line arguments
```
parser.add_argument("image", help="input image path")
```
- Positional argument (required): the path to the input image. 

```
parser.add_argument("--grid", type=parse_xy, default=(32,32), help="grid size, e.g. 32x32 or 48x36")
```
- Optional argument (`--grid`):
    - Takes a value such as `32x32`. 
    - Uses the earlier helper `parse_xy` to parse it into a tuple `(32,32)`.
    - Default: `(32,32)` if no specification. 
    - Defines how many cells in width and height. 

```
parser.add_argument("--colors", type=int, default=8, help="number of colors K")
```
- Number of colors to quantize the image to (default=8)

```
parser.add_argument("--cell", type=int, default=28, help="cell size (pixels) for board_numbers.png")
```
- Pixel size of each cell when drawing the numbered board. 

```
parser.add_argument("--out", type=str, default="cbn_out", help="output folder")
```
- Output directory name (default=`"cbn_out"`)
- The folder will be created automatically if it doesn't exist. 

4. Parse the arguments
```
args = parser.parse_args()
```
- Parses all the arguments from the command line into an `args` object.

5. Convert input/output paths to Path objects
```
in_path = Path(args.image)
out_dir = Path(args.out)
```
- Converts plain strings to `Path` objects (from `pathlib`). 

6. Process the image
```
labels, palette, preview_small = quantize_image_to_grid(
    in_path, grid_w=args.grid[0], grid_h=args.grid[1], k_colors=args.colors
)
```
- Calls your earlier quantization function:
    - `in_path`: input image file
    - `grid_w`, `grid_h`: grid size (from `--grid`)
    - `k_colors`: number of colors (from `--colors`)
- Returns:
    - `labels`: 2D array of color labels 1...K
    - `palette`: dict mapping label -> (R,G,B)
    - `preview_small`: small colorlized grid image

7. Save all results
```
save_outputs(out_dir, labels, palette, preview_small, cell_px=args.cell)
```
- Call the save_output() helper
- Saves everything (NumPy array, JSON palette, preview, and numbered board) into the output directory.
- `cell_px` defines the zoom level for `board_numbers.png`. 

8. Print summary messages
```
print("Done. Wrote:")
print(f"- {out_dir/'labels.npy'} (HxW int labels 1...K)")
print(f"- {out_dir/'palette.json'} ({{label: [R,G,B]}})")
print(f"- {out_dir/'board_numbers.png'} (grid with per-cell numbers)")
print(f"- {out_dir/'poster_preview.png'} (K-color pixel preview)")
```
- Prints a clear summary of what was generated and where the files are saved.

9. Run only if hte script is executed directly
```
if __name__ in "__main__":
    main()
```
- This line ensures that `main()` runs only when execute this file directly, not when it's imported as a module.
- When imported, nothing happens automatically. 


## Color By Number 
### Import modules
1. `import argparse`
- Imports python's build-in argument parsing library
- It lets you create command-line interfaces, which you can define options, defaults, hep text, etc. 

2. `import json`
- Loads and saves data in JSON (JavaScript Object Notation) format, a universal text data format. 
- Useful for storing things such as the palette

3. `import os`
- Gives access to operating system utilities, including paths, environment variables, etc. 

4. `from pathlib import Path`
- Imports `Path` from the modern `pathlib` module 
- Provides an object-oriented way to handle file system paths. 
- `Path` objects automatically adjust to Windows (`\`) or macOS/Linux (`/`) paths. 

5. `import datetime`
- Imports python's date and time utilities, which is used for timestamps, filenames, or loggings. 

6. `import numpy as np`
- Import NumPy, a powerful numerical computing library.
- Used for:
    - Arrays and matrices
    - Image data manipulation
    - Math operations

7. `import pygame`
- Imports teh Pygame library, a popular framework for building games and interactive visualizations in python.
- It handles: 
    - Windows and screen display
    - Drawing graphics
    - Keyboard/mouse input
    - Sound playback

8. `from PIL import Image`
- Imports `Image` from the Pillow library, python's standard image-processing toolkit. 
- It can:
    - Open and save images
    - Convert color modes
    - Resize, crop, draw, or paste images

### Utility IO
#### `load_puzzle()`
```
def load_puzzle(pdir: Path):
```
- Defines a function that loads puzzle data from a directory (`pdir`).
- `pdir` is a `Path` object pointing to the folder that contains your saved files. 

1. Load the labels array
```
labels = np.load(pdir/"labels.npy")
```
- uses NumPy to load the array you saved earlier with `np.save()`. 
- This gives you back the 2D grid of integers where:
    - Each entry is a label between `1...K`, representing a color region
    - Shape = `(height, width)` of the puzzle grid.

2. Load the color palette (JSON)
```
with open(pdir/"palette.json", "r") as f:
    palette = {int(k): tuple(v) for k, v in json.load(f).items()}
```
- Opens the JSON file you created earlier
- `json.load(f)` reads it as a dictionary, such as `{"1": [255,0,0], "2":[0,255,0]}`
- The dictionary comprehension converts:
    - Key `"1"` -> integer `1`
    - Value `[255,0,0]` -> tuple `(255,0,0)`
- Final result: `{1: (255,0,0), 2: (0,255,0)}`

3. Define the preview image path
```
preview_path = pdir / "browser_preview.jpb"
```
- Sets the expected preview image filename
- This is the small thumbnail used in the browser screen. 

4. Check if the preview image exists
```
if not preview_path.exists():
```
- If the file `browser_preview.jpg` does not exist in the folder, then we have to generate one automatically. 

5. Auto-generate a fallback preview
```
img = render_solved_pil(labels, palette, scale=8)
```
- Calls another function `render_solved_pil()` that:
    - Takes the `labels` array and `palette` colors
    - Creates a PIL Image of the fully solved puzzle (each label -> its color)
    - Scales it up by `scale=8` for visibility
- Essentially, it reconstructs the color preview from data.

```
preview_path = pdir/"_autogen_preview.png"
img.save(preview_path)
```
- Sets the path for the autogenerated preview
- Saves the rendered image as `_autogen_prevew.png` inside the puzzle directory.

6. Return everything
```
return labels, palette, preview_path
```
- Returns three objects:
    - `labels` -> 2D NumPy array (grid of numbers)
    - `palette` -> dictionary mapping number -> (R,G,B)
    - `preview_path` -> the `Path` to the preview image file

#### `render_solved_pil()`
```
def render_solved_pil(labels: np.ndarray, palette: dict[int, tuple], scale=1):
```
- Defines the function `render_solved_pil()`
- Parameters:
    - `labels`: a 2D NumPy array of integers (shape=height x width)
        - Each number represents a color label
    - `palette`: a dictionary mapping label -> RGB color
    - `scale`: how much to enlarge the image (default 1 = no scaling)
- Goal: Create a full-color image from these labels. 

1. Get grid dimensions
```
h, w = labels.shape
```
- Reads the height (`h`) and width (`w`) of the grid from the NumPy array
- Example: if `labels` is 32x32, then `h=32`, `w=32`.

2. Create a new empty image
```
img = Image.new("RGB", (w, h))
```
- Creates a blank RGB image of size `(w, h)` pixels
- Initially, every pixel is black `(0,0,0)` by default. 

3. Access pixel map
```
pix = img.load()
```
- Gets a pixel access object
- This allows you to color each cell individually

4. Paint each pixel using the label and palette
```
for y in range(h):
    for x in range(w):
        pix[x,y] = palette[int(labels[y,x])]
```
- Loops through all pixel coordinates `(x,y)` in the grid
- For each pixel:
    - Reads the label number at that position: `labels[y,x]`
    - Looks up that number in the `palette` dictionary to get its RGB color
    - Assigns that color to the image pixel
- By the end of this double loop, every pixel in `img` matches its correct color from the palette. 

5. Optional scaling
```
if scale > 1:
    img = img.resize((w * scale, h * scale), Image.Resampling.MEAREST)
```
- If you set `scale` > 1, the final image is enlarged for easier viewing. 
- `Image.Resampling.NEAREST` ensures sharp pixel edges (no blurring)

6. Return the final image
```
return img
```
- Returns the PIL Image object that represents the fully colored, completed puzzle. 

### Button
Pygame GUI component: `ImageButton`. 
It represents a clickable button that displays an image, with hover and scaling effects.

#### Class overview
```
class ImageButton:
"""
Image-based button with hover state
- rect: where the button should sit on screen
- img_path: normal PNG
- hover_img_path: hover PNG
- scale_mode: 'fit' (default), 'stretch', 'fit_no_upscale', 'none'
- padding: inset (px) inside rect before fitting/scaling the image
- hover_scale: optional subtle enlargement on hover
"""
```
- The button displays an image (PNG)
- When the mouse hovers, it display a different hover image or scale slightly larger
- The button's size and position are defined by a `pygame.Rect`. 
- Different scaling modes determine how the image fits into the rectangle:
    - `fit`: keep aspect ratio, fit as large as possible
    - `stretch`: distort to exactly fill the rectangle
    - `fit_no_upscale`: same as `fit` but won't enlarge small images
    - `none`: no scaling at all
- `padding`: margin inside the rect
- `hover_scale`: how much to enlarge the image when hover 

#### `__init__`: Constructor
```
def __init__(self, rect: pygame.Rect, img_path: str, hover_img_path: str | None=None, scale_mode: str="fit", padding: int=0, hover_scale: float=1.0)
```
- Initialize the button object.

1. Store properties
```
self.rect = pygame.Rect(rect)
self.scale_mode = scale_mode
self.padding = int(padding)
self.hover_scale = float(hover_scale)
self.enabled = True
```
- Converts `rect` into a proper `pygame.Rect` object
- Stores configuration settings
- Sets the button to clickable by default

2. Define helper to load image
```
def _load(path):
    s = pygame.image.load(path).convert_alpha()
    return s
```
- Internal helper function for loading images with tranparency (`convert_alpha()` keeps the alpha channel for PNGs)

3. Load main and hover images
```
self.img = _load(img_path)
if hover_img_path and Path(hover_img_path).exists():
    self.img_hover = _load(hover_img_path)
else:
    self.img_hover = self.img
```
- Loads the normal button image
- If a separate hover image path is provided and exists, load it
- Otherwise, fall backto using the same image for both states

4. Initialize cache
```
self._cache_size = None
self._scaled_normal = None
self._scaled_hover = None
```
- These are cached copies of scaled images
- The button might be drawn many times, so instead of resizing the image every frame, it stores the scaled versions.
- `_cache_size` tracks the last size used. 

#### `_rescale_if_needed`: Resize logic
```
def _rescale_if_needed(self):
    if self._cache_size == self.rect.size:
        return
```
- If the rectangle size hasn't changed since last time, reuse the cache. 

1. Get dimentions
```
w, h = self.rect.size
iw, ih = self.img.get_size()
maxw, maxh = max(1, w-2*self.padding), max(1, h-2*self.padding)
```
- `w, h`: target button area size
- `iw, ih`: original image dimensions
- `maxw, maxh`: available space inside the button

2. Different scaling modes
**Stretch**
```
if self.scale_mode == "stretch":
    tn = (maxw, maxh)
    self._scaled_normal = pygame.transform.smoothscale(self.img, tn)
    self._scaled_hover = pygame.transform.smoothscale(self.img_hover, tn)
```
- Scales image exactly to fill width & height
- `smoothscale`: high quality scaling
- Both normal and hover images are resized

**Fit/FIt-no-upscale**
```
elif self.scale_mode in ("fit", "fit_no_upscale"):
    scale = min(maxw/iw, maxh/ih)
    if self.scale_mode == "fit_no_upscale":
        scale = min(1.0, scale)
    tw, th = max(1, int(iw*scale)), max(1, int(ih*scale))
    self._scaled_normal = pygame.transform.smoothscale(self.img, (tw, th))
    self._scaled_hover = pygame.transform.smoothscale(self.img_hover, (tw, th))
```
- Calculates a uniform scale factor to fit within the box while keeping aspect ratio
- `fit_no_upscale` prevents enlargement
- Resizes both versions accordingly 

**None**
```
else:
    self._scaled_normal = self.img
    self._scaled_hover = self.img_hover
```
- Keeps the images at original size

3. Update cache
```
self._cache_size = self.rect.size
```
- Records the size so we know when to skip re-scaling later

#### `draw`: Render the button
```
def draw(self, surf: pygame.Surface):
```
- Draws the button on the given surface (`surf`), usually the main pygame screen. 

1. Ensure images are scaled
```
self._rescale_if_needed()
```
- Calls scaling logic if needed

2. Check if mouse is hovering
```
hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
```
- `collidepoint()` returns `True` if the mouse cursor is currently inside the button rectangle
- Only counts if the button is enabled

3. Pick correct image
```
s = self._scaled_hover if hovered else self._scaled_normal
```
- Chooses the hover image when the mouse is over the button; otherwise, the normal one. 

4. Optional hover enlargement
```
if hovered and self.hover_scale != 1.0:
    tw, th = s.get_size()
    tw2, th2 = max(1, int(tw*self.hover_scale)), max(1, int(th*self.hover_scale))
    s = pygame.transform.smoothscale(s, (tw2, th2))
```
- If hover scaling is enabled, enlarge the image smoothly with that factor
- Creates a slight "zoom-in" effect when hovered

5. Draw the image centered in its rectangle
```
surf.blit(s, s.get_rect(center=self.rect.center))
```
- Blits (draws) the image onto the target surface
- Centers it within the button rectangle

#### `clicked`: Detect button press
```
def clicked(self, event) -> bool:
    return (self.enabled 
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos))
```
- Checks if:
    - The button is enabled
    - The event is a left mouse click (`button == 1`)
    - The click position is inside the button rectangle
- Returns `True` if the button was clicked

#### `set_enabled`: Enable or disable button
```
def set_enabled(self, val: bool):
    self.enabled = bool(val)
```
- Turns the button on or off
- Disabled buttons can't be hovered or clicked


### Constants
```
STATE_WELCOME = "WELCOME"
STATE_BROWSER = "BROWSER"
STATE_PLAY = "PLAY"
STATE_FINISHED = "FINISHED"
```
- `STATE_WELCOME`: The welcome screen shown when the app starts
- `STATE_BROWSER`: The level/puzzle browser where the user can choose which puzzle to play
- `STATE_PLAY`: The main gameplay state where teh player fills colors or interacts with the puzzle
- `STATE_FINISH`: The end screen after a puzzle is completed


### Color By Number APP
#### Class definition and initialization
```
class ColorByNumberApp:
    def __init__(self, puzzles_dir: Path, width=1100, height=800):
```
- Defines the main application class
- `puzzles_dir`: a folder containing all saved puzzle data
- `width`, `height`: window size in pixels
- Everything inside `__init__()` runs once when create an instance of this app

1. Initialize pygame and window
```
pygame.init()
pygame.display.set_caption("Color By Number")
self.screen = pygame.display.set_mode((width, height))
self.W, self.H = width, height
self.clock = pygame.time.Clock()
```
- `pygame.init()`: initialize all pygame subsystems
- `set_caption()`: sets the window title
- `display.set_mode()`: creates the main game window of the specified size
- Stores `width` and `height` as `self.W` and `self.H`
- Creates a `Clock` object to control FPS and timing during the game loop

2. Fonts setup
```
self.font = pygame.font.SysFont(None, 28)
self.big_font = pygame.font.SysFont(None, 48)
self.slogan_font = pygame.font.Font("font/AaZhuNiWoMingMeiXiangChunTian-2.ttf", 28)
self.title_font = pygame.font.Font("font/LiXuKeShuFa-1.ttf", 44)
```
- Loads different fonts for different text sizes or purposes:
    - `SysFont(None, 28)` uses a default system font.
    - Two custom fonts are loaded from the `font/` directory:
        - One for slogan, another for title. 
- These fonts are used later rendering text on menus or UI

3. Define color palette (UI colors)
```
self.bg = (250,250,250)
self.panel = (255,255,255)
self.grid_c = (210,210,210)
self.text_c = (40,40,40)
```
- Common color variables (RGB tuples):
    - `bg`: light gray background
    - `panel`: pure white UI panels
    - `grid_c`: light gray grid lines
    - `text_c`: dark gray text color

4. Game state variable
```
self.state = STATE_WELCOME
```
- Sets teh initial screen state to `WELCOME`
- The app will change this value later to navigate between screens

5. Load puzzle list
```
self.puzzles = []
```
- Prepares an empty list to hold all available puzzles found in `puzzles_dir`

**Scan and load each puzzle folder**
```
for sub in sorted(p for p in Path(puzzles_dir).iterdir() if p.is_dir()):
    try: 
        labels, palette, preview_img_path = load_puzzle(sub)
        complete_path = sub/"browser_complete.jpg"
        preview_surf = self._load_square_preview(preview_img_path, 360)
        if complete_path.exists():
            complete_surf = self._load_square_preview(complete_path, 360)
```
- Iterates through all subdirectories inside `puzzles_dir`
- For each:
    - Calls `load_puzzle()`, which load `labels.npy`, `palette.json`, and a preview image path
    - Prepares paths for:
        - `browser_preview.jpg`: the small puzzle preview
        - `browser_complete.jpg`: the finished/colored preview (if exists)
    - Loads both images into pygame surfaces (`preview_surf` and `complete_surf`) using `_load_square_preview()`

**Store puzzle info**
```
self.puzzles.append(
    "name": sub.name.
    "dir": sub,
    "labels": labels,
    "palette": palette,
    "preview": preview_surf,
    "complete_preview": complete_surf,
)
```
- Adds each puzzle as a dictionary into the `self.puzzles` list

**Handle loading errors**
```
except Exception as e:
    print(f"Skipping {sub}: {e}")
```
- If something goes wrong, it skips that puzzle. 

6. Welcome screen setup
**Button for "Start"**
```
bw, bh = 440, 60
self.btn_start = ImageButton(
    pygame.Rect((self.W-440)//2, int(self.H//2+200), bw, bh),
    str("assets/btn_start.png"),
    str("assets/btn_start_hover.png"),
    scale_mode="fit", padding=6, hover_scale=1.03
)
```
- Creates a Start Button centered horizontally and near the bottom of the screen
- Uses the `ImageButton` class
- Slightly enlarges on hover
- The button switches images when hovered

**Welcome image**
```
self.welcome_img = None
welcome_path = Path("assets/welcome.jpg")
if welcome_img.exists():
    try:
        self.welcome_img = pygame.image_load(str(welcome_path)).convert.alpha()
    except Exception as e:
        print(f"[welcome image load failed] {e}")
```
- Tries to load a welcome background image if available
- Stores it as a pygame surface
- Handles missing or corrupted files gracefully

7. Browser layout settings
```
self.browser_scroll = 0
self.browser_cell = 420
self.browser_cols = 2
self.browser_card_max = 140
self.browser_card_gap = 50
self.browser_title_h = 100
```
- Defines how the browser screen looks:
    - `browser_scroll`: scroll offset when there are many puzzles
    - `browser_cell`: vertical space per puzzle card
    - `browser_cols`: how many columns of puzzles to show
    - `browser_card_max`: maximum number of puzzles to show per scroll page
    - `browser_card_gap`: space between cards
    - `browser_title_h`: height of the title area above cards

8. Gameplay variables
```
self.active = None
self.selected_label = 1
self.filled_ok = None
```
- `active`: when the user starts playing, this holds the selected puzzle's info
- `selected_label`: the currently chosen color (label number)
- `filled_ok`: grid tracking which cells are already colored correctly

9. Off-screen drawing board setup
```
self.BASE_CELL = 26
self.board_surface = None
self.min_zoom_fit = 0.5
self.max_zoom = 6.0
```
- Sets up values for the "play" canvas:
    - Each grid cell is 26x26 pixels logically
    - The board is drawn on an offscreen surface first
    - Allows zooming between 0.5x and 6x

10. Camera and interaction state
```
self.zoom = 1.0
self.pan = pygame.Vector2(30,30)
self.dragging = False
self.drag_anchor = None
```
- `zoom`: current zoom level
- `pan`: 2D vector offset for camera movement
- `dragging`: whether the mouse is dragging the board
- `drag_anchor`: starting point for drag motion

```
self.painting = False
self.last_paint_cell = None
self.dragging_pan = False
self.progress_dirty = False
```
- `painting`: whether the player is currently coloring cells
- `last_paint_cell`: used to avoid redundant painting on same cell
- `dragging_pan`: speficially tracks camera drag
- `progress_dirty`: marks unsaved progress that should be saved after a paint action

11. Palette bar
```
self.palette_bar_h = 110
self.palette_swatches = []
self.palette_page = 0
self._palette_pages = 1
self._palette_left_btn = pygame.Rect(0,0,0,0)
self._palette_right_btn = pygame.Rect(0,0,0,0)
```
- The color palette sits at the bottom of the play screen
- Stores:
    - Bar height (`palette_bar_h`)
    - List of clickable swatches (`palette_swatches`)
    - Pagination variables if there are too many colors to show at once
    - Rectangles for left/right arrow buttons to flip between palette pages

12. Back button in play screen
```
self.btn_play_back = ImageButton(
    pygame.Rect(16, 12, 110, 40),
    str("assets/btn_back.png"),
    str("assets/btn_back_hover.png"),
    scale_mode="fit", padding=4, hover_scale=1.03
)
```
- Adds a small Back Button inthe top left corner of the play screen
- It can return the user to the browser screen

13. Buttons in finish screen
```
self.btn_save = ImageButton(
    pygame.Rect((self.W-440)//2, self.H-60*2-40, 440, 60),
    str("assets/btn_save.png"),
    str("assets/btn_save_hover.png"),
    scale_mode="fit", padding=6, hover_scale=1.03
)
self.btn_back = ImageButton(
    pygame.Rect((self.W-440)//2, self.H-60-20, 440, 60),
    str("assets/btn_back_finish.png"),
    str("assets/btn_back_finish_hover.png"),
    scale_mode="fit", padding=6, hover_scale=1.03
)
```
- Two buttons on the FINISHED screen:
    - `btn_save`: save the final result
    - `btn_back`: go back to the browser
- Both centered horizontally at the bottom, with small hover animations

#### helper
1. `_fill_cell_if_match(self, cx, cy)`
**Function definition**
```
def _fill_cell_if_match(self, cx, cy):
    """Fill cell (cx, cy) if it's the selected label and not already filled."""
```
- The function tries to fill the grid cell at coordinates `(cx, cy)`, but only if:
    - The cell's number matches the currently selected label
    - The cell hasn't already been filled

**Retrieves the grid**
```
labels = self.active["labels"]
H, W = labels.shape
```
- Retrieves the label grid for the currently active puzzle
- `H` and `W` = number of rows and columns

**Ensure coordinates are valid**
```
if not (0 <= cx < W and 0 <= cy < H):
    return False
```
- Checks if the given coordinates are within bounds
- If the player's cursor is outside the grid, do nothing

**Get the label number**
```
lab = int(labels[cy, cx])
```
- Gets the label number of that specific cell

**Define filling conditions**
```
if (not self.filled_ok[cy, cx]) and (lab == self.selected_label):
    self.filled_ok[cy, cx] = True
    self.color_filled[lab] += 1
    self.progress_dirty = True
    return True
```
- Checks:
    - If that cell isn't already filled (`filled_ok` = False)
    - And its label equals the currently selected color (`lab == self.selected_label`)
- If both conditions hold:
    - Marks that cell as filled (`True`)
    - Increments a counter (`self.color_filled[lab]`) that tracks how many cells of that color have been filled
    - Marks `self.progress_dirty = True` so the app knows to autosave progress later
    - Returns `True` to indicate something was filled

**Return**
```
return False
```
- If the cell didn't match or was already filled, returns False

2. `_bresenham_cell(self, c0, c1)`
**Function definition**
```
def _bresenham_cell(self, c0, c1):
    """Yield grid cells between c0 and c1 inclusive using Bresenham."""
```
Bresenham's line algorithm: a classic alogrithm to find all the grid cells that form a straight line between two points `(c0)` and `(c1)`
When the player drags the mouse from one cell to another, the app can fill in all cells between them, creating a smooth painting stroke instead of just discrete clicks.

**Unpack coordinates**
```
x0, y0 = c0
x1, y1 = c1
```
- Unpacks the starting (`c0`) and ending (`c1`) cell coordinates

**Setup Bresenham parameters**
```
dx = abs(x1-x0); sx = 1 if x0 < x1 else -1
dy = -abs(y1-y0); sy = 1 if y0 < y1 else -1
err = dx+dy
```
- Sets up Bresenham's parameters:
    - `dx`, `dy` = absolute differences between x and y
    - `sx`, `sy` = step direction (+1 or -1)
    - `err` = cumulative error used to decide when to move along x or y

**Start generator**
```
while True:
    yield (x0, y0)
```
- This function is a generator, it yields each grid coordinate one by one instead of returning a list
- The first yielded cell is the starting cell `(x0,y0)`. 

**Stop when cell reached**
```
if x0 == x1 and y0 == y1:
    break
```
- When the end cell is reached, stop generating

**Bresenham math**
```
e2 = 2*err
if e2 >= dy:
    err += dy
    x0 += sx
if e2 <= dx:
    err += dx
    y0 += sy
```
- Bresenham's math: adjusts error terms and moves horizontally or vertically to stay as close as possible to the ideal line. 
- Details about [Bresenham algorithm](https://www.geeksforgeeks.org/dsa/bresenhams-line-generation-algorithm/)

3. `_paint_line_between(self, c0, c1)`
**Function definition**
```
def _paint_line_between(self, c0, c1):
    """Paint along the path between two cells, respecting selected label."""
```
- Ties the previous two functions together, which paints a continuous stroke between two cells. 

**Ties 2 previous functions**
```
for cx, cy in self._bresenham_cell(c0, c1):
    self._fill_cell_if_match(cx, cy)
```
- Uses `_bresenham_cell()` to get all intermediate cells between `c0` and `c1`
- For each of those cells, calls `_fill_cell_if_match()`
- So when the player drags quickly, every cell along the line gets filled. 

4. `_fit_center(self, surf, max_w, max_h)`
**Function definition**
```
def _fit_center(self, surf, max_w, max_h):
    """Scale surf to fit inside (max_w, max_h) while keeping aspect ratio"""
```
- Given a pygame surface and a bounding box, resize the image so that it fits inside the box while keeping its original proportions. 
- This prevents images from looking stretched or squashed. 

**Handle missing input**
```
if surf is None:
    return None
```
- If no surface is provided, simply return `None`

**Get the original surface size**
```
sw, sh = surf.get_size()
```
- `get_size()` returns the image's original width and height
    - `sw`: surface width
    - `sh`: surface height

**Calculate scale factor**
```
scale = min(max_w/sw, max_h/sh)
```
- Computes how much to scale the image so it fits within the given box
- `max_w/sw`: how much is neede to scale to fit width
- `max_h/sh`: how much is to scale to fit height
- Using `min()` ensures both width and height will stay within the box:
    - if the image too width, the width becomes the limiting factor
    - if the image too tall, the height becomes the limiting factor
- This keeps aspect ratio intact

**Compute target size**
```
tw, th = int(sw*scale), int(sh*scale)
```
- Multiples the original size by the scale factor to get the target width and height
- Uses `int()` to round down to whole pixels

**Resize smoothly**
```
return pygame.transform.smoothscale(surf, (tw, th))
```
- Uses pygame's `smoothscale()` to resize the image to new dimensions
- `smoothscale` gives higher-quality results than basic `scale`
- Returns the resized pygame surface

5. `_load_square_preview()`
**Function header**
```
def _load_square_preview(self, img_path: Path, box: int) -> pygame.Surface:
```
- `img_path`: the path to an image file
- `box`: the target size (both width and height) of the final square
- Returns a `pygame.Surface`, the format pygame uses to display images

**Load the image using Pillow**
```
img = Image.open(img_path).convert("RGB")
```
- Opens the image with Pillow (`Image.open()`)
- Converts it to RGB color mode (removes alpha if any)
- Now `img` is a `PIL.Image` object, which is easy to manipulate

**Get its dimensions**
```
w, h = img.size
```
- Retrieves the original width and height of the image

**Compute scale factor to fit inside the square**
```
scale = box/max(w,h)
```
- Finds the ratio to scale the image so that its largest dimension equals the square size (`box`)

**Resize the image**
```
img2 = img.resize((int(w*scale), int(h*scale)), Image.Resampling.NEAREST)
```
- Resizes the image proportionally using the scale factor
- `Image.Resampling.NEAREST` = nearest-neighbor resampling, preserves hard pixel edges
- `img2` is now the resized image

**Create a white square "canvas"**
```
canvas = Image.new("RGB", (box, box), (255,255,255))
```
- Creates a new blank square image of size `box x box`
- Fills it with white color
- This is a letterbox background, ensures all previews are square

**Center the resized image on canvas**
```
cx = (box - img2.size(0))//2
cy = (box - img2.size[1])//2
canvas.paste(img2, (cx, cy))
```
- Calculates offsets `(cx, cy)` to center the smaller image inside the white square
    - `cx` = horizontal padding (left margin)
    - `cy` = vertical padding (top margin)
- `paste()` places the resized image onto the white canvas

**Convert Pillow image to pygame surface**
```
mode = canvas.mode
data = canvas.tobytes()
surf = pygame.image.fromstring(data, canvas.size, mode)
```
- `canvas.mode` gives color mode
- `canvas.tobytes()` converts the image into a raw bytes buffer of pixel data
- `pygame.image.fromstring()` takes that byte data and creates a `pygame.Surface`

**Return surface**
```
return surf
```
- Returns the final `pygame.Surface`, a perfectly square, centered, scaled preview ready to `blit()` onto the main screen. 

6. `compute_min_zoom_fit()`
**Function definition**
```
def _compute_min_zoom_fit(self, labels):
```
- Takes `labels`, a 2D NumPy array
- Its shape defines the puzzle's height and width in number of cells
- Goal: figure out the minimum zoom level needed so the entire puzzle fits comfortably in visible region

**Get grid dimention**
```
H, W = labels.shape
```
- extracts the height (`H` rows) and width (`W` columns) of the puzzle grid

**Compute board size in pixels**
```
board_w = W*self.BASE_CELL
board_h = H*self.BASE_CELL
```
- Each grid cell has a fixed logical pixel size. Multiply by the number of cells to get the full board's pixel dimensions before zooming.

**Define available screen area**
```
margin = 20
avail_w = self.W-margin*2
avail_h = self.H-self.palette_bar_h-margin*2
```
- The app window has width `self.W` and height `self.H`
- But not all of it is available for showing the puzzle:
    - Subtract small margins on both sides
    - Remove the bottom palette bar area
- the results:
    - `avail_w` = usable horizontal space
    - `avail_h` = usable vertical space

**Handle edge cases**
```
if board_w == 0 or board_h == 0:
    return 0.5
```
- If the board has 0 width or height, return a default zoom value to prevent division errors. 

**Compute the zoom factor which fits the board in view**
```
return min(avail_w/board_w, avail_h/board_h)
```
- The zoom value determines how large each pixel of the board should appear on screen
    - `zoom=1.0`: 1 board pixel = 1 screen pixel
    - `zoom<1.0`: zoomed out (board appeared smaller)
    - `zoom>1.0`: zoomed in (board appeared larger)
- To fit the whole board on screen:
    - The scaled board width = `board_w*zoom` <= `avail_w`
    - The scaled board height = `board_h*zoom` <= `avail_h`
    - So taking the minimum ensures both dimensions fit


7. `_clamp_pan()`
**Function definition**
```
def _clamp_pan(self, labels):
    """Keep the board within a reasonable border. Centers it if smaller than the viewport"""
```
- Adjust the camera's `self.pan` (x,y offset) so that:
    - The player cannot drag the board outside the screen
    - If the board is smaller than the view, it is centered. 

**Get puzzle dimensions**
```
H, W = labels.shape
bw = W*self.BASE_CELL*self.zoom
bh = H*self.BASE_CELL*self.zoom
```
- `labels` is the grid of cells (height `H`, width `W`)
- `BASE_CELL` is the base pixel size per cell
- Multiply by `self.zoom` to get the actual pixel size on screen after scaling
    - `bw`, `bh`: the displayed width and height of the board

**Define the viewport area**
```
viewport_x = 0
viewport_y = 0
viewport_w = self.W
viewport_h = self.H-self.palette_bar_h
```
- The viewport = the visible window are where the board can appear
- The palette bar takes up space at the bottom, so `viewport_h` excludes that area
- Typically:
    - `(viewport_x, viewport_y)` = top_left corner of visible area
    - `(viewport_w, viewport_h)` = its size

**Define margin**
```
margin = 80
```
- Defines how much extra border is allowed before clamping

**Clamp horizontal position (X)**
```
if bw+2*margin <= viewport_w:
    self.pan.x = viewport_x + (viewport_w - bw) * 0.5
```
- If the board (plus some margin) is narrower than the viewport, the player cannot pan left or right. 
- So it is centered horizontally in the viewport

**Otherwise, board is wider than viewport**
```
else:
    min_x = viewport_x + viewport_w - bw - margin
    max_x = viewport_x + margin
    self.pan.x = max(min(self.pan.x, max_x), min_x)
```
- When the board is larger than the visible area:
    - `min_x` = the furthest that can pan left (the board's right edge is just visible)
    - `max_x` = the furthest that can pan right (so the board's left edge is just visible)
- Ensures `pan.x` stays within `[min_x, max_x]`
- If the player drag too far right, it stops at `max_x`
- If the player drag too far left, it stops at `min_x`

**Clamp vertical position (Y)**
```
if bh + 2*margin <= viewport_h:
    self.pan.y = viewport_y + (viewport_h - bh) * 0.5
else:
    min_y = viewport_y + viewport_h - bh - margin
    max_y = viewport_y + margin
    self.pan.y = max(min(self.pan.y, max_y), min_y)
```
- If the board is shorter than the available height, enter it vertically.
- otherwise:
    - `min_y` = how far that can pan up before the board bottom is hidden
    - `max_y` = how far that can pan down before the board top is hidden
    - clamp `pan.y` to stay within `[min_y, max_y]`

8. `_reset_camera()`
**Function definition**
```
def _reset_camera(self, labels):
```
- `labels`: the 2D NumPy array representing the puzzle grid
- Recalculates `self.zoom` (scale level) and `self.pan` (position offset) based on puzzle size and window dimensions

**Compute and store the minimum zoom level**
```
self.min_zoom_fit = max(0.1, self._compute_min_zoom_fit(labels))
```
- Calls `_compute_min_zoom_fit()` to get the zoom level that makes the entire puzzle board just fit inside the visible area
- Uses `max(0.1, ...)` to ensure the zoom never goes below `0.1` (prevents the board from shrinking to almost nothing). 
- This gets the smallest usable zoom that fits the full puzzle on screen

**Set the initial zoom**
```
self.zoom = max(self.min_zoom_fit, min(self.max_zoom, self.min_zoom_fit*1.0))
```
- Starts zooming at a pleasant level (not too small, not too zoomed in)
    - It multiplies `min_zoom_fit * 1.0`, which effectively same as `min_zoom_fit`, but this gives flexibility if you want to start slightly zoomed in later. 
- `min(..., self.max_zoom)` caps the zoom to avoid exceeding allowed zoom limits
- `max(..., self.min_zoom_fit)` ensures it is not smaller than the fit level
- `self.zoom` is clamped between `[min_zoom_fit, max_zoom]`

**Compute the board's pixel size at this zoom**
```
H, W = labels.shape
board_w = W * self.BASE_CELL * self.zoom
board_h = H * self.BASE_CELL * self.zoom
```
- Gets number of rows (`H`) and columns (`W`)
- Multiply by `BASE_CELL`, and gets the board size that will appear on screen

**Center the board on screen**
```
self.pan = pygame.Vector2((self.W - board_w) * 0.5, (self.H - self.palette_bar_h - board_h) * 0.5 + 20)
```
- This creates a 2D vector for camera offset (`self.pan`)
    - `(self.W - board_w) * 0.5` centers the board horizontally, the left margin and right margin will be equal
    - `(self.H - self.palette_bar_h - board_h) * 0.5` centers it vertically, but excludes the palette bar. 
    - The `+20` adds a small top margin
- Now, the puzzle appears neatly centered in the playable area when first loaded

**Clamp to safe bounds**
```
self._clamp_pan(labels)
```
- Calls `_clamp_pan()` to make sure the calculated pan position does not violate boundaries.

9. `_screen_to_board()`
**Function definition**
```
def _screen_to_board(self, pos):
```
- Takes the `pos`, which is a tuple of screen coordinates, usually the mouse position `(sx, sy)`
    - `sx`, `sy` are measured in screen pixels
- Goal: Convert `(sx, sy)` into coordinates on the puzzle board, taking into account panning and zooming

**Unpack the position**
```
sx, sy = pos
```
- Extracts the x and y components of the mouse position

**Convert from screen to board coordinates**
```
bx = (sx - self.pan.x) / self.zoom
by = (sy - self.pan.y) / self.zoom
```
- The board is drawn on screen with:
    - Zoom: scaling (enlarging or shrinking the board)
    - Pan: offset (shifting the board's positon on screen)
- To reverse the transformation:
    - Subtract the pan offset (`self.pan`) to move the origin back to the board's top-left
    - Divide by zoom (`self.zoom`) to undo the scaling
- That gives the actual position `(bx, by)` in board coordinate units, measured in board pixels

**Return the board coordinates**
```
return bx, by
```
- Returns a tuple of floats `(bx, by)` representing the position in board space

10. `_board_to_cell()`
**Function definition**
```
def _board_to_cell(self, labels, bx, by):
```
- Takes:
    - `labels`: the 2D NumPy array that represents your puzzle grid
    - `bx`, `by`: coordinates in board space (like the ones returned by `_screen_to_board()`)
- Returns:
    - A tuple `(cx, cy)`, the cell indcies (column and row) in the puzzle grid, or
    - `None` if the position is outside the board

**Get puzzle dimensions**
```
H, W = labels.shape
```
- Reads the puzzle grid's height (`H`) and width (`W`), in number of cells not pixels

**Handle negative coordinates**
```
if bx < 0 or by < 0:
    return None
```
- If the board coordinates are negative (to the left or above the puzzle), return `None`
- This means the user clicked outside the grid

**Convert board pixels to cell indices**
```
cx = int(bx // self.BASE_CELL)
cy = int(by // self.BASE_CELL)
```
- Each puzzle cell is a square of size `BASE_CELL` pixels
- Using floor division (`//`) to converts pixel coordinates to integer cell coordinates

**Check boundaries**
```
if 0 <= cx < W and 0 <= cy < H:
    return cx, cy
return None
```
- Makes sure the computed cell coordinates are within the grid limits
- If the player clicked within the puzzle area:
    - Returns `(cx, cy)`, valid cell position
- Otherwise, return `None`

11. `_prepare_board_surface()`
**Function definition**
```
def _prepare_board_surface(self, labels):
```
- Goal: to create a surface that is big enough to hold the entire board. 

**Get grid size**
```
H, W = labels.shape
```
- Retrieves `H` height and `W` width

**Create an offscreen surface**
```
self.board_surface = pygame.Surface((W * self.BASE_CELL, H * self.BASE_CELL))
```
- Creates a new pygame `surface` object, whose size is computed in pixels:
    - Each puzzle cell is `BASE_CELL` x `BASE_CELL` pixels
    - Multiply by the number of cells to get total pixel dimensions

12. `_draw_board()`
Draw the entire puzzle grid. 
**Function definition**
```
def _draw_board(self, labels, palette, filled_ok, show_numbers):
```
- Parameters:
    - `labels`: 2D NumPy array that stores the color label number for each cell (1,2,3, ...)
    - `palette`: dictionary mapping `{label_number: (R,G,B)}`, the color for each label
    - `filled_ok`: 2D boolean array showing which cells have already been filled by the player (`True`=filled, `False`=not filled)
    - `show_numbers`: Boolean flag, whether to draw the label numbers in unfilled cells
- Goal: Draw the current board state (colored cells + unfilled cell numbers) onto the offscreen surface

**Prepare the surface**
```
s = self.board_surface
s.fill((255,255,255))
```
- `s` is a shorthand reference to the `self.board_surface`
- `.fill((255,255,255))` fills the entire surface with white

**Prepare a font for numbers**
```
font = pygame.font.SysFont(None, max(12, int(self.BASE_CELL * 0.55)))
```
- Creates a pygame font for drawing numbers on the cells
- The size is dynamically scaled based on the cell size (`BASE_CELL`)
    - Typically, 55% of cell height looks visually balanced
    - Ensures at least size 12 so numbers do not vanish on tiny cells

**Get puzzle dimensions**
```
H, W = labels.shape
```
- Extracts the number of rows (`H`) and columns (`W`)

**Define colors**
```
highlight_bg = (230,230,230)
empty_bg = (250,250,250)
```
- `highlight_bg`: light gray background for currently selected label cells
- `empty_bg`: slightly lighter gray for other unfilled cells. 

**Loop through all grid cells**
```
for y in range(H):
    for x in range(W):
        rect = pygame.Rect(x * self.BASE_CELL, y * self.BASE_CELL, self.BASE_CELL, self.BASE_CELL)
        lab = int(labels[y,x])
```
- Iterates through every cell position
- Creates a `pygame.Rect` object that represents the cell's pixel rectangle on the surface:
    - Top-left corner = `(x * cell_size, y * cell_size)`
    - size = `(cell_size, cell_size)`
- Reads that cell's color label (`lab`) from `labels`

**Draw filled and unfilled cells**
```
if filled_ok[y, x]:
    pygame.draw.rect(s, palette[lab], rect)
```
- if the cell is already filled, fill its rectangle with its corresponding color from `palette`
- this represents "paint" pixels. 
- These cells are fully colored, no number drawn on top

**else: draw unfilled cell**
```
else:
    if lab == self.selected_label:
        pygame.draw.rect(s, highlight_bg, rect)
    else:
        pygame.draw.rect(s, empty_bg, rect)
```
- If the cell is not yet filled:
    - check if its label equals the currently selected color (`self.selected_label`)
    - if yes, draw a highlighted background (light gray)
    - if no, draw the normal pale background

**Draw number inside uniflled cells**
```
if show_numbers:
    n = str(int(labels[y,x]))
    num_color = (90,90,90) if (lab == self.selected_label) else (120,120,120)
    ts = font.render(n, True, num_color)
    s.blit(ts, ts.get_rect(center=rect.center))
```
- only runs if `show_numbers=True`
- convets the label into a string
- Chooses number color:
    - Darken gray `(90,90,90)` if the cell's label matches the currently selected color
    - Lighter gray `(120,120,120)` for others
- Renders the number using pygame font system
- centers the rendered text inside the cell's rectangle

13. `_draw_palette_bar()`
Draws the bottom color palette bar, the row of colored swatches that players use to pick which color/label they want to fill
**Function definition**
```
def _draw_palette_bar(self, palette: dict[int, tuple]):
```
- Draws the palette bar UI at the bottom of the screen
- The function uses the current game state to determie what to display and how

**Setup and draw the background**
```
mouse_pos = pygame.mouse.get_pos()
y0 = self.H - self.palette_bar_h
pygame.draw.rect(self.screen, self.panel, (0, y0, self.W, self.palette_bar_h))
pygame.draw.line(self.screen, self.grid_c, (0, y0), (self.W, y0), 1)
```
- `mouse_pos`: current mouse coordinates 
- `y0`: the vertical start position (top edge) of the palette bar
- Fills the palette area with background color `self.panel`
- Draw a divider line above it
- This sets up the white rectangle at the bottom of the window

**Layout constants**
```
padding_x = 12
padding_y = 10
arrows_w = 40
arrows_gap = 8
```
- Adds margins around the palette and reserves space for the left/right arrow buttons
- `arrows_w = 40`: each arrow button is 40px wide

**Compute usable drawing area**
```
usable_w = self.W - padding_x * 2 - arrows_w * 2 - arrows_gap * 2
usable_h = self.palette_bar_h - padding_y * 2
```
- `usable_w` = total horizontal space available for color swatches
- `usable_h` = available vertical space for one row of color squares

**Determine swatch size and grid layout**
```
sw = max(16, usable_h)
sh = sw
cols = max(1, usable_w // sw)
per_page = 10
total_colors = len(palette)
```
- Each color square's side = height of usabel area
- `cols`: number of swatches that could fit, but we hard-limit to `per_page = 10`
- `total_colors`: total number of colors in the palette (K)

**Pagination logic**
```
self._palette_pages = max(1, (total_colors + per_page - 1) // per_page)
self.palette_page = max(0, min(self.palette_page, self._palette_pages - 1))
```
- Calculates how many pages are needed
    - Formula `(N + per_page - 1) // per_page` = ceiling division
- Ensures `self.palette_page` stays valid

**Define arrow button rectangles**
```
left_x = padding_x
right_x = self.W - padding_x - arrow_w
btn_y = y0 + (self.palette_bar_h - sh) // 2
self._palette_left_btn = pygame.Rect(left_x, btn_y, arrows_w, sh)
self._palette_right_btn = pygame.Rect(right_x, btn_y, arrows_w, sh)
```
- Calculates where to place the arrow buttons:
    - Left one near the left padding
    - Right one near the right padding
    - Vertically centered within the palette bar
- These arrow button will be clickable between color pages

**Inner helper: draw_arrow()**
```
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
```
- This nested function draws one arrow button (left/right)
    - Detects hover, and changes background shade:
        - unenabled: gray
        - hovered: black border + gray background
        - enabled + not hover: black border + white background
    - Draws rounded rectangle background and border
    - Calculates triangle points (`pts`) for left/right arrow
    - Changes arrow color based on whether the button is active or disabled

**Draw both arrow buttons**
```
draw_arrow(self._palette_left_btn, "left", self.palette_page > 0)
draw_arrow(self._palette_right_btn, "right", self.palette_page < self._palette_pages - 1)
```
- Left arrow only enabled if not on the first page
- Right arrow only enabled if not on the last page

**Determine which colors are visible on this page**
```
labels_sorted = list(range(1, total_colors + 1))
start = self.palette_page * per_page
end = min(total_colors, start + per_page)
visible = labels_sorted[start:end]
```
- Gets the range of label numbers shown on the current page
- Example:
    - Page 0: labels 1-10
    - Page 1: labels 11-20

**Compute drawing positions for color square**
```
band_left = self._palette_left_btn.right + arrows_pag
band_right = self._palette_right_btn.left - arrows_pag
band_width = band_rigth - band_left
sw = sh = band_width // per_page
row_w = per_page * sw
start_x = band_left + (band_width - row_w) // 2
grid_y0 = y0 + (self.palette_bar_h - sh) // 2
```
- Calculates exact pixel region between arrows
- Ensures 10 equally sized swatches fill the available band perfectly
- Centers the row vertically and horizontally
- Perfectly aligned, equal-sized color squares across the palette bar

**Fonts and color contrast helpers**
```
base_font = pygame.font.SysFont(None, max(12, int(sw * 0.45)))
selected_font = pygame.font.SysFont(None, max(14, int(sw * 0.65)))

def is_dark(rgb):
    r,g,b = rgb
    return (0.2126*r + 0.7152*g + 0.0722*b) < 140
```
- Uses a smaller base font and a larger font for the currently selected color
- `is_dark()` uses the standard luminance formula to detect dark colors, helps decide whether to render text in white or black for contrast

**Draw all visible color swatches**
```
self.palette_swatches.clear()
x = start_x
for label in visible:
    rect = pygame.Rect(x, grid_y0, sw, sh)
    col_rgb = palette[label]
    pygame.draw.rect(self.screen, col_rgb, rect)
```
- Loops over each color label visible on this page
- Creates a rect and fills it with the color

**Determine if this color is "done"**
```
done = self.color_filled.get(label, 0) >= self.color_total.get(label, 0)
```
- Compares:
    - `color_filled[label]`: how many cells of that color the player has already filled
    - `color_total[label]`: total cells that sould be filled for that color
- if equal, all cells of this color are done

**Show either checkmark or number**
```
if done:
    check_color = (255,255,255) if is_dark(col_rgb) else (0,0,0)
    check_txt = base_font.render("√", True, check_color)
    self.screen.blit(check_txt, check_txt.get_rect(center=rect.center))
```
- Draws a checkmark in the center of the color box
- Color contrasts automatically (white on dark, black on light)

```
else:
    font_for_label = selected_font if label == self.selected_label else base_font
    txt_color = (255,255,255) if is_dark(col_rgb) else (0,0,0)
    txt = font_for_label.render(str(label), True, txt_color)
    self.screen.blit(txt, txt.get_rect(center=rect.center))
```
- Draws the color's label number
- Bigger font if it is the currently selected color
- Auto contrast text color based on background brightness

**Draw progress bar for selected color**
```
if (label == self.selected_label) and (not done):
    tot = max(1, self.color_total.get(label, 1))
    filled = min(tot, self.color_filled.get(label, 0))
    bar_margin = max(2, int(sw*0.1))
    bar_h = max(2, int(sw*0.05))
    bar_w = rect.w-bar_margin*2
    bar_x = rect.x+bar_margin
    bar_y = rect.bottom-int(sw*0.2)
    bar_color = (255,255,255) if is_dark(col_rgb) else (0,0,0)
    pygame.draw.rect(self.screen, bar_color, (bar_x-1, bar_y-1, bar_w+2, bar_h+2), 1)
    prog_w = int(bar_w*(filled/tot))
    if prog_w > 0:
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, prog_w, bar_h))
```
- Only for the selected color and if it is not complete
- Draws a small bar near the bottom of the color box:
    - thin rectangular track
    - width proportional to `filled/tot`
    - color chosen for contrast

**Store clickable regions**
```
self.palette_swatches.append((label, rect))
x += sw
```
- Saves `(label, rect)` tuples to `self.palette_swatches`, later used to detect clicks to color boxes
- Moves x-positon to the next square

#### Progress I/O
1. `_progress_paths()`
Utilities for managing where the game stores and loads a player's puzzle progress files
**Function definition**
```
def _progress_paths(self, puzzle_dir: Path):
    """Return (npy_path, json_path) for a puzzle's progress"""
```
- Takes 1 argument `puzzle_dir`, which is a folder of a specific puzzle.
- It returns a tuple of two file paths:
    - `.progress_filled.npy`: where filled-cell data (the painting progress) is saved
    - `.progress_state.json`: where metadata (i.e. selected color, completion status) is stored

**Ensure puzzle_dir is a path**
```
pdir = Path(puzzle_dir)
```
- Converts the input to a proper `Path` object. This guarantees to use `/` regardless of operating system.

**Return two file paths**
```
return (pdir/".progress_filled.npy", pdir/".progress_state.json")
```
- Uses the `/` operator from `pathlib` to create two full file paths inside that puzzle's directory
- They both start with a dot (`.`), making them hidden files in most systems. 

2. `_save_progress()`
Autosave system. It saves everything needed to resume a puzzle later. 
**Function definition**
```
def _save_progress(self):
    """Save current play state for the active puzzle"""
```
- Goal: Save the current puzzle's progress to disk. 

**Check if saving makes sense**
```
if not self.active or self.filled_ok is None:
    return 
```
- `self.active`: the currently open puzzle dictionary (set when entering PLAY mode)
- `self.filled_ok`: 2D boolean array marking which cells are filled
- If no puzzle is active or the filled mask doesn't exist, there is nothing to save. 

**Get save file paths**
```
npy_path, json_path = self._progress_paths(self.active["dir"])
```
- Gets two file paths inside the current puzzle's folder:
    - `.progress_filled.npy`: where the filled cell grid will go
    - `.progress_state.json`: where camera & UI info will go

**Make sure directory exists**
```
npy_path.parent.mkdir(parents=True, exist_ok=True)
```
- Creates the puzzle directory if it does not exist
- Ensures that saving won't fail due to missing folder

**Save the filled cells grid**
```
np.save(npy_path, self.filled_ok.astype(np.bool_))
```
- Converts `self.filled_ok` to boolean type expilicity
- Saves it as a `.npy` binary NumPy file using `np.save`

**Save other play state**
```
save = {
    "selected_label": int(self.selected_label),
    "palette_page": int(self.palette_page),
    "zoom": float(self.zoom),
    "pan": [float(self.pan.x), float(self.pan.y)],
}
```
- `"selected_label"`: color number the player had selected last
- `"palette_page"`: color-page they were viewing
- `"zoom"`: current zoom level of the board
- `"pan"`: camera offset (so board stays in same view position)

**Write state to JSON file**
```
with open(json_path, "w") as f:
    json.dump(state, f)
```
- opens `.progress_state.json` for writing
- saves the dictionary as readable JSON text

**Error handling**
```
except Exception as e:
    print(f"[progress save failed] {e}")
```
- If anything goes wrong (missing disk, permission error), print an error message but don't crash the game. 

3. `_load_progress()`
It restores when the player reopens a puzzle. 
**Function definition**
```
def _load_progress(self, puzzle) -> bool:
    """Load progress if present; returns True if loaded"""
```
- `puzzle`: a dictionary representing the active puzzle. 
- Returns `True` if progress was successfully loaded from disk, otherwise `False`
- The function rebuilds the entire gameplay state from previously saved `.progress_filled.npy` and `.progress_state.json`

**Get progress file paths**
```
npy_path, json_path = self._progress_paths(puzzle["dir"])
loaded = False
```
- Calls `_progress_paths()` to get the standard save file names inside the puzzle's folder:
    - `.progress_filled.npy`: the boolean grid of filled cells
    - `.progress_state.json`: metadata like zoom/pan/color
- Initializes `loaded = False`, to later report whether anything was restored

**Create a fresh empty board by default**
```
self.filled_ok = np.zeros_like(puzzle["labels"], dtype=bool)
```
- Initializes a new boolean matrix (`same shape as puzzle["labels"]`) with all values `False`, means no cells are filled. 
- This serves as a safe fallback if no save file exists or it fails to load

**Try loading the `.npy` file**
```
if npy_path.exists():
    try:
        filled = np.load(npy_path, allow_pickle=False)
        if filled.shape == puzzle["labels"].shape:
            self.filled_ok = filled.astype(bool, copy=True)
            loaded = True
    except Exception as e:
        print(f"[progress load failed] {e}")
```
- If `.progress_filled.npy` exists:
    - Uses `np.load()` to load the NumPy array
    - Ensures the array shape matches the puzzle's current grid shape 
    - Converts to `bool` and stores in `self.filled_ok`
    - Marks `loaded = True`
- If any error occurs, print a warning but don't crash
- Now `self.filled_ok[y,x]` tells which cells were already filled

**Double-check the mask shape**
```
if self.filled_ok is None or self.filled_ok.shape != puzzle["labels"].shape:
    self.filled_ok = np.zeros_like(puzzle["labels"], dtype=bool)
```
- Ensures that `filled_ok` is always a valid boolean array with the correct dimensions
- This covers cases where loading failed or gave mismatched data

**Try loading UI state from `.json`**
```
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
```
- If `.progress_state.json` exists:
    - Reads and parses the JSON data into dictionary `s`
    - Restores:
        - `selected_label`: last chosen color
        - `palette_page`: which palette page was open
        - `zoom`: last zoom level
        - `pan`: last camera offset, converted back into `pygame.Vector2`
- Uses `.get()` with defaults so missing fields don't cause crashes
- This lets the player return to exactly the same zoom and position they left off with

**Recalculate per-color progress**
```
labels = puzzle["labels"]
K = len(puzzle["palette"])
self.color_total = {k: int((labels == k).sum()) for k in range(1, K+1)}
self.color_filled = {k: int((self.filled_ok & (labels == k)).sum()) for k in range(1, K+1)}
```
- Computes:
    - `color_total`: how many cells exist for each color label
    - `color_filled`: how many of those cells are already filled
- Uses NumPy logic:
    - `(labels == k)` gives a mask of all cells belonging to color `k`
    - `(self.filled_ok & (labels == k))` gives only the filled ones
It keeps the palette progress indicators (numbers, checkmarks, bars) accurate

**Clamp camera position**
```
self._clamp_pan(labels)
```
- Ensures `self.pan` (camera offset) is within valid range
- Prevents the board from being off-screen if a saved zoom/pan combination was slightly out of bounds

**Return whether loading succeeded**
```
return loaded
```
- Returns `True` if a valid `.npy` file was successfully loaded; otherwise `False`

4. `_puzzle_progress()`
A quick progress calculator that lets the game show how much of a puzzle is completed without fully loading it into memory or entering playing mode. It is used in the browser screen, so each puzzle card can display its progress bar. 
**Function definition**
```
def _puzzle_progress(self, puzzle) -> float
    """
    Return complete fraction [0...1] for a puzzle by reading its saved mask if present.
    Uses .progress_filled.npy if it exists; otherwise 0.0
    """
```
- Returns a float between 0 and 1, representing the completion percentage of a puzzle:
    - `0.0`: no cells filled 
    - `1.0`: puzzle completely filled
- Reads the `.progress_filled.npy` file (the boolean mask saved by `_save_progress()`)

**Get puzzle data**
```
labels = puzzle["labels"]
total = labels.size
```
- `labels`: a 2D NumPy array of integers, each cell's color label (1,2,3, ...)
- `labels.size`: total number of cells in the puzzle (`H x W`)


**Handle empty puzzles safely**
```
if total <= 0:
    return 0.0
```
- If the puzzle has no cells, immediately return 0.0 to avoid division by zero

**Locate progress file**
```
npy_path = puzzle["dir"] / ".progress_filled.npy"
```
- Builds the expected path for the saved boolean grid file

**If progress file exists, try to read it**
```
if npy_path.exists():
    try:
        filled = np.load(npy_path, allow_pickle=False)
        if filled.shape == labels.shape:
            return float(filled.astype(bool).sum()) / float(total)
    except Exception:
        pass
```
- Checks whether `.progress_filled.npy` exists
- If it exists:
    - Load it with NumPy (`np.load`)
    - Verify the array's shape matches the puzzle's label array
    - Convert it to boolean (`True` = filled, `False` = unfilled)
    - Count how many cells are `True` with `.sum()`
    - Divide by total number of cells to get a fraction between 0 and 1.
    - Return that as a float

**Fallback**
```
return 0.0
```
- If:
    - `.progress_filled.npy` doesn't exist
    - Or loading fails
    - Or shape doesn't match
- Returns 0.0

5. `_is_puzzle_complete()`
Check whether a puzzle is fully completed
**Function definition**
```
def _is_puzzle_complete(self, puzzle) -> bool:
```
- A small helper method that takes a `puzzle` dictionary and returns a Boolean value
- Goal: determine whether the player has finished the entire puzzle

**Return statement**
```
return self._puzzle_progress(puzzle) >= 0.999
```
- Calls `_puzzle_progress()` and returns a float between 0.0 and 1.0, representing completion percentage

6. `_preview_surface_for_browser()`
Decides which preview image to display for each puzzle on the browser screen, whether the finished picture or the regular one
**Function definition**
```
def _preview_surface_for_browser(self, puzzle) -> pygame.Surface:
    """Return completed preview if complete & available, else regular preview"""
```
- A helper method that takes a single `puzzle` dictionary (one entry from your `self.puzzles` list)
- Returns a `pygame.Surface`, the image surface that should be displayed on the browser screen for that puzzle's card

**Check completion & availability**
```
if self._is_puzzle_complete(puzzle) and puzzle.get("complete_preview") is not None:
```
- Calls `_is_puzzle_complete(puzzle)`, returns `True` if at least 99.9% of the puzzle's cells are filled
- Then checks:
    - Does the `puzzle` dictionary contain a non-None `"complete_preview"` key?
    - This typically points to an image showing the finished version of the puzzle
- Both conditions must be true:
    - The puzzle is fully solved
    - There's a ready-made "finished" preview image available

**Return the completed preview if available**
```
return puzzle["complete_preview"]
```
- If both conditions are met, use the completed version. 

**Fallback to regular preview**
```
return puzzle["preview"]
```
- If the puzzle is not finished, or there's no complete preview image available, fall back to the default preview

#### State screen
1. `draw_welcome()`
Rendered for the game's welcome screen, the first screen players see when they open your Color By Number app. 
It draws the background, the title image, a short tagline, and the start button.

**Function definition**
```
def draw_welcome(self):
```
- Render (draw) all elements of the welcome screen to the main pygame window

**Fill the screen background**
```
self.screen.fill(self.bg)
```
- Fills teh entire game window with the background color stored in `self.bg`

**Draw teh welcome image**
```
if self.welcome_img:
```
- Checks if a welcome image was successfully loaded earlier in `__init__`. 
- If yes, draw it, otherwise skip

**Fit and scale the image nicely**
```
fitted = self._fit_center(self.welcome_img, int(self.W * 0.5), int(self.H * 0.5))
```
- Calls `_fit_center()`, which rescales the image proportionally to fit within half the window width and half the window height
- Ensures the image looks balanced and not distorted, regardless of screen size

**Compute centered position**
```
rect = fitted.get_rect(center=(self.W//2, int(self.H * 0.32)))
```
- Gets the rectangle describing the fitted image's size
- Positions its center at the horizontal center (`self.W//2`) and vertical position `= 32%` down from the top of the window. 
    - Slightly above the screen center, gives space below for the tagline and start button

**Draw the welcome image**
```
self.screen.blit(fitted, rect)
```
- Blits (draws) the fitted image onto the main window at the computed position

**Draw the tagline / subtitle below the image**
```
tagline = self.slogan_font.render("长生不老 钓鱼爬山", True, (0,76,153))
tagline_rect = tagline.get_rect(center=(self.W//2, rect.bottom+40))
self.screen.blit(tagline, tagline_rect)
```
- `self.slogan_font`: a custom font loaded earlier
- `.render("长生不老 钓鱼爬山", True, (0,76,153))`
    - Renders the phrase into a text surface
    - Anti-aliased, dark blue color
- `.get_rect(center=(self.W//2, rect.bottom+40))`
    - Centers the text horizontally
    - Places it 40 pixels below the bottom of the welcome image
- `.blit(tagline, tagline_rect)`: draws the text surface onto the main screen

**Draw the Start button**
```
self.btn_start.draw(self.screen)
```
- Calls the `.draw()` method of the `ImageButton` instance, which:
    - Handles hover effects
    - Draws the button's image
    - Keeps it interactive


2. `draw_browser()`
It draws the scrollable grid of puzzle cards, each showing either a preview or a completed image, along with their progress bars. It also has a fixed title header on the top of the screen. 
**Function definition**
```
def draw_browser(self):
```
- This method draws the entire puzzle selection screen, where all puzzles are displayed as clickable cards in a scrollable grid layout

**Clear the background**
```
self.screen.fill(self.bg)
```
- Clears the previous frame by filling the screen with background color `self.bg`

**Create a header panel**
```
header_rect = pygame.Rect(0,0,self.W, self.browser_title_h)
```
- Defines a rectangle for the title area at the top
- It spans the full screen width (`self.W`) and has height `self.browser_title_h`

**Setup scrollable area below the header**
```
gap = self.browser_card_gap
area_top = header_rect.bottom + 20
```
- `gap`: spacing between puzzle cards
- `area_top`: vertical position where the grid area starts

**Compute card sizes**
```
avail_w = self.W - gap * (self.browser_cols + 1)
size_by_w = avail_w // self.browser_cols
item_w = item_h = size_by_w
```
- Computes how large each puzzle card should be:
    - `avail_w`: total usable horizontal space (after accounting for gaps between and around columns)
    - `browser_cols`: number of columns
    - Each card's width and height = `size_by_w`

**Center the grid horizontally**
```
row_w = self.browser_cols * item_w + (self.browser_cols - 1) * gap
left_x = (self.W - row_w) // 2
```
- `row_w`: total width of all cards + gaps in one row
- `left_x`: x-position of the first column, horizontally centers the grid widthin the window

**Handle scrolling boundaries**
```
total_rows = (len(self.puzzles) + self.browser_cols - 1) // self.browser_cols
content_h = max(0, total_rows * (item_h + gap) - gap)
viewport_h = self.H - area_top - 20
min_scroll = min(0, viewport_h - content_h)
max_scroll = 0
self.browser_scroll = max(min(self.browser_scroll, max_scroll), min_scroll)
self._browser_min_scroll = min_scroll
self._browser_max_scroll = max_scroll
```
- `total_rows`: how many rows of puzzles exist
- `content_h`: total vertical height needed to show all puzzle cards (rows x card height + gaps)
- `viewport_h`: visible height of the scroll area
- `min_scroll`: the lowest allowed scroll offset
- `max_scroll`: the top scroll limit
- Clamp `self.browser_scroll` between those limits

**Restrict drawing to the grid area**
```
self.screen.set_clip(pygame.Rect(0, area_top, self.W, self.H - area_top))
```
- Restricts all drawing to the region below the header bar
- Anything drawn outside this clip rectangle will be ignored

**Compute card positions**
```
self.browser_item_rects = []
for i, p in enumerate(self.puzzles):
    col = i % self.browser_cols
    row = i // self.browser_cols
    x = left_x + col * (item_w + gap)
    y = area_top + self.browser_scroll + row * (item_h + gap)
    self.browser_item_rects.append(pygame.Rect(x, y, item_w, item_h))
```
- Loops over all puzzles
- Calculates grid coordinates:
    - `col`, `row`: position in grid
    - `x`, `y`: pixel coordinates
- Builds a `pygame.Rect` for each card
- Stores all these in `self.browser_item_rects` for click detection

**Draw puzzle cards**
```
for r, p in zip(self.browser_item_rects, self.puzzles):
```
- Iterates over each puzzle and its corresponding rectangle

**Draw card background and border**
```
pygame.draw.rect(self.screen, self.panel, r)
pygame.draw.rect(self.screen, (0,0,0), r, 1)
```
- Fills card background and adds a thin black border

**Draw puzzle preview**
```
src = self._preview_surface_for_browser(p)
sw, sh = src.get_width(), src.get_height()
tw = th = r.w
scale = max(tw/sw, th/sh)
scaled_w, scaled_h = int(sw*scale), int(sh*scale)
scaled = pygame.transform.smoothscale(src, (scaled_w, scaled_h))
ox = max(0, (scaled_w - tw)//2)
oy = max(0, (scaled_h - th)//2)
self.screen.blit(scaled, r, area=pygame.Rect(ox, oy, tw, th))
```
- `src`: the preview iamge surface, from `_preview_surface_for_browser(p)`, which returns either the unfinished or completed image depending on progress
- `scale`: scales the image so it covers the card
- Crops the central part of the scaled image (`ox`, `oy` define the cropping offset)
- `blit()` draws the central square region into the card area

**Draw progress bar**
```
if not self._is_complete(p):
    frac = self._puzzle_progress(p)
    bar_h = max(3, r.h//30)
    bar_pad = max(8, r.w//18)
    bar_w = r.w - bar_pad*2
    bar_x = r.w + bar_pad
    bar_y = r.bottom - bar_pad - bar_h
```
- Only draw progress if puzzle isn't fully done
- Computes the position and size of a small progress bar near the bottom of the card

**Draw progress bar track and fill**
```
bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
bg_color = (230,230,230,150)
fill_color = (115,145,210,240)
pygame.draw.rect(bar_surf, bg_color, (0,0,bar_w,bar_h), border_radius=4)
fill_w = int(bar_w * frac)
if fill_w > 0:
    pygame.draw.rect(bar_surf, fill_color, (0,0,fill_w,bar_h), border_radius=4)
self.screen.blit(bar_surf, (bar_x, bar_y))
```
- Creates a small semi-transparent surface for the bar
- Draws a gray track and a blue fill portion based on `frac`
- Blits the bar to the card position

**Reset clipping**
```
self.screen.set_clip(None)
```
- Removes the clipping rectangle so the next drawing (header) won't be restricted

**Draw fixed header with title**
```
pygame.draw.rect(self.screen, self.panel, header_rect)
title_surf = self.title_font.render("彩虹都害羞，不愿上镜头", True, (0,76,153))
self.screen.blit(title_surf, title_surf.get_rect(center=header_rect.center))
```
- Draws the title bar
- Renders the title text in dark blue
- Centers the title horizontally and vertically within the header

3. `draw_play()`
This function handles drawing the main gameplay screen, the zoomable, pannable board where players actually fill in cells with color. 

**Function definition**
```
def draw_play(self):
```
- It is responsible for drawing one full frame of the play screen

**Clear the screen**
```
self.screen.fill(self.bg)
```
- Clears the previous frame by filling the window with the background color

**Retrieve current puzzle data**
```
labels = self.active["labels"]
palette = self.active["palette"]
```
- `self.active` is the currently opened puzzle dictionary
- `labels`: 2D NumPy array of integers
- `palette`: a dictionary of RGB colors

**Update the board image**
```
show_numbers = (self.zoom >= 1.25)
self._draw_board(labels, palette, self.filled_ok, show_numbers)
```
- `self.zoom` is the current zoom factor (camera scale)
- only show numbers when zoomed in enough
- `_draw_board()` redraws the offscreen `self.board_surface`
    - fills each cell with its color if already filled
    - otherwise shows its number
    - or a highlight if it is the currently selected color

**Apply zoom and pan**
```
scaled = pygame.transform.scale(self.board_surface, (int(self.board_surface.get_width() * self.zoom), int(self.board_surface.get_height() * self.zoom)))
self.screen.blit(scaled, self.pan)
```
- scales the board surface by the current zoom level
- blits it at position `self.pan`, which is the camera's top-left offset
- zoom = scale, pan = move viewport around

**Prepare to draw optional grid lines**
```
H, W = labels.shape
cell_screen_w = self.BASE_CELL * self.zoom
cell_screen_h = self.BASE_CELL * self.zoom
gx0, gy0 = self.pan.x, self.pan.y
```
- Computes grid dimensions in screen pixels after zoom
- `BASE_CELL`: logical size. After zooming, each cell's visible size = `BASE_CELL * zoom`
- `gx0`, `gy0`: the top-left corner of the board on the screen

**Draw 1 pixel thin grid lines**
```
if cell_screen_w >= 12 and cell_screen_h >= 12:
    grid_color = (215,215,215)
```
- only draw fine grid line when cells are large (>= 12 pixels)

**Draw vertical grid lines**
```
for x in range(W+1):
    xpix = int(gx0 + x * cell_screen_w)
    pygame.draw.aaline(self.screen, grid_color, (xpix, gy0), (xpix, gy0 + H * cell_screen_h))
```
- Draws a vertical anti-aliased line for every column boundary

**Draw horizontal grid lines**
```
for y in range(H+1):
    ypix = int(gy0 + y * cell_screen_h)
    pygame.draw.aaline(self.screen, grid_color, (gx0, ypix), (gx0 + W * cell_screen_w, ypix))
```
- Draw lines for each row

**Draw the back button**
```
self.screen.set_clip(None)
self.btn_play_back.draw(self.screen)
```
- Remove any clipping restriction
- draws the back button, which lets the player return the browser screen

**Draw the palette bar at bottom**
```
self._draw_palette_bar(palette)
```
- Calls the previous `_draw_palette_bar()` method to render:
    - the color swatches
    - selection highlight
    - checkmarks for finished colors
    - page arrows

4. `draw_finished()`
Render the finish screen, which displays the completed image in full color and offers two buttons: save and back. 
**Function defnition**
```
def draw_finished(self):
```
- Called after a puzzle is completely filled

**Fill background**
```
self.screen.fill(self.bg)
```
- Clears the previous frame and fills the window with background color

**Get current puzzle data**
```
labels = self.active["labels"]
palette = self.active["palette"]
```
- `self.active` stores the currently completed puzzle
- `labels`: the grid of color labels
- `palette`: mapping RGB for each color

**Layout constants for positioning**
```
margin = 30
gap_img_to_first_btn = 24
gap_between_buttons = 12
```
- Layout padding constants:
    - `margin`: padding from screen edges
    - `gap_img_to_first_btn`: space between the completed image and the first button
    - `gap_between_buttons`: vertical space between two buttons

**Get button sizes**
```
btn_w, btn_h = self.btn_save.rect.size
```
- Reads the pixel size of the save button image

**Define area for solved image**
```
area = pygame.Rect(margin, margin, self.W - margin * 2, self.H - margin * 2 - 90)
```
- Defines a large rectangle area where the solved image will be displayed
- Leaves margins on all sides and extra space at the bottom for buttons

**Render the solved puzzle image**
```
solved = render_solved_pil(labels, palette, scale=1)
sw, sh = solved.size
if sw == 0 or sh == 0:
    return
```
- calls the earlier function `render_solved_pil()`
    - creates a crisp color image from the label grid using the palette
- Gets its size `(sw, sh)` and ensures it is not empty

**Compute scale to fit screen area**
```
scale = min(area.w/sw, area.h/sh)
scale = max(1, int(scale))
solved = solved.resize((sw*scale, sh*scale), Image.Resampling.NEAREST)
```
- Calculates how much to scale the image so it fits inside the defined area
    - `min(area.w/sw, area.h/sh)` picks whichever dimension would hit the limit first
- `max(1, int(scale))` ensures scale >= 1
- Uses `Image.Resampling.NEAREST` for pixel-perfect scaling

**Convert Pillow image to pygame surface**
```
surf = pygame.image.fromstring(solved.tobytes(), solved.size, solved.mode)
```
- Converts the Pillow image into a `pygame.Surface` for drawing on the game window

**Center the solved image on screen**
```
img_rect = surf.get_rect(center=area.center)
self.screen.blit(surf, img_rect)
```
- centers the scaled image inside the area

**Position the buttons below the image**
```
y0 = img_rect.bottom + gap_img_to_first_btn
self.btn_save.rect.topleft = ((self.W-btn_w)//2, int(y0))
self.btn_back.rect.topleft = ((self.W-self.btn_back.rect.w)//2, int(y0+btn_h+gap_between_buttons))
```
- `y0`:vertical position right below the finished image
- both buttons are centered horizontally
- `btn_save` placed below image, `btn_back` below the save button

**Draw buttons**
```
self.btn_save.draw(self.screen)
self.btn_back.draw(self.screen)
```
- renders the save and back buttons with their hover effect

#### Event handling
1. `handle_events()`
This function reads pygame events each frame. 

**Overall**
- Loops over `pygame.event.get()` and reacts based on the current screen state:
    - `WELCOME`: click Start
    - `BROWSER`: scroll, click a puzzle
    - `PLAY`: esc/back, zoom, pan, paint, palette click, autosave/finish
    - `FINISHED`: save/back
- Returns `False` to quit the app, `True` to keep running

**Global quit**
```
if e.type == pygame.QUIT:
    if self.state == STATE_PLAY:
        self._save_progress()
    return False
```
- For game termination, if in PLAY, save progress, then exit

**WELCOME**
```
if self.state == STATE_WELCOME:
    if self.btn_start.clicked(e):
        self.state = STATE_BROWSER
```
- clicking the start button switches to browser screen

**BROWSER**
*Scroll wheel*
```
if e.type == pygame.MOUSEWHEEL:
    mx, my = pygame.mouse.get_pos()
    if my >= self.browser_title_h:
        self.browser_scroll += e.y * 40
        if hasattr(self, "_browser_min_scroll"):
            self.browser_scroll = max(min(self.browser_scroll, self._browser_max_scroll), self._browser_min_scroll)
```
- Wheel scrolls list only if the cursor is below the header
- Uses the bounds `(_browser_min_scroll, _browser_max_scroll)` computed in `draw_browser()` to clamp

*Click a card*
```
elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
    for rect, puzzle in zip(self.browser_item_rects, self.puzzles):
        if rect.collidepoint(e.pos):
            if self._is_puzzle_complete(puzzle):
                self._enter_finished(puzzle)
            else:
                self._enter_play(puzzle)
            break
```
- Left click on a card: 
    - If complete, jump to finish screen
    - else, enter play screen

**PLAY**
*ESC to browser*
```
if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
    self._save_progress()
    self.state = STATE_BROWSER
```

*Zoom with wheel*
```
elif e.type == pygame.MOUSEWHEEL:
    mx, my = pygame.mouse.get_pos()
    before = pygame.Vector2(self._screen_to_board(mx, my))
    self.zoom *= (1.12 if e.y > 0 else 1/1.12)
    self.zoom = max(self.min_zoom_fit, min(self.zoom, self.max_zoom))
    after = pygame.Vector2(self._screen_to_board(mx, my))
    self.pan += (after - before) * self.zoom
    self._clamp_pan(self.active["labels"])
```
- `mx,my = pygame.mouse.get_pos()`: get the mouse position in screen pixels
- `before`: converts that screen point to board coordinates at current zoom/pan
- `self.zoom`: scroll in (x1.12), scroll down (/1.12)
- clamp the zoom so never zoom out past limits
- `after`: recompute the board coordinates under the same screen point but using the new zoom (while the pan unchanged)
- `self.pan`: 
    - adjust pan so the cursor stays anchored on the same board point as before
    - screen = board * zoom + pan
    - before zoom: (mx, my) = before * zoom_old + pan_old
    - after zoom: (mx, my) = before * zoom_new + pan_new
    - Keeps (mx, my) not changed, so pan_new = (after - before) * zoom_new
    - example: before zoom: (mx,my) = (200,200); after zoom x2, at the same screen position, it is (100,100) (each cell size needs more pixels to represent). To pan the board and make that position to be (200,200) again, pan_new = (100-200)*2 = (-200,-200), meaning moving left -200 pixels and top -200 pixels. Now (mx,my) = (200,200) again. 
- `self._clamp_pan`: relimit the camera position after a change, so keeps the board within bounds to prevent overscrolling into empty space. 

*Mouse down*
```
elif e.type == pygame.MOUSEBUTTONDOWN:
```
- the block that addresses the action with mouse button press down

*1.Left mouse button*
```
if e.button == 1:
```

*1.1 Back button in play UI*
```
if self.btn_play_back.rect.collidepoint(e.pos):
    self._save_progress()
    self.state = STATE_BROWSER
    return True
```
- If the click is inside the back button region
    - save current puzzle progress
    - switch game state to browser screen
- `return True` to stop further handling of the click

*1.2 Palette arrows*
```
if self._palette_left_btn.collidepoint(e.pos) and self.palette_page > 0:
    self.palette_page -= 1
    return True
if self._palette_right_btn.collidepoint(e.pos) and self.palette_page < self._palette_page - 1:
    self.palette_page += 1
    return True
```
- If the click hits the left arrow, move to previous color page
- If it hits the right arrow, move to the next color page

*1.3 Palette swatches*
```
for lab, r in self.palette_swatches:
    if r.collidepoint(e.pos):
        if self.color_filled.get(lab, 0) < self.color_total.get(lab, 0):
            self.selected_label = lab
        return True
```
- Loops through all visible boxes
- If the click is insid one box:
    - Check if that color is completed
    - If not, set it as the currently selected color

*1.4 Painting or Panning*
```
bx, by = self._screen_to_board(e.pos)
cell = self._board_to_cell(self.active["labels"], bx, by)
```
- Convert mouse position in screen coordinates to board coordinates
- Next, convert to grid cell

*1.5 If the click is inside a valid cell*
```
if cell is not None:
    cx, cy = cell
    start_lab = int(self.active["labels"][cy,cx])
    if (start_lab == self.selected_label) and (not self.filled_ok[cy, cx]):
        self.painting = True
        self.last_paint_cell = (cx, cy)
        self._fill_cell_if_match(cx, cy)
```
- Gets the cell's color label (`start_lab`)
- If it matches the current selected color (`self.selected_label`) and it is not flled, then start painting:
    - `self.painting = True`: mark that a drag-paint is in progress
    - `self.last_paint_cell = (cx, cy)`: store where the stroke started
    - Meanwhile, fill that cell with `_fill_cell_if_match()`

*1.6 otherwise, start panning*
```
else:
    self.dragging_pan = True
    self.drag_anchor = pygame.Vector2(e,pos)
```
- If the clicked cell does not match the selected color or is already filled, treat it as a drag to move camera action. 
- Store current mouse position in `drag_anchor`

*1.7 If the click is outside the board entirely*
```
else:
    self.dragging_pan = True
    self.drag_anchor = pygame.Vector2(e.pos)
```
- If the click outside puzzle area, start panning

*2. Middle or right mouse button*
```
elif e.button is (2,3):
    self.dragging_pan = True
    self.drag_anchor = pygame.Vector2(e.pos)
```
- If click middle or right button, start panning
- Sets `dragging_pan = True`

*Mouse move*
```
elif e.type == pygame.MOUSEMOTION:
```
- When the mouse moved while a button is pressed
- It addresses with 2 cases:
    - painting (when the user click down on the coloring cell)
    - panning (when the user click down on other place of the screen)

*1. Painting mode*
```
if self.painting:
```
- `self.painting` is `True` when the player pressed the left button on a correct, unfilled cell
- Then as the mouse moves, we have to fill every cell that the cursor passes through

*1.1 Convert mouse position to board coordinates*
```
bx, by = self._screen_to_board(e.pos)
```
- `_screen_to_board()` converts the `e.pos` to from screen pixels to board coordinates

*1.2 Find the corresponding cell*
```
cell = self._board_to_cell(self.active["labels"], bx, by)
```
- Converts board coordinates into cell coordinates

*1.3 if mouse move to a new valid cell*
```
if cell is not None and cell != self.last_paint_cell:
```
- skip if:
    - The mouse is still on the same cell
    - outside the board
- otherwise, fill in the cells between previous and current cell

*1.4 paint along the path*
```
self._paint_line_between(self.last_paint_cell, cell)
```
- uses `_paint_line_between()` to apply Bresenham line algorithm to paint the cells between two points
- each of the cell along the line using `_fill_cell_if_match()` to determine painting

*1.5 update the last paint cell
```
self.last_paint_cell = cell
```
- save the current cell as the new `last_current_cell`, prepare for the next movement

*2. Panning mode*
```
elif self.dragging_pan and self.drag_anchor is not None:
```
- When the user is not painting but dragging the board

*2.1 compute movement delta*
```
delta = pygame.Vector2(e.pos) - self.drag_anchor
```
- Compute how far the mouse moved since last frame
- `delta.x` and `delta.y` show movement in pixels

*2.2 update camera position*
```
self.pan += delta
```
- Moves the board's pan offset by the delta

*2.3 update anchor point*
```
self.drag_anchor = pygame.Vector2(e.pos)
```
- Store the current mouse position as the new anchor for the next motion event

*2.4 clamp camera*
```
self._clamp_pan(self.active["labels"])
```
- calls `_clamp_pan()` to ensure the board stays in screen boundaries

*Mouse up*
```
elif e.type == pygame.MOUSEBUTTONUP:
```
- Determines what to do when the user finishes painting or stops panning

*1. Left mouse button release while painting*
```
if e.button == 1 and self.painting:
```
- Only trigger this when:
    - Left mouse button released
    - The user was painting
- It handles the end of a paint stroke

*1.1 End the painting stroke*
```
self.painting = False
self.last_paint_cell = None
```
- stops painting mode
- clears the last paint cell record

*1.2 autoadvance to the next color (if this color is completed)*
```
lab = self.selected_label
if self.color_filled.get(lab, 0) >= self.color_total.get(lab, 0):
    for nxt in range(1, len(self.active["labels"]) + 1):
        if self.color_filled.get(nxt, 0) < self.color_total.get(nxt, 0):
            self.selected_label = nxt
            break
```
- `lab = self.selected_label`: the color the user was using
- `self.color_total[lab]`: the number of cell in total of that label
- `self.color_filled[lab]`: the number of cells that have been filled
- if `self.color_total` equals to `self.color_filled`, the label filling is completed
- Loop through the colors in order, and find the next color that have not been completed yet
- swatch `self.selected_label` to that color

*1.3 Check if the entire puzzle is complete*
```
if self.filled_ok.all():
    self._save_progress()
    self.progress_dirty = False
    self.state = STATE_FINISHED
    return True
```
- `self.filled_ok` is a 2D boolean array. Cell filled = `True`; Cell unfilled = `False`
- `.all()` returns `True` if every cell is filled
- When complete:
    - Save the current progress
    - Mark `progress_dirty = False`
    - Switch state to `STATE_FINISHED`
    - Ends handling for this frame

*1.4 Save if any progress changed this stroke*
```
if self.progress_dirty:
    self._save_progress()
    self.progress_dirty = False
```
- If any cells were painted in this stroke:
    - save the progress to file
    - reset `progress_dirty`

*2. Stop panning*
```
elif e.button in (1,2,3) and self.dragging_pan:
    self.draggping_pan = False
    self.drag_anchor = None
```
- If any of the mouse buttons were released and the user was dragging:
    - Stop dragging 
    - clear anchor position

**FINISHED**
```
elif self.state == STATE_FINISHED:
    if self.btn_back.clicked(e):
        self.state = STATE_BROWSER
    elif self.btn_save.clicked(e):
        self._save_finished_png()
```
- click back button: return browser screen
- click save button: export the finished image as PNG

**Keep running**
```
return True
```
- Continue the game loop


#### Transitions & Actions 
1. `_enter_play()`
Wires all the elements, restore the saved progress, and decide whether to show the PLAY screen or the FINISH screen. 
**Function definition**
```
def _enter_play(self, puzzle):
    self.active = puzzle
```
- Set the clicked puzzle as current active one

**Update the setup**
```
self.board_surface = None
self._prepare_board_surface(self.active["labels"])
```
- Clear previous offscreen board surface, create a new surface sized to the gird (width = `W*BASE_CELL`, height = `H*BASE_CELL`)

**setup UI defaults**
```
self.selected_label = 1
self.palette_page = 0
self._reset_camera(self.active["labels"])
```
- Set up UI defaults:
    - start on color 1, palette on page 0
    - call `_reset_camera()` to compute the minimum zoom that fits and center the board, clamped to bounds

**Counters**
```
labels = self.active["labels"]
K = len(self.active["palette"])
self.filled_ok = np.zeros_like(labels, dtype=bool)
self.color_total - {k: int((labels==k).sum()) for k in range(1, K+1)}
self.color_filled = (k: 0 for k in range(1, K+1))
```
- Initialize progress data:
    - `filled_ok`: a boolean HxW mask, all False
    - `color_total`: for each label `k`, the number of cells for this label
    - `color_filled`: for each label `k`, the number of cells that has already been filled
- Later these placeholders can be overwritten by saved data
```
self._load_progress(self.active)
```
- Read:
    - `.progress_filled.npy`: restores `filled_ok`
    - `.progress_state.json`: restores `selected_label`, `palette_page`, `zoom`, `pan`
    - recompute `color_total` and `color_filled` from the loaded mask

**If finished, show FINISH screen**
```
if self.filled_ok is not None and self.filled_ok.size > 0 and self.filled > ok.all():
    self.state = STATE_FINISHED
    return
```
- If all the cells are filled, directly go to FINISHED screen

```
self.state = STATE_PLAY
```
- Otherwise, enter PLAY state. 

2. `_enter_finished()`
Go straight into FINISHED screen
**Function definition**
```
def _enter_finished(self, puzzle):
    self.active = puzzle
    self.state = STATE_FINISHED
```
- Set clicked puzzle as the current active one
- Change the state to STATE_FINISHED, then the FINISH screen will be drawed. 

3. `_save_finished_png()`
The function creates and saves a final colored PNG image of the completed puzzle
**Function definition**
```
def _save_finished_ong(self):
```
- This function is to export the finished puzzle as an image. 

**Get puzzle data**
```
labels = self.active["labels"]
palette = self.active["palette"]
```
- `self.active`: the currently active puzzle
- `labels`: 2D NumPy array containing integers `1...K`
- `palette`: a dictionary mapping those labels to RGB colors

**Create filename**
```
stem = self.active["dir"].name
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out = Path(f"{stem}_finished_{ts}.png")
```
- `stem`: puzzle's folder name
- `ts`: timestamp of the current date/time
- `Path` to turn it into a path object for saving

**Choose scale**
```
scale = max(4, 512 // max(labels.shape))
```
- `labels.shape` gives height and width of the gird
- `max(labels.shape)` takes the largest dimension (lanscape=width; potrait=height)
- `512 // max()` makes the image roughly ~512 pixels on its largest side
- `max(4, ...)` ensures at least 4x upscaling. 

**Render the solved image**
```
img = render_solved_pil(labels, palette, scale)
```
- Calls `render_solved_pil`:
    - creates a PIL.Image whose each cell is colored according to `palette[label]`
    - Scales the image up by the chose scale factor

**Save image**
```
img.save(out)
```
- Writes the image as a PNG file using Pillow

**Print confirmation**
```
print(f"[Saved] {out.resolve()}")
```
- Prints a message in terminal with the absolute path to the saved image

#### Main loop
1. `run()`
**Function definition**
```
def run(self):
```
- Start the app

**Start running loop**
```
running = True
while running:
```
- `running` is a boolean flag control the game loop
- as long as `running` stays `True`, the program will:
    - process input
    - draw the current screen
    - update the display
    - repeat

**Handle all events**
```
running = self.handle_events()
```
- calls `handle_events()` method to check:
    - quitting the window
    - button clicks
    - scorlling
    - painting and dragging
- If the user closes the window, `handle_events()` returns False, which sets `running = False` and the loop ends

**Draw screen**
```
if self.state == STATE_WELCOME:
    self.draw_welcome()
elif self.state == STATE_BROWSER:
    self.draw_browser()
elif self.state == STATE_PLAY:
    self.draw_play()
elif self.state == STATE_FINISHED:
    self.draw_finished()
```
- According to the `state`, draw the corresponding screen

**Update display**
```
pygame.display.flit()
```
- Updates the screen with whatever was drawn this frame
- pygame draws to an off-screen buffer first, `flip()` swaps it to the visible window

**Control frame rate**
```
self.clock.tick(60)
```
- Usees a pygame clock to limit the game loop to 60 frames per seconds. 

**Quit**
```
pygame.quit()
```
- When the loop ends, exit pygame

#### Entry
1. `main()`
This function accepts inputs. It starts the game when run the script from the command line
**Function definition**
```
def main():
```
- Defines main function for accepting inputs in command line

**Create argument parser**
```
ap = argparse.ArgumentParser(description="Color-by-Number Game")
```
- Uses python's built-in `argparse` module to handle command line arguments

**Define command line arguments**
```
ap.add_argument("--puzzles", type=str, default="./puzzles", help="directory containing puzzle folders")
ap.add_argument("--width", type=int, default=1000)
ap.add_argument("--height", type=int, default=800)
```
- `--puzzles`: folder path containing all puzzle subfolders
- `--width`: window width
- `--height`: window height

**parse arguments**
```
args = ap.parse_args()
```
- Reads and validates the arguments from command line
- Stores values in objects

**Create game application**
```
app = ColorByNumberApp(Path(args.puzzles), width=args.width, height=args.height)
```
- Instantiates the main game class `ColorByNumberApp`, passing:
    - `puzzles_dir`: the puzzles folder
    - `width` and `height`: the window size
- Insdie `ColorByNumberApp.__init__()`, it:
    - initializes pygame
    - loads puzzles
    - setup UI colors, fonts and buttons
    - prepares for the first frame

**Start game loop**
```
app.run()
```
- calls `run()` to starts the main game loop
- Then the program can:
    - handles events
    - draws screens
    - updates continuously until the user quits






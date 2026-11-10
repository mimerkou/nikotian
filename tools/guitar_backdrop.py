"""Nikotian — Guitar Collection v1.1.
Replace the light studio background of juan-hernandez-01 (Sonata) with the rust backdrop of the other
Juan Hernández photographs. Instrument pixels are untouched; edge pixels are un-mixed from the old
background and re-mixed onto the new one; the floor shadow (absent from the other JH photographs) becomes
backdrop. Enclosed light areas (headstock slots, saddle) are never touched: only background connected
to the image border is replaced. The shadow zone (lowest 10%) and the protected nut box are set for this
photograph (400×759); do not reuse on another photograph without checking them."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def replace_backdrop(src, dst, B_NEW):
    B_NEW = np.asarray(B_NEW, float)
    img = np.asarray(Image.open(src).convert('RGB')).astype(float)
    H, W, _ = img.shape
    B_OLD = np.median(np.concatenate([img[:, :3].reshape(-1, 3), img[:, -3:].reshape(-1, 3)]), axis=0)

    R, G, Bc = img[..., 0], img[..., 1], img[..., 2]
    dist_old = np.linalg.norm(img - B_OLD, axis=2)
    yy = np.arange(H)[:, None].repeat(W, 1)
    lum = img.mean(axis=2)
    sat = img.max(axis=2) - img.min(axis=2)
    shadow = (yy >= int(H * 0.9)) & ((((Bc - R) >= 2) & (lum > 120)) | ((Bc - R) >= 6))   # bluish floor shadow
    halo = (lum >= 236) & (sat <= 12)            # white clipping halo just outside the outline (lighter than the backdrop)
    # Protected: the bone nut (white, touches the background at its ends) — never background.
    protect = np.zeros((H, W), bool); protect[125:131, 176:218] = True
    cand = ((dist_old < 20) | shadow | halo) & ~protect

    lab, n = ndi.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))

    band = ndi.binary_dilation(bg, iterations=2) & ~bg
    fg = ~bg & ~band

    def nconv(values, mask, sigma):
        m = mask.astype(float)
        num = np.stack([ndi.gaussian_filter(values[..., k] * m, sigma) for k in range(3)], -1)
        den = ndi.gaussian_filter(m, sigma)[..., None]
        return num / np.maximum(den, 1e-6), den[..., 0]

    B_loc, wb = nconv(img, bg, 3.0)
    B_loc = np.where((wb > 1e-3)[..., None], B_loc, B_OLD)
    # Edge pixels: un-mix. For each band pixel, the foreground colour F is the fg neighbour (radius 3) that
    # best explains the pixel as a mix of F and the local background; alpha = projection on B→F.
    best_res = np.full((H, W), np.inf); a = np.zeros((H, W)); has_f = np.zeros((H, W), bool)
    pad = 3
    P = np.pad(img, ((pad, pad), (pad, pad), (0, 0)), mode='edge')
    PF = np.pad(fg, pad, mode='constant')
    for dy in range(-pad, pad + 1):
        for dx in range(-pad, pad + 1):
            if dy == 0 and dx == 0:
                continue
            F = P[pad + dy:pad + dy + H, pad + dx:pad + dx + W]
            ok = PF[pad + dy:pad + dy + H, pad + dx:pad + dx + W] & band
            d = F - B_loc
            den = np.maximum(np.sum(d * d, axis=2), 1e-6)
            al = np.clip(np.sum((img - B_loc) * d, axis=2) / den, 0, 1)
            res = np.linalg.norm(img - (B_loc + al[..., None] * d), axis=2) + 0.5 * np.hypot(dy, dx)
            upd = ok & (res < best_res) & (den > 25 ** 2)
            best_res[upd] = res[upd]; a[upd] = al[upd]; has_f |= upd
    near_bg = np.linalg.norm(img - B_loc, axis=2) < 18
    a = np.where(near_bg | ~has_f, 0.0, a)

    out = img.copy()
    # band: same pixel, its background share moved from the old (local) background to the new one
    out[band] = (img + (1 - a)[..., None] * (B_NEW - B_loc))[band]
    # background: new colour + the photograph's own fine grain (low-frequency shading/shadow removed)
    B_fine, _ = nconv(img, bg, 1.0)
    grain = np.clip(img - B_fine, -8, 8)
    # floor shadow: its own residue would leave streaks; use the grain of a clean backdrop patch instead
    ref = grain[200:260, 0:50]
    tile = np.tile(ref, (H // 60 + 1, W // 50 + 1, 1))[:H, :W]
    grain = np.where(shadow[..., None], tile, grain)
    out[bg] = (B_NEW + grain * 2.6)[bg]                     # grain scaled towards the σ≈2–3 of the JH 02–05 backdrops
    out = np.clip(out, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(dst, quality=98, subsampling=0, optimize=True)

    return {'oldBackdrop': [int(v) for v in B_OLD], 'backgroundPx': int(bg.sum()), 'edgePx': int(band.sum()), 'untouchedPx': int(fg.sum())}

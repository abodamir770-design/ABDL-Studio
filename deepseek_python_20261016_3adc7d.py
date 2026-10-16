# ============================================================
#   ABDL STUDIO  ::  PROFESSIONAL DESIGN SUITE
#   Splash Screen + Full Design Studio
#   Single file. Auto-installs. No commands needed.
# ============================================================

import sys, subprocess, os, threading, math, time, random

def _bootstrap():
    try:
        from PIL import Image  # noqa
        return
    except ImportError:
        pass
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "--quiet", "--disable-pip-version-check", "Pillow"])
    except Exception:
        pass
_bootstrap()

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import (Image, ImageDraw, ImageFont, ImageTk, ImageFilter,
                 ImageEnhance, ImageOps, ImageChops)

# ============================================================
# THEME — DEEP BLUE PROFESSIONAL
# ============================================================
NAVY_DEEP   = "#02040f"
NAVY        = "#0a1428"
NAVY_MID    = "#0f1e3d"
NAVY_HI     = "#16294f"
BLUE        = "#1e6fff"
BLUE_HI     = "#4d94ff"
BLUE_GLOW   = "#7fb4ff"
CYAN        = "#22d3ee"
BORDER      = "#1e3054"
TEXT        = "#eaf2ff"
MUTED       = "#6b8ab8"
OK          = "#22c55e"

F_TITLE  = ("Impact", 24)
F_H      = ("Segoe UI Semibold", 11)
F_BODY   = ("Segoe UI", 9)
F_SMALL  = ("Segoe UI", 8)
F_MONO   = ("Consolas", 8)
F_MONOB  = ("Consolas", 9, "bold")

# ============================================================
# CANVAS PRESETS
# ============================================================
PRESETS = {
    "Discord Server Banner":   (960,  540),
    "Discord Server Icon":     (512,  512),
    "Discord Profile Avatar":  (512,  512),
    "Discord Embed Image":     (600,  300),
    "YouTube Thumbnail":       (1280, 720),
    "YouTube Channel Banner":  (2560, 1440),
    "Twitter / X Header":      (1500, 500),
    "Instagram Post":          (1080, 1080),
    "Instagram Story":         (1080, 1920),
    "Twitch Panel":            (320,  100),
    "Twitch Offline Banner":   (1920, 1080),
    "Custom":                  (1000, 1000),
}

# ============================================================
# IMAGE ENGINE
# ============================================================
class Engine:
    @staticmethod
    def from_scratch(w, h, bg="#0b0b12"):
        return Image.new("RGBA", (w, h), bg)

    @staticmethod
    def fit(img, w, h, mode="cover"):
        iw, ih = img.size
        s = max(w/iw, h/ih) if mode == "cover" else min(w/iw, h/ih)
        nw, nh = int(iw*s), int(ih*s)
        img = img.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(img, ((w-nw)//2, (h-nh)//2), img if img.mode == "RGBA" else None)
        return canvas

    @staticmethod
    def brightness(i, v): return ImageEnhance.Brightness(i).enhance(v)
    @staticmethod
    def contrast(i, v):   return ImageEnhance.Contrast(i).enhance(v)
    @staticmethod
    def saturation(i, v): return ImageEnhance.Color(i).enhance(v)
    @staticmethod
    def sharpness(i, v):  return ImageEnhance.Sharpness(i).enhance(v)

    @staticmethod
    def blur(i, r):
        return i if r <= 0 else i.filter(ImageFilter.GaussianBlur(r))

    @staticmethod
    def sharpen_pro(i, a=1.5):
        return i.filter(ImageFilter.UnsharpMask(radius=2, percent=int(a*100), threshold=3))

    @staticmethod
    def vignette(img, strength=0.55, softness=1.3):
        w, h = img.size
        grad = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(grad)
        cx, cy = w/2, h/2
        max_d = math.hypot(cx, cy)
        step = max(2, int(min(w, h)/220))
        for r in range(0, int(max_d), step):
            t = r / max_d
            val = int(255 * min(1, max(0, (t - 0.35) * softness)))
            d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=val, width=step)
        grad = grad.filter(ImageFilter.GaussianBlur(radius=int(min(w,h)*0.05)))
        dark = Image.new("RGBA", (w, h), (0, 0, 0, int(255*strength)))
        dark.putalpha(grad.point(lambda p: int(p * strength)))
        return Image.alpha_composite(img.convert("RGBA"), dark)

    @staticmethod
    def glow(img, color=(34, 211, 238), radius=18, strength=0.75):
        base = img.convert("RGBA")
        alpha = base.split()[3]
        c = ImageColor.getrgb(color) if isinstance(color, str) else tuple(color)
        solid = Image.new("RGBA", base.size, c + (255,))
        solid.putalpha(alpha)
        g = solid.filter(ImageFilter.GaussianBlur(radius))
        g.putalpha(g.split()[3].point(lambda p: int(p*strength)))
        return Image.alpha_composite(base, g)

    @staticmethod
    def gradient_overlay(img, c1, c2, opacity=0.5, vertical=True):
        w, h = img.size
        base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c1 = ImageColor.getrgb(c1) if isinstance(c1, str) else c1
        c2 = ImageColor.getrgb(c2) if isinstance(c2, str) else c2
        rng = h if vertical else w
        for i in range(rng):
            t = i / rng
            r = int(c1[0] + (c2[0]-c1[0])*t)
            g = int(c1[1] + (c2[1]-c1[1])*t)
            b = int(c1[2] + (c2[2]-c1[2])*t)
            a = int(255*opacity)
            if vertical:
                ImageDraw.Draw(base).line([(0,i),(w,i)], fill=(r,g,b,a))
            else:
                ImageDraw.Draw(base).line([(i,0),(i,h)], fill=(r,g,b,a))
        return Image.alpha_composite(img.convert("RGBA"), base)

    @staticmethod
    def rounded_mask(img, radius):
        w, h = img.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
        out = img.convert("RGBA").copy()
        out.putalpha(ImageChops.multiply(out.split()[3], mask))
        return out

    @staticmethod
    def circle_mask(img):
        w, h = img.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, w, h], fill=255)
        out = img.convert("RGBA").copy()
        out.putalpha(ImageChops.multiply(out.split()[3], mask))
        return out

    @staticmethod
    def smart_enhance(img, preset="Clean Pro"):
        img = img.convert("RGBA")
        if preset == "Clean Pro":
            img = Engine.contrast(img, 1.12); img = Engine.saturation(img, 1.10)
            img = Engine.sharpen_pro(img, 1.4); img = Engine.vignette(img, 0.35)
        elif preset == "Cinematic":
            img = Engine.contrast(img, 1.22); img = Engine.saturation(img, 0.92)
            img = Engine.gradient_overlay(img, "#1e6fff", "#02040f", opacity=0.22)
            img = Engine.vignette(img, 0.55); img = Engine.sharpen_pro(img, 1.3)
        elif preset == "Neon Cyber":
            img = Engine.saturation(img, 1.35); img = Engine.contrast(img, 1.18)
            img = Engine.gradient_overlay(img, "#22d3ee", "#02040f", opacity=0.28)
            img = Engine.glow(img, (34, 211, 238), 14, 0.35)
            img = Engine.vignette(img, 0.5)
        elif preset == "Vibrant Pop":
            img = Engine.saturation(img, 1.45); img = Engine.brightness(img, 1.06)
            img = Engine.contrast(img, 1.08); img = Engine.sharpen_pro(img, 1.5)
        elif preset == "Moody":
            img = Engine.saturation(img, 0.78); img = Engine.contrast(img, 1.25)
            img = Engine.brightness(img, 0.94); img = Engine.vignette(img, 0.7)
        elif preset == "Soft Dream":
            img = Engine.brightness(img, 1.10); img = Engine.saturation(img, 1.08)
            img = Engine.blur(img, 0.6)
            img = Engine.gradient_overlay(img, "#7fb4ff", "#e0f2ff", opacity=0.15)
        elif preset == "Dark Pro":
            img = Engine.brightness(img, 0.86); img = Engine.contrast(img, 1.20)
            img = Engine.saturation(img, 1.05); img = Engine.vignette(img, 0.65)
            img = Engine.sharpen_pro(img, 1.4)
        return img

# ============================================================
# FONTS
# ============================================================
_FONT_CACHE = {}
def load_font(size, bold=True):
    key = (size, bold)
    if key in _FONT_CACHE: return _FONT_CACHE[key]
    names = (["impact.ttf", "arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]
             if bold else ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"])
    for n in names:
        try:
            f = ImageFont.truetype(n, size)
            _FONT_CACHE[key] = f
            return f
        except Exception:
            continue
    f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f

# ============================================================
# SPLASH SCREEN  —  the beautiful blue opening
# ============================================================
class SplashScreen:
    W, H = 920, 620

    def __init__(self, on_finish):
        self.on_finish = on_finish
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.configure(bg=NAVY_DEEP)
        self.root.attributes("-topmost", True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - self.W) // 2
        y = (sh - self.H) // 2
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg=NAVY_DEEP, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Build the static beautiful background once
        self._build_background()

        # Animated overlay values
        self.t = 0.0
        self.progress = 0.0
        self._text_items = []       # (canvas_id, delay, duration)
        self._load_frames = []

        # Sequence of appearing text
        self.steps = [
            ("ABDL",               "Impact",      58, BLUE_GLOW, 10,  0.0, 1.0),
            ("PROFESSIONAL DESIGN SUITE", "Consolas", 12, MUTED,  10,  0.5, 1.2),

            ("A complete graphic studio,",  "Segoe UI", 13, TEXT, 30,  1.6, 1.0),
            ("built for creators who refuse to compromise.",
                                            "Segoe UI", 13, TEXT, 30,  2.1, 1.0),

            ("◆   DESIGN LOGOS, BANNERS, ICONS  ◆", "Consolas", 10, CYAN, 30, 3.0, 1.0),
            ("◆   SMART ENHANCE ANY IMAGE      ◆", "Consolas", 10, CYAN, 30, 3.4, 1.0),
            ("◆   FULL EFFECTS + EXPORT SUITE  ◆", "Consolas", 10, CYAN, 30, 3.8, 1.0),

            ("Made with dedication.",              "Segoe UI", 11, BLUE_HI, 30, 4.8, 1.0),
            ("Six months. Thousands of hours.",    "Segoe UI", 11, BLUE_HI, 30, 5.3, 1.0),
            ("Every pixel placed by hand — for you.", "Segoe UI", 11, BLUE_GLOW, 30, 5.8, 1.0),

            ("ENJOY  THE  STUDIO.",                "Impact",   26, "#ffffff", 10, 6.8, 1.5),
        ]

        self.text_ids = []
        self.text_meta = []          # dict with creation timestamps
        self.animating = True
        self._animate()

    # ---------- background ----------
    def _build_background(self):
        W, H = self.W, self.H

        # Deep blue vertical gradient
        img = Image.new("RGB", (W, H), NAVY_DEEP)
        d = ImageDraw.Draw(img)
        for y in range(H):
            t = y / H
            r = int(2  + (10 - 2) * t)
            g = int(6  + (20 - 6) * t)
            b = int(24 + (58 - 24) * t)
            d.line([(0, y), (W, y)], fill=(r, g, b))

        # Soft radial glow behind title area
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        cx, cy = W//2, int(H*0.28)
        for i in range(28):
            r = 60 + i * 14
            a = max(0, int(70 * (1 - i/28)))
            gd.ellipse([cx-r, cy-r, cx+r, cy+r],
                       outline=(30, 110, 255, a), width=3)
        glow = glow.filter(ImageFilter.GaussianBlur(28))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

        # Grid dots (very subtle)
        d = ImageDraw.Draw(img, "RGBA")
        for gx in range(0, W, 32):
            for gy in range(0, H, 32):
                d.point((gx, gy), fill=(30, 80, 150, 40))

        # Corner accents
        d = ImageDraw.Draw(img, "RGBA")
        for (ox, oy, dx, dy) in [(0,0,1,1), (W,0,-1,1), (0,H,1,-1), (W,H,-1,-1)]:
            d.line([(ox+20*dx, oy+20*dy), (ox+120*dx, oy+20*dy)],
                   fill=(34, 211, 238, 180), width=2)
            d.line([(ox+20*dx, oy+20*dy), (ox+20*dx, oy+120*dy)],
                   fill=(34, 211, 238, 180), width=2)

        self._bg_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self._bg_img, anchor="nw")

        # Central panel (dark translucent card)
        pw, ph = 660, 480
        px, py = (W - pw)//2, int(H*0.16)
        panel = tk.Frame(self.canvas, bg=NAVY)
        # not used; drawn via canvas rects
        self.canvas.create_rectangle(px, py, px+pw, py+ph,
                                     fill="#0a1428", outline=BORDER, width=1)

        # top accent line
        self.canvas.create_rectangle(px, py, px+pw, py+2,
                                     fill=CYAN, outline="")

        # progress bar container
        self.bar_x1, self.bar_y1 = px + 60, py + ph - 60
        self.bar_x2, self.bar_y2 = px + pw - 60, py + ph - 40
        self.canvas.create_rectangle(self.bar_x1, self.bar_y1,
                                     self.bar_x2, self.bar_y2,
                                     fill="#0f1e3d", outline=BORDER)
        self.bar_fill = self.canvas.create_rectangle(
            self.bar_x1 + 2, self.bar_y1 + 2,
            self.bar_x1 + 2, self.bar_y2 - 2,
            fill=CYAN, outline="")

        # loading text
        self.load_txt = self.canvas.create_text(
            W//2, self.bar_y2 + 22,
            text="Preparing studio  ·  0%",
            font=("Consolas", 9), fill=MUTED)

    # ---------- animation ----------
    def _animate(self):
        if not self.animating:
            return
        self.t += 0.033

        # Spawn text items whose time has come
        for (text, family, size, color, delay_slot, spawn_t, dur) in self.steps:
            key = text
            if any(m["key"] == key for m in self.text_meta):
                continue
            if self.t >= spawn_t:
                # position determined by order
                idx = len(self.text_ids)
                self._create_text_entry(text, family, size, color, dur, key)

        # Update fade + slight float for each text item
        for meta in list(self.text_meta):
            age = self.t - meta["born"]
            if age < 0: continue
            alpha = min(1.0, age / meta["dur"]) if meta["dur"] > 0 else 1.0
            # fade-in only (kept visible)
            if alpha < 0.02: alpha = 0.02
            col = self._blend(meta["color"], NAVY, alpha)
            self.canvas.itemconfigure(meta["id"], fill=col)

            # tiny upward float for the title
            if meta.get("float"):
                dy = -math.sin(age * 1.2) * 1.5
                self.canvas.coords(meta["id"], meta["x"], meta["y"] + dy)

        # progress bar fill
        self.progress = min(1.0, self.progress + 0.011 + random.random()*0.006)
        w = (self.bar_x2 - self.bar_x1 - 4) * self.progress
        self.canvas.coords(self.bar_fill,
                           self.bar_x1 + 2, self.bar_y1 + 2,
                           self.bar_x1 + 2 + w, self.bar_y2 - 2)
        self.canvas.itemconfigure(self.load_txt,
                                  text=f"Preparing studio  ·  {int(self.progress*100)}%")

        if self.progress >= 1.0 and self.t > 7.5:
            self._finish()
            return

        self.root.after(30, self._animate)

    def _create_text_entry(self, text, family, size, color, dur, key):
        W = self.W
        # layout: distribute vertical positions
        base_y = 250
        spacing = 28
        idx = len(self.text_ids)

        # special positions for the brand
        if key == "ABDL":
            y = 200
            font = ("Impact", size)
            cid = self.canvas.create_text(W//2, y, text=text,
                                          font=font, fill=color)
            self.canvas.itemconfigure(cid, fill=self._blend(color, NAVY, 0.02))
            self._animate_glow_pulse(cid, color)
        elif key == "PROFESSIONAL DESIGN SUITE":
            y = 250
            cid = self.canvas.create_text(W//2, y, text=text,
                                          font=(family, size), fill=color)
        elif key.startswith("◆"):
            y = 320 + (idx - 6) * 22
            cid = self.canvas.create_text(W//2, y, text=text,
                                          font=(family, size), fill=color)
        elif "Made with" in key or "Six months" in key or "Every pixel" in key:
            y = 425 + (idx - 9) * 20
            cid = self.canvas.create_text(W//2, y, text=text,
                                          font=(family, size), fill=color)
        elif key == "ENJOY  THE  STUDIO.":
            y = 520
            cid = self.canvas.create_text(W//2, y, text=text,
                                          font=(family, size), fill=color)
        else:
            # Body description lines
            y = 285 + (idx - 2) * 22
            cid = self.canvas.create_text(W//2, y, text=text,
                                          font=(family, size), fill=color)

        self.text_ids.append(cid)
        self.text_meta.append({
            "id": cid, "key": key, "color": color,
            "born": self.t, "dur": dur,
            "x": W//2, "y": y,
            "float": key == "ABDL",
        })

    def _animate_glow_pulse(self, cid, base_color):
        def pulse(state=0):
            if not self.animating: return
            t = (math.sin(self.t * 2.0) + 1) / 2
            r = int(30  + (127 - 30)  * t)
            g = int(110 + (180 - 110) * t)
            b = int(255)
            self.canvas.itemconfigure(cid, fill=f"#{r:02x}{g:02x}{b:02x}")
            self.root.after(50, pulse)
        pulse()

    def _blend(self, c1, c2, t):
        c1 = c1.lstrip("#"); c2 = c2.lstrip("#")
        r1, g1, b1 = int(c1[0:2],16), int(c1[2:4],16), int(c1[4:6],16)
        r2, g2, b2 = int(c2[0:2],16), int(c2[2:4],16), int(c2[4:6],16)
        r = int(r1*t + r2*(1-t))
        g = int(g1*t + g2*(1-t))
        b = int(b1*t + b2*(1-t))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _finish(self):
        self.animating = False
        try:
            self.root.destroy()
        except Exception:
            pass
        self.on_finish()

    def run(self):
        self.root.mainloop()

# ============================================================
# MAIN APP (studio) — starts after splash
# ============================================================
class NeonButton(tk.Button):
    def __init__(self, master, text, command, color=BLUE, **kw):
        super().__init__(master, text=text, command=command,
                         bg=color, fg="#fff", activebackground=BLUE_HI,
                         activeforeground="#fff", bd=0, relief="flat",
                         font=("Segoe UI Semibold", 10), padx=14, pady=10,
                         cursor="hand2", **kw)
        self._c = color
        self.bind("<Enter>", lambda e: self.configure(bg=BLUE_HI))
        self.bind("<Leave>", lambda e: self.configure(bg=self._c))

class GhostButton(tk.Button):
    def __init__(self, master, text, command, **kw):
        super().__init__(master, text=text, command=command,
                         bg=NAVY_MID, fg=TEXT, activebackground=NAVY_HI,
                         activeforeground=CYAN, bd=0, relief="flat",
                         font=("Segoe UI Semibold", 10), padx=14, pady=10,
                         cursor="hand2", **kw)
        self.bind("<Enter>", lambda e: self.configure(bg=NAVY_HI, fg=CYAN))
        self.bind("<Leave>", lambda e: self.configure(bg=NAVY_MID, fg=TEXT))

def section_label(parent, text):
    tk.Label(parent, text=text, font=F_MONOB, fg=BLUE_GLOW, bg=NAVY)\
        .pack(anchor="w", padx=18, pady=(14, 6))

class NavButton(tk.Frame):
    def __init__(self, master, icon, label, sub, command):
        super().__init__(master, bg=NAVY, cursor="hand2")
        self.command = command; self.active = False
        self.icon = tk.Label(self, text=icon, font=("Segoe UI", 15), fg=CYAN, bg=NAVY)
        self.icon.pack(side="left", padx=(16, 10), pady=14)
        box = tk.Frame(self, bg=NAVY); box.pack(side="left", fill="x", expand=True, pady=12)
        self.title = tk.Label(box, text=label, font=F_H, fg=TEXT, bg=NAVY, anchor="w")
        self.title.pack(anchor="w")
        self.sub = tk.Label(box, text=sub, font=F_SMALL, fg=MUTED, bg=NAVY, anchor="w")
        self.sub.pack(anchor="w")
        for w in (self, self.icon, box, self.title, self.sub):
            w.bind("<Button-1>", lambda e: self.command())
            w.bind("<Enter>", self._enter); w.bind("<Leave>", self._leave)
    def _bg(self, c):
        self.configure(bg=c)
        for w in (self.icon, self.title, self.sub): w.configure(bg=c)
        for ch in self.winfo_children():
            ch.configure(bg=c)
            for s in ch.winfo_children(): s.configure(bg=c)
    def _enter(self, e):
        if not self.active: self._bg(NAVY_MID)
    def _leave(self, e):
        if not self.active: self._bg(NAVY)
    def set_active(self, v):
        self.active = v
        self._bg(NAVY_HI if v else NAVY)
        self.title.configure(fg=CYAN if v else TEXT)

class Project:
    def __init__(self):
        self.image = None
        self.original = None
        self.preset_name = "Discord Server Banner"
        self.history = []
    def push_history(self):
        if self.image:
            self.history.append(self.image.copy())
            if len(self.history) > 12: self.history.pop(0)
    def undo(self):
        if self.history:
            self.image = self.history.pop()
            return True
        return False

# ============================================================
# VIEWS
# ============================================================
class BaseView(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=NAVY_DEEP)
        self.app = app
        self.project = app.project

class DashboardView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        pad = tk.Frame(self, bg=NAVY_DEEP); pad.pack(fill="both", expand=True, padx=30, pady=26)
        tk.Label(pad, text="DASHBOARD", font=F_TITLE, fg=CYAN, bg=NAVY_DEEP).pack(anchor="w")
        tk.Label(pad, text="Start a project. Pick a canvas preset, load an image, or create from scratch.",
                 font=F_BODY, fg=MUTED, bg=NAVY_DEEP).pack(anchor="w", pady=(0, 22))

        actions = tk.Frame(pad, bg=NAVY_DEEP); actions.pack(fill="x", pady=(0, 22))
        self._card(actions, "◆  CREATE FROM SCRATCH", "Start with a blank canvas", self._new_blank)
        self._card(actions, "⬆  LOAD IMAGE", "Open a PNG / JPG / WEBP", self._load_img)
        self._card(actions, "✦  SMART ENHANCE", "Auto-upgrade any banner", self._quick_enhance)

        tk.Label(pad, text="CANVAS PRESETS", font=F_MONOB, fg=BLUE_GLOW, bg=NAVY_DEEP)\
            .pack(anchor="w", pady=(8, 10))
        grid = tk.Frame(pad, bg=NAVY_DEEP); grid.pack(fill="both", expand=True)
        for i, (name, (w, h)) in enumerate(PRESETS.items()):
            r, c = divmod(i, 4)
            self._preset_card(grid, name, w, h).grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        for c in range(4): grid.columnconfigure(c, weight=1)

    def _card(self, parent, title, sub, cmd):
        f = tk.Frame(parent, bg=NAVY, highlightthickness=1, highlightbackground=BORDER, cursor="hand2")
        f.pack(side="left", fill="both", expand=True, padx=4)
        inner = tk.Frame(f, bg=NAVY); inner.pack(padx=16, pady=18, fill="both", expand=True)
        tk.Label(inner, text=title, font=F_H, fg=TEXT, bg=NAVY).pack(anchor="w")
        tk.Label(inner, text=sub, font=F_SMALL, fg=MUTED, bg=NAVY).pack(anchor="w", pady=(2, 0))
        def enter(e): f.configure(highlightbackground=CYAN, bg=NAVY_MID); inner.configure(bg=NAVY_MID)
        def leave(e): f.configure(highlightbackground=BORDER, bg=NAVY); inner.configure(bg=NAVY)
        for w in (f, inner, *inner.winfo_children()):
            w.bind("<Button-1>", lambda e: cmd())
            w.bind("<Enter>", enter); w.bind("<Leave>", leave)

    def _preset_card(self, parent, name, w, h):
        f = tk.Frame(parent, bg=NAVY, highlightthickness=1, highlightbackground=BORDER, cursor="hand2")
        inner = tk.Frame(f, bg=NAVY); inner.pack(padx=12, pady=12, fill="both", expand=True)
        ratio = tk.Canvas(inner, width=80, height=48, bg=NAVY_HI, highlightthickness=0)
        ratio.pack(pady=(0, 8))
        rw = 76; rh = int(76 * h / w) if w > h else 76
        if rh > 44: rh = 44; rw = int(44 * w / h)
        ratio.create_rectangle((80-rw)//2, (48-rh)//2, (80+rw)//2, (48+rh)//2, outline=CYAN, width=2)
        tk.Label(inner, text=name, font=F_SMALL, fg=TEXT, bg=NAVY, wraplength=160).pack()
        tk.Label(inner, text=f"{w} × {h}", font=F_MONO, fg=MUTED, bg=NAVY).pack()
        def apply(e=None):
            self.project.preset_name = name
            self.project.push_history()
            self.project.image = Engine.from_scratch(w, h)
            self.project.original = self.project.image.copy()
            self.app.set_status(f"Canvas: {name}  ({w}×{h})")
        def enter(e): f.configure(highlightbackground=CYAN)
        def leave(e): f.configure(highlightbackground=BORDER)
        for widget in (f, inner, *inner.winfo_children()):
            widget.bind("<Button-1>", apply)
            widget.bind("<Enter>", enter); widget.bind("<Leave>", leave)
        return f

    def _new_blank(self):
        w, h = PRESETS[self.project.preset_name]
        self.project.push_history()
        self.project.image = Engine.from_scratch(w, h)
        self.project.original = self.project.image.copy()
        self.app.set_status(f"New blank canvas: {w}×{h}")
        self.app.show("logo")

    def _load_img(self):
        p = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All", "*.*")])
        if not p: return
        try: img = Image.open(p).convert("RGBA")
        except Exception as e:
            messagebox.showerror("ABDL", f"Could not open:\n{e}"); return
        self.project.push_history()
        self.project.original = img.copy()
        self.project.image = img.copy()
        self.app.set_status(f"Loaded: {os.path.basename(p)}  ({img.size[0]}×{img.size[1]})")

    def _quick_enhance(self):
        if not self.project.image:
            self._load_img()
        if self.project.image:
            self.project.push_history()
            self.project.image = Engine.smart_enhance(self.project.image, "Clean Pro")
            self.app.show("enhance")
            self.app.set_status("Applied: Clean Pro")

class LogoView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=330)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="LOGO FORGE", font=("Impact", 20), fg=CYAN, bg=NAVY)\
            .pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(left, text="Build a logo. Text, shape, glow, gradient.",
                 font=F_SMALL, fg=MUTED, bg=NAVY).pack(anchor="w", padx=18)

        section_label(left, "BRAND TEXT")
        self.var_text = tk.StringVar(value="ABDL")
        tk.Entry(left, textvariable=self.var_text, bg=NAVY_HI, fg=TEXT,
                 insertbackground=CYAN, bd=0, font=("Segoe UI Semibold", 12),
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=CYAN).pack(fill="x", padx=18, ipady=7)

        section_label(left, "SIZE")
        self.var_size = tk.IntVar(value=140)
        row = tk.Frame(left, bg=NAVY); row.pack(fill="x", padx=18, pady=3)
        tk.Scale(row, from_=40, to=320, orient="horizontal", variable=self.var_size,
                 bg=NAVY, fg=TEXT, troughcolor=NAVY_HI, highlightthickness=0, bd=0,
                 sliderrelief="flat", activebackground=CYAN, showvalue=False, length=200,
                 command=lambda v: self._render()).pack(fill="x", expand=True)

        section_label(left, "SHAPE")
        sf = tk.Frame(left, bg=NAVY); sf.pack(anchor="w", padx=18)
        self.var_shape = tk.StringVar(value="ring")
        for label, val in [("None","none"), ("Ring","ring"), ("Disc","circle"), ("Box","rect")]:
            tk.Radiobutton(sf, text=label, variable=self.var_shape, value=val,
                           bg=NAVY, fg=TEXT, selectcolor=NAVY_HI,
                           activebackground=NAVY, activeforeground=CYAN,
                           font=F_BODY, bd=0, highlightthickness=0,
                           command=self._render).pack(side="left", padx=2)

        section_label(left, "COLORS")
        self.var_fg = tk.StringVar(value="#22d3ee")
        self.var_bg = tk.StringVar(value="#0a1428")
        self.var_accent = tk.StringVar(value="#1e6fff")
        self._color_row(left, "Text color", self.var_fg)
        self._color_row(left, "Background", self.var_bg)
        self._color_row(left, "Accent", self.var_accent)

        section_label(left, "STYLE")
        self.var_glow = tk.BooleanVar(value=True)
        self.var_grad = tk.BooleanVar(value=False)
        self.var_meta = tk.BooleanVar(value=False)
        for text, var in [("Neon glow", self.var_glow),
                          ("Metallic gradient", self.var_grad),
                          ("3D shadow feel", self.var_meta)]:
            tk.Checkbutton(left, text="  " + text, variable=var, bg=NAVY, fg=TEXT,
                           selectcolor=NAVY_HI, activebackground=NAVY,
                           activeforeground=CYAN, font=F_BODY, bd=0,
                           highlightthickness=0, command=self._render)\
                .pack(anchor="w", padx=18, pady=1)

        tk.Frame(left, bg=NAVY, height=10).pack()
        NeonButton(left, "✓  RENDER LOGO", self._render).pack(fill="x", padx=18, pady=(0, 8))
        GhostButton(left, "⬇  APPLY TO CANVAS", self._apply).pack(fill="x", padx=18, pady=(0, 16))

        right = tk.Frame(self, bg=NAVY_DEEP); right.pack(side="left", fill="both", expand=True)
        self.preview_lbl = tk.Label(right, bg=NAVY_DEEP)
        self.preview_lbl.pack(expand=True)
        self._render()

    def _color_row(self, parent, label, var):
        row = tk.Frame(parent, bg=NAVY); row.pack(fill="x", padx=18, pady=2)
        tk.Label(row, text=label, font=F_SMALL, fg=TEXT, bg=NAVY, width=12, anchor="w")\
            .pack(side="left")
        sw = tk.Label(row, text="      ", bg=var.get(), cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        sw.pack(side="left")
        def pick(e=None):
            c = colorchooser.askcolor(color=var.get())[1]
            if c:
                var.set(c); sw.configure(bg=c); self._render()
        sw.bind("<Button-1>", pick)

    def _render(self, *_):
        W = H = 640
        bg = Image.new("RGBA", (W, H), self.var_bg.get())
        d = ImageDraw.Draw(bg)
        cx, cy = W//2, H//2
        shape = self.var_shape.get()
        accent = self.var_accent.get()
        if shape == "circle":
            r = int(W*0.40); d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=accent, width=5)
        elif shape == "ring":
            r = int(W*0.43); d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=accent, width=16)
        elif shape == "rect":
            p = int(W*0.12); d.rectangle([p, p, W-p, H-p], outline=accent, width=5)

        font = load_font(self.var_size.get(), bold=True)
        txt = self.var_text.get()

        if self.var_glow.get() and txt:
            gl = Image.new("RGBA", (W, H), (0,0,0,0))
            gd = ImageDraw.Draw(gl)
            bb = gd.textbbox((0, 0), txt, font=font)
            x = (W - (bb[2]-bb[0]))//2 - bb[0]
            y = (H - (bb[3]-bb[1]))//2 - bb[1]
            gd.text((x, y), txt, font=font, fill=self.var_fg.get())
            gl = gl.filter(ImageFilter.GaussianBlur(18))
            bg = Image.alpha_composite(bg, gl)
            d = ImageDraw.Draw(bg)

        if txt:
            bb = d.textbbox((0, 0), txt, font=font)
            x = (W - (bb[2]-bb[0]))//2 - bb[0]
            y = (H - (bb[3]-bb[1]))//2 - bb[1]
            if self.var_meta.get():
                d.text((x+3, y+3), txt, font=font, fill="#00000088")
                d.text((x+1, y+1), txt, font=font, fill="#ffffff44")
            d.text((x, y), txt, font=font, fill=self.var_fg.get())

        small = bg.resize((460, 460), Image.LANCZOS)
        self._img_ref = ImageTk.PhotoImage(small)
        self.preview_lbl.configure(image=self._img_ref)

    def _apply(self):
        if not self.project.image:
            w, h = PRESETS[self.project.preset_name]
            self.project.image = Engine.from_scratch(w, h)
        W, H = self.project.image.size
        tmp = self.project.image.copy()
        d = ImageDraw.Draw(tmp)
        cx, cy = W//2, H//2
        shape = self.var_shape.get(); accent = self.var_accent.get()
        if shape == "circle":
            r = int(min(W,H)*0.40); d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=accent, width=5)
        elif shape == "ring":
            r = int(min(W,H)*0.43); d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=accent, width=16)
        elif shape == "rect":
            p = int(min(W,H)*0.12); d.rectangle([p, p, W-p, H-p], outline=accent, width=5)
        size = int(self.var_size.get() * min(W, H) / 640)
        font = load_font(max(20, size), bold=True)
        txt = self.var_text.get()
        if txt:
            bb = d.textbbox((0,0), txt, font=font)
            x = (W - (bb[2]-bb[0]))//2 - bb[0]
            y = (H - (bb[3]-bb[1]))//2 - bb[1]
            d.text((x, y), txt, font=font, fill=self.var_fg.get())
        self.project.push_history()
        self.project.image = tmp
        self.app.set_status("Logo applied to canvas")

class EnhanceView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=330)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="SMART ENHANCE", font=("Impact", 20), fg=CYAN, bg=NAVY)\
            .pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(left, text="Load your banner. One click. Same style, way better.",
                 font=F_SMALL, fg=MUTED, bg=NAVY).pack(anchor="w", padx=18)

        section_label(left, "STYLE PRESETS")
        for p in ["Clean Pro", "Cinematic", "Neon Cyber", "Vibrant Pop",
                  "Moody", "Soft Dream", "Dark Pro"]:
            GhostButton(left, "  " + p, lambda n=p: self._apply(n))\
                .pack(fill="x", padx=18, pady=2)

        section_label(left, "MANUAL OVERRIDE")
        self.var_b  = tk.DoubleVar(value=1.0)
        self.var_c  = tk.DoubleVar(value=1.0)
        self.var_s  = tk.DoubleVar(value=1.0)
        self.var_sh = tk.DoubleVar(value=1.0)
        self.var_v  = tk.DoubleVar(value=0.0)
        for lbl, v in [("Brightness", self.var_b), ("Contrast", self.var_c),
                       ("Saturation", self.var_s), ("Sharpness", self.var_sh),
                       ("Vignette", self.var_v)]:
            r = tk.Frame(left, bg=NAVY); r.pack(fill="x", padx=18, pady=2)
            tk.Label(r, text=lbl, font=F_SMALL, fg=TEXT, bg=NAVY, width=11, anchor="w").pack(side="left")
            tk.Scale(r, from_=0.4, to=2.5, orient="horizontal", variable=v,
                     resolution=0.05, bg=NAVY, fg=TEXT, troughcolor=NAVY_HI,
                     highlightthickness=0, bd=0, sliderrelief="flat",
                     activebackground=CYAN, length=170)\
                .pack(side="left", fill="x", expand=True, padx=4)
        GhostButton(left, "✓  APPLY MANUAL", self._manual).pack(fill="x", padx=18, pady=(10, 6))
        section_label(left, "HISTORY")
        GhostButton(left, "↶  UNDO", self._undo).pack(fill="x", padx=18, pady=2)

    def _apply(self, name):
        if not self.project.image: return
        self.project.push_history()
        self.project.image = Engine.smart_enhance(self.project.image, name)
        self.app.set_status(f"Enhance: {name}")

    def _manual(self):
        if not self.project.image: return
        self.project.push_history()
        i = self.project.image
        i = Engine.brightness(i, self.var_b.get())
        i = Engine.contrast(i, self.var_c.get())
        i = Engine.saturation(i, self.var_s.get())
        i = Engine.sharpen_pro(i, self.var_sh.get())
        if self.var_v.get() > 0: i = Engine.vignette(i, self.var_v.get())
        self.project.image = i
        self.app.set_status("Applied manual adjustments")

    def _undo(self):
        if self.project.undo(): self.app.set_status("Undone")

class EffectsView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=330)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="EFFECTS LAB", font=("Impact", 20), fg=CYAN, bg=NAVY)\
            .pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(left, text="Filters, overlays and finishing touches.",
                 font=F_SMALL, fg=MUTED, bg=NAVY).pack(anchor="w", padx=18)

        section_label(left, "FILTERS")
        GhostButton(left, "  Vignette (dark edges)", self._vignette).pack(fill="x", padx=18, pady=2)
        GhostButton(left, "  Neon Glow (cyan)",      self._glow).pack(fill="x", padx=18, pady=2)
        GhostButton(left, "  Soft Blur",             self._blur).pack(fill="x", padx=18, pady=2)

        section_label(left, "GRADIENT OVERLAY")
        self.var_c1 = tk.StringVar(value="#22d3ee")
        self.var_c2 = tk.StringVar(value="#02040f")
        self._crow(left, "Top color",    self.var_c1)
        self._crow(left, "Bottom color", self.var_c2)
        self.var_op = tk.DoubleVar(value=0.35)
        r = tk.Frame(left, bg=NAVY); r.pack(fill="x", padx=18, pady=4)
        tk.Label(r, text="Opacity", font=F_SMALL, fg=TEXT, bg=NAVY, width=11, anchor="w").pack(side="left")
        tk.Scale(r, from_=0.05, to=0.9, resolution=0.05, orient="horizontal",
                 variable=self.var_op, bg=NAVY, fg=TEXT, troughcolor=NAVY_HI,
                 highlightthickness=0, bd=0, sliderrelief="flat",
                 activebackground=CYAN, length=170).pack(side="left", fill="x", expand=True)
        GhostButton(left, "✓  APPLY GRADIENT", self._gradient).pack(fill="x", padx=18, pady=6)

        section_label(left, "MASK / FRAME")
        GhostButton(left, "  Circle crop",       self._circle).pack(fill="x", padx=18, pady=2)
        GhostButton(left, "  Rounded corners",   self._rounded).pack(fill="x", padx=18, pady=2)
        GhostButton(left, "  Fit to canvas",     self._fit).pack(fill="x", padx=18, pady=2)

    def _crow(self, parent, label, var):
        row = tk.Frame(parent, bg=NAVY); row.pack(fill="x", padx=18, pady=2)
        tk.Label(row, text=label, font=F_SMALL, fg=TEXT, bg=NAVY, width=12, anchor="w").pack(side="left")
        sw = tk.Label(row, text="      ", bg=var.get(), cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        sw.pack(side="left")
        def pick(e=None):
            c = colorchooser.askcolor(color=var.get())[1]
            if c: var.set(c); sw.configure(bg=c)
        sw.bind("<Button-1>", pick)

    def _need(self):
        if not self.project.image:
            messagebox.showinfo("ABDL", "Load or create a canvas first."); return False
        return True

    def _vignette(self):
        if not self._need(): return
        self.project.push_history()
        self.project.image = Engine.vignette(self.project.image, 0.55)
        self.app.set_status("Vignette applied")

    def _glow(self):
        if not self._need(): return
        self.project.push_history()
        self.project.image = Engine.glow(self.project.image, (34,211,238), 16, 0.55)
        self.app.set_status("Neon glow applied")

    def _blur(self):
        if not self._need(): return
        self.project.push_history()
        self.project.image = Engine.blur(self.project.image, 2.5)
        self.app.set_status("Blur applied")

    def _gradient(self):
        if not self._need(): return
        self.project.push_history()
        self.project.image = Engine.gradient_overlay(self.project.image,
                                                      self.var_c1.get(),
                                                      self.var_c2.get(),
                                                      self.var_op.get())
        self.app.set_status("Gradient overlay applied")

    def _circle(self):
        if not self._need(): return
        self.project.push_history()
        self.project.image = Engine.circle_mask(self.project.image)
        self.app.set_status("Circle mask applied")

    def _rounded(self):
        if not self._need(): return
        self.project.push_history()
        w, h = self.project.image.size
        self.project.image = Engine.rounded_mask(self.project.image, int(min(w,h)*0.06))
        self.app.set_status("Rounded corners applied")

    def _fit(self):
        if not self._need(): return
        self.project.push_history()
        w, h = self.project.image.size
        self.project.image = Engine.fit(self.project.image, w, h, "cover")
        self.app.set_status("Fitted to canvas")

class ExportView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        pad = tk.Frame(self, bg=NAVY_DEEP); pad.pack(fill="both", expand=True, padx=30, pady=26)
        tk.Label(pad, text="EXPORT", font=F_TITLE, fg=CYAN, bg=NAVY_DEEP).pack(anchor="w")
        tk.Label(pad, text="Save your design. Choose format and target size.",
                 font=F_BODY, fg=MUTED, bg=NAVY_DEEP).pack(anchor="w", pady=(0, 22))

        card = tk.Frame(pad, bg=NAVY, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(card, bg=NAVY); inner.pack(padx=22, pady=20, fill="x")

        tk.Label(inner, text="FORMAT", font=F_MONOB, fg=BLUE_GLOW, bg=NAVY).pack(anchor="w")
        self.var_fmt = tk.StringVar(value="PNG")
        row = tk.Frame(inner, bg=NAVY); row.pack(anchor="w", pady=(4, 12))
        for f in ["PNG", "JPG", "WEBP"]:
            tk.Radiobutton(row, text=f, variable=self.var_fmt, value=f,
                           bg=NAVY, fg=TEXT, selectcolor=NAVY_HI,
                           activebackground=NAVY, activeforeground=CYAN,
                           font=F_BODY, bd=0, highlightthickness=0)\
                .pack(side="left", padx=(0, 12))

        tk.Label(inner, text="RESIZE TO PRESET", font=F_MONOB, fg=BLUE_GLOW, bg=NAVY).pack(anchor="w")
        self.var_size = tk.StringVar(value="Original")
        opts = ["Original"] + [f"{k}  ({v[0]}×{v[1]})" for k, v in PRESETS.items()]
        menu = tk.OptionMenu(inner, self.var_size, *opts)
        menu.configure(bg=NAVY_HI, fg=TEXT, activebackground=NAVY_MID,
                       activeforeground=CYAN, bd=0, highlightthickness=0,
                       font=F_BODY, anchor="w")
        menu["menu"].configure(bg=NAVY, fg=TEXT, activebackground=BLUE, activeforeground="#fff")
        menu.pack(anchor="w", pady=(4, 12), fill="x")

        self.var_quality = tk.IntVar(value=95)
        rowq = tk.Frame(inner, bg=NAVY); rowq.pack(fill="x", pady=(4, 6))
        tk.Label(rowq, text="Quality", font=F_BODY, fg=TEXT, bg=NAVY, width=10, anchor="w").pack(side="left")
        tk.Scale(rowq, from_=50, to=100, orient="horizontal", variable=self.var_quality,
                 bg=NAVY, fg=TEXT, troughcolor=NAVY_HI, highlightthickness=0,
                 bd=0, sliderrelief="flat", activebackground=CYAN, length=300)\
            .pack(side="left", fill="x", expand=True)

        NeonButton(inner, "⬇  SAVE FILE", self._save).pack(anchor="w", pady=(14, 0))

        self.preview = tk.Label(pad, bg=NAVY_DEEP)
        self.preview.pack(expand=True, pady=10)

    def refresh_preview(self):
        if not self.project.image: return
        img = self.project.image.copy()
        img.thumbnail((520, 320), Image.LANCZOS)
        self._ref = ImageTk.PhotoImage(img)
        self.preview.configure(image=self._ref)

    def _save(self):
        if not self.project.image:
            messagebox.showinfo("ABDL", "Nothing to export."); return
        fmt = self.var_fmt.get()
        ext = {"PNG": ".png", "JPG": ".jpg", "WEBP": ".webp"}[fmt]
        p = filedialog.asksaveasfilename(defaultextension=ext,
                                         filetypes=[(fmt, f"*{ext}")],
                                         initialfile=f"abdl_design{ext}")
        if not p: return
        img = self.project.image.copy()
        sel = self.var_size.get()
        if sel != "Original":
            name = sel.split("  (")[0]
            if name in PRESETS:
                w, h = PRESETS[name]
                img = Engine.fit(img, w, h, "cover")
        if fmt == "JPG":
            bg = Image.new("RGB", img.size, (0, 0, 0))
            bg.paste(img, mask=img.split()[3])
            bg.save(p, "JPEG", quality=self.var_quality.get())
        elif fmt == "WEBP":
            img.save(p, "WEBP", quality=self.var_quality.get())
        else:
            img.save(p, "PNG")
        messagebox.showinfo("ABDL", f"Saved:\n{p}")
        self.app.set_status(f"Exported: {os.path.basename(p)}")

class IconView(BaseView):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=330)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="ICON STUDIO", font=("Impact", 20), fg=CYAN, bg=NAVY)\
            .pack(anchor="w", padx=18, pady=(18, 2))
        tk.Label(left, text="Server icons, avatars, profile pictures.",
                 font=F_SMALL, fg=MUTED, bg=NAVY).pack(anchor="w", padx=18)

        section_label(left, "LOAD BASE IMAGE")
        GhostButton(left, "⬆  OPEN IMAGE", self._load).pack(fill="x", padx=18, pady=2)

        section_label(left, "MASK SHAPE")
        self.var_shape = tk.StringVar(value="circle")
        for label, val in [("Circle", "circle"), ("Rounded", "rounded"), ("Square", "square")]:
            tk.Radiobutton(left, text=label, variable=self.var_shape, value=val,
                           bg=NAVY, fg=TEXT, selectcolor=NAVY_HI,
                           activebackground=NAVY, activeforeground=CYAN,
                           font=F_BODY, bd=0, highlightthickness=0)\
                .pack(anchor="w", padx=18, pady=1)

        section_label(left, "FRAME")
        self.var_frame = tk.BooleanVar(value=True)
        self.var_frame_color = tk.StringVar(value=CYAN)
        self.var_frame_width = tk.IntVar(value=14)
        tk.Checkbutton(left, text="  Neon frame", variable=self.var_frame,
                       bg=NAVY, fg=TEXT, selectcolor=NAVY_HI,
                       activebackground=NAVY, activeforeground=CYAN,
                       font=F_BODY, bd=0, highlightthickness=0)\
            .pack(anchor="w", padx=18, pady=2)
        r = tk.Frame(left, bg=NAVY); r.pack(fill="x", padx=18, pady=2)
        tk.Label(r, text="Color", font=F_SMALL, fg=TEXT, bg=NAVY, width=6).pack(side="left")
        sw = tk.Label(r, text="      ", bg=CYAN, cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        sw.pack(side="left")
        def pick(e=None):
            c = colorchooser.askcolor(color=self.var_frame_color.get())[1]
            if c: self.var_frame_color.set(c); sw.configure(bg=c)
        sw.bind("<Button-1>", pick)
        rw = tk.Frame(left, bg=NAVY); rw.pack(fill="x", padx=18, pady=2)
        tk.Label(rw, text="Width", font=F_SMALL, fg=TEXT, bg=NAVY, width=6).pack(side="left")
        tk.Scale(rw, from_=2, to=40, orient="horizontal", variable=self.var_frame_width,
                 bg=NAVY, fg=TEXT, troughcolor=NAVY_HI, highlightthickness=0,
                 bd=0, sliderrelief="flat", activebackground=CYAN, length=180)\
            .pack(side="left", fill="x", expand=True)

        tk.Frame(left, bg=NAVY, height=8).pack()
        NeonButton(left, "✓  BUILD ICON", self._build).pack(fill="x", padx=18, pady=(0, 16))

        self.preview = tk.Label(self, bg=NAVY_DEEP)
        self.preview.pack(expand=True)

    def _load(self):
        p = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")])
        if not p: return
        try: img = Image.open(p).convert("RGBA")
        except Exception as e:
            messagebox.showerror("ABDL", str(e)); return
        self.project.push_history()
        self.project.original = img.copy()
        self.project.image = img.copy()
        self._show_preview(img)

    def _build(self):
        if not self.project.image:
            self._load(); return
        img = self.project.image.copy()
        w, h = img.size
        s = min(w, h)
        img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
        shape = self.var_shape.get()
        if shape == "circle":
            img = Engine.circle_mask(img)
        elif shape == "rounded":
            img = Engine.rounded_mask(img, int(s * 0.15))
        if self.var_frame.get():
            frame = Image.new("RGBA", img.size, (0,0,0,0))
            d = ImageDraw.Draw(frame)
            color = self.var_frame_color.get()
            fw = self.var_frame_width.get()
            if shape == "circle":
                d.ellipse([fw//2, fw//2, s-fw//2, s-fw//2], outline=color, width=fw)
            elif shape == "rounded":
                d.rounded_rectangle([fw//2, fw//2, s-fw//2, s-fw//2],
                                    radius=int(s*0.15), outline=color, width=fw)
            else:
                d.rectangle([fw//2, fw//2, s-fw//2, s-fw//2], outline=color, width=fw)
            img = Image.alpha_composite(img, frame)
        self.project.push_history()
        self.project.image = img
        self.app.set_status("Icon built")
        self._show_preview(img)

    def _show_preview(self, img):
        p = img.copy(); p.thumbnail((420, 420), Image.LANCZOS)
        self._ref = ImageTk.PhotoImage(p)
        self.preview.configure(image=self._ref)

# ============================================================
# MAIN APP
# ============================================================
class ABDLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ABDL Studio  —  Professional Design Suite")
        self.geometry("1400x880")
        self.minsize(1200, 780)
        self.configure(bg=NAVY_DEEP)
        self.project = Project()
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=NAVY_DEEP, height=84)
        header.pack(fill="x"); header.pack_propagate(False)
        brand = tk.Frame(header, bg=NAVY_DEEP); brand.pack(side="left", padx=26, pady=12)
        tk.Label(brand, text="ABDL", font=("Impact", 30), fg=CYAN, bg=NAVY_DEEP).pack(anchor="w")
        tk.Label(brand, text="PROFESSIONAL  DESIGN  SUITE", font=F_MONO, fg=MUTED, bg=NAVY_DEEP)\
            .pack(anchor="w")

        right = tk.Frame(header, bg=NAVY_DEEP); right.pack(side="right", padx=26, pady=22)
        self.status_lbl = tk.Label(right, text="Ready", font=F_SMALL, fg=MUTED, bg=NAVY_DEEP)
        self.status_lbl.pack(anchor="e")
        tk.Label(right, text="◆  6 modules  ◆  export PNG / JPG / WEBP",
                 font=F_MONO, fg=BLUE_GLOW, bg=NAVY_DEEP).pack(anchor="e")

        tk.Frame(self, bg=CYAN, height=2).pack(fill="x")

        body = tk.Frame(self, bg=NAVY_DEEP); body.pack(fill="both", expand=True)

        sb = tk.Frame(body, bg=NAVY, width=230); sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Label(sb, text="MODULES", font=F_MONOB, fg=BLUE_GLOW, bg=NAVY)\
            .pack(anchor="w", padx=18, pady=(18, 6))

        items = [
            ("dashboard", "◆", "Dashboard",      "start here"),
            ("logo",      "✦", "Logo Forge",     "text logos & marks"),
            ("icon",      "◉", "Icon Studio",    "server icons"),
            ("enhance",   "★", "Smart Enhance",  "upgrade any banner"),
            ("effects",   "▲", "Effects Lab",    "filters & overlays"),
            ("export",    "⬇", "Export",         "save your work"),
        ]
        self.nav = {}
        for key, icon, label, sub in items:
            btn = NavButton(sb, icon, label, sub, lambda k=key: self.show(k))
            btn.pack(fill="x", pady=1)
            self.nav[key] = btn

        tk.Label(sb, text="ABDL  ::  v2.0", font=F_MONO, fg=MUTED, bg=NAVY)\
            .pack(side="bottom", pady=14)

        self.content = tk.Frame(body, bg=NAVY_DEEP)
        self.content.pack(side="left", fill="both", expand=True)

        self.views = {
            "dashboard": DashboardView(self.content, self),
            "logo":      LogoView(self.content, self),
            "icon":      IconView(self.content, self),
            "enhance":   EnhanceView(self.content, self),
            "effects":   EffectsView(self.content, self),
            "export":    ExportView(self.content, self),
        }
        for v in self.views.values():
            v.place(relx=0, rely=0, relwidth=1, relheight=1)

        toolbar = tk.Frame(self, bg=NAVY_MID, height=46)
        toolbar.pack(fill="x", side="bottom"); toolbar.pack_propagate(False)
        tk.Label(toolbar, text="  ⌘ ABDL  •  quick actions", font=F_MONO,
                 fg=MUTED, bg=NAVY_MID).pack(side="left", padx=12)
        GhostButton(toolbar, "↶  UNDO", self.undo).pack(side="right", padx=4, pady=6)
        GhostButton(toolbar, "⬆  LOAD", self.load_any).pack(side="right", padx=4, pady=6)
        NeonButton(toolbar, "⬇  SAVE", self.quick_save).pack(side="right", padx=4, pady=6)

        self.show("dashboard")

    def show(self, key):
        for k, btn in self.nav.items():
            btn.set_active(k == key)
        self.views[key].tkraise()
        if key == "export":
            self.views["export"].refresh_preview()

    def set_status(self, txt):
        self.status_lbl.configure(text=txt, fg=BLUE_GLOW)

    def undo(self):
        if self.project.undo(): self.set_status("Undone")

    def load_any(self):
        self.views["dashboard"]._load_img()

    def quick_save(self):
        if not self.project.image:
            messagebox.showinfo("ABDL", "Nothing to save yet.")
            return
        self.show("export")
        self.views["export"]._save()

# ============================================================
# ENTRY
# ============================================================
def launch_app():
    app = ABDLApp()
    app.mainloop()

if __name__ == "__main__":
    splash = SplashScreen(on_finish=launch_app)
    splash.run()
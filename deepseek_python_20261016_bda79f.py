# -*- coding: utf-8 -*-
# ============================================================
#   עבדול סטודיו  ::  סוויטת עיצוב מקצועית
# ============================================================

import sys, subprocess, os, threading, math, random

def _boot():
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
_boot()

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import (Image, ImageDraw, ImageFont, ImageTk, ImageFilter,
                 ImageEnhance, ImageChops, ImageColor, ImageOps)

# ============================================================
# צבעים — כחול עמוק
# ============================================================
DEEP    = "#02040f"
NAVY    = "#0a1428"
NAVY_M  = "#0f1e3d"
NAVY_H  = "#16294f"
BLUE    = "#1e6fff"
BLUE_H  = "#4d94ff"
CYAN    = "#22d3ee"
BORDER  = "#1e3054"
TEXT    = "#eaf2ff"
MUTED   = "#6b8ab8"

# פונטים עבריים עבים ועגולים
F_TITLE  = ("Segoe UI", 26, "bold")
F_H      = ("Segoe UI", 12, "bold")
F_B      = ("Segoe UI", 10)
F_S      = ("Segoe UI", 9)
F_BIG    = ("Segoe UI Black", 46, "bold")
F_MONO   = ("Consolas", 8)

# ============================================================
# גדלים
# ============================================================
PRESETS = {
    "באנר דיסקורד":      (960,  540),
    "אייקון דיסקורד":    (512,  512),
    "תמונת פרופיל":      (512,  512),
    "תמונה להטמעה":      (600,  300),
    "תמונת יוטיוב":      (1280, 720),
    "באנר יוטיוב":       (2560, 1440),
    "כותרת טוויטר":      (1500, 500),
    "פוסט אינסטגרם":     (1080, 1080),
    "סטורי אינסטגרם":    (1080, 1920),
    "פאנל טוויץ'":       (320,  100),
    "באנר טוויץ'":       (1920, 1080),
    "מותאם אישית":       (1000, 1000),
}

# ============================================================
# מנוע עיבוד תמונה
# ============================================================
class Engine:
    @staticmethod
    def blank(w, h, bg="#0a1428"):
        return Image.new("RGBA", (w, h), bg)

    @staticmethod
    def fit(img, w, h, mode="cover"):
        iw, ih = img.size
        s = max(w/iw, h/ih) if mode == "cover" else min(w/iw, h/ih)
        nw, nh = int(iw*s), int(ih*s)
        img = img.resize((nw, nh), Image.LANCZOS)
        c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c.paste(img, ((w-nw)//2, (h-nh)//2), img if img.mode == "RGBA" else None)
        return c

    @staticmethod
    def bright(i, v): return ImageEnhance.Brightness(i).enhance(v)
    @staticmethod
    def contr(i, v):  return ImageEnhance.Contrast(i).enhance(v)
    @staticmethod
    def sat(i, v):    return ImageEnhance.Color(i).enhance(v)
    @staticmethod
    def sharp(i, v):  return ImageEnhance.Sharpness(i).enhance(v)

    @staticmethod
    def blur(i, r):
        return i if r <= 0 else i.filter(ImageFilter.GaussianBlur(r))

    @staticmethod
    def unsharp(i, a=1.5):
        return i.filter(ImageFilter.UnsharpMask(radius=2, percent=int(a*100), threshold=3))

    @staticmethod
    def vignette(img, s=0.55, soft=1.3):
        w, h = img.size
        grad = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(grad)
        cx, cy = w/2, h/2
        max_d = math.hypot(cx, cy)
        step = max(2, int(min(w, h)/220))
        for r in range(0, int(max_d), step):
            t = r / max_d
            v = int(255 * min(1, max(0, (t - 0.35) * soft)))
            d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=v, width=step)
        grad = grad.filter(ImageFilter.GaussianBlur(radius=int(min(w,h)*0.05)))
        dark = Image.new("RGBA", (w, h), (0, 0, 0, int(255*s)))
        dark.putalpha(grad.point(lambda p: int(p * s)))
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
    def grad_over(img, c1, c2, op=0.5):
        w, h = img.size
        base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c1 = ImageColor.getrgb(c1) if isinstance(c1, str) else c1
        c2 = ImageColor.getrgb(c2) if isinstance(c2, str) else c2
        for i in range(h):
            t = i / h
            r = int(c1[0] + (c2[0]-c1[0])*t)
            g = int(c1[1] + (c2[1]-c1[1])*t)
            b = int(c1[2] + (c2[2]-c1[2])*t)
            a = int(255*op)
            ImageDraw.Draw(base).line([(0,i),(w,i)], fill=(r,g,b,a))
        return Image.alpha_composite(img.convert("RGBA"), base)

    @staticmethod
    def round_mask(img, r):
        w, h = img.size
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
        out = img.convert("RGBA").copy()
        out.putalpha(ImageChops.multiply(out.split()[3], m))
        return out

    @staticmethod
    def circle_mask(img):
        w, h = img.size
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).ellipse([0, 0, w, h], fill=255)
        out = img.convert("RGBA").copy()
        out.putalpha(ImageChops.multiply(out.split()[3], m))
        return out

    # ===== הקסם — פי 10,000 יותר יפה =====
    @staticmethod
    def magic(img, style="חד ומקצועי"):
        img = img.convert("RGBA")
        if style == "חד ומקצועי":
            img = Engine.contr(1.18)
            img = Engine.contr(img, 1.15)
            img = Engine.sat(img, 1.15)
            img = Engine.unsharp(img, 1.6)
            img = Engine.vignette(img, 0.38)
        elif style == "קולנועי":
            img = Engine.contr(img, 1.25)
            img = Engine.sat(img, 0.94)
            img = Engine.grad_over(img, "#1e6fff", "#02040f", 0.25)
            img = Engine.vignette(img, 0.58)
            img = Engine.unsharp(img, 1.4)
        elif style == "ניאון":
            img = Engine.sat(img, 1.40)
            img = Engine.contr(img, 1.20)
            img = Engine.grad_over(img, "#22d3ee", "#02040f", 0.30)
            img = Engine.glow(img, (34, 211, 238), 14, 0.40)
            img = Engine.vignette(img, 0.50)
        elif style == "צבעוני":
            img = Engine.sat(img, 1.50)
            img = Engine.bright(img, 1.08)
            img = Engine.contr(img, 1.10)
            img = Engine.unsharp(img, 1.6)
        elif style == "חלום":
            img = Engine.bright(img, 1.12)
            img = Engine.sat(img, 1.10)
            img = Engine.blur(img, 0.6)
            img = Engine.grad_over(img, "#7fb4ff", "#e0f2ff", 0.15)
        elif style == "אפל":
            img = Engine.bright(img, 0.86)
            img = Engine.contr(img, 1.22)
            img = Engine.sat(img, 1.05)
            img = Engine.vignette(img, 0.68)
            img = Engine.unsharp(img, 1.5)
        elif style == "רטרו":
            img = Engine.sat(img, 0.85)
            img = Engine.contr(img, 1.10)
            img = Engine.grad_over(img, "#ffb070", "#3a1a55", 0.18)
            img = Engine.vignette(img, 0.42)
        return img

# ============================================================
# פונטים
# ============================================================
_FONTS = {}
def load_font(size, bold=True):
    key = (size, bold)
    if key in _FONTS: return _FONTS[key]
    for n in (["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]
              if bold else ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]):
        try:
            f = ImageFont.truetype(n, size)
            _FONTS[key] = f
            return f
        except Exception:
            continue
    f = ImageFont.load_default()
    _FONTS[key] = f
    return f

def rtl(text):
    """הופך סדר תווים בשביל PIL שיצייר עברית נכון"""
    return text[::-1]

# ============================================================
# מסך פתיחה
# ============================================================
class SplashScreen:
    W, H = 920, 640

    def __init__(self, on_done):
        self.on_done = on_done
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.configure(bg=DEEP)
        self.root.attributes("-topmost", True)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")

        self.c = tk.Canvas(self.root, width=self.W, height=self.H,
                           bg=DEEP, highlightthickness=0)
        self.c.pack(fill="both", expand=True)

        self._bg()
        self.t = 0.0
        self.progress = 0.0
        self._meta = []

        self.steps = [
            ("עבדול",                "Segoe UI Black", 72, CYAN,     0.0, 1.0),
            ("סטודיו",              "Segoe UI Black", 72, "#ffffff", 0.3, 1.0),
            ("סוויטת עיצוב מקצועית", "Segoe UI",       14, MUTED,    0.9, 1.0),
            ("תוכנה אחת. כל העיצוב שלך.", "Segoe UI",  16, TEXT,     1.8, 1.0),
            ("◆  עיצוב לוגואים ובאנרים  ◆", "Segoe UI", 12, CYAN,    2.8, 1.0),
            ("◆  קסם אוטומטי לתמונות     ◆", "Segoe UI", 12, CYAN,   3.2, 1.0),
            ("◆  אפקטים מקצועיים + ייצוא  ◆", "Segoe UI", 12, CYAN,  3.6, 1.0),
            ("נבנה באהבה, פיקסל אחר פיקסל.", "Segoe UI", 13, BLUE_H, 4.6, 1.0),
            ("עבור  עבדול.",          "Segoe UI Black", 32, "#ffffff", 6.0, 1.5),
        ]
        self._animate()

    def _bg(self):
        W, H = self.W, self.H
        img = Image.new("RGB", (W, H), DEEP)
        d = ImageDraw.Draw(img)
        for y in range(H):
            t = y/H
            d.line([(0,y),(W,y)], fill=(int(2+8*t), int(6+18*t), int(24+44*t)))
        glow = Image.new("RGBA", (W,H), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        cx, cy = W//2, int(H*0.30)
        for i in range(30):
            r = 60 + i*14
            a = max(0, int(70*(1-i/30)))
            gd.ellipse([cx-r, cy-r, cx+r, cy+r],
                       outline=(30, 110, 255, a), width=3)
        glow = glow.filter(ImageFilter.GaussianBlur(28))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
        d = ImageDraw.Draw(img, "RGBA")
        for gx in range(0, W, 32):
            for gy in range(0, H, 32):
                d.point((gx,gy), fill=(30,80,150,40))
        for (ox, oy, dx, dy) in [(0,0,1,1),(W,0,-1,1),(0,H,1,-1),(W,H,-1,-1)]:
            d.line([(ox+20*dx,oy+20*dy),(ox+120*dx,oy+20*dy)],
                   fill=(34,211,238,180), width=2)
            d.line([(ox+20*dx,oy+20*dy),(ox+20*dx,oy+120*dy)],
                   fill=(34,211,238,180), width=2)
        self._bg_img = ImageTk.PhotoImage(img)
        self.c.create_image(0, 0, image=self._bg_img, anchor="nw")

        pw, ph = 680, 500
        px, py = (W-pw)//2, int(H*0.15)
        self.c.create_rectangle(px, py, px+pw, py+ph,
                                fill=NAVY, outline=BORDER, width=1)
        self.c.create_rectangle(px, py, px+pw, py+2, fill=CYAN, outline="")

        self.bx1, self.by1 = px+60, py+ph-60
        self.bx2, self.by2 = px+pw-60, py+ph-40
        self.c.create_rectangle(self.bx1, self.by1, self.bx2, self.by2,
                                fill=NAVY_M, outline=BORDER)
        self.bar = self.c.create_rectangle(
            self.bx1+2, self.by1+2, self.bx1+2, self.by2-2,
            fill=CYAN, outline="")
        self.load_txt = self.c.create_text(
            W//2, self.by2+22, text="טוען  ·  0%",
            font=("Segoe UI", 9), fill=MUTED)

    def _animate(self):
        self.t += 0.033
        for (text, fam, size, color, spawn, dur) in self.steps:
            if any(m["key"] == text for m in self._meta):
                continue
            if self.t >= spawn:
                self._add(text, fam, size, color, dur)

        for m in list(self._meta):
            age = self.t - m["born"]
            if age < 0: continue
            a = min(1.0, age/m["dur"]) if m["dur"] > 0 else 1.0
            if a < 0.02: a = 0.02
            col = self._mix(m["color"], NAVY, a)
            self.c.itemconfigure(m["id"], fill=col)
            if m.get("float"):
                dy = -math.sin(age*1.2)*1.5
                self.c.coords(m["id"], m["x"], m["y"]+dy)

        self.progress = min(1.0, self.progress + 0.011 + random.random()*0.006)
        w = (self.bx2 - self.bx1 - 4) * self.progress
        self.c.coords(self.bar, self.bx1+2, self.by1+2,
                      self.bx1+2+w, self.by2-2)
        self.c.itemconfigure(self.load_txt,
                             text=f"טוען  ·  {int(self.progress*100)}%")

        if self.progress >= 1.0 and self.t > 7.5:
            try: self.root.destroy()
            except Exception: pass
            self.on_done()
            return
        self.root.after(30, self._animate)

    def _add(self, text, fam, size, color, dur):
        W = self.W
        idx = len(self._meta)
        if text == "עבדול":
            y = 210
        elif text == "סטודיו":
            y = 290
        elif "סוויטת" in text:
            y = 355
        elif "תוכנה אחת" in text:
            y = 390
        elif text.startswith("◆"):
            y = 435 + (idx-5)*22
        elif "נבנה" in text:
            y = 520
        elif "עבור" in text:
            y = 570
        else:
            y = 300 + idx*22

        cid = self.c.create_text(W//2, y, text=text,
                                 font=(fam, size), fill=color,
                                 justify="center")
        self._meta.append({"id": cid, "key": text, "color": color,
                           "born": self.t, "dur": dur,
                           "x": W//2, "y": y,
                           "float": text == "עבדול"})

    def _mix(self, c1, c2, t):
        c1 = c1.lstrip("#"); c2 = c2.lstrip("#")
        r1,g1,b1 = int(c1[0:2],16), int(c1[2:4],16), int(c1[4:6],16)
        r2,g2,b2 = int(c2[0:2],16), int(c2[2:4],16), int(c2[4:6],16)
        return f"#{int(r1*t+r2*(1-t)):02x}{int(g1*t+g2*(1-t)):02x}{int(b1*t+b2*(1-t)):02x}"

    def run(self):
        self.root.mainloop()

# ============================================================
# כפתורים
# ============================================================
class Btn(tk.Button):
    def __init__(self, master, text, cmd, color=BLUE, **kw):
        super().__init__(master, text=text, command=cmd,
                         bg=color, fg="#fff", activebackground=BLUE_H,
                         activeforeground="#fff", bd=0, relief="flat",
                         font=("Segoe UI", 10, "bold"), padx=14, pady=10,
                         cursor="hand2", **kw)
        self._c = color
        self.bind("<Enter>", lambda e: self.configure(bg=BLUE_H))
        self.bind("<Leave>", lambda e: self.configure(bg=self._c))

class Ghost(tk.Button):
    def __init__(self, master, text, cmd, **kw):
        super().__init__(master, text=text, command=cmd,
                         bg=NAVY_M, fg=TEXT, activebackground=NAVY_H,
                         activeforeground=CYAN, bd=0, relief="flat",
                         font=("Segoe UI", 10, "bold"), padx=14, pady=10,
                         cursor="hand2", **kw)
        self.bind("<Enter>", lambda e: self.configure(bg=NAVY_H, fg=CYAN))
        self.bind("<Leave>", lambda e: self.configure(bg=NAVY_M, fg=TEXT))

def sec(parent, text):
    tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
             fg=CYAN, bg=NAVY).pack(anchor="e", padx=18, pady=(14, 6))

class Nav(tk.Frame):
    def __init__(self, master, icon, label, sub, cmd):
        super().__init__(master, bg=NAVY, cursor="hand2")
        self.cmd = cmd; self.active = False
        self.icon = tk.Label(self, text=icon, font=("Segoe UI", 15), fg=CYAN, bg=NAVY)
        self.icon.pack(side="right", padx=(10, 16), pady=14)
        box = tk.Frame(self, bg=NAVY)
        box.pack(side="right", fill="x", expand=True, pady=12)
        self.title = tk.Label(box, text=label, font=("Segoe UI", 11, "bold"),
                              fg=TEXT, bg=NAVY, anchor="e")
        self.title.pack(anchor="e")
        self.sub = tk.Label(box, text=sub, font=F_S, fg=MUTED, bg=NAVY, anchor="e")
        self.sub.pack(anchor="e")
        for w in (self, self.icon, box, self.title, self.sub):
            w.bind("<Button-1>", lambda e: self.cmd())
            w.bind("<Enter>", self._e); w.bind("<Leave>", self._l)
    def _bg(self, c):
        self.configure(bg=c)
        for w in (self.icon, self.title, self.sub): w.configure(bg=c)
        for ch in self.winfo_children():
            ch.configure(bg=c)
            for s in ch.winfo_children(): s.configure(bg=c)
    def _e(self, e):
        if not self.active: self._bg(NAVY_M)
    def _l(self, e):
        if not self.active: self._bg(NAVY)
    def set_active(self, v):
        self.active = v
        self._bg(NAVY_H if v else NAVY)
        self.title.configure(fg=CYAN if v else TEXT)

class Project:
    def __init__(self):
        self.image = None; self.original = None
        self.preset = "באנר דיסקורד"; self.history = []
    def push(self):
        if self.image:
            self.history.append(self.image.copy())
            if len(self.history) > 12: self.history.pop(0)
    def undo(self):
        if self.history:
            self.image = self.history.pop(); return True
        return False

# ============================================================
# מסכים
# ============================================================
class Base(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=DEEP)
        self.app = app; self.p = app.p

class HomeView(Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        pad = tk.Frame(self, bg=DEEP); pad.pack(fill="both", expand=True, padx=30, pady=26)
        tk.Label(pad, text="בית", font=F_TITLE, fg=CYAN, bg=DEEP).pack(anchor="e")
        tk.Label(pad, text="בחר קנבס, טען תמונה, או התחל מחדש.",
                 font=F_B, fg=MUTED, bg=DEEP).pack(anchor="e", pady=(0, 22))

        acts = tk.Frame(pad, bg=DEEP); acts.pack(fill="x", pady=(0, 22))
        self._card(acts, "◆  קנבס ריק", "התחל מאפס", self._blank)
        self._card(acts, "⬆  טען תמונה", "PNG / JPG / WEBP", self._load)
        self._card(acts, "✦  קסם אוטומטי", "שדרג כל תמונה", self._magic)

        tk.Label(pad, text="גדלים מוכנים", font=("Segoe UI", 9, "bold"),
                 fg=CYAN, bg=DEEP).pack(anchor="e", pady=(8, 10))
        grid = tk.Frame(pad, bg=DEEP); grid.pack(fill="both", expand=True)
        for i, (name, (w, h)) in enumerate(PRESETS.items()):
            r, c = divmod(i, 4)
            self._pre(grid, name, w, h).grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        for c in range(4): grid.columnconfigure(c, weight=1)

    def _card(self, parent, title, sub, cmd):
        f = tk.Frame(parent, bg=NAVY, highlightthickness=1,
                     highlightbackground=BORDER, cursor="hand2")
        f.pack(side="right", fill="both", expand=True, padx=4)
        inner = tk.Frame(f, bg=NAVY); inner.pack(padx=16, pady=18, fill="both", expand=True)
        tk.Label(inner, text=title, font=("Segoe UI", 11, "bold"),
                 fg=TEXT, bg=NAVY).pack(anchor="e")
        tk.Label(inner, text=sub, font=F_S, fg=MUTED, bg=NAVY).pack(anchor="e")
        def en(e): f.configure(highlightbackground=CYAN)
        def lv(e): f.configure(highlightbackground=BORDER)
        for w in (f, inner, *inner.winfo_children()):
            w.bind("<Button-1>", lambda e: cmd())
            w.bind("<Enter>", en); w.bind("<Leave>", lv)

    def _pre(self, parent, name, w, h):
        f = tk.Frame(parent, bg=NAVY, highlightthickness=1,
                     highlightbackground=BORDER, cursor="hand2")
        inner = tk.Frame(f, bg=NAVY); inner.pack(padx=12, pady=12, fill="both", expand=True)
        cv = tk.Canvas(inner, width=80, height=48, bg=NAVY_H, highlightthickness=0)
        cv.pack(pady=(0, 8))
        rw = 76; rh = int(76*h/w) if w > h else 76
        if rh > 44: rh = 44; rw = int(44*w/h)
        cv.create_rectangle((80-rw)//2, (48-rh)//2, (80+rw)//2, (48+rh)//2,
                            outline=CYAN, width=2)
        tk.Label(inner, text=name, font=F_S, fg=TEXT, bg=NAVY,
                 wraplength=160).pack()
        tk.Label(inner, text=f"{w} × {h}", font=F_MONO, fg=MUTED, bg=NAVY).pack()
        def ap(e=None):
            self.p.preset = name
            self.p.push()
            self.p.image = Engine.blank(w, h)
            self.p.original = self.p.image.copy()
            self.app.status(f"נבחר: {name}  ({w}×{h})")
        def en(e): f.configure(highlightbackground=CYAN)
        def lv(e): f.configure(highlightbackground=BORDER)
        for widget in (f, inner, *inner.winfo_children()):
            widget.bind("<Button-1>", ap)
            widget.bind("<Enter>", en); widget.bind("<Leave>", lv)
        return f

    def _blank(self):
        w, h = PRESETS[self.p.preset]
        self.p.push()
        self.p.image = Engine.blank(w, h)
        self.p.original = self.p.image.copy()
        self.app.status(f"קנבס חדש: {w}×{h}")
        self.app.show("logo")

    def _load(self):
        path = filedialog.askopenfilename(
            filetypes=[("תמונות", "*.png *.jpg *.jpeg *.webp *.bmp"), ("הכל", "*.*")])
        if not path: return
        try: img = Image.open(path).convert("RGBA")
        except Exception as e:
            messagebox.showerror("עבדול", f"לא ניתן לפתוח:\n{e}"); return
        self.p.push()
        self.p.original = img.copy()
        self.p.image = img.copy()
        self.app.status(f"נטען: {os.path.basename(path)}  ({img.size[0]}×{img.size[1]})")

    def _magic(self):
        if not self.p.image: self._load()
        if self.p.image:
            self.p.push()
            self.p.image = Engine.magic(self.p.image, "חד ומקצועי")
            self.app.show("magic")
            self.app.status("הופעל: חד ומקצועי")

class LogoView(Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=340)
        left.pack(side="right", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="מחולל לוגו", font=("Segoe UI", 20, "bold"),
                 fg=CYAN, bg=NAVY).pack(anchor="e", padx=18, pady=(18, 2))
        tk.Label(left, text="טקסט, צורה, זוהר, גרדיאנט.",
                 font=F_S, fg=MUTED, bg=NAVY).pack(anchor="e", padx=18)

        sec(left, "טקסט")
        self.v_text = tk.StringVar(value="עבדול")
        tk.Entry(left, textvariable=self.v_text, bg=NAVY_H, fg=TEXT,
                 insertbackground=CYAN, bd=0, font=("Segoe UI", 12, "bold"),
                 justify="right", highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=CYAN)\
            .pack(fill="x", padx=18, ipady=7)

        sec(left, "גודל")
        self.v_size = tk.IntVar(value=140)
        tk.Scale(left, from_=40, to=320, orient="horizontal", variable=self.v_size,
                 bg=NAVY, fg=TEXT, troughcolor=NAVY_H, highlightthickness=0, bd=0,
                 sliderrelief="flat", activebackground=CYAN, showvalue=False,
                 length=280, command=lambda v: self._render()).pack(fill="x", padx=18)

        sec(left, "צורה")
        sf = tk.Frame(left, bg=NAVY); sf.pack(anchor="e", padx=18)
        self.v_shape = tk.StringVar(value="ring")
        for lbl, val in [("ללא","none"),("טבעת","ring"),("עיגול","circle"),("ריבוע","rect")]:
            tk.Radiobutton(sf, text=lbl, variable=self.v_shape, value=val,
                           bg=NAVY, fg=TEXT, selectcolor=NAVY_H,
                           activebackground=NAVY, activeforeground=CYAN,
                           font=F_B, bd=0, highlightthickness=0,
                           command=self._render).pack(side="right", padx=2)

        sec(left, "צבעים")
        self.v_fg = tk.StringVar(value="#22d3ee")
        self.v_bg = tk.StringVar(value="#0a1428")
        self.v_ac = tk.StringVar(value="#1e6fff")
        self._crow(left, "צבע טקסט", self.v_fg)
        self._crow(left, "רקע", self.v_bg)
        self._crow(left, "הדגשה", self.v_ac)

        sec(left, "סגנון")
        self.v_glow = tk.BooleanVar(value=True)
        self.v_shad = tk.BooleanVar(value=False)
        for t, v in [("זוהר ניאון", self.v_glow), ("צל תלת-ממדי", self.v_shad)]:
            tk.Checkbutton(left, text="  " + t, variable=v, bg=NAVY, fg=TEXT,
                           selectcolor=NAVY_H, activebackground=NAVY,
                           activeforeground=CYAN, font=F_B, bd=0,
                           highlightthickness=0, command=self._render)\
                .pack(anchor="e", padx=18, pady=1)

        tk.Frame(left, bg=NAVY, height=8).pack()
        Btn(left, "✓  רנדר לוגו", self._render).pack(fill="x", padx=18, pady=(0, 8))
        Ghost(left, "⬇  החל על הקנבס", self._apply).pack(fill="x", padx=18, pady=(0, 16))

        right = tk.Frame(self, bg=DEEP)
        right.pack(side="left", fill="both", expand=True)
        self.prev = tk.Label(right, bg=DEEP)
        self.prev.pack(expand=True)
        self._render()

    def _crow(self, parent, lbl, var):
        row = tk.Frame(parent, bg=NAVY); row.pack(fill="x", padx=18, pady=2)
        tk.Label(row, text=lbl, font=F_S, fg=TEXT, bg=NAVY,
                 width=12, anchor="e").pack(side="right")
        sw = tk.Label(row, text="      ", bg=var.get(), cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        sw.pack(side="right")
        def pk(e=None):
            c = colorchooser.askcolor(color=var.get())[1]
            if c: var.set(c); sw.configure(bg=c); self._render()
        sw.bind("<Button-1>", pk)

    def _render(self, *_):
        W = H = 640
        bg = Image.new("RGBA", (W, H), self.v_bg.get())
        d = ImageDraw.Draw(bg)
        cx, cy = W//2, H//2
        shape = self.v_shape.get(); ac = self.v_ac.get()
        if shape == "circle":
            r = int(W*0.40); d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ac, width=5)
        elif shape == "ring":
            r = int(W*0.43); d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ac, width=16)
        elif shape == "rect":
            p = int(W*0.12); d.rectangle([p, p, W-p, H-p], outline=ac, width=5)

        font = load_font(self.v_size.get(), bold=True)
        txt = rtl(self.v_text.get())

        if self.v_glow.get() and txt:
            gl = Image.new("RGBA", (W, H), (0,0,0,0))
            gd = ImageDraw.Draw(gl)
            bb = gd.textbbox((0,0), txt, font=font)
            x = (W - (bb[2]-bb[0]))//2 - bb[0]
            y = (H - (bb[3]-bb[1]))//2 - bb[1]
            gd.text((x, y), txt, font=font, fill=self.v_fg.get())
            gl = gl.filter(ImageFilter.GaussianBlur(18))
            bg = Image.alpha_composite(bg, gl)
            d = ImageDraw.Draw(bg)

        if txt:
            bb = d.textbbox((0,0), txt, font=font)
            x = (W - (bb[2]-bb[0]))//2 - bb[0]
            y = (H - (bb[3]-bb[1]))//2 - bb[1]
            if self.v_shad.get():
                d.text((x+3, y+3), txt, font=font, fill="#00000088")
                d.text((x+1, y+1), txt, font=font, fill="#ffffff44")
            d.text((x, y), txt, font=font, fill=self.v_fg.get())

        small = bg.resize((460, 460), Image.LANCZOS)
        self._ref = ImageTk.PhotoImage(small)
        self.prev.configure(image=self._ref)

    def _apply(self):
        if not self.p.image:
            w, h = PRESETS[self.p.preset]
            self.p.image = Engine.blank(w, h)
        W, H = self.p.image.size
        tmp = self.p.image.copy()
        d = ImageDraw.Draw(tmp)
        cx, cy = W//2, H//2
        shape = self.v_shape.get(); ac = self.v_ac.get()
        if shape == "circle":
            r = int(min(W,H)*0.40); d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=ac, width=5)
        elif shape == "ring":
            r = int(min(W,H)*0.43); d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=ac, width=16)
        elif shape == "rect":
            p = int(min(W,H)*0.12); d.rectangle([p,p,W-p,H-p], outline=ac, width=5)
        size = int(self.v_size.get() * min(W,H) / 640)
        font = load_font(max(20, size), bold=True)
        txt = rtl(self.v_text.get())
        if txt:
            bb = d.textbbox((0,0), txt, font=font)
            x = (W - (bb[2]-bb[0]))//2 - bb[0]
            y = (H - (bb[3]-bb[1]))//2 - bb[1]
            d.text((x, y), txt, font=font, fill=self.v_fg.get())
        self.p.push()
        self.p.image = tmp
        self.app.status("הלוגו הוחל על הקנבס")

class MagicView(Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=340)
        left.pack(side="right", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="קסם אוטומטי", font=("Segoe UI", 20, "bold"),
                 fg=CYAN, bg=NAVY).pack(anchor="e", padx=18, pady=(18, 2))
        tk.Label(left, text="טען תמונה — הפוך אותה לפי 10,000 יותר יפה.",
                 font=F_S, fg=MUTED, bg=NAVY).pack(anchor="e", padx=18)

        sec(left, "סגנונות קסם")
        for s in ["חד ומקצועי", "קולנועי", "ניאון", "צבעוני",
                  "חלום", "אפל", "רטרו"]:
            Ghost(left, "  " + s, lambda n=s: self._ap(n))\
                .pack(fill="x", padx=18, pady=2)

        sec(left, "כוונון ידני")
        self.v_b  = tk.DoubleVar(value=1.0)
        self.v_c  = tk.DoubleVar(value=1.0)
        self.v_s  = tk.DoubleVar(value=1.0)
        self.v_sh = tk.DoubleVar(value=1.0)
        self.v_v  = tk.DoubleVar(value=0.0)
        for lbl, v in [("בהירות", self.v_b), ("ניגודיות", self.v_c),
                       ("רוויה", self.v_s), ("חדות", self.v_sh),
                       ("הילה כהה", self.v_v)]:
            r = tk.Frame(left, bg=NAVY); r.pack(fill="x", padx=18, pady=2)
            tk.Label(r, text=lbl, font=F_S, fg=TEXT, bg=NAVY,
                     width=11, anchor="e").pack(side="right")
            tk.Scale(r, from_=0.4, to=2.5, orient="horizontal", variable=v,
                     resolution=0.05, bg=NAVY, fg=TEXT, troughcolor=NAVY_H,
                     highlightthickness=0, bd=0, sliderrelief="flat",
                     activebackground=CYAN, length=170)\
                .pack(side="right", fill="x", expand=True, padx=4)
        Ghost(left, "✓  החל כוונון", self._man).pack(fill="x", padx=18, pady=(10, 6))

        sec(left, "היסטוריה")
        Ghost(left, "↶  בטל", self._undo).pack(fill="x", padx=18, pady=2)

        right = tk.Frame(self, bg=DEEP)
        right.pack(side="left", fill="both", expand=True)
        self.prev = tk.Label(right, bg=DEEP)
        self.prev.pack(expand=True)
        self.refresh()

    def refresh(self):
        if not self.p.image: return
        img = self.p.image.copy()
        img.thumbnail((520, 420), Image.LANCZOS)
        self._ref = ImageTk.PhotoImage(img)
        self.prev.configure(image=self._ref)

    def _ap(self, name):
        if not self.p.image:
            messagebox.showinfo("עבדול", "טען תמונה קודם."); return
        self.p.push()
        self.p.image = Engine.magic(self.p.image, name)
        self.refresh()
        self.app.status(f"הופעל: {name}")

    def _man(self):
        if not self.p.image: return
        self.p.push()
        i = self.p.image
        i = Engine.bright(i, self.v_b.get())
        i = Engine.contr(i, self.v_c.get())
        i = Engine.sat(i, self.v_s.get())
        i = Engine.unsharp(i, self.v_sh.get())
        if self.v_v.get() > 0:
            i = Engine.vignette(i, self.v_v.get())
        self.p.image = i
        self.refresh()
        self.app.status("הוחל כוונון ידני")

    def _undo(self):
        if self.p.undo():
            self.refresh()
            self.app.status("בוטל")

class EffectsView(Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        left = tk.Frame(self, bg=NAVY, width=340)
        left.pack(side="right", fill="y"); left.pack_propagate(False)
        tk.Label(left, text="אפקטים", font=("Segoe UI", 20, "bold"),
                 fg=CYAN, bg=NAVY).pack(anchor="e", padx=18, pady=(18, 2))
        tk.Label(left, text="מסננים, שכבות וגימור.",
                 font=F_S, fg=MUTED, bg=NAVY).pack(anchor="e", padx=18)

        sec(left, "מסננים")
        Ghost(left, "  הילה כהה", self._vig).pack(fill="x", padx=18, pady=2)
        Ghost(left, "  זוהר ניאון כחול", self._glow).pack(fill="x", padx=18, pady=2)
        Ghost(left, "  טשטוש עדין", self._blur).pack(fill="x", padx=18, pady=2)

        sec(left, "גרדיאנט")
        self.v_c1 = tk.StringVar(value="#22d3ee")
        self.v_c2 = tk.StringVar(value="#02040f")
        self._crow(left, "צבע עליון", self.v_c1)
        self._crow(left, "צבע תחתון", self.v_c2)
        self.v_op = tk.DoubleVar(value=0.35)
        r = tk.Frame(left, bg=NAVY); r.pack(fill="x", padx=18, pady=4)
        tk.Label(r, text="שקיפות", font=F_S, fg=TEXT, bg=NAVY,
                 width=11, anchor="e").pack(side="right")
        tk.Scale(r, from_=0.05, to=0.9, resolution=0.05, orient="horizontal",
                 variable=self.v_op, bg=NAVY, fg=TEXT, troughcolor=NAVY_H,
                 highlightthickness=0, bd=0, sliderrelief="flat",
                 activebackground=CYAN, length=170)\
            .pack(side="right", fill="x", expand=True)
        Ghost(left, "✓  החל גרדיאנט", self._grad).pack(fill="x", padx=18, pady=6)

        sec(left, "מסגרת / חיתוך")
        Ghost(left, "  חיתוך עגול", self._circle).pack(fill="x", padx=18, pady=2)
        Ghost(left, "  פינות מעוגלות", self._round).pack(fill="x", padx=18, pady=2)
        Ghost(left, "  התאם לקנבס", self._fit).pack(fill="x", padx=18, pady=2)

    def _crow(self, parent, lbl, var):
        row = tk.Frame(parent, bg=NAVY); row.pack(fill="x", padx=18, pady=2)
        tk.Label(row, text=lbl, font=F_S, fg=TEXT, bg=NAVY,
                 width=12, anchor="e").pack(side="right")
        sw = tk.Label(row, text="      ", bg=var.get(), cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        sw.pack(side="right")
        def pk(e=None):
            c = colorchooser.askcolor(color=var.get())[1]
            if c: var.set(c); sw.configure(bg=c)
        sw.bind("<Button-1>", pk)

    def _need(self):
        if not self.p.image:
            messagebox.showinfo("עבדול", "טען או צור קנבס קודם."); return False
        return True

    def _vig(self):
        if not self._need(): return
        self.p.push(); self.p.image = Engine.vignette(self.p.image, 0.55)
        self.app.status("הילה כהה הוחלה")

    def _glow(self):
        if not self._need(): return
        self.p.push(); self.p.image = Engine.glow(self.p.image, (34,211,238), 16, 0.55)
        self.app.status("זוהר ניאון הוחל")

    def _blur(self):
        if not self._need(): return
        self.p.push(); self.p.image = Engine.blur(self.p.image, 2.5)
        self.app.status("טשטוש הוחל")

    def _grad(self):
        if not self._need(): return
        self.p.push()
        self.p.image = Engine.grad_over(self.p.image, self.v_c1.get(),
                                        self.v_c2.get(), self.v_op.get())
        self.app.status("גרדיאנט הוחל")

    def _circle(self):
        if not self._need(): return
        self.p.push(); self.p.image = Engine.circle_mask(self.p.image)
        self.app.status("חיתוך עגול הוחל")

    def _round(self):
        if not self._need(): return
        self.p.push()
        w, h = self.p.image.size
        self.p.image = Engine.round_mask(self.p.image, int(min(w,h)*0.06))
        self.app.status("פינות מעוגלות הוחלו")

    def _fit(self):
        if not self._need(): return
        self.p.push()
        w, h = self.p.image.size
        self.p.image = Engine.fit(self.p.image, w, h, "cover")
        self.app.status("הותאם לקנבס")

class ExportView(Base):
    def __init__(self, master, app):
        super().__init__(master, app)
        pad = tk.Frame(self, bg=DEEP); pad.pack(fill="both", expand=True, padx=30, pady=26)
        tk.Label(pad, text="ייצוא", font=F_TITLE, fg=CYAN, bg=DEEP).pack(anchor="e")
        tk.Label(pad, text="שמור את העיצוב שלך. בחר פורמט וגודל.",
                 font=F_B, fg=MUTED, bg=DEEP).pack(anchor="e", pady=(0, 22))

        card = tk.Frame(pad, bg=NAVY, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(card, bg=NAVY); inner.pack(padx=22, pady=20, fill="x")

        tk.Label(inner, text="פורמט", font=("Segoe UI", 9, "bold"),
                 fg=CYAN, bg=NAVY).pack(anchor="e")
        self.v_fmt = tk.StringVar(value="PNG")
        row = tk.Frame(inner, bg=NAVY); row.pack(anchor="e", pady=(4, 12))
        for f in ["PNG", "JPG", "WEBP"]:
            tk.Radiobutton(row, text=f, variable=self.v_fmt, value=f,
                           bg=NAVY, fg=TEXT, selectcolor=NAVY_H,
                           activebackground=NAVY, activeforeground=CYAN,
                           font=F_B, bd=0, highlightthickness=0)\
                .pack(side="right", padx=(12, 0))

        tk.Label(inner, text="שנה גודל לפריסט", font=("Segoe UI", 9, "bold"),
                 fg=CYAN, bg=NAVY).pack(anchor="e")
        self.v_size = tk.StringVar(value="מקורי")
        opts = ["מקורי"] + [f"{k}  ({v[0]}×{v[1]})" for k, v in PRESETS.items()]
        menu = tk.OptionMenu(inner, self.v_size, *opts)
        menu.configure(bg=NAVY_H, fg=TEXT, activebackground=NAVY_M,
                       activeforeground=CYAN, bd=0, highlightthickness=0,
                       font=F_B, anchor="e", justify="right")
        menu["menu"].configure(bg=NAVY, fg=TEXT, activebackground=BLUE,
                               activeforeground="#fff")
        menu.pack(anchor="e", pady=(4, 12), fill="x")

        self.v_q = tk.IntVar(value=95)
        rq = tk.Frame(inner, bg=NAVY); rq.pack(fill="x", pady=(4, 6))
        tk.Label(rq, text="איכות", font=F_B, fg=TEXT, bg=NAVY,
                 width=8, anchor="e").pack(side="right")
        tk.Scale(rq, from_=50, to=100, orient="horizontal", variable=self.v_q,
                 bg=NAVY, fg=TEXT, troughcolor=NAVY_H, highlightthickness=0,
                 bd=0, sliderrelief="flat", activebackground=CYAN, length=300)\
            .pack(side="right", fill="x", expand=True)

        Btn(inner, "⬇  שמור קובץ", self._save).pack(anchor="e", pady=(14, 0))

        self.prev = tk.Label(pad, bg=DEEP)
        self.prev.pack(expand=True, pady=10)

    def refresh(self):
        if not self.p.image: return
        img = self.p.image.copy()
        img.thumbnail((520, 320), Image.LANCZOS)
        self._ref = ImageTk.PhotoImage(img)
        self.prev.configure(image=self._ref)

    def _save(self):
        if not self.p.image:
            messagebox.showinfo("עבדול", "אין מה לייצא."); return
        fmt = self.v_fmt.get()
        ext = {"PNG": ".png", "JPG": ".jpg", "WEBP": ".webp"}[fmt]
        path = filedialog.asksaveasfilename(defaultextension=ext,
                                            filetypes=[(fmt, f"*{ext}")],
                                            initialfile=f"עבדול{ext}")
        if not path: return
        img = self.p.image.copy()
        sel = self.v_size.get()
        if sel != "מקורי":
            name = sel.split("  (")[0]
            if name in PRESETS:
                w, h = PRESETS[name]
                img = Engine.fit(img, w, h, "cover")
        if fmt == "JPG":
            bg = Image.new("RGB", img.size, (0, 0, 0))
            bg.paste(img, mask=img.split()[3])
            bg.save(path, "JPEG", quality=self.v_q.get())
        elif fmt == "WEBP":
            img.save(path, "WEBP", quality=self.v_q.get())
        else:
            img.save(path, "PNG")
        messagebox.showinfo("עבדול", f"נשמר:\n{path}")
        self.app.status(f"יוצא: {os.path.basename(path)}")

# ============================================================
# אפליקציה ראשית
# ============================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("עבדול סטודיו  —  סוויטת עיצוב מקצועית")
        self.geometry("1400x880")
        self.minsize(1200, 780)
        self.configure(bg=DEEP)
        self.p = Project()
        self._build()

    def _build(self):
        h = tk.Frame(self, bg=DEEP, height=84); h.pack(fill="x"); h.pack_propagate(False)
        b = tk.Frame(h, bg=DEEP); b.pack(side="right", padx=26, pady=12)
        tk.Label(b, text="עבדול", font=("Segoe UI Black", 32, "bold"),
                 fg=CYAN, bg=DEEP).pack(anchor="e")
        tk.Label(b, text="סטודיו  ·  סוויטת עיצוב מקצועית",
                 font=F_MONO, fg=MUTED, bg=DEEP).pack(anchor="e")

        r = tk.Frame(h, bg=DEEP); r.pack(side="left", padx=26, pady=22)
        self.st = tk.Label(r, text="מוכן", font=F_S, fg=MUTED, bg=DEEP)
        self.st.pack(anchor="w")
        tk.Label(r, text="◆  5 מודולים  ◆  ייצוא PNG / JPG / WEBP",
                 font=F_MONO, fg=BLUE_H, bg=DEEP).pack(anchor="w")

        tk.Frame(self, bg=CYAN, height=2).pack(fill="x")

        body = tk.Frame(self, bg=DEEP); body.pack(fill="both", expand=True)

        sb = tk.Frame(body, bg=NAVY, width=230); sb.pack(side="right", fill="y")
        sb.pack_propagate(False)
        tk.Label(sb, text="מודולים", font=("Segoe UI", 9, "bold"),
                 fg=CYAN, bg=NAVY).pack(anchor="e", padx=18, pady=(18, 6))

        items = [
            ("home",   "◆", "בית",         "מסך התחלה"),
            ("logo",   "✦", "מחולל לוגו",  "טקסט, צורות, זוהר"),
            ("magic",  "★", "קסם אוטומטי", "שדרוג תמונות"),
            ("effects","▲", "אפקטים",      "מסננים ושכבות"),
            ("export", "⬇", "ייצוא",       "שמירת העיצוב"),
        ]
        self.nav = {}
        for key, icon, lbl, sub in items:
            btn = Nav(sb, icon, lbl, sub, lambda k=key: self.show(k))
            btn.pack(fill="x", pady=1)
            self.nav[key] = btn

        tk.Label(sb, text="עבדול  ·  v2.0", font=F_MONO, fg=MUTED, bg=NAVY)\
            .pack(side="bottom", pady=14)

        self.content = tk.Frame(body, bg=DEEP)
        self.content.pack(side="right", fill="both", expand=True)

        self.views = {
            "home":    HomeView(self.content, self),
            "logo":    LogoView(self.content, self),
            "magic":   MagicView(self.content, self),
            "effects": EffectsView(self.content, self),
            "export":  ExportView(self.content, self),
        }
        for v in self.views.values():
            v.place(relx=0, rely=0, relwidth=1, relheight=1)

        tb = tk.Frame(self, bg=NAVY_M, height=46)
        tb.pack(fill="x", side="bottom"); tb.pack_propagate(False)
        tk.Label(tb, text="  ⌘  עבדול סטודיו  ·  פעולות מהירות",
                 font=F_MONO, fg=MUTED, bg=NAVY_M).pack(side="right", padx=12)
        Ghost(tb, "↶  בטל", self.undo).pack(side="left", padx=4, pady=6)
        Ghost(tb, "⬆  טען", self.load).pack(side="left", padx=4, pady=6)
        Btn(tb, "⬇  שמור", self.qsave).pack(side="left", padx=4, pady=6)

        self.show("home")

    def show(self, key):
        for k, b in self.nav.items():
            b.set_active(k == key)
        self.views[key].tkraise()
        if key in ("export", "magic"):
            self.views[key].refresh()

    def status(self, t):
        self.st.configure(text=t, fg=BLUE_H)

    def undo(self):
        if self.p.undo(): self.status("בוטל")

    def load(self):
        self.views["home"]._load()

    def qsave(self):
        if not self.p.image:
            messagebox.showinfo("עבדול", "אין מה לשמור."); return
        self.show("export"); self.views["export"]._save()

def launch():
    App().mainloop()

if __name__ == "__main__":
    SplashScreen(launch).run()
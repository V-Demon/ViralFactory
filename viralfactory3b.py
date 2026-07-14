"""
VIRAL FACTORY 2.0 - PATCHED WITH PLUGIN SUPPORT
Supporte templates multiples, effets avancés, animations, IA, ET plugins communautaires !
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import glob
import importlib.util

# ======================= CONFIGURATION =======================
TEMPLATES_DIR = Path("templates/")
FONTS_DIR = Path("fonts/")
EFFECTS_DIR = Path("effects/")
OUTPUT_DIR = Path("output/")
CACHE_DIR = Path("cache/")
PLUGINS_DIR = Path("plugins/")

for directory in [OUTPUT_DIR, CACHE_DIR, PLUGINS_DIR]:
    directory.mkdir(exist_ok=True)

# ======================= PLUGIN SYSTEM =======================
# Registre global des effets texte personnalisés
TEXT_EFFECT_REGISTRY = {}

def register_text_effect(name: str):
    """Décorateur pour enregistrer un effet texte dans plugins/"""
    def decorator(func):
        TEXT_EFFECT_REGISTRY[name] = func
        return func
    return decorator

def load_plugins():
    """Charge dynamiquement tous les plugins dans plugins/"""
    plugin_files = sorted(glob.glob(str(PLUGINS_DIR / "*.py")))
    for plugin_path in plugin_files:
        if "__pycache__" in plugin_path:
            continue
        try:
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"🔌 Plugin chargé : {Path(plugin_path).stem}")
        except Exception as e:
            print(f"⚠️ Échec du chargement du plugin {plugin_path}: {e}")

# Charge les plugins au démarrage
load_plugins()

# ======================= ENUMS & DATACLASSES =======================
class TextAlignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"

class EffectType(Enum):
    OUTLINE = "outline"
    GLOW = "glow"
    SHADOW = "shadow"
    GRADIENT = "gradient"
    DISTORTION = "distortion"
    MOTION_BLUR = "motion_blur"
    GLITCH = "glitch"
    RAINBOW = "rainbow"
    FIRE = "fire"
    NEON = "neon"

@dataclass
class TextConfig:
    content: str
    position: Tuple[float, float]  # (x_ratio, y_ratio)
    font_file: str
    font_size_ratio: float
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    alignment: TextAlignment = TextAlignment.CENTER
    max_width: Optional[int] = None
    rotation: float = 0.0
    effects: List[str] = None

@dataclass
class OverlayConfig:
    image_path: str
    position: Tuple[float, float]
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0

# ======================= CHARGEMENT TEMPLATES =======================
def load_templates(template_file: str = "templates.json") -> Dict:
    """Charge les templates depuis JSON avec validation"""
    with open(TEMPLATES_DIR / template_file) as f:
        templates = json.load(f)
    return templates

TEMPLATES = load_templates()

# ======================= EFFETS TEXTE AVANCÉS =======================
class TextEffects:
    # (Mêmes méthodes que dans ton fichier original — inchangées)
    @staticmethod
    def outline(draw, text, x, y, font, fill="white", outline_color="black", outline_width=6):
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill)

    @staticmethod
    def glow(img, text, x, y, font, color=(255, 240, 0), intensity=20, radius=15):
        glow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        for i in range(radius, 0, -2):
            alpha = int((i / radius) * intensity * 12)
            glow_color = (*color[:3], alpha)
            for dx in range(-i, i + 1, 2):
                for dy in range(-i, i + 1, 2):
                    glow_draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=5))
        img.paste(glow_layer, (0, 0), glow_layer)
        draw = ImageDraw.Draw(img)
        draw.text((x, y), text, font=font, fill=color)

    @staticmethod
    def shadow(draw, text, x, y, font, fill="white", shadow_color=(0, 0, 0, 180), offset=(5, 5)):
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=fill)

    @staticmethod
    def gradient(img, text, x, y, font, color_start=(255, 0, 0), color_end=(255, 255, 0)):
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((x, y), text, font=font, fill=255)
        bbox = mask_draw.textbbox((x, y), text, font=font)
        width = bbox[2] - bbox[0]
        gradient = Image.new('RGBA', img.size, (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        for i in range(width):
            ratio = i / width
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            gradient_draw.rectangle([(bbox[0] + i, bbox[1]), (bbox[0] + i + 1, bbox[3])], fill=(r, g, b, 255))
        img.paste(gradient, (0, 0), mask)

    @staticmethod
    def rainbow(img, text, x, y, font):
        colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (148,0,211)]
        draw = ImageDraw.Draw(img)
        offset_x = 0
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            draw.text((x + offset_x, y), char, font=font, fill=color)
            bbox = draw.textbbox((0, 0), char, font=font)
            offset_x += bbox[2] - bbox[0]

    @staticmethod
    def neon(img, text, x, y, font, color=(0, 255, 255)):
        TextEffects.glow(img, text, x, y, font, color=color, intensity=30, radius=20)
        draw = ImageDraw.Draw(img)
        TextEffects.outline(draw, text, x, y, font, fill=color, outline_color=(255,255,255), outline_width=2)

    @staticmethod
    def glitch(img, text, x, y, font, color=(255, 0, 0)):
        draw = ImageDraw.Draw(img)
        draw.text((x - 3, y), text, font=font, fill=(255, 0, 0, 180))
        draw.text((x + 3, y), text, font=font, fill=(0, 255, 255, 180))
        draw.text((x, y + 2), text, font=font, fill=(0, 255, 0, 180))
        draw.text((x, y), text, font=font, fill=color)

# ======================= EFFETS D'IMAGE =======================
# (Class ImageEffects inchangée — copiée telle quelle)
class ImageEffects:
    @staticmethod
    def deep_fry(img: Image.Image, intensity: float = 0.7) -> Image.Image:
        img = ImageEnhance.Color(img).enhance(2.0 + intensity)
        img = ImageEnhance.Contrast(img).enhance(2.0 + intensity)
        img = img.convert('RGB')
        img = img.filter(ImageFilter.SHARPEN)
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        return img

    @staticmethod
    def vintage(img: Image.Image) -> Image.Image:
        img = ImageEnhance.Color(img).enhance(0.7)
        sepia = Image.new('RGBA', img.size, (112, 66, 20, 50))
        img = Image.alpha_composite(img.convert('RGBA'), sepia)
        img = ImageEnhance.Contrast(img).enhance(0.8)
        return img

    @staticmethod
    def vignette(img: Image.Image, intensity: float = 0.5) -> Image.Image:
        width, height = img.size
        vignette = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(vignette)
        center_x, center_y = width // 2, height // 2
        max_dist = ((width/2)**2 + (height/2)**2) ** 0.5
        for y in range(height):
            for x in range(width):
                dist = ((x - center_x)**2 + (y - center_y)**2) ** 0.5
                value = int(255 * (1 - (dist / max_dist) * intensity))
                vignette.putpixel((x, y), value)
        img = img.convert('RGBA')
        black = Image.new('RGBA', img.size, (0, 0, 0, 0))
        return Image.composite(img, black, vignette)

    @staticmethod
    def pixelate(img: Image.Image, pixel_size: int = 10) -> Image.Image:
        small = img.resize((img.size[0] // pixel_size, img.size[1] // pixel_size), Image.NEAREST)
        return small.resize(img.size, Image.NEAREST)

    @staticmethod
    def blur_edges(img: Image.Image, blur_radius: int = 20) -> Image.Image:
        mask = Image.new('L', img.size, 255)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([(blur_radius, blur_radius), (img.size[0]-blur_radius, img.size[1]-blur_radius)], fill=0)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
        blurred = img.filter(ImageFilter.GaussianBlur(10))
        return Image.composite(img, blurred, mask)

# ======================= OVERLAYS =======================
class OverlayManager:
    @staticmethod
    def add_overlay(img: Image.Image, config: OverlayConfig) -> Image.Image:
        overlay = Image.open(EFFECTS_DIR / config.image_path).convert('RGBA')
        new_size = (int(overlay.width * config.scale), int(overlay.height * config.scale))
        overlay = overlay.resize(new_size, Image.LANCZOS)
        if config.rotation != 0:
            overlay = overlay.rotate(config.rotation, expand=True)
        if config.opacity < 1.0:
            alpha = overlay.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(config.opacity)
            overlay.putalpha(alpha)
        x = int(img.width * config.position[0])
        y = int(img.height * config.position[1])
        img.paste(overlay, (x - overlay.width // 2, y - overlay.height // 2), overlay)
        return img

    @staticmethod
    def add_arrow(img: Image.Image, start: Tuple[float, float], end: Tuple[float, float], color="red", thickness=10):
        draw = ImageDraw.Draw(img)
        sp = (int(img.width * start[0]), int(img.height * start[1]))
        ep = (int(img.width * end[0]), int(img.height * end[1]))
        draw.line([sp, ep], fill=color, width=thickness)
        import math
        angle = math.atan2(ep[1]-sp[1], ep[0]-sp[0])
        al, aw = 30, 20
        p1 = ep
        p2 = (int(ep[0] - al*math.cos(angle) + aw*math.sin(angle)), int(ep[1] - al*math.sin(angle) - aw*math.cos(angle)))
        p3 = (int(ep[0] - al*math.cos(angle) - aw*math.sin(angle)), int(ep[1] - al*math.sin(angle) + aw*math.cos(angle)))
        draw.polygon([p1, p2, p3], fill=color)
        return img

# ======================= MOTEUR PRINCIPAL (PATCHÉ) =======================
class MemeGenerator:
    def __init__(self, templates: Dict = None):
        self.templates = templates or TEMPLATES
        self.text_effects = TextEffects()
        self.image_effects = ImageEffects()
        self.overlay_manager = OverlayManager()

    def load_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        try:
            return ImageFont.truetype(str(FONTS_DIR / font_name), size)
        except:
            return ImageFont.load_default()

    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        words = text.split()
        lines, current = [], []
        for word in words:
            test = ' '.join(current + [word])
            w = font.getbbox(test)[2] - font.getbbox(test)[0]
            if w <= max_width:
                current.append(word)
            else:
                if current: lines.append(' '.join(current))
                current = [word]
        if current: lines.append(' '.join(current))
        return lines

    def render_text(self, img: Image.Image, config: TextConfig) -> Image.Image:
        W, H = img.size
        font_size = int(H * config.font_size_ratio)
        font = self.load_font(config.font_file, font_size)
        max_width = config.max_width or int(W * 0.9)
        lines = self.wrap_text(config.content, font, max_width)
        x = int(W * config.position[0])
        y = int(H * config.position[1])
        draw = ImageDraw.Draw(img)
        for i, line in enumerate(lines):
            line_y = y + i * (font_size + 10)
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            if config.alignment == TextAlignment.CENTER:
                line_x = x - line_w // 2
            elif config.alignment == TextAlignment.LEFT:
                line_x = x
            else:
                line_x = x - line_w

            if config.effects:
                for effect in config.effects:
                    # 1. Plugins personnalisés
                    if effect in TEXT_EFFECT_REGISTRY:
                        TEXT_EFFECT_REGISTRY[effect](draw, img, line, line_x, line_y, font, color=config.color[:3])
                    # 2. Effets natifs
                    elif effect == "outline":
                        self.text_effects.outline(draw, line, line_x, line_y, font, fill=config.color[:3])
                    elif effect == "glow":
                        self.text_effects.glow(img, line, line_x, line_y, font, color=config.color[:3])
                    elif effect == "shadow":
                        self.text_effects.shadow(draw, line, line_x, line_y, font, fill=config.color[:3])
                    elif effect == "rainbow":
                        self.text_effects.rainbow(img, line, line_x, line_y, font)
                    elif effect == "neon":
                        self.text_effects.neon(img, line, line_x, line_y, font, color=config.color[:3])
                    elif effect == "glitch":
                        self.text_effects.glitch(img, line, line_x, line_y, font, color=config.color[:3])
                    elif effect == "gradient":
                        self.text_effects.gradient(img, line, line_x, line_y, font)
                    else:
                        print(f"⚠️ Effet inconnu ignoré : {effect}")
                        draw.text((line_x, line_y), line, font=font, fill=config.color)
            else:
                draw.text((line_x, line_y), line, font=font, fill=config.color)
        return img

    def create(self,
               template_name: str,
               texts: List[TextConfig] = None,
               overlays: List[OverlayConfig] = None,
               image_effects: List[str] = None,
               custom_image: Optional[str] = None,
               output_name: Optional[str] = None) -> str:
        if custom_image and os.path.exists(custom_image):
            img = Image.open(custom_image).convert('RGBA')
        elif template_name in self.templates:
            config = self.templates[template_name]
            img = Image.open(TEMPLATES_DIR / config["background"]).convert('RGBA')
        else:
            raise ValueError(f"Template '{template_name}' introuvable")

        if image_effects:
            for effect in image_effects:
                method = getattr(self.image_effects, effect, None)
                if method:
                    img = method(img)

        if overlays:
            for overlay in overlays:
                img = self.overlay_manager.add_overlay(img, overlay)

        if texts:
            for text_config in texts:
                img = self.render_text(img, text_config)

        if not output_name:
            output_name = f"{template_name}_{hash(str(texts)) % 100000}.png"
        output_path = OUTPUT_DIR / output_name
        img.save(output_path, quality=95)
        print(f"✅ Mème créé → {output_path}")
        return str(output_path)

# ======================= RACCOURCIS =======================
def quick_meme(template: str, top: str = "", bottom: str = "", effect: str = "outline") -> str:
    generator = MemeGenerator()
    texts = []
    if top:
        texts.append(TextConfig(content=top, position=(0.42, 0.0), font_file="Roboto-Bold.ttf", font_size_ratio=0.09, effects=[effect]))
    if bottom:
        texts.append(TextConfig(content=bottom, position=(0.58, 0.9), font_file="Roboto-Bold.ttf", font_size_ratio=0.09, effects=[effect]))
    return generator.create(template, texts=texts)

# ======================= EXEMPLE PLUGIN-FRIENDLY =======================
if __name__ == "__main__":
    # Exemple avec effet personnalisé (si un plugin déclare "fire")
    try:
        quick_meme("smirking_girl", top="Ahah...", bottom="tu as cliqué sur le lien?", effect="fire")
    except:
        quick_meme("smirking_girl", top="Ohoh...", bottom="tu as cliqué sur le lien?")

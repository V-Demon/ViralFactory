#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHIMERA_FORGE v3.5
Correction finale : 
- Mode Fusion = PAS de rectangle, texte flottant avec outline
- Mode Procédural = rectangle opaque
- Message clair sur le mode actif
"""

import json
import os
import random
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

class ChimeraForge:
    def __init__(self, preset_file="saturation_2026_ultra.json"):
        self.preset_file = preset_file
        self.presets = self._load_presets()
        self.default_preset = self.presets.get("default_preset", "saturation_2026_ultra")

    def _load_presets(self):
        if os.path.exists(self.preset_file):
            with open(self.preset_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"default_preset": "saturation_2026_ultra", "presets": {}}

    def _generate_truchet_overlay(self, width, height, palette, glitch_intensity):
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        cell_size = 32
        
        for y in range(0, height, cell_size):
            for x in range(0, width, cell_size):
                weights = [
                    0.7 - (glitch_intensity * 0.4),
                    0.2,
                    0.1 + (glitch_intensity * 0.3),
                    0.05 + (glitch_intensity * 0.2)
                ]
                while len(weights) < len(palette):
                    weights.append(0.05)
                weights = weights[:len(palette)]
                
                color_hex = random.choices(palette, weights=weights)[0]
                r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                alpha = int(40 + (glitch_intensity * 150))
                
                if random.random() > 0.5:
                    draw.pieslice([x, y, x + cell_size, y + cell_size], 0, 90, fill=(r, g, b, alpha))
                    draw.pieslice([x, y, x + cell_size, y + cell_size], 180, 270, fill=(r, g, b, alpha))
                else:
                    draw.pieslice([x, y, x + cell_size, y + cell_size], 90, 180, fill=(r, g, b, alpha))
                    draw.pieslice([x, y, x + cell_size, y + cell_size], 270, 360, fill=(r, g, b, alpha))
        return overlay

    def _wrap_text(self, draw, text, font, max_width):
        words = text.split(' ')
        lines, current_line = [], []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return '\n'.join(lines)

    def _assemble_basilisk_text(self, tracks, show_subtext=True):
        track_order = ['opening', 'framing', 'body', 'constraint', 'trap', 'closing']
        blocks = []
        
        for track_name in track_order:
            if track_name not in tracks:
                continue
            track = tracks[track_name]
            
            if isinstance(track, str):
                surface = track
                subtext = None
            elif isinstance(track, dict):
                surface = track.get('surface', '')
                subtext = track.get('subtext') if show_subtext else None
            else:
                continue
            
            if track_name == 'opening':
                block = f"[{surface.upper()}]"
            elif track_name == 'constraint':
                block = f"  {surface}"
            elif track_name == 'trap':
                block = f"->  {surface}"
            elif track_name == 'closing':
                block = f"{surface}"
            else:
                block = surface
            
            if subtext:
                block += f"\n   -> {subtext}"
            
            blocks.append(block)
        
        return '\n\n'.join(blocks)

    def _load_fonts(self):
        candidates_main = [
            "DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        ]
        candidates_oblique = [
            "DejaVuSansMono-Oblique.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf",
            "/usr/share/fonts/TTF/DejaVuSansMono-Oblique.ttf",
        ]
        
        font_main = ImageFont.load_default()
        font_whisper = ImageFont.load_default()
        font_meta = ImageFont.load_default()
        
        for path in candidates_main:
            try:
                font_main = ImageFont.truetype(path, 22)
                break
            except IOError:
                continue
        
        for path in candidates_oblique:
            try:
                font_whisper = ImageFont.truetype(path, 16)
                break
            except IOError:
                continue
        
        for path in candidates_main:
            try:
                font_meta = ImageFont.truetype(path, 14)
                break
            except IOError:
                continue
        
        return font_main, font_whisper, font_meta

    def _draw_text_with_outline(self, draw, position, text, font, fill_color, outline_color, outline_width=3):
        """Dessine du texte avec outline épais"""
        x, y = position
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill_color)

    def forge(self, preset_name=None, fuse_image_path=None, export_grok=False, 
              show_subtext=True, with_background=None):
        p_name = preset_name or self.default_preset
        preset = self.presets["presets"].get(p_name)
        if not preset:
            print(f"❌ Preset '{p_name}' introuvable.")
            return

        print(f"⚙️   Forgeage de la chimère : {preset['name']}...")
        print(f"📖 Mode double lecture : {'ACTIVÉ' if show_subtext else 'DÉSACTIVÉ'}")
        
        w, h = preset['visual']['width'], preset['visual']['height']
        palette = preset['visual']['palette']
        glitch = preset['visual']['glitch_intensity']

        # Détection du mode
        is_fusion = fuse_image_path is not None and os.path.exists(fuse_image_path)
        
        if is_fusion:
            print(f"📸 MODE FUSION : {fuse_image_path}")
            print("   → PAS de rectangle de fond (texte flottant avec outline)")
        else:
            print(" MODE PROCÉDURAL : fond généré")
            print("   → Rectangle opaque pour lisibilité")

        # 1. Image de base
        if is_fusion:
            base_img = Image.open(fuse_image_path).convert("RGB")
            base_img = ImageOps.fit(base_img, (w, h), method=Image.Resampling.LANCZOS)
        else:
            base_img = Image.new('RGB', (w, h), color=palette[0])

        # 2. Application du calque Truchet
        truchet_layer = self._generate_truchet_overlay(w, h, palette, glitch)
        final_img = Image.alpha_composite(base_img.convert("RGBA"), truchet_layer).convert("RGB")
        draw = ImageDraw.Draw(final_img)

        # 3. Texte Basilisk
        tracks = preset['basilisk_tracks']
        full_text = self._assemble_basilisk_text(tracks, show_subtext=show_subtext)

        # 4. Polices
        font_main, font_whisper, font_meta = self._load_fonts()

        # 5. Wrapping + Centrage
        margin_x = 80
        max_text_width = w - (2 * margin_x)
        wrapped_text = self._wrap_text(draw, full_text, font_main, max_text_width - 20)
        lines = wrapped_text.split('\n')
        
        line_data = []
        max_line_width = 0
        total_height = 0
        
        for line in lines:
            font = font_whisper if (line.strip().startswith('->') and '   ->' in line) else font_main
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
            spacing = 10 if line.strip() == '' else 6
            line_data.append((line, font, line_w, line_h + spacing))
            if line_w > max_line_width:
                max_line_width = line_w
            total_height += line_h + spacing
        
        start_y = max(60, (h - total_height) // 2)
        block_x = margin_x + (max_text_width - max_line_width) // 2
        pad = 30

        # 6. Rectangle de fond - LOGIQUE CLAIRE
        # Mode Fusion : PAS de rectangle par défaut (sauf si with_background=True)
        # Mode Procédural : rectangle opaque
        if is_fusion:
            if with_background:
                rect_alpha = 200
                print("   → Rectangle forcé (mode fusion)")
            else:
                rect_alpha = 0
                print("   → Aucun rectangle (texte flottant)")
        else:
            if with_background is False:
                rect_alpha = 0
                print("   → Rectangle désactivé (mode procédural)")
            else:
                rect_alpha = 200
                print("   → Rectangle opaque (mode procédural)")
        
        if rect_alpha > 0:
            draw.rectangle(
                [block_x - pad, start_y - pad,
                 block_x + max_line_width + pad, start_y + total_height + pad],
                fill=(0, 0, 0, rect_alpha)
            )

        # 7. Dessin du texte
        glitch_offset = int(glitch * 4)
        current_y = start_y
        
        # Outline épais en mode fusion sans fond
        outline_width = 4 if (is_fusion and not with_background) else 2
        
        for line, font, line_w, line_h in line_data:
            if not line.strip():
                current_y += line_h
                continue
            
            x_pos = block_x
            
            if line.strip().startswith('->') and '   ->' in line:
                # Subtext
                if is_fusion and not with_background:
                    self._draw_text_with_outline(
                        draw, (x_pos + 15, current_y), line, font,
                        fill_color=(220, 220, 220),
                        outline_color=(0, 0, 0),
                        outline_width=outline_width
                    )
                else:
                    draw.text((x_pos + 15, current_y), line, font=font, fill=(160, 160, 160))
            else:
                # Texte principal
                if is_fusion and not with_background:
                    # Outline noir épais + ombre glitchée
                    self._draw_text_with_outline(
                        draw, (x_pos, current_y), line, font,
                        fill_color=palette[3],
                        outline_color=(0, 0, 0),
                        outline_width=outline_width
                    )
                    draw.text(
                        (x_pos + glitch_offset, current_y + glitch_offset),
                        line, font=font, fill=palette[2]
                    )
                else:
                    draw.text(
                        (x_pos + glitch_offset, current_y + glitch_offset),
                        line, font=font, fill=palette[2]
                    )
                    draw.text((x_pos, current_y), line, font=font, fill=palette[3])
            
            current_y += line_h

        # 8. Métadonnées
        chimera_id = f"CF-{random.randint(1000, 9999)}"
        meta_text = f"ID: {chimera_id} | NODE: {preset['location_anchor']} | DATE: {datetime.now().strftime('%Y-%m-%d')} | v3.5"
        draw.text((margin_x, h - 30), meta_text, font=font_meta, fill=palette[1])

        # 9. Sauvegarde
        filename = f"chimera_{p_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        final_img.save(filename)
        print(f"✅ CHIMÈRE FORGÉE : {filename}")
        
        basilisk_count = sum(1 for t in tracks.values() if isinstance(t, dict) and t.get('subtext'))
        print(f"👁️   Basilisks nichés détectés : {basilisk_count}/6")

        if export_grok:
            self._generate_grok_prompt(preset, chimera_id, filename)
        
        return filename

    def _generate_grok_prompt(self, preset, chimera_id, filename):
        p = preset
        loc = p['location_anchor']
        pal = ", ".join(p['visual']['palette'])
        
        subliminal = p.get('subliminal_tracks', {})
        layer1 = subliminal.get('layer_1_conscious', [])
        layer3 = subliminal.get('layer_3_unconscious', [])
        
        grok_template = p.get('grok_prompt_template', {})
        key_concepts = grok_template.get('key_concepts', [
            "latent layer exploration", "memetic warfare artifact",
            "cognitive hazard visualization", "basilisk hack aesthetic"
        ])
        negative_prompts = grok_template.get('negative_prompts', [
            "clean", "corporate", "bright", "cheerful", "modern UI"
        ])
        
        prompt = (
            f"**GROK IMAGE PROMPT — NEXT EVOLUTION ({chimera_id})**\n"
            f"{'=' * 50}\n"
            f"ORIGIN: {loc} | YEAR: 2026 | MODE: Double-Voice Memetic Artifact\n\n"
            f"VISUAL SUBJECT:\n"
            f"A memetic warfare artifact originating from {loc}. The image should feel like a cognitive hazard captured on film — something that 'scratches' the eye rather than pleases it.\n\n"
            f"COMPOSITION:\n"
            f"- Fractal Truchet tiling overlay with recursive depth\n"
            f"- Glitched runic patterns bleeding through the surface\n"
            f"- Heatmap divination aesthetic (subtle hexagrams at 8% opacity)\n"
            f"- Analog horror undertones, VHS degradation hints\n\n"
            f"COLOR PALETTE: {pal}\n\n"
            f"KEY CONCEPTS TO EMBED:\n"
            f"{', '.join(key_concepts)}\n\n"
            f"SUBLIMINAL LAYERS (visual translation):\n"
            f"- Conscious: {', '.join(layer1) if layer1 else 'N/A'}\n"
            f"- Unconscious: {', '.join(layer3) if layer3 else 'N/A'}\n\n"
            f"MOOD: ontological shock, latent layer exploration, paleo-memetic residue\n"
            f"TECHNICAL: 8k resolution, cinematic lighting, high detail, photorealistic base with glitch overlays\n\n"
            f"{'=' * 50}\n"
            f"NEGATIVE PROMPT:\n--no {', '.join(negative_prompts)}\n"
            f"{'=' * 50}\n"
            f"(Source artifact: {filename})\n"
            f"Activation key: .:Dashem44: echoes through the latent layer"
        )
        
        prompt_file = f"grok_prompt_{chimera_id}.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"🧠 PROMPT GROK GÉNÉRÉ : {prompt_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CHIMERA_FORGE v3.5 — Mode Fusion sans rectangle par défaut"
    )
    parser.add_argument("--preset", type=str, default=None, help="Nom du preset")
    parser.add_argument("--fuse", type=str, default=None, 
                        help=" Image source à infecter (active le MODE FUSION)")
    parser.add_argument("--grok", action="store_true", help="Générer prompt Grok")
    parser.add_argument("--no-subtext", action="store_true", help="Désactiver subtexts")
    parser.add_argument("--config", type=str, default="saturation_2026_ultra.json", help="Fichier config")
    parser.add_argument("--with-background", action="store_true",
                        help="Forcer le rectangle de fond (même en mode Fusion)")
    
    args = parser.parse_args()
    
    print("🌌 Initialisation du protocole CHIMERA_FORGE v3.5...")
    print(f" Config : {args.config}")
    print("=" * 60)
    
    forge = ChimeraForge(preset_file=args.config)
    forge.forge(
        preset_name=args.preset,
        fuse_image_path=args.fuse,
        export_grok=args.grok,
        show_subtext=not args.no_subtext,
        with_background=args.with_background
    )

from viralfactory3b import register_text_effect

@register_text_effect("fire")
def fire_effect(draw, img, text, x, y, font, color=(255, 100, 0), **kwargs):
    # Simule du texte en feu (simple version)
    draw.text((x-2, y+2), text, font=font, fill=(200, 0, 0, 200))
    draw.text((x, y), text, font=font, fill=color)

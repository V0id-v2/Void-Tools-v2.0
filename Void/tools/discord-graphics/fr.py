import sys, os, time

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    pass

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("\033[31m[!] Erreur : La librairie 'Pillow' n'est pas installée.\033[0m")
    print("\033[37m -> Tapez 'pip install Pillow' dans votre invite de commande.\033[0m")
    input("\nAppuyez sur Entrée pour quitter...")
    sys.exit(1)

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def create_gradient_bg(size, color1, color2):
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    # Dégradé vertical simple
    for y in range(size[1]): 
        r = int(color1[0] + (color2[0] - color1[0]) * (y / size[1]))
        g = int(color1[1] + (color2[1] - color1[1]) * (y / size[1]))
        b = int(color1[2] + (color2[2] - color1[2]) * (y / size[1]))
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    return img

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return (0, 0, 0)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def main():
    cls()
    print("\033[31m" + r"""
  ___  _  ___  ___  ___  ___  ___    ___  ___  ___   __   _  __  ___  ___ 
 |   \| |/ __|/ __|/ _ \| _ \|   \  / __|| _ \/   \ |  \ | ||  \|   \| _ \
 | |) | |\__ \ (__| (_) |   /| |) || (_ ||  /|  -  || | \| || | | |) |   /
 |___/|_||___/\___|\___/|_|_\|___/  \___||_|_\|_|_|_|_|\___||_|\____/|_|_\
    """ + "\033[0m")
    print("\033[37m  Générateur de Logos et Bannières Discord\033[0m\n")

    text = input("\033[31m [=]\033[0m Texte Principal (Ex: VOID) >> ").strip() or "VOID"
    subtext = input("\033[31m [=]\033[0m Sous-texte (Bannière uniquement, Ex: v2.0) >> ").strip()
    
    print("\n\033[37m  Les couleurs doivent être au format HEX (ex: FF0000 pour rouge, 000000 pour noir)\033[0m")
    c1_input = input("\033[31m [=]\033[0m Couleur dégradé haut (HEX) [def: 8B0000] >> ").strip() or "8B0000"
    c2_input = input("\033[31m [=]\033[0m Couleur dégradé bas (HEX)  [def: 000000] >> ").strip() or "000000"
    text_color_input = input("\033[31m [=]\033[0m Couleur du texte (HEX)     [def: FFFFFF] >> ").strip() or "FFFFFF"

    c1 = hex_to_rgb(c1_input)
    c2 = hex_to_rgb(c2_input)
    text_color = hex_to_rgb(text_color_input)

    # Configuration du dossier de sortie
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", "Void - Output", "Graphics"))
    os.makedirs(out_dir, exist_ok=True)

    try:
        # Essaie de charger des polices Windows classiques
        font_logo = ImageFont.truetype("impact.ttf", 100)
        font_banner = ImageFont.truetype("impact.ttf", 150)
        font_sub = ImageFont.truetype("arialbd.ttf", 60)
    except:
        font_logo = ImageFont.load_default()
        font_banner = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        print("\033[33m [!] Police Impact/Arial non trouvée, utilisation de la police par défaut.\033[0m")

    # --- 1. Logo Discord (512x512) ---
    print("\n\033[31m [+]\033[0m Génération du Logo (512x512)...")
    logo = create_gradient_bg((512, 512), c1, c2)
    draw_l = ImageDraw.Draw(logo)
    
    try:
        bb = draw_l.textbbox((0,0), text, font=font_logo)
        w = bb[2] - bb[0]; h = bb[3] - bb[1]
    except:
        w = len(text) * 20; h = 20

    draw_l.text(((512-w)/2, (512-h)/2 - 10), text, fill=text_color, font=font_logo)
    logo_path = os.path.join(out_dir, f"Logo_{text}.png")
    logo.save(logo_path)
    print(f"\033[32m [✔]\033[0m Logo sauvegardé : {logo_path}")

    # --- 2. Bannière Discord (1920x480) ---
    print("\033[31m [+]\033[0m Génération de la Bannière (1920x480)...")
    banner = create_gradient_bg((1920, 480), c1, c2)
    draw_b = ImageDraw.Draw(banner)

    try:
        bb2 = draw_b.textbbox((0,0), text, font=font_banner)
        w2 = bb2[2] - bb2[0]; h2 = bb2[3] - bb2[1]
    except:
        w2 = len(text) * 40; h2 = 40

    center_x = 1920 / 2
    center_y = 480 / 2
    draw_b.text((center_x - w2/2, center_y - h2/2 - (20 if subtext else 0)), text, fill=text_color, font=font_banner)

    if subtext:
        try:
            bb3 = draw_b.textbbox((0,0), subtext, font=font_sub)
            w3 = bb3[2] - bb3[0]
        except:
            w3 = len(subtext) * 20
        draw_b.text((center_x - w3/2, center_y + h2/2 + 20), subtext, fill=text_color, font=font_sub)

    banner_path = os.path.join(out_dir, f"Banner_{text}.png")
    banner.save(banner_path)
    print(f"\033[32m [✔]\033[0m Bannière sauvegardée : {banner_path}")

    print("\n\033[37m Appuyez sur Entrée pour retourner...\033[0m")
    input()

if __name__ == "__main__":
    main()

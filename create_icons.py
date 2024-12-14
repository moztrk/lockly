from PIL import Image, ImageDraw
import os

def create_directory():
    if not os.path.exists('assets'):
        os.makedirs('assets')

def create_lockly_logo():
    # Modern logo oluştur (150x150)
    img = Image.new('RGBA', (150, 150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Koyu arka plan daire
    draw.ellipse([10, 10, 140, 140], fill='#1A1A1A')
    
    # Yeşil dış halka
    draw.ellipse([10, 10, 140, 140], outline='#00FF00', width=3)
    
    # Kilit şekli
    draw.rectangle([50, 60, 100, 110], fill='#00FF00')  # Kilit gövdesi
    draw.arc([45, 40, 105, 70], 0, 180, fill='#00FF00', width=8)  # Kilit halkası
    
    img.save('assets/lockly_logo.png')

def create_action_icons():
    # Modern ikonlar için renk paleti
    colors = {
        'primary': '#00FF00',    # Hacker yeşili
        'danger': '#E74C3C',     # Silme/Tehlike
        'warning': '#F1C40F',    # Uyarı
        'info': '#3498DB',       # Bilgi
        'success': '#2ECC71'     # Başarı
    }
    
    # İkon boyutları
    size = 24
    
    # Yeni şifre ikonu
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.line([12, size//2, size-12, size//2], fill=colors['primary'], width=2)
    draw.line([size//2, 12, size//2, size-12], fill=colors['primary'], width=2)
    img.save('assets/add_icon.png')
    
    # Yenile ikonu
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.arc([4, 4, size-4, size-4], 45, 315, fill=colors['primary'], width=2)
    draw.polygon([(size-8, 4), (size-4, 8), (size-12, 12)], fill=colors['primary'])
    img.save('assets/refresh_icon.png')
    
    # Çıkış ikonu
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.line([8, size//2, size-8, size//2], fill=colors['danger'], width=2)
    draw.line([size-12, size//2-4, size-8, size//2], fill=colors['danger'], width=2)
    draw.line([size-12, size//2+4, size-8, size//2], fill=colors['danger'], width=2)
    img.save('assets/logout_icon.png')
    
    # Arama ikonu
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 16, 16], outline=colors['primary'], width=2)
    draw.line([14, 14, 20, 20], fill=colors['primary'], width=2)
    img.save('assets/search_icon.png')
    
    # Zar ikonu (rastgele şifre)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, 20, 20], outline=colors['primary'], width=2)
    draw.ellipse([8, 8, 10, 10], fill=colors['primary'])
    draw.ellipse([14, 14, 16, 16], fill=colors['primary'])
    img.save('assets/dice_icon.png')

def create_window_icon():
    # Pencere ikonu (32x32)
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Kilit şekli
    draw.rectangle([8, 12, 24, 28], fill='#00FF00')  # Gövde
    draw.arc([11, 6, 21, 16], 0, 180, fill='#00FF00', width=2)  # Halka
    
    img.save('assets/lock_icon.png')

def main():
    create_directory()
    create_lockly_logo()
    create_window_icon()
    create_action_icons()

if __name__ == '__main__':
    main() 
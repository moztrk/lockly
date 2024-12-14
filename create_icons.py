from PIL import Image, ImageDraw
import os

def create_directory():
    if not os.path.exists('assets'):
        os.makedirs('assets')

def create_lockly_logo():
    # Logo oluştur (150x150)
    img = Image.new('RGBA', (150, 150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Kalkan şekli
    draw.ellipse([25, 25, 125, 125], fill='#3498DB')
    draw.rectangle([45, 60, 105, 100], fill='#ECF0F1')
    draw.ellipse([50, 70, 70, 90], fill='#3498DB')
    
    img.save('assets/lockly_logo.png')

def create_lock_icon():
    # Pencere ikonu oluştur (32x32)
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Basit kilit şekli
    draw.rectangle([8, 12, 24, 28], fill='#3498DB')
    draw.rectangle([11, 6, 21, 12], fill='#3498DB')
    
    img.save('assets/lock_icon.png')

def create_action_icon(filename, color, icon_type):
    # 16x16 boyutunda aksiyon ikonları
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if icon_type == 'add':
        # Artı işareti
        draw.rectangle([7, 3, 9, 13], fill=color)
        draw.rectangle([3, 7, 13, 9], fill=color)
    elif icon_type == 'refresh':
        # Yenileme oku
        points = [(3, 8), (7, 4), (11, 8), (7, 12)]
        draw.polygon(points, fill=color)
    elif icon_type == 'logout':
        # Çıkış kapısı
        draw.rectangle([3, 3, 13, 13], outline=color)
        draw.line([8, 8, 12, 8], fill=color, width=2)
    elif icon_type == 'search':
        # Büyüteç
        draw.ellipse([3, 3, 11, 11], outline=color)
        draw.line([9, 9, 13, 13], fill=color, width=2)
    elif icon_type == 'dice':
        # Zar
        draw.rectangle([3, 3, 13, 13], outline=color)
        draw.ellipse([5, 5, 7, 7], fill=color)
        draw.ellipse([9, 9, 11, 11], fill=color)
    
    img.save(f'assets/{filename}.png')

def create_eye_icon():
    # Göz ikonu (24x24)
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Göz şekli
    draw.ellipse([4, 8, 20, 16], outline='#00FF00', width=2)
    draw.ellipse([10, 10, 14, 14], fill='#00FF00')
    
    img.save('assets/eye_icon.png')

def create_lock_small_icon():
    # Küçük kilit ikonu (24x24)
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Kilit gövdesi
    draw.rectangle([8, 10, 16, 18], outline='#00FF00', width=2)
    # Kilit halkası
    draw.arc([9, 6, 15, 12], 0, 180, fill='#00FF00', width=2)
    
    img.save('assets/lock_small_icon.png')

def main():
    create_directory()
    create_lockly_logo()
    create_lock_icon()
    create_eye_icon()
    create_lock_small_icon()
    
    # Aksiyon ikonlarını oluştur
    create_action_icon('add_icon', '#FFFFFF', 'add')
    create_action_icon('refresh_icon', '#FFFFFF', 'refresh')
    create_action_icon('logout_icon', '#FFFFFF', 'logout')
    create_action_icon('search_icon', '#7F8C8D', 'search')
    create_action_icon('dice_icon', '#FFFFFF', 'dice')

if __name__ == '__main__':
    main() 
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QStackedWidget, QMessageBox, QDialog, QScrollArea, 
                           QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtGui import QColor, QIcon, QFont, QPainter, QPalette
import sys
from datetime import datetime
from veritabani import VeritabaniYoneticisi
from main import SifreYoneticisi
import random

class MatrixRain(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chars = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rain)
        self.timer.start(50)
        
        self.matrix_chars = ''.join([chr(i) for i in range(0x30A0, 0x30FF)])
        self.drops = []
        self.kilit_renk = QColor(0, 255, 0)  # Varsayılan renk
        self.init_drops()

    def init_drops(self):
        width = self.parent().width() if self.parent() else 800
        # Her 20 piksel için bir damla oluştur
        for x in range(0, width, 20):
            self.drops.append({
                'x': x,
                'y': random.randint(-100, 0),
                'speed': random.randint(3, 8),
                'chars': []
            })
    
    def update_rain(self):
        height = self.parent().height() if self.parent() else 600
        
        for drop in self.drops:
            # Yeni karakter ekle
            if random.random() < 0.1:  # %10 şans
                drop['chars'].append({
                    'char': random.choice(self.matrix_chars),
                    'opacity': 255,
                    'y': drop['y']
                })
            
            # Karakterleri güncelle
            for char in drop['chars']:
                char['opacity'] = max(0, char['opacity'] - 5)
            
            # Görünmez karakterleri kaldır
            drop['chars'] = [c for c in drop['chars'] if c['opacity'] > 0]
            
            # Damlayı aşağı kaydır
            drop['y'] += drop['speed']
            
            # Ekranın altına ulaşınca sıfırla
            if drop['y'] > height + 100:
                drop['y'] = random.randint(-100, 0)
                drop['chars'] = []
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont('Consolas', 14))
        
        for drop in self.drops:
            for char in drop['chars']:
                color = QColor(self.kilit_renk)
                color.setAlpha(char['opacity'])
                painter.setPen(color)
                painter.drawText(
                    QPoint(drop['x'], char['y']), 
                    char['char']
                )

class GirisPenceresi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        
        # Matrix yağmuru arka planı
        self.matrix_rain = MatrixRain(self)
        self.matrix_rain.setGeometry(self.rect())
        self.matrix_rain.lower()
        
        self.init_ui()

    def init_ui(self):
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(50, 50, 50, 50)
        
        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 0.95);
                border: none;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        container_duzen = QVBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(100, 100))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        container_duzen.addWidget(logo_label)
        
        # Başlık
        self.baslik = QLabel("LOCKLY")
        self.baslik.setFont(QFont('Segoe UI', 36, QFont.Bold))
        self.baslik.setAlignment(Qt.AlignCenter)
        self.baslik.setStyleSheet("color: #FFFFFF;")
        container_duzen.addWidget(self.baslik)
        
        self.alt_baslik = QLabel("Güvenli Şifre Yöneticisi")
        self.alt_baslik.setFont(QFont('Segoe UI', 14))
        self.alt_baslik.setAlignment(Qt.AlignCenter)
        self.alt_baslik.setStyleSheet("color: #B0B0B0;")
        container_duzen.addWidget(self.alt_baslik)
        
        container_duzen.addSpacing(30)
        
        # Input stil tanımı
        input_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.3);
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
            }
        """
        
        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")
        self.kullanici_adi.setMinimumHeight(45)
        self.kullanici_adi.setStyleSheet(input_style)
        
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setMinimumHeight(45)
        self.sifre.setStyleSheet(input_style)
        self.sifre.returnPressed.connect(self.giris_yap)
        
        # Butonlar
        buton_stili = """
            QPushButton {
                background-color: #4A90E2;
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868B0;
            }
        """
        
        kayit_buton_stili = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """
        
        self.giris_butonu = QPushButton("Giriş Yap")
        self.giris_butonu.setMinimumHeight(45)
        self.giris_butonu.clicked.connect(self.giris_yap)
        self.giris_butonu.setStyleSheet(buton_stili)
        
        self.kayit_butonu = QPushButton("Kayıt Ol")
        self.kayit_butonu.setMinimumHeight(45)
        self.kayit_butonu.clicked.connect(self.kayit_ekranina_git)
        self.kayit_butonu.setStyleSheet(kayit_buton_stili)
        
        buton_duzen = QHBoxLayout()
        buton_duzen.addWidget(self.giris_butonu)
        buton_duzen.addWidget(self.kayit_butonu)
        
        form_duzen = QVBoxLayout()
        form_duzen.setSpacing(15)
        form_duzen.addWidget(self.kullanici_adi)
        form_duzen.addWidget(self.sifre)
        form_duzen.addLayout(buton_duzen)
        
        container_duzen.addLayout(form_duzen)
        container_duzen.addStretch()
        
        # Alt bilgi
        self.alt_bilgi = QLabel("© 2024 Lockly")
        self.alt_bilgi.setAlignment(Qt.AlignCenter)
        self.alt_bilgi.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        container_duzen.addWidget(self.alt_bilgi)
        
        # Hakkında butonu
        hakkinda_buton = QPushButton("Hakkında")
        hakkinda_buton.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.5);
                text-decoration: none;
                font-family: 'Segoe UI';
                font-size: 12px;
                min-width: 0;
                padding: 5px;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: underline;
            }
        """)
        hakkinda_buton.setCursor(Qt.PointingHandCursor)
        hakkinda_buton.clicked.connect(self.hakkinda_goster)
        container_duzen.addWidget(hakkinda_buton, alignment=Qt.AlignCenter)
        
        self.container.setLayout(container_duzen)
        duzen.addWidget(self.container)
        
        self.setLayout(duzen)
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Minimum boyutları ayarla
        width = max(800, self.width())
        height = max(600, self.height())
        if width != self.width() or height != self.height():
            self.resize(width, height)

    def giris_yap(self):
        kullanici_adi = self.kullanici_adi.text()
        sifre = self.sifre.text()
        
        if self.ana_pencere.yonetici.kullanici_giris(kullanici_adi, sifre):
            self.ana_pencere.ana_ekrani_goster()
        else:
            hata_kutusu = QMessageBox(self)
            hata_kutusu.setWindowTitle("Hata")
            hata_kutusu.setText("Giriş başarısız!")
            hata_kutusu.setIcon(QMessageBox.Warning)
            hata_kutusu.setStyleSheet("""
                QMessageBox {
                    background-color: rgba(25, 25, 35, 0.95);
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QMessageBox QPushButton {
                    background-color: #4A90E2;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
            """)
            hata_kutusu.exec_()

    def kayit_ekranina_git(self):
        self.ana_pencere.stacked_widget.setCurrentIndex(1)

    def hakkinda_goster(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Hakkında")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0A0A0A;
                border: 1px solid #00FF00;
            }
        """)
        
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(30, 30, 30, 30)
        
        # Logo
        logo = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(100, 100))
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        duzen.addWidget(logo)
        
        # Başlık
        baslik = QLabel("LOCKLY")
        baslik.setFont(QFont('Consolas', 24, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #00FF00;")
        duzen.addWidget(baslik)
        
        # İçerik
        icerik = QLabel("""
        <div style='color: #00FF00;'>
            <p style='text-align: center;'>
            Lockly, modern ve güvenli bir şifre yönetim uygulamasıdır.
            </p>
            
            <p><b style='color: #00FF00;'>Özellikler:</b></p>
            <ul>
                <li>AES-256 şifreleme ile güvenli depolama</li>
                <li>Güçlü şifre oluşturucu</li>
                <li>Şifre gücü analizi</li>
                <li>Güvenli şifre paylaşımı</li>
                <li>Kolay arama ve filtreleme</li>
                <li>Modern ve kullanıcı dostu arayüz</li>
            </ul>
            
            <p><b style='color: #00FF00;'>Güvenlik:</b></p>
            <p>
            Tüm verileriniz yerel veritabanında şifrelenmiş olarak saklanır.
            Şifrelerinize yalnızca siz erişebilirsiniz.
            </p>
            
            <p><b style='color: #00FF00;'>Versiyon:</b> 1.0.0</p>
            <p><b style='color: #00FF00;'>Geliştirici:</b> Lockly Team</p>
            
            <p><b style='color: #00FF00;'>İletişim:</b></p>
            <p>
            E-posta: destek@lockly.com<br>
            Web: www.lockly.com
            </p>
        </div>
        """)
        icerik.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 14px;
                background-color: rgba(0, 255, 0, 0.05);
                padding: 15px;
                border-radius: 8px;
            }
        """)
        icerik.setWordWrap(True)
        icerik.setTextFormat(Qt.RichText)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidget(icerik)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #00FF00;
                background-color: transparent;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #0A0A0A;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #00FF00;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        duzen.addWidget(scroll)
        
        # Kapat butonu
        kapat = QPushButton("Kapat")
        kapat.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border: 1px solid #00FF00;
                border-radius: 5px;
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 14px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """)
        kapat.clicked.connect(dialog.close)
        duzen.addWidget(kapat, alignment=Qt.AlignCenter)
        
        dialog.setLayout(duzen)
        dialog.exec_()

class KayitPenceresi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()

    def init_ui(self):
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(50, 50, 50, 50)
        
        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 0.95);
                border: none;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        container_duzen = QVBoxLayout()
        
        # Logo ve başlık
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(80, 80))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        container_duzen.addWidget(logo_label)
        
        self.baslik = QLabel("Yeni Hesap Oluştur")
        self.baslik.setFont(QFont('Segoe UI', 28, QFont.Bold))
        self.baslik.setAlignment(Qt.AlignCenter)
        self.baslik.setStyleSheet("color: #FFFFFF;")
        container_duzen.addWidget(self.baslik)
        
        container_duzen.addSpacing(30)
        
        # Input stil tanımı
        input_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.3);
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
            }
        """
        
        # Form alanları
        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")
        self.kullanici_adi.setMinimumHeight(45)
        self.kullanici_adi.setStyleSheet(input_style)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("E-posta")
        self.email.setMinimumHeight(45)
        self.email.setStyleSheet(input_style)
        
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setMinimumHeight(45)
        self.sifre.setStyleSheet(input_style)
        
        self.sifre_tekrar = QLineEdit()
        self.sifre_tekrar.setPlaceholderText("Şifre Tekrar")
        self.sifre_tekrar.setEchoMode(QLineEdit.Password)
        self.sifre_tekrar.setMinimumHeight(45)
        self.sifre_tekrar.setStyleSheet(input_style)
        
        # Şifre gücü göstergesi
        self.guc_etiketi = QLabel()
        self.guc_etiketi.setAlignment(Qt.AlignCenter)
        self.guc_etiketi.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-family: 'Segoe UI';
            font-size: 13px;
        """)
        
        self.sifre.textChanged.connect(self.sifre_gucunu_goster)
        
        # Butonlar
        buton_duzen = QHBoxLayout()
        buton_duzen.setSpacing(15)
        
        self.geri_butonu = QPushButton("Geri")
        self.geri_butonu.setMinimumHeight(45)
        self.geri_butonu.setCursor(Qt.PointingHandCursor)
        self.geri_butonu.clicked.connect(lambda: self.ana_pencere.stacked_widget.setCurrentIndex(0))
        self.geri_butonu.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        self.kayit_butonu = QPushButton("Kayıt Ol")
        self.kayit_butonu.setMinimumHeight(45)
        self.kayit_butonu.setCursor(Qt.PointingHandCursor)
        self.kayit_butonu.clicked.connect(self.kayit_ol)
        self.kayit_butonu.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868B0;
            }
        """)
        
        buton_duzen.addWidget(self.geri_butonu)
        buton_duzen.addWidget(self.kayit_butonu)
        
        container_duzen.addWidget(self.kullanici_adi)
        container_duzen.addWidget(self.email)
        container_duzen.addWidget(self.sifre)
        container_duzen.addWidget(self.sifre_tekrar)
        container_duzen.addWidget(self.guc_etiketi)
        container_duzen.addLayout(buton_duzen)
        container_duzen.addStretch()
        
        # Alt bilgi
        self.alt_bilgi = QLabel("© 2024 Lockly")
        self.alt_bilgi.setAlignment(Qt.AlignCenter)
        self.alt_bilgi.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        container_duzen.addWidget(self.alt_bilgi)
        
        self.container.setLayout(container_duzen)
        duzen.addWidget(self.container)
        self.setLayout(duzen)

    def sifre_gucunu_goster(self):
        sifre = self.sifre.text()
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre)
        
        renk = {
            "Zayıf": "#ff4444",
            "Orta": "#ffbb33",
            "Güçlü": "#00C851"
        }
        
        self.guc_etiketi.setText(f"Şifre Gücü: <font color='{renk[guc]}'>{guc}</font>")
        
    def kayit_ol(self):
        if self.sifre.text() != self.sifre_tekrar.text():
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return
            
        guc, _ = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(self.sifre.text())
        if guc == "Zayıf":
            QMessageBox.warning(self, "Hata", "Şifre çok zayıf!")
            return
            
        if self.ana_pencere.yonetici.kullanici_kayit(
            self.kullanici_adi.text(),
            self.sifre.text(),
            self.email.text()
        ):
            QMessageBox.information(self, "Başarılı", "Kayıt başarıyla tamamlandı!")
            self.ana_pencere.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Hata", "Kayıt başarısız!")

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.yonetici = SifreYoneticisi()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Lockly - Güvenli Şifre Yöneticisi')
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon('assets/lock_icon.png'))
        
        # Ana tema renklerini ayarla - Sadece koyu tema
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#000000"))
        palette.setColor(QPalette.WindowText, QColor("#00FF00"))
        palette.setColor(QPalette.Base, QColor("#1A1A1A"))
        palette.setColor(QPalette.AlternateBase, QColor("#333333"))
        palette.setColor(QPalette.Text, QColor("#00FF00"))
        palette.setColor(QPalette.Button, QColor("#333333"))
        palette.setColor(QPalette.ButtonText, QColor("#00FF00"))
        self.setPalette(palette)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Ekranları oluştur
        self.giris_ekrani = GirisPenceresi(self)
        self.kayit_ekrani = KayitPenceresi(self)
        
        # Ekranları stack'e ekle
        self.stacked_widget.addWidget(self.giris_ekrani)
        self.stacked_widget.addWidget(self.kayit_ekrani)
        
    def ana_ekrani_goster(self):
        if not hasattr(self, 'ana_ekran'):
            self.ana_ekran = AnaEkran(self)
            self.stacked_widget.addWidget(self.ana_ekran)
        self.stacked_widget.setCurrentWidget(self.ana_ekran)

class AnaEkran(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()
        
        # Otomatik yenileme için timer ekle
        self.yenileme_timer = QTimer()
        self.yenileme_timer.timeout.connect(self.sifreleri_yukle)
        self.yenileme_timer.start(5000)
        
        # İlk yüklemeyi yap
        QTimer.singleShot(100, self.sifreleri_yukle)

    def sifreleri_yukle(self):
        """Şifreleri veritabanından yükle ve kartları oluştur"""
        # Mevcut kartları temizle
        while self.kartlar_duzen.count():
            item = self.kartlar_duzen.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        sifreler = self.ana_pencere.yonetici.sifreleri_getir()
        if not sifreler:
            # Şifre yoksa bilgi mesajı göster
            bos_mesaj = QLabel("Henüz hiç şifre eklenmemiş.\nYeni şifre eklemek için üstteki 'Yeni Şifre' butonunu kullanın.")
            bos_mesaj.setStyleSheet("""
                color: rgba(255, 255, 255, 0.5);
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 20px;
            """)
            bos_mesaj.setAlignment(Qt.AlignCenter)
            self.kartlar_duzen.addWidget(bos_mesaj)
            return
            
        sifreler.sort(key=lambda x: x[5], reverse=True)  # Tarihe göre sırala
        
        for sifre in sifreler:
            kart = self.sifre_karti_olustur(sifre)
            self.kartlar_duzen.addWidget(kart)
        
        self.kartlar_duzen.addStretch()

    def init_ui(self):
        # Ana düzen
        ana_duzen = QVBoxLayout()
        ana_duzen.setSpacing(20)
        ana_duzen.setContentsMargins(30, 30, 30, 30)
        
        # Üst bar
        ust_bar = QWidget()
        ust_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 0.95);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        ust_duzen = QHBoxLayout()
        
        # Sol grup (Yeni Şifre ve Yenile butonları)
        sol_butonlar = QHBoxLayout()
        
        yeni_sifre = QPushButton()
        yeni_sifre.setIcon(QIcon("assets/add_icon.png"))
        yeni_sifre.setIconSize(QSize(20, 20))
        yeni_sifre.setText("Yeni Şifre")
        yeni_sifre.clicked.connect(self.yeni_sifre_ekle)
        yeni_sifre.setCursor(Qt.PointingHandCursor)
        yeni_sifre.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 7px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 8px 15px;
                padding-left: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        yenile = QPushButton()
        yenile.setIcon(QIcon("assets/refresh_icon.png"))
        yenile.setIconSize(QSize(20, 20))
        yenile.setText("Yenile")
        yenile.clicked.connect(self.sifreleri_yukle)
        yenile.setCursor(Qt.PointingHandCursor)
        yenile.setStyleSheet(yeni_sifre.styleSheet().replace("#4CAF50", "#4A90E2")
                                               .replace("#45a049", "#357ABD")
                                               .replace("#3d8b40", "#2868B0"))
        
        sol_butonlar.addWidget(yeni_sifre)
        sol_butonlar.addWidget(yenile)
        
        # Sağ grup (Kullanıcı bilgisi ve Çıkış)
        sag_grup = QHBoxLayout()
        
        kullanici_label = QLabel(f"Hoş geldiniz, {self.ana_pencere.yonetici.mevcut_kullanici}")
        kullanici_label.setStyleSheet("""
            color: white;
            font-family: 'Segoe UI';
            font-size: 14px;
            padding-right: 15px;
        """)
        
        cikis = QPushButton()
        cikis.setIcon(QIcon("assets/logout_icon.png"))
        cikis.setIconSize(QSize(20, 20))
        cikis.setText("Çıkış Yap")
        cikis.clicked.connect(self.cikis_yap)
        cikis.setCursor(Qt.PointingHandCursor)
        cikis.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                border: none;
                border-radius: 7px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 8px 15px;
                padding-left: 10px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        
        sag_grup.addWidget(kullanici_label)
        sag_grup.addWidget(cikis)
        
        ust_duzen.addLayout(sol_butonlar)
        ust_duzen.addStretch()
        ust_duzen.addLayout(sag_grup)
        
        ust_bar.setLayout(ust_duzen)
        ana_duzen.addWidget(ust_bar)
        
        # Kartların container'ı için arka plan widget
        kartlar_arka_plan = QWidget()
        kartlar_arka_plan.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 0.95);
                border-radius: 15px;
            }
        """)
        kartlar_arka_plan_duzen = QVBoxLayout()
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Kartların container'ı
        self.kartlar_widget = QWidget()
        self.kartlar_widget.setStyleSheet("background: transparent;")
        self.kartlar_duzen = QVBoxLayout()
        self.kartlar_duzen.setSpacing(15)
        self.kartlar_duzen.setContentsMargins(20, 20, 20, 20)
        self.kartlar_widget.setLayout(self.kartlar_duzen)
        
        scroll.setWidget(self.kartlar_widget)
        kartlar_arka_plan_duzen.addWidget(scroll)
        kartlar_arka_plan.setLayout(kartlar_arka_plan_duzen)
        
        ana_duzen.addWidget(kartlar_arka_plan)
        
        self.setLayout(ana_duzen)
        self.setStyleSheet("""
            QWidget {
                background-color: #0A0A0A;
            }
        """)

    def sifre_duzenle(self, sifre):
        dialog = SifreEkleDuzenleDialog(self.ana_pencere, sifre)
        if dialog.exec_() == QDialog.Accepted:
            self.sifreleri_yukle()
            self.basarili_bildirim_goster("Şifre başarıyla güncellendi!")

    def sifre_sil(self, sifre_id):
        if self.ana_pencere.yonetici.sifre_sil(sifre_id):
            self.sifreleri_yukle()
            self.basarili_bildirim_goster("Şifre başarıyla silindi!")
        else:
            self.hata_bildirim_goster("Şifre silinemedi!")

    def cikis_yap(self):
        self.yenileme_timer.stop()
        self.ana_pencere.yonetici.kullanici_cikis()
        self.ana_pencere.stacked_widget.setCurrentIndex(0)

    def basarili_bildirim_goster(self, mesaj):
        """Başarılı işlem bildirimi göster"""
        bildirim = QMessageBox(self)
        bildirim.setWindowTitle("Başarılı")
        bildirim.setText(mesaj)
        bildirim.setIcon(QMessageBox.Information)
        bildirim.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E2E;
                border: 2px solid #2ECC71;
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 20px;
                min-width: 300px;
            }
            QMessageBox QPushButton {
                background-color: #2ECC71;
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        bildirim.exec_()

    def hata_bildirim_goster(self, mesaj):
        """Hata bildirimi göster"""
        bildirim = QMessageBox(self)
        bildirim.setWindowTitle("Hata")
        bildirim.setText(mesaj)
        bildirim.setIcon(QMessageBox.Critical)
        bildirim.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E2E;
                border: 2px solid #E74C3C;
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 20px;
                min-width: 300px;
            }
            QMessageBox QPushButton {
                background-color: #E74C3C;
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        bildirim.exec_()

    def sifre_karti_olustur(self, sifre):
        """Şifre kartı widget'ı oluştur"""
        kart = QWidget()
        kart.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 0.95);
                border-radius: 10px;
                padding: 15px;
            }
            QWidget:hover {
                background-color: rgba(30, 30, 40, 0.95);
            }
        """)
        
        duzen = QVBoxLayout()
        duzen.setSpacing(10)
        
        # Başlık ve butonlar satırı
        ust_kisim = QHBoxLayout()
        
        baslik = QLabel(sifre[1])
        baslik.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Segoe UI';
        """)
        ust_kisim.addWidget(baslik)
        
        buton_grubu = QHBoxLayout()
        buton_grubu.setSpacing(8)
        
        # Buton stili
        buton_stili = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 5px;
                color: white;
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """
        
        # Şifre alanı
        sifre_alani = QLabel("••••••••")
        sifre_alani.setStyleSheet("""
            color: white;
            background-color: rgba(255, 255, 255, 0.05);
            padding: 8px 12px;
            border-radius: 5px;
            font-family: 'Consolas';
            font-size: 14px;
        """)
        
        # Göster/Gizle butonu
        goster_buton = QPushButton("👁️")
        goster_buton.setStyleSheet(buton_stili)
        goster_buton.setCursor(Qt.PointingHandCursor)
        goster_buton.setToolTip("Şifreyi Göster/Gizle")
        
        def toggle_sifre():
            if sifre_alani.text() == "••••••••":
                sifre_alani.setText(sifre[2])
                goster_buton.setText("🔒")
            else:
                sifre_alani.setText("••••••••")
                goster_buton.setText("👁️")
        
        goster_buton.clicked.connect(toggle_sifre)
        
        # Kopyala butonu
        kopyala = QPushButton("📋")
        kopyala.setStyleSheet(buton_stili)
        kopyala.setToolTip("Şifreyi Kopyala")
        kopyala.setCursor(Qt.PointingHandCursor)
        kopyala.clicked.connect(lambda: self.kopyalama_bildirimi(sifre[2]))
        
        # Düzenle butonu
        duzenle = QPushButton("✏️")
        duzenle.setStyleSheet(buton_stili)
        duzenle.setToolTip("Şifreyi Düzenle")
        duzenle.setCursor(Qt.PointingHandCursor)
        duzenle.clicked.connect(lambda: self.sifre_duzenle(sifre))
        
        # Sil butonu
        sil = QPushButton("🗑️")
        sil.setStyleSheet(buton_stili)
        sil.setToolTip("Şifreyi Sil")
        sil.setCursor(Qt.PointingHandCursor)
        sil.clicked.connect(lambda: self.sil_onay_kutusu(sifre))
        
        # Butonları ekle
        for buton in [goster_buton, kopyala, duzenle, sil]:
            buton_grubu.addWidget(buton)
        
        ust_kisim.addStretch()
        ust_kisim.addLayout(buton_grubu)
        
        duzen.addLayout(ust_kisim)
        duzen.addWidget(sifre_alani)
        
        # Güvenlik seviyesi göstergesi
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre[2])
        
        # Geri bildirimleri formatlama
        if guc == "Güçlü":
            geri_bildirim = "✓ Bu şifre güvenlik standartlarını karşılıyor."
        else:
            geri_bildirim = "Öneriler:\n• " + "\n• ".join(geri_bildirim)
        
        # Güvenlik göstergesi container'ı
        guc_container = QWidget()
        guc_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
            }
        """)
        guc_duzen = QHBoxLayout()
        
        # Güvenlik seviyesine göre renk ve ikon
        guc_renk = {
            "Zayıf": "#E74C3C",
            "Orta": "#F1C40F",
            "Güçlü": "#2ECC71"
        }
        
        guc_ikon = {
            "Zayıf": "🔓",
            "Orta": "🔐",
            "Güçlü": "🛡️"
        }
        
        # Progress bar
        progress = QProgressBar()
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {guc_renk[guc]};
                border-radius: 3px;
            }}
        """)
        
        if guc == "Zayıf":
            progress.setValue(33)
        elif guc == "Orta":
            progress.setValue(66)
        else:
            progress.setValue(100)
        
        # Güvenlik seviyesi etiketi
        guc_label = QLabel(f"{guc_ikon[guc]} Güvenlik: {guc}")
        guc_label.setStyleSheet(f"""
            color: {guc_renk[guc]};
            font-family: 'Segoe UI';
            font-size: 13px;
            font-weight: bold;
        """)
        
        # Geri bildirim etiketi
        bilgi_label = QLabel(geri_bildirim)
        bilgi_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-family: 'Segoe UI';
            font-size: 12px;
            padding: 5px 0;
            line-height: 1.4;
        """)
        bilgi_label.setWordWrap(True)
        
        # Sol grup (ikon ve seviye)
        sol_grup = QVBoxLayout()
        sol_grup.addWidget(guc_label)
        sol_grup.addWidget(progress)
        
        guc_duzen.addLayout(sol_grup, stretch=1)
        guc_duzen.addWidget(bilgi_label, stretch=2)
        guc_container.setLayout(guc_duzen)
        
        duzen.addWidget(guc_container)
        
        # Alt bilgiler
        if sifre[3]:  # Website
            website = QLabel(f"🌐 {sifre[3]}")
            website.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            duzen.addWidget(website)
            
        if sifre[4]:  # Açıklama
            aciklama = QLabel(f"📝 {sifre[4]}")
            aciklama.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            duzen.addWidget(aciklama)
        
        tarih = QLabel(f"🕒 {sifre[5]}")
        tarih.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px;")
        duzen.addWidget(tarih)
        
        kart.setLayout(duzen)
        return kart

    def kopyalama_bildirimi(self, sifre):
        """Şifreyi panoya kopyala ve bildirim göster"""
        QApplication.clipboard().setText(sifre)
        self.basarili_bildirim_goster("Şifre panoya kopyalandı!")

    def sil_onay_kutusu(self, sifre):
        """Silme onay kutusu göster"""
        onay = QMessageBox(self)
        onay.setWindowTitle("Şifre Sil")
        onay.setText(f"'{sifre[1]}' başlıklı şifre kalıcı olarak silinecek.")
        onay.setInformativeText("Bu işlemi geri alamazsınız.")
        onay.setIcon(QMessageBox.Warning)
        onay.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        onay.setDefaultButton(QMessageBox.No)
        
        # Evet/Hayır butonlarını özelleştir
        evet_buton = onay.button(QMessageBox.Yes)
        evet_buton.setText("✔ Evet, Sil")
        evet_buton.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)

        hayir_buton = onay.button(QMessageBox.No)
        hayir_buton.setText("✖ Vazgeç")
        hayir_buton.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)

        onay.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E2E;
                border: 2px solid #E74C3C;
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 20px;
                min-width: 300px;
            }
            QLabel#qt_msgbox_label { 
                color: white;
                font-weight: bold;
                font-size: 15px;
            }
            QLabel#qt_msgbox_informativelabel { 
                color: #E74C3C;
                font-size: 13px;
                margin-top: -10px;
            }
        """)
        
        if onay.exec_() == QMessageBox.Yes:
            self.sifre_sil(sifre[0])

    def yeni_sifre_ekle(self):
        """Yeni şifre ekleme dialog'unu göster"""
        dialog = SifreEkleDuzenleDialog(self.ana_pencere)
        if dialog.exec_() == QDialog.Accepted:
            self.sifreleri_yukle()
            self.basarili_bildirim_goster("Şifre başarıyla eklendi!")

class SifreEkleDuzenleDialog(QDialog):
    def __init__(self, ana_pencere, sifre_bilgisi=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.sifre_bilgisi = sifre_bilgisi
        self.setFixedWidth(500)
        
        # Pencere özelliklerini ayarla
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Arka plan rengini ayarla
        self.setStyleSheet("""
            QDialog {
                background: #1E1E2E;
                border: 2px solid rgba(74, 144, 226, 0.3);
                border-radius: 20px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(0, 0, 0, 0)

        # Başlık çubuğu
        baslik_cubugu = QWidget()
        baslik_cubugu.setStyleSheet("""
            QWidget {
                background: rgba(74, 144, 226, 0.1);
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }
        """)
        baslik_duzen = QHBoxLayout()
        baslik_duzen.setContentsMargins(20, 15, 20, 15)
        
        baslik = QLabel("Yeni Şifre Ekle" if not self.sifre_bilgisi else "Şifre Düzenle")
        baslik.setStyleSheet("""
            color: #4A90E2;
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: bold;
        """)
        
        kapat_buton = QPushButton("✕")
        kapat_buton.setCursor(Qt.PointingHandCursor)
        kapat_buton.clicked.connect(self.reject)
        kapat_buton.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4A90E2;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 5px 10px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: rgba(231, 76, 60, 0.1);
                color: #E74C3C;
            }
        """)
        
        baslik_duzen.addWidget(baslik)
        baslik_duzen.addStretch()
        baslik_duzen.addWidget(kapat_buton)
        baslik_cubugu.setLayout(baslik_duzen)
        duzen.addWidget(baslik_cubugu)

        # Ana içerik alanı
        icerik = QWidget()
        icerik_duzen = QVBoxLayout()
        icerik_duzen.setSpacing(15)
        icerik_duzen.setContentsMargins(30, 20, 30, 20)
        
        # Form alanları için stil
        form_stili = """
            QLineEdit {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px 15px;
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit:hover {
                background: rgba(255, 255, 255, 0.07);
                border: 2px solid rgba(74, 144, 226, 0.3);
            }
            QLineEdit:focus {
                background: rgba(74, 144, 226, 0.1);
                border: 2px solid #4A90E2;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
            }
            QLabel {
                color: #4A90E2;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 500;
            }
        """
        icerik.setStyleSheet(form_stili)

        # Form alanları
        for label_text, placeholder in [
            ("Başlık", "Örn: Gmail, Twitter, Netflix..."),
            ("Şifre", "Güçlü bir şifre girin"),
            ("Website (opsiyonel)", "Örn: www.gmail.com"),
            ("Açıklama (opsiyonel)", "Bu şifre hakkında not ekleyin")
        ]:
            label = QLabel(label_text)
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setMinimumHeight(45)
            
            if label_text == "Şifre":
                # Şifre alanı için özel container
                sifre_container = QHBoxLayout()
                self.sifre = input_field
                self.sifre.setEchoMode(QLineEdit.Password)
                self.sifre.textChanged.connect(self.sifre_analizi_guncelle)
                
                # Göster/Gizle butonu
                goster_gizle = QPushButton("👁️")
                goster_gizle.setFixedSize(45, 45)
                goster_gizle.setCursor(Qt.PointingHandCursor)
                goster_gizle.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 255, 255, 0.05);
                        border: none;
                        border-radius: 10px;
                        color: white;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.1);
                    }
                """)
                
                def toggle_sifre_goster():
                    if self.sifre.echoMode() == QLineEdit.Password:
                        self.sifre.setEchoMode(QLineEdit.Normal)
                        goster_gizle.setText("🔒")
                    else:
                        self.sifre.setEchoMode(QLineEdit.Password)
                        goster_gizle.setText("👁️")
                
                goster_gizle.clicked.connect(toggle_sifre_goster)
                
                # Rastgele şifre butonu
                rastgele = QPushButton("🎲")
                rastgele.setFixedSize(45, 45)
                rastgele.setCursor(Qt.PointingHandCursor)
                rastgele.setToolTip("Rastgele güçlü şifre üret")
                rastgele.setStyleSheet(goster_gizle.styleSheet())
                rastgele.clicked.connect(lambda: self.sifre.setText(
                    self.ana_pencere.yonetici.guvenli_sifre_olustur()
                ))
                
                sifre_container.addWidget(self.sifre)
                sifre_container.addWidget(goster_gizle)
                sifre_container.addWidget(rastgele)
                
                icerik_duzen.addWidget(label)
                icerik_duzen.addLayout(sifre_container)
                
                # Şifre analizi container'ı
                self.analiz_container = QWidget()
                self.analiz_container.hide()
                self.analiz_container.setStyleSheet("""
                    QWidget {
                        background: rgba(255, 255, 255, 0.03);
                        border-radius: 12px;
                        padding: 15px;
                        margin-top: 5px;
                    }
                """)
                
                analiz_duzen = QVBoxLayout()
                analiz_duzen.setSpacing(10)
                
                self.guc_label = QLabel()
                self.progress = QProgressBar()
                self.progress.setTextVisible(False)
                self.progress.setFixedHeight(6)
                self.bilgi_label = QLabel()
                
                self.bilgi_label.setStyleSheet("""
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 13px;
                    line-height: 1.4;
                """)
                self.bilgi_label.setWordWrap(True)
                
                analiz_duzen.addWidget(self.guc_label)
                analiz_duzen.addWidget(self.progress)
                analiz_duzen.addWidget(self.bilgi_label)
                
                self.analiz_container.setLayout(analiz_duzen)
                icerik_duzen.addWidget(self.analiz_container)
                
            else:
                icerik_duzen.addWidget(label)
                icerik_duzen.addWidget(input_field)
                if label_text == "Başlık":
                    self.baslik = input_field
                elif label_text == "Website (opsiyonel)":
                    self.website = input_field
                elif label_text == "Açıklama (opsiyonel)":
                    self.aciklama = input_field

        icerik.setLayout(icerik_duzen)
        duzen.addWidget(icerik)

        # Alt buton alanı
        buton_container = QWidget()
        buton_container.setStyleSheet("""
            QWidget {
                background: rgba(74, 144, 226, 0.1);
                border-bottom-left-radius: 18px;
                border-bottom-right-radius: 18px;
            }
        """)
        
        buton_duzen = QHBoxLayout()
        buton_duzen.setContentsMargins(20, 15, 20, 15)
        buton_duzen.setSpacing(15)
        
        iptal = QPushButton("İptal")
        iptal.setMinimumHeight(45)
        iptal.clicked.connect(self.reject)
        iptal.setCursor(Qt.PointingHandCursor)
        iptal.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: 500;
                padding: 12px 24px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        kaydet = QPushButton("Kaydet")
        kaydet.setMinimumHeight(45)
        kaydet.clicked.connect(self.kaydet)
        kaydet.setCursor(Qt.PointingHandCursor)
        kaydet.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A90E2, stop:1 #357ABD);
                border: none;
                border-radius: 12px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #357ABD, stop:1 #2868B0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2868B0, stop:1 #1E4F8C);
            }
        """)
        
        buton_duzen.addWidget(iptal)
        buton_duzen.addWidget(kaydet)
        buton_container.setLayout(buton_duzen)
        duzen.addWidget(buton_container)
        
        self.setLayout(duzen)

        # Eğer düzenleme modundaysa, mevcut bilgileri doldur
        if self.sifre_bilgisi:
            self.baslik.setText(self.sifre_bilgisi[1])
            self.sifre.setText(self.sifre_bilgisi[2])
            self.website.setText(self.sifre_bilgisi[3])
            self.aciklama.setText(self.sifre_bilgisi[4])

    def sifre_analizi_guncelle(self):
        """Şifre değiştiğinde güvenlik analizini güncelle"""
        sifre = self.sifre.text()
        
        if not sifre:
            self.analiz_container.hide()
            return
        else:
            self.analiz_container.show()
        
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre)
        
        # Renk ve değerleri ayarla
        guc_renk = {
            "Zayıf": "#E74C3C",
            "Orta": "#F1C40F",
            "Güçlü": "#2ECC71"
        }
        
        guc_ikon = {
            "Zayıf": "🔓",
            "Orta": "🔐",
            "Güçlü": "🛡️"
        }
        
        # Progress bar güncelle
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {guc_renk[guc]};
                border-radius: 3px;
            }}
        """)
        
        if guc == "Zayıf":
            self.progress.setValue(33)
        elif guc == "Orta":
            self.progress.setValue(66)
        else:
            self.progress.setValue(100)
        
        # Etiketleri güncelle
        self.guc_label.setText(f"{guc_ikon[guc]} Güvenlik: {guc}")
        self.guc_label.setStyleSheet(f"""
            color: {guc_renk[guc]};
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: bold;
        """)
        
        if guc == "Güçlü":
            self.bilgi_label.setText("✓ Bu şifre güvenlik standartlarını karşılıyor.")
            self.bilgi_label.setStyleSheet("""
                color: #2ECC71;
                font-family: 'Segoe UI';
                font-size: 13px;
                line-height: 1.4;
            """)
        else:
            self.bilgi_label.setText("Öneriler:\n• " + "\n• ".join(geri_bildirim))
            self.bilgi_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                font-family: 'Segoe UI';
                font-size: 13px;
                line-height: 1.4;
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'oldPos'):
            del self.oldPos

    def kaydet(self):
        """Şifreyi kaydet veya güncelle"""
        if not self.baslik.text() or not self.sifre.text():
            QMessageBox.warning(
                self, 
                "Hata", 
                "Başlık ve şifre alanları zorunludur!",
                QMessageBox.Ok,
                QMessageBox.Ok
            )
            return
            
        guc, _ = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(self.sifre.text())
        if guc == "Zayıf":
            # Zayıf şifre uyarı kutusu
            uyari = QMessageBox(self)
            uyari.setWindowTitle("Zayıf Şifre")
            uyari.setText("Bu şifre zayıf olarak değerlendirildi.")
            uyari.setInformativeText("Yine de kaydetmek istiyor musunuz?")
            uyari.setIcon(QMessageBox.Warning)
            uyari.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            uyari.setDefaultButton(QMessageBox.No)
            
            # Butonları özelleştir
            evet_buton = uyari.button(QMessageBox.Yes)
            evet_buton.setText("Evet, Devam Et")
            evet_buton.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #E74C3C, stop:1 #C0392B);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #C0392B, stop:1 #A93226);
                }
            """)

            hayir_buton = uyari.button(QMessageBox.No)
            hayir_buton.setText("Şifreyi Güçlendir")
            hayir_buton.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4A90E2, stop:1 #357ABD);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #357ABD, stop:1 #2868B0);
                }
            """)

            uyari.setStyleSheet("""
                QMessageBox {
                    background-color: #1E1E2E;
                    border: 2px solid #E74C3C;
                    border-radius: 15px;
                }
                QMessageBox QLabel {
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    padding: 20px;
                }
            """)
            
            if uyari.exec_() == QMessageBox.No:
                return

        if self.sifre_bilgisi:  # Düzenleme modu
            basarili = self.ana_pencere.yonetici.sifre_guncelle(
                self.sifre_bilgisi[0],
                self.baslik.text(),
                self.sifre.text(),
                self.website.text(),
                self.aciklama.text()
            )
        else:  # Yeni şifre ekleme
            basarili = self.ana_pencere.yonetici.sifre_ekle(
                self.baslik.text(),
                self.sifre.text(),
                self.website.text(),
                self.aciklama.text()
            )
            
        if basarili:
            self.accept()
        else:
            # Hata mesaj kutusu
            hata = QMessageBox(self)
            hata.setWindowTitle("Hata")
            hata.setText("Şifre kaydedilemedi!")
            hata.setIcon(QMessageBox.Critical)
            hata.setStandardButtons(QMessageBox.Ok)
            
            hata.setStyleSheet("""
                QMessageBox {
                    background-color: #1E1E2E;
                    border: 2px solid #E74C3C;
                    border-radius: 15px;
                }
                QMessageBox QLabel {
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #E74C3C, stop:1 #C0392B);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #C0392B, stop:1 #A93226);
                }
            """)
            
            hata.exec_()

def main():
    app = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
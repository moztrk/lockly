from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QStackedWidget, QMessageBox, QDialog, QScrollArea, 
                           QProgressBar, QDesktopWidget, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtGui import QColor, QIcon, QFont, QPainter, QPalette
import sys
from datetime import datetime
from veritabani import VeritabaniYoneticisi
from main import SifreYoneticisi
import random
import re

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
        
        # Şifremi Unuttum butonu
        sifremi_unuttum = QPushButton("Şifremi Unuttum")
        sifremi_unuttum.setCursor(Qt.PointingHandCursor)
        sifremi_unuttum.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #4A90E2;
                font-size: 13px;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #357ABD;
            }
        """)
        sifremi_unuttum.clicked.connect(self.sifremi_unuttum_dialog)
        
        # Butonları düzene ekle
        buton_duzen.addWidget(sifremi_unuttum)
        
    def sifremi_unuttum_dialog(self):
        dialog = SifreSifirlama(self.ana_pencere)
        dialog.exec_()

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

    def sifre_gucunu_goster(self):
        """Şifre gücünü değerlendir ve göster"""
        sifre = self.sifre.text()
        if not sifre:
            self.guc_etiketi.clear()
            return
            
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre)
        
        if guc == "Güçlü":
            renk = "#2ECC71"  # Yeşil
        elif guc == "Orta":
            renk = "#F1C40F"  # Sarı
        else:
            renk = "#E74C3C"  # Kırmızı
            
        self.guc_etiketi.setStyleSheet(f"color: {renk};")
        self.guc_etiketi.setText(f"Şifre Gücü: {guc}\n" + "\n".join(geri_bildirim))

    def init_ui(self):
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(50, 50, 50, 50)
        
        # Logo ve başlık
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(100, 100))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        duzen.addWidget(logo_label)
        
        baslik = QLabel("Yeni Hesap Oluştur")
        baslik.setFont(QFont('Segoe UI', 28, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #FFFFFF;")
        duzen.addWidget(baslik)
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 35, 0.95);
                border-radius: 15px;
                padding: 20px;
            }
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
                border: 1px solid #4A90E2;
                background-color: rgba(255, 255, 255, 0.08);
            }
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
            QLabel {
                color: white;
                font-family: 'Segoe UI';
            }
        """)
        form_duzen = QVBoxLayout(form_container)
        form_duzen.setSpacing(15)
        
        # Form alanları
        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")
        self.kullanici_adi.setMinimumHeight(45)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("E-posta")
        self.email.setMinimumHeight(45)
        
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setMinimumHeight(45)
        self.sifre.textChanged.connect(self.sifre_gucunu_goster)
        
        self.sifre_tekrar = QLineEdit()
        self.sifre_tekrar.setPlaceholderText("Şifre Tekrar")
        self.sifre_tekrar.setEchoMode(QLineEdit.Password)
        self.sifre_tekrar.setMinimumHeight(45)
        
        self.guc_etiketi = QLabel()
        self.guc_etiketi.setAlignment(Qt.AlignCenter)
        
        form_duzen.addWidget(self.kullanici_adi)
        form_duzen.addWidget(self.email)
        form_duzen.addWidget(self.sifre)
        form_duzen.addWidget(self.sifre_tekrar)
        form_duzen.addWidget(self.guc_etiketi)
        
        # Butonlar
        buton_duzen = QHBoxLayout()
        
        self.geri_butonu = QPushButton("Geri")
        self.geri_butonu.setMinimumHeight(45)
        self.geri_butonu.clicked.connect(lambda: self.ana_pencere.stacked_widget.setCurrentIndex(0))
        
        self.kayit_butonu = QPushButton("Kayıt Ol")
        self.kayit_butonu.setMinimumHeight(45)
        self.kayit_butonu.clicked.connect(self.kayit_ol)
        
        buton_duzen.addWidget(self.geri_butonu)
        buton_duzen.addWidget(self.kayit_butonu)
        
        form_duzen.addLayout(buton_duzen)
        duzen.addWidget(form_container)
        
        self.setLayout(duzen)

    def kayit_ol(self):
        kullanici_adi = self.kullanici_adi.text().strip()
        email = self.email.text().strip()
        sifre = self.sifre.text()
        sifre_tekrar = self.sifre_tekrar.text()
        
        # Boş alan kontrolü
        if not kullanici_adi or not email or not sifre or not sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return
            
        # E-posta format kontrolü
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir e-posta adresi girin!")
            return
            
        # Şifre eşleşme kontrolü
        if sifre != sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return
            
        # Kullanıcı adı ve e-posta kontrolü
        try:
            self.ana_pencere.yonetici.vt.imlec.execute("""
                SELECT kullanici_adi, email FROM kullanicilar 
                WHERE kullanici_adi = %s OR email = %s
            """, (kullanici_adi, email))
            
            mevcut = self.ana_pencere.yonetici.vt.imlec.fetchone()
            if mevcut:
                if mevcut[0] == kullanici_adi:
                    QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten kayıtlı!")
                else:
                    QMessageBox.warning(self, "Hata", "Bu e-posta adresi zaten kayıtlı!")
                return
        except Exception as e:
            print(f"Kullanıcı kontrolü hatası: {e}")
            return
            
        # Kayıt işlemi
        if self.ana_pencere.yonetici.kullanici_kayit(kullanici_adi, sifre, email):
            QMessageBox.information(self, "Başarılı", "Kayıt başarıyla tamamlandı!")
            self.ana_pencere.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Hata", "Kayıt başarısız!")

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lockly - Güvenli Şifre Yöneticisi")
        self.setMinimumSize(1000, 600)
        
        # Pencereyi merkeze al
        ekran = QDesktopWidget().screenGeometry()
        pencere = self.geometry()
        x = (ekran.width() - pencere.width()) // 2
        y = (ekran.height() - pencere.height()) // 2
        self.move(x, y)
        
        # Şifre yöneticisi
        self.yonetici = SifreYoneticisi()
        
        # Stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Giriş ekranı
        self.giris_ekrani = GirisPenceresi(self)
        self.stacked_widget.addWidget(self.giris_ekrani)
        
        # Kayıt ekranı
        self.kayit_ekrani = KayitPenceresi(self)
        self.stacked_widget.addWidget(self.kayit_ekrani)
        
        # Ana ekran
        self.ana_ekran = AnaEkran(self)
        self.stacked_widget.addWidget(self.ana_ekran)
        
        # Başlangıçta giriş ekranını göster
        self.stacked_widget.setCurrentIndex(0)
        
    def ana_ekrani_goster(self):
        """Ana ekranı göster ve güncelle"""
        self.ana_ekran.sifreleri_yukle()  # Şifreleri yeniden yükle
        self.stacked_widget.setCurrentIndex(2)  # Ana ekranı göster
        
    def closeEvent(self, event):
        """Uygulama kapatılırken veritabanı bağlantısını kapat"""
        self.yonetici.kapat()
        event.accept()

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
        kopyala.clicked.connect(lambda: self.sifre_kopyala(sifre[2]))
        
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
        sil.clicked.connect(lambda: self.sifre_sil(sifre[0]))
        
        # Butonları ekle
        for buton in [goster_buton, kopyala, duzenle, sil]:
            buton_grubu.addWidget(buton)
        
        ust_kisim.addStretch()
        ust_kisim.addLayout(buton_grubu)
        
        duzen.addLayout(ust_kisim)
        duzen.addWidget(sifre_alani)
        
        # Güvenlik seviyesi göstergesi
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre[2])
        
        # Progress bar
        progress = QProgressBar()
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        
        if guc == "Güçlü":
            deger = 100
            renk = "#2ECC71"
        elif guc == "Orta":
            deger = 66
            renk = "#F1C40F"
        else:
            deger = 33
            renk = "#E74C3C"
        
        progress.setValue(deger)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {renk};
                border-radius: 3px;
            }}
        """)
        
        guc_label = QLabel(f"Güvenlik: {guc}")
        guc_label.setStyleSheet(f"""
            color: {renk};
            font-family: 'Segoe UI';
            font-size: 12px;
        """)
        
        guc_duzen = QHBoxLayout()
        guc_duzen.addWidget(progress)
        guc_duzen.addWidget(guc_label)
        
        duzen.addLayout(guc_duzen)
        
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

    def sifreyi_goster_gizle(self, kart, sifre):
        """Şifreyi göster/gizle"""
        sifre_label = kart.findChild(QLabel, "", options=Qt.FindChildrenRecursively)
        for label in kart.findChildren(QLabel):
            if label.text().startswith("Şifre:"):
                if label.property("gizli"):
                    label.setText(f"Şifre: {sifre}")
                    label.setProperty("gizli", False)
                else:
                    label.setText(f"Şifre: {'•' * len(sifre)}")
                    label.setProperty("gizli", True)
                break

    def sifre_kopyala(self, sifre):
        """Şifreyi panoya kopyala"""
        QApplication.clipboard().setText(sifre)
        QMessageBox.information(self, "Başarılı", "Şifre panoya kopyalandı!")
        
    def sifre_duzenle(self, sifre_id):
        """Şifre düzenleme dialogunu göster"""
        dialog = SifreEkleDuzenleDialog(self.ana_pencere, sifre_id)
        if dialog.exec_() == QDialog.Accepted:
            self.sifreleri_yukle()
            
    def sifre_sil(self, sifre_id):
        """Şifreyi sil"""
        cevap = QMessageBox.question(
            self,
            "Onay",
            "Bu şifreyi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if cevap == QMessageBox.Yes:
            if self.ana_pencere.yonetici.sifre_sil(sifre_id):
                self.sifreleri_yukle()
                QMessageBox.information(self, "Başarılı", "Şifre başarıyla silindi!")
            else:
                QMessageBox.warning(self, "Hata", "Şifre silinemedi!")

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
        yeni_sifre.clicked.connect(self.sifre_ekle)
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
        """)
        
        yenile = QPushButton()
        yenile.setIcon(QIcon("assets/refresh_icon.png"))
        yenile.setIconSize(QSize(20, 20))
        yenile.setText("Yenile")
        yenile.clicked.connect(self.sifreleri_yukle)
        yenile.setCursor(Qt.PointingHandCursor)
        yenile.setStyleSheet(yeni_sifre.styleSheet().replace("#4CAF50", "#4A90E2")
                           .replace("#45a049", "#357ABD"))
        
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
        
    def sifre_ekle(self):
        dialog = SifreEkleDuzenleDialog(self.ana_pencere)
        if dialog.exec_() == QDialog.Accepted:
            self.sifreleri_yukle()
            
    def cikis_yap(self):
        self.yenileme_timer.stop()
        self.ana_pencere.yonetici.kullanici_cikis()
        self.ana_pencere.stacked_widget.setCurrentIndex(0)
        
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
            "Zayıf": "��",
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
            self.bilgi_label.setText("Öneriler:\n" + "\n• ".join(geri_bildirim))
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

    def yeni_sifre_form(self):
        """Yeni şifre belirleme formunu göster"""
        # Mevcut widgetları temizle
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.layout())
            
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(30, 30, 30, 30)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(64, 64))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        duzen.addWidget(logo_label)
        
        baslik = QLabel("Yeni Şifre Belirle")
        baslik.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 20px 0;
        """)
        baslik.setAlignment(Qt.AlignCenter)
        duzen.addWidget(baslik)
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                padding: 20px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-size: 14px;
                min-height: 45px;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLabel {
                color: white;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """)
        form_duzen = QVBoxLayout(form_container)
        form_duzen.setSpacing(15)
        
        # Şifre alanları
        self.yeni_sifre = QLineEdit()
        self.yeni_sifre.setPlaceholderText("Yeni şifrenizi girin")
        self.yeni_sifre.setEchoMode(QLineEdit.Password)
        
        self.yeni_sifre_tekrar = QLineEdit()
        self.yeni_sifre_tekrar.setPlaceholderText("Yeni şifrenizi tekrar girin")
        self.yeni_sifre_tekrar.setEchoMode(QLineEdit.Password)
        
        form_duzen.addWidget(QLabel("Yeni Şifre"))
        form_duzen.addWidget(self.yeni_sifre)
        form_duzen.addWidget(QLabel("Şifre Tekrar"))
        form_duzen.addWidget(self.yeni_sifre_tekrar)
        
        duzen.addWidget(form_container)
        
        # Güncelle butonu
        guncelle_buton = QPushButton("Şifreyi Güncelle")
        guncelle_buton.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                padding: 12px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        guncelle_buton.clicked.connect(self.sifreyi_guncelle)
        duzen.addWidget(guncelle_buton)
        
        self.setLayout(duzen)
        
    def sifreyi_guncelle(self):
        """Yeni şifreyi kontrol et ve güncelle"""
        yeni_sifre = self.yeni_sifre.text()
        yeni_sifre_tekrar = self.yeni_sifre_tekrar.text()
        
        # Şifre kontrolü
        if not yeni_sifre or not yeni_sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return
            
        if yeni_sifre != yeni_sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return
            
        # Şifre gücü kontrolü
        guc, _ = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(yeni_sifre)
        if guc == "Zayıf":
            QMessageBox.warning(self, "Hata", "Lütfen daha güçlü bir şifre seçin!")
            return
            
        try:
            # Kullanıcı ID'sini bul
            self.ana_pencere.yonetici.vt.imlec.execute("""
                SELECT id FROM kullanicilar WHERE email = %s
            """, (self.email,))
            
            kullanici = self.ana_pencere.yonetici.vt.imlec.fetchone()
            if not kullanici:
                QMessageBox.warning(self, "Hata", "Kullanıcı bulunamadı!")
                return
                
            # Şifreyi güncelle
            if self.ana_pencere.yonetici.sifre_sifirla(kullanici[0], yeni_sifre):
                QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla güncellendi!")
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", "Şifre güncellenemedi!")
                
        except Exception as e:
            print(f"Şifre güncelleme hatası: {e}")
            QMessageBox.warning(self, "Hata", "Bir hata oluştu!")

class SifreSifirlama(QDialog):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.setWindowTitle("Şifremi Unuttum")
        self.setFixedWidth(500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
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
        
        baslik = QLabel("Şifremi Unuttum")
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

        # Ana içerik
        icerik = QWidget()
        icerik_duzen = QVBoxLayout()
        icerik_duzen.setSpacing(15)
        icerik_duzen.setContentsMargins(30, 20, 30, 20)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(64, 64))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        icerik_duzen.addWidget(logo_label)
        
        # Açıklama
        aciklama = QLabel("Hesabınıza kayıtlı e-posta adresine\ndoğrulama kodu göndereceğiz.")
        aciklama.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-family: 'Segoe UI';
            font-size: 14px;
        """)
        aciklama.setAlignment(Qt.AlignCenter)
        icerik_duzen.addWidget(aciklama)
        
        # Input stil tanımı
        input_stili = """
            QLineEdit {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px 15px;
                color: white;
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
        """
        
        # Kullanıcı adı alanı
        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")
        self.kullanici_adi.setMinimumHeight(45)
        self.kullanici_adi.setStyleSheet(input_stili)
        icerik_duzen.addWidget(self.kullanici_adi)
        
        icerik.setLayout(icerik_duzen)
        duzen.addWidget(icerik)

        # Alt butonlar
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
        
        gonder = QPushButton("Kod Gönder")
        gonder.setMinimumHeight(45)
        gonder.clicked.connect(self.kod_gonder)
        gonder.setCursor(Qt.PointingHandCursor)
        gonder.setStyleSheet("""
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
        """)
        
        buton_duzen.addWidget(iptal)
        buton_duzen.addWidget(gonder)
        buton_container.setLayout(buton_duzen)
        duzen.addWidget(buton_container)
        
        self.setLayout(duzen)

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

    def kod_gonder(self):
        """Kullanıcı adına ait e-posta adresine doğrulama kodu gönder"""
        kullanici_adi = self.kullanici_adi.text()
        
        if not kullanici_adi:
            QMessageBox.warning(self, "Hata", "Lütfen kullanıcı adınızı girin!")
            return
            
        # Veritabanından e-posta adresini al
        email = self.ana_pencere.yonetici.kullanici_eposta_getir(kullanici_adi)
        
        if not email:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adına ait hesap bulunamadı!")
            return
            
        try:
            # Doğrulama kodunu oluştur ve gönder
            kod = self.ana_pencere.yonetici.dogrulama_kodu_olustur(kullanici_adi)
            self.ana_pencere.yonetici.dogrulama_kodu_gonder(email, kod)
            
            # Doğrulama ekranını aç
            dogrulama = KodDogrulama(self.ana_pencere, email, kullanici_adi)  # kod parametresini kaldırdık
            self.accept()
            if dogrulama.exec_() == QDialog.Accepted:
                # Şifre sıfırlama formunu göster
                sifirla = YeniSifreBelirle(self.ana_pencere, kullanici_adi)
                sifirla.exec_()
                
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Doğrulama kodu gönderilemedi!\nHata: {str(e)}")

class KodDogrulama(QDialog):
    def __init__(self, ana_pencere, email, kullanici_adi):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.email = email
        self.kullanici_adi = kullanici_adi
        self.setWindowTitle("Doğrulama Kodu")
        self.setFixedWidth(500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
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
        
        baslik = QLabel("Doğrulama Kodu")
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

        # Ana içerik
        icerik = QWidget()
        icerik_duzen = QVBoxLayout()
        icerik_duzen.setSpacing(15)
        icerik_duzen.setContentsMargins(30, 20, 30, 20)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(64, 64))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        icerik_duzen.addWidget(logo_label)
        
        # Açıklama
        aciklama = QLabel(f"E-posta adresinize ({self.email}) gönderilen\n6 haneli doğrulama kodunu girin.")
        aciklama.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-family: 'Segoe UI';
            font-size: 14px;
        """)
        aciklama.setAlignment(Qt.AlignCenter)
        icerik_duzen.addWidget(aciklama)
        
        # Kod giriş alanı
        self.kod_input = QLineEdit()
        self.kod_input.setPlaceholderText("Doğrulama Kodu")
        self.kod_input.setMaxLength(6)
        self.kod_input.setMinimumHeight(45)
        self.kod_input.setAlignment(Qt.AlignCenter)
        self.kod_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px 15px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 18px;
                letter-spacing: 5px;
            }
            QLineEdit:hover {
                background: rgba(255, 255, 255, 0.07);
                border: 2px solid rgba(74, 144, 226, 0.3);
            }
            QLineEdit:focus {
                background: rgba(74, 144, 226, 0.1);
                border: 2px solid #4A90E2;
            }
        """)
        icerik_duzen.addWidget(self.kod_input)
        
        # Yeni kod gönder linki
        yeni_kod = QPushButton("Yeni kod gönder")
        yeni_kod.setCursor(Qt.PointingHandCursor)
        yeni_kod.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #4A90E2;
                font-family: 'Segoe UI';
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #357ABD;
            }
        """)
        icerik_duzen.addWidget(yeni_kod, alignment=Qt.AlignCenter)
        
        icerik.setLayout(icerik_duzen)
        duzen.addWidget(icerik)

        # Alt butonlar
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
        
        dogrula = QPushButton("Doğrula")
        dogrula.setMinimumHeight(45)
        dogrula.clicked.connect(self.kodu_dogrula)
        dogrula.setCursor(Qt.PointingHandCursor)
        dogrula.setStyleSheet("""
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
        """)
        
        buton_duzen.addWidget(iptal)
        buton_duzen.addWidget(dogrula)
        buton_container.setLayout(buton_duzen)
        duzen.addWidget(buton_container)
        
        self.setLayout(duzen)

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

    def kodu_dogrula(self):
        """Girilen kodu doğrula"""
        kod = self.kod_input.text()
        if len(kod) != 6:
            QMessageBox.warning(self, "Hata", "Lütfen 6 haneli kodu eksiksiz girin!")
            return
            
        if self.ana_pencere.yonetici.dogrulama_kodu_kontrol_et(self.kullanici_adi, kod):
            self.accept()  # Kod doğruysa pencereyi kapat
        else:
            QMessageBox.warning(self, "Hata", "Doğrulama kodu hatalı veya süresi dolmuş!")

class YeniSifreBelirle(QDialog):
    def __init__(self, ana_pencere, kullanici_adi):  # email yerine kullanici_adi alıyoruz
        super().__init__()
        self.ana_pencere = ana_pencere
        self.kullanici_adi = kullanici_adi  # kullanici_adi'nı saklıyoruz
        self.setWindowTitle("Yeni Şifre Belirle")
        self.setFixedWidth(500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
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
        
        baslik = QLabel("Yeni Şifre Belirle")
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

        # Ana içerik
        icerik = QWidget()
        icerik_duzen = QVBoxLayout()
        icerik_duzen.setSpacing(15)
        icerik_duzen.setContentsMargins(30, 20, 30, 20)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(64, 64))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        icerik_duzen.addWidget(logo_label)
        
        # Açıklama
        aciklama = QLabel("Hesabınız için yeni bir şifre belirleyin.")
        aciklama.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-family: 'Segoe UI';
            font-size: 14px;
        """)
        aciklama.setAlignment(Qt.AlignCenter)
        icerik_duzen.addWidget(aciklama)
        
        # Şifre alanları
        self.yeni_sifre = QLineEdit()
        self.yeni_sifre.setPlaceholderText("Yeni Şifre")
        self.yeni_sifre.setEchoMode(QLineEdit.Password)
        self.yeni_sifre.setMinimumHeight(45)
        self.yeni_sifre.textChanged.connect(self.sifre_gucunu_goster)
        
        self.sifre_tekrar = QLineEdit()
        self.sifre_tekrar.setPlaceholderText("Yeni Şifre (Tekrar)")
        self.sifre_tekrar.setEchoMode(QLineEdit.Password)
        self.sifre_tekrar.setMinimumHeight(45)
        
        input_stili = """
            QLineEdit {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px 15px;
                color: white;
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
        """
        
        self.yeni_sifre.setStyleSheet(input_stili)
        self.sifre_tekrar.setStyleSheet(input_stili)
        
        icerik_duzen.addWidget(self.yeni_sifre)
        icerik_duzen.addWidget(self.sifre_tekrar)
        
        # Şifre gücü göstergesi
        self.guc_container = QWidget()
        self.guc_container.hide()
        self.guc_container.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        guc_duzen = QVBoxLayout()
        guc_duzen.setSpacing(10)
        
        self.guc_label = QLabel()
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.bilgi_label = QLabel()
        self.bilgi_label.setWordWrap(True)
        
        guc_duzen.addWidget(self.guc_label)
        guc_duzen.addWidget(self.progress)
        guc_duzen.addWidget(self.bilgi_label)
        
        self.guc_container.setLayout(guc_duzen)
        icerik_duzen.addWidget(self.guc_container)
        
        icerik.setLayout(icerik_duzen)
        duzen.addWidget(icerik)

        # Alt butonlar
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
        
        kaydet = QPushButton("Şifreyi Kaydet")
        kaydet.setMinimumHeight(45)
        kaydet.clicked.connect(self.sifreyi_kaydet)
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
        """)
        
        buton_duzen.addWidget(iptal)
        buton_duzen.addWidget(kaydet)
        buton_container.setLayout(buton_duzen)
        duzen.addWidget(buton_container)
        
        self.setLayout(duzen)

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

    def sifre_gucunu_goster(self):
        """Şifre değiştiğinde güvenlik analizini güncelle"""
        sifre = self.yeni_sifre.text()
        
        if not sifre:
            self.guc_container.hide()
            return
        else:
            self.guc_container.show()
        
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre)
        
        # Renk ve değerleri ayarla
        guc_renk = {
            "Zayıf": "#E74C3C",
            "Orta": "#F1C40F",
            "Güçlü": "#2ECC71"
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
        self.guc_label.setText(f"Şifre Gücü: {guc}")
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
            """)
        else:
            self.bilgi_label.setText("Öneriler:\n• " + "\n• ".join(geri_bildirim))
            self.bilgi_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                font-family: 'Segoe UI';
                font-size: 13px;
            """)

    def sifreyi_kaydet(self):
        """Yeni şifreyi kaydet"""
        if self.yeni_sifre.text() != self.sifre_tekrar.text():
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return
            
        guc, _ = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(self.yeni_sifre.text())
        if guc == "Zayıf":
            cevap = QMessageBox.question(
                self,
                "Zayıf Şifre",
                "Bu şifre zayıf olarak değerlendirildi. Yine de kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if cevap == QMessageBox.No:
                return
        
        try:
            # Şifreyi güncelle
            if self.ana_pencere.yonetici.kullanici_sifre_guncelle(self.kullanici_adi, self.yeni_sifre.text()):
                QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla güncellendi!")
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", "Şifre güncellenemedi!")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Şifre güncellenirken bir hata oluştu: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Uygulama ikonu ayarla
    app.setWindowIcon(QIcon("assets/logo.png"))
    
    # Uygulama stili
    app.setStyle("Fusion")
    
    # Koyu tema
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 27, 40))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 25))
    palette.setColor(QPalette.AlternateBase, QColor(27, 28, 40))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(27, 28, 40))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
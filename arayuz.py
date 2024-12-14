from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QStackedWidget, QMessageBox, QTableWidget, 
                           QTableWidgetItem, QDialog, QSpinBox, QInputDialog, QMenu, QScrollArea, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont
import sys
from datetime import datetime
from veritabani import VeritabaniYoneticisi
from main import SifreYoneticisi

class GirisPenceresi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()

    def init_ui(self):
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(50, 50, 50, 50)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(150, 150))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        duzen.addWidget(logo_label)
        
        # Başlık
        baslik = QLabel("Lockly")
        baslik.setFont(QFont('Segoe UI', 36, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        duzen.addWidget(baslik)
        
        alt_baslik = QLabel("Güvenli Şifre Yöneticisi")
        alt_baslik.setFont(QFont('Segoe UI', 14))
        alt_baslik.setAlignment(Qt.AlignCenter)
        duzen.addWidget(alt_baslik)
        
        duzen.addSpacing(30)
        
        # Giriş formu
        form_duzen = QVBoxLayout()
        form_duzen.setSpacing(15)
        
        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")
        self.kullanici_adi.setMinimumHeight(40)
        
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setMinimumHeight(40)
        
        form_duzen.addWidget(self.kullanici_adi)
        form_duzen.addWidget(self.sifre)
        
        # Butonlar
        buton_duzen = QHBoxLayout()
        buton_duzen.setSpacing(15)
        
        giris_butonu = QPushButton("Giriş Yap")
        giris_butonu.setMinimumHeight(40)
        giris_butonu.clicked.connect(self.giris_yap)
        giris_butonu.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
            }
            QPushButton:hover {
                background-color: #219A52;
            }
        """)
        
        kayit_butonu = QPushButton("Kayıt Ol")
        kayit_butonu.setMinimumHeight(40)
        kayit_butonu.clicked.connect(self.kayit_ekranina_git)
        
        buton_duzen.addWidget(giris_butonu)
        buton_duzen.addWidget(kayit_butonu)
        
        form_duzen.addLayout(buton_duzen)
        duzen.addLayout(form_duzen)
        
        # Alt bilgi
        alt_bilgi = QLabel("© 2024 Lockly. Tüm hakları saklıdır.")
        alt_bilgi.setAlignment(Qt.AlignCenter)
        alt_bilgi.setStyleSheet("color: #7F8C8D;")
        duzen.addStretch()
        duzen.addWidget(alt_bilgi)
        
        # Hakkında butonu
        hakkinda_buton = QPushButton("Hakkında")
        hakkinda_buton.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #00FF00;
                text-decoration: underline;
                font-family: 'Consolas';
                font-size: 12px;
                min-width: 0;
                padding: 5px;
            }
            QPushButton:hover {
                color: #008800;
            }
        """)
        hakkinda_buton.setCursor(Qt.PointingHandCursor)
        hakkinda_buton.clicked.connect(self.hakkinda_goster)
        duzen.addWidget(hakkinda_buton, alignment=Qt.AlignCenter)
        
        self.setLayout(duzen)

    def giris_yap(self):
        kullanici_adi = self.kullanici_adi.text()
        sifre = self.sifre.text()
        
        if self.ana_pencere.yonetici.kullanici_giris(kullanici_adi, sifre):
            self.ana_pencere.ana_ekrani_goster()
        else:
            QMessageBox.warning(self, "Hata", "Giriş başarısız!")

    def kayit_ekranina_git(self):
        self.ana_pencere.stacked_widget.setCurrentIndex(1)

    def hakkinda_goster(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Hakkında")
        dialog.setFixedSize(500, 400)
        
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
                background-color: #1A1A1A;
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
                background-color: #1A1A1A;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1A1A1A;
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
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
        """)
        duzen.addWidget(scroll)
        
        # Kapat butonu
        kapat = QPushButton("Kapat")
        kapat.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 20px;
                border-radius: 4px;
                font-family: 'Consolas';
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """)
        kapat.clicked.connect(dialog.close)
        duzen.addWidget(kapat, alignment=Qt.AlignCenter)
        
        dialog.setLayout(duzen)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                border: 1px solid #00FF00;
            }
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 20px;
                border-radius: 4px;
                font-family: 'Consolas';
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """)
        
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
        
        # Logo ve Başlık
        logo_label = QLabel()
        logo_pixmap = QIcon("assets/lockly_logo.png").pixmap(QSize(100, 100))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        duzen.addWidget(logo_label)
        
        baslik = QLabel("Yeni Hesap Oluştur")
        baslik.setFont(QFont('Segoe UI', 24, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        duzen.addWidget(baslik)
        
        duzen.addSpacing(20)
        
        # Kayıt formu
        form_duzen = QVBoxLayout()
        form_duzen.setSpacing(15)
        
        self.kullanici_adi = QLineEdit()
        self.kullanici_adi.setPlaceholderText("Kullanıcı Adı")
        self.kullanici_adi.setMinimumHeight(40)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("E-posta")
        self.email.setMinimumHeight(40)
        
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setMinimumHeight(40)
        
        self.sifre_tekrar = QLineEdit()
        self.sifre_tekrar.setPlaceholderText("Şifre Tekrar")
        self.sifre_tekrar.setEchoMode(QLineEdit.Password)
        self.sifre_tekrar.setMinimumHeight(40)
        
        form_duzen.addWidget(self.kullanici_adi)
        form_duzen.addWidget(self.email)
        form_duzen.addWidget(self.sifre)
        form_duzen.addWidget(self.sifre_tekrar)
        
        # Şifre gücü göstergesi
        self.guc_etiketi = QLabel()
        self.guc_etiketi.setAlignment(Qt.AlignCenter)
        self.guc_etiketi.setStyleSheet("font-size: 16px;")
        form_duzen.addWidget(self.guc_etiketi)
        
        self.sifre.textChanged.connect(self.sifre_gucunu_goster)
        
        # Butonlar
        buton_duzen = QHBoxLayout()
        buton_duzen.setSpacing(15)
        
        kayit_butonu = QPushButton("Kayıt Ol")
        kayit_butonu.setMinimumHeight(40)
        kayit_butonu.clicked.connect(self.kayit_ol)
        kayit_butonu.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
            }
            QPushButton:hover {
                background-color: #219A52;
            }
        """)
        
        geri_butonu = QPushButton("Geri")
        geri_butonu.setMinimumHeight(40)
        geri_butonu.clicked.connect(lambda: self.ana_pencere.stacked_widget.setCurrentIndex(0))
        
        buton_duzen.addWidget(geri_butonu)
        buton_duzen.addWidget(kayit_butonu)
        
        form_duzen.addLayout(buton_duzen)
        duzen.addLayout(form_duzen)
        
        # Alt bilgi
        alt_bilgi = QLabel("© 2024 Lockly. Tüm hakları saklıdır.")
        alt_bilgi.setAlignment(Qt.AlignCenter)
        alt_bilgi.setStyleSheet("color: #7F8C8D;")
        duzen.addStretch()
        duzen.addWidget(alt_bilgi)
        
        self.setLayout(duzen)

    def sifre_gucunu_goster(self):
        sifre = self.sifre.text()
        guc, geri_bildirim = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre)
        
        renk = {
            "Zayıf": "red",
            "Orta": "orange",
            "Güçlü": "green"
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

class SifreEkleDuzenleDialog(QDialog):
    def __init__(self, ana_pencere, sifre_bilgisi=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.sifre_bilgisi = sifre_bilgisi
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Şifre " + ("Düzenle" if self.sifre_bilgisi else "Ekle"))
        self.setMinimumWidth(400)
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(30, 30, 30, 30)
        
        # Başlık
        baslik = QLabel("Şifre " + ("Düzenle" if self.sifre_bilgisi else "Ekle"))
        baslik.setFont(QFont('Segoe UI', 18, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)
        duzen.addWidget(baslik)
        
        # Form alanları
        self.baslik = QLineEdit()
        self.baslik.setPlaceholderText("Başlık")
        self.baslik.setMinimumHeight(35)
        
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setMinimumHeight(35)
        
        self.website = QLineEdit()
        self.website.setPlaceholderText("Website (opsiyonel)")
        self.website.setMinimumHeight(35)
        
        self.aciklama = QLineEdit()
        self.aciklama.setPlaceholderText("Açıklama (opsiyonel)")
        self.aciklama.setMinimumHeight(35)
        
        # Rastgele şifre oluşturma
        sifre_duzen = QHBoxLayout()
        sifre_duzen.addWidget(self.sifre)
        rastgele_buton = QPushButton("Rastgele")
        rastgele_buton.setIcon(QIcon("assets/dice_icon.png"))  # Zar ikonu ekleyin
        rastgele_buton.clicked.connect(self.rastgele_sifre_olustur)
        sifre_duzen.addWidget(rastgele_buton)
        
        # Var olan şifre bilgilerini doldur
        if self.sifre_bilgisi:
            self.baslik.setText(self.sifre_bilgisi[1])
            self.sifre.setText(self.sifre_bilgisi[2])
            self.website.setText(self.sifre_bilgisi[3])
            self.aciklama.setText(self.sifre_bilgisi[4])
        
        # Düzene ekle
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #34495E;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_duzen = QVBoxLayout()
        form_duzen.setSpacing(15)
        
        form_duzen.addWidget(self.baslik)
        form_duzen.addLayout(sifre_duzen)
        form_duzen.addWidget(self.website)
        form_duzen.addWidget(self.aciklama)
        
        form_container.setLayout(form_duzen)
        duzen.addWidget(form_container)
        
        # Butonlar
        butonlar = QHBoxLayout()
        butonlar.setSpacing(15)
        
        kaydet = QPushButton("Kaydet")
        kaydet.setMinimumHeight(35)
        kaydet.clicked.connect(self.kaydet)
        kaydet.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
            }
            QPushButton:hover {
                background-color: #219A52;
            }
        """)
        
        iptal = QPushButton("İptal")
        iptal.setMinimumHeight(35)
        iptal.clicked.connect(self.reject)
        
        butonlar.addWidget(iptal)
        butonlar.addWidget(kaydet)
        duzen.addLayout(butonlar)
        
        self.setLayout(duzen)
    
    def rastgele_sifre_olustur(self):
        sifre = self.ana_pencere.yonetici.guvenli_sifre_olustur()
        self.sifre.setText(sifre)
    
    def kaydet(self):
        baslik = self.baslik.text()
        sifre = self.sifre.text()
        website = self.website.text()
        aciklama = self.aciklama.text()
        
        if not baslik or not sifre:
            QMessageBox.warning(self, "Hata", "Başlık ve şifre zorunludur!")
            return
        
        guc, _ = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre)
        if guc == "Zayıf":
            yanit = QMessageBox.question(
                self, "Zayıf Şifre",
                "Bu şifre zayıf görünüyor. Yine de kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No
            )
            if yanit == QMessageBox.No:
                return
        
        if self.sifre_bilgisi:  # Düzenleme
            if self.ana_pencere.yonetici.sifre_guncelle(
                self.sifre_bilgisi[0], baslik, sifre, website, aciklama
            ):
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", "Şifre güncellenemedi!")
        else:  # Yeni ekleme
            if self.ana_pencere.yonetici.sifre_ekle(baslik, sifre, website, aciklama):
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", "Şifre eklenemedi!")

class AnaEkran(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()
        self.sifreleri_yukle()
    
    def init_ui(self):
        duzen = QVBoxLayout()
        duzen.setSpacing(20)
        duzen.setContentsMargins(30, 30, 30, 30)
        
        # Üst bar
        ust_bar = QWidget()
        ust_bar.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #00FF00;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        ust_duzen = QHBoxLayout()
        ust_duzen.setSpacing(15)
        
        # Sol grup (Yeni Şifre ve Yenile butonları)
        sol_butonlar = QHBoxLayout()
        
        yeni_sifre = QPushButton("Yeni Şifre")
        yeni_sifre.setIcon(QIcon("assets/add_icon.png"))
        yeni_sifre.clicked.connect(self.yeni_sifre_ekle)
        yeni_sifre.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 15px;
                font-family: 'Consolas';
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """)
        
        yenile = QPushButton("Yenile")
        yenile.setIcon(QIcon("assets/refresh_icon.png"))
        yenile.clicked.connect(self.sifreleri_yukle)
        yenile.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 15px;
                font-family: 'Consolas';
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """)
        
        sol_butonlar.addWidget(yeni_sifre)
        sol_butonlar.addWidget(yenile)
        
        # Sağ grup (Kullanıcı bilgisi ve Çıkış)
        sag_grup = QHBoxLayout()
        
        kullanici_label = QLabel(f"Hoş geldiniz, {self.ana_pencere.yonetici.mevcut_kullanici}")
        kullanici_label.setStyleSheet("""
            color: #00FF00;
            font-family: 'Consolas';
            padding-right: 10px;
        """)
        
        cikis = QPushButton("Çıkış Yap")
        cikis.setIcon(QIcon("assets/logout_icon.png"))
        cikis.clicked.connect(self.cikis_yap)
        cikis.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 15px;
                font-family: 'Consolas';
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """)
        
        sag_grup.addWidget(kullanici_label)
        sag_grup.addWidget(cikis)
        
        ust_duzen.addLayout(sol_butonlar)
        ust_duzen.addStretch()
        ust_duzen.addLayout(sag_grup)
        
        ust_bar.setLayout(ust_duzen)
        duzen.addWidget(ust_bar)
        
        # Arama çubuğu
        arama_container = QWidget()
        arama_container.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #00FF00;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        arama_duzen = QHBoxLayout()
        
        self.arama_kutusu = QLineEdit()
        self.arama_kutusu.setPlaceholderText("Şifrelerde ara...")
        self.arama_kutusu.textChanged.connect(self.sifreleri_filtrele)
        self.arama_kutusu.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #00FF00;
                border-radius: 4px;
                background-color: #333333;
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #00FF00;
                background-color: #1A1A1A;
            }
        """)
        
        arama_duzen.addWidget(self.arama_kutusu)
        arama_container.setLayout(arama_duzen)
        duzen.addWidget(arama_container)
        
        # Şifre kartları için scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1A1A1A;
                border: 1px solid #00FF00;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: 1px solid #00FF00;
                background: #1A1A1A;
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
        
        # Kartların container'ı
        self.kartlar_widget = QWidget()
        self.kartlar_duzen = QVBoxLayout()
        self.kartlar_duzen.setSpacing(10)
        self.kartlar_widget.setLayout(self.kartlar_duzen)
        
        scroll.setWidget(self.kartlar_widget)
        duzen.addWidget(scroll)
        
        self.setLayout(duzen)
    
    def sifreleri_filtrele(self):
        aranan = self.arama_kutusu.text().lower()
        for i in range(self.kartlar_duzen.count()):
            item = self.kartlar_duzen.itemAt(i)
            if item.widget():
                satir_gorunsun = False
                for j in range(item.widget().layout().count()):
                    sub_item = item.widget().layout().itemAt(j)
                    if sub_item.widget():
                        if aranan in sub_item.widget().text().lower():
                            satir_gorunsun = True
                            break
                item.widget().layout().setRowHidden(0, not satir_gorunsun)
    
    def sifreleri_yukle(self):
        # Mevcut kartları temizle
        while self.kartlar_duzen.count():
            item = self.kartlar_duzen.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
        sifreler = self.ana_pencere.yonetici.sifreleri_getir()
        
        # Şifreleri tarihe göre ters sırala (en yeni en üstte)
        sifreler.sort(key=lambda x: x[5], reverse=True)
        
        # Kartları oluştur
        for sifre in sifreler:
            # Her şifre için kart oluştur
            kart = QWidget()
            kart.setStyleSheet("""
                QWidget {
                    background-color: #1A1A1A;
                    border: 1px solid #00FF00;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
                QWidget:hover {
                    background-color: #333333;
                    border: 2px solid #00FF00;
                }
                QLabel {
                    color: #00FF00;
                    font-family: 'Consolas';
                }
            """)
            
            kart_duzen = QVBoxLayout()
            kart_duzen.setSpacing(10)
            
            # Üst kısım: Başlık ve butonlar
            ust_kisim = QHBoxLayout()
            
            # Başlık
            baslik = QLabel(sifre[1])
            baslik.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            """)
            ust_kisim.addWidget(baslik)
            
            # Butonlar
            buton_grubu = QHBoxLayout()
            buton_grubu.setSpacing(5)
            
            # Buton stili
            buton_stili = """
                QPushButton {
                    background-color: #1A1A1A;
                    border: 1px solid #00FF00;
                    color: #00FF00;
                    font-size: 16px;
                    padding: 5px;
                    border-radius: 15px;
                    min-width: 30px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #00FF00;
                    color: #000000;
                }
                QPushButton:pressed {
                    background-color: #008800;
                    color: #000000;
                }
            """
            
            # Göster/Gizle butonu
            goster_buton = QPushButton("👁️")
            goster_buton.setFixedSize(35, 35)
            goster_buton.setStyleSheet(buton_stili)
            goster_buton.setToolTip("Şifreyi Göster/Gizle")
            goster_buton.setCursor(Qt.PointingHandCursor)
            
            # Şifre alanı
            sifre_alani = QLabel("••••••••")
            sifre_alani.setStyleSheet("font-size: 14px; padding: 5px;")
            
            # Closure kullanarak doğru bağlantıyı sağla
            def make_toggle_function(label, button, password):
                def toggle():
                    if label.text() == "••••••••":
                        label.setText(password)
                        button.setText("🔒")
                    else:
                        label.setText("••••••••")
                        button.setText("👁️")
                return toggle

            toggle_func = make_toggle_function(sifre_alani, goster_buton, sifre[2])
            goster_buton.clicked.connect(toggle_func)
            
            # Kopyala butonu
            kopyala_buton = QPushButton("📋")
            kopyala_buton.setFixedSize(35, 35)
            kopyala_buton.setStyleSheet(buton_stili)
            kopyala_buton.setToolTip("Şifreyi Panoya Kopyala")
            kopyala_buton.setCursor(Qt.PointingHandCursor)
            kopyala_buton.clicked.connect(lambda: self.sifre_kopyala(sifre[2]))
            
            # Düzenle butonu
            duzenle_buton = QPushButton("✏️")
            duzenle_buton.setFixedSize(35, 35)
            duzenle_buton.setStyleSheet(buton_stili)
            duzenle_buton.setToolTip("Şifreyi Düzenle")
            duzenle_buton.setCursor(Qt.PointingHandCursor)
            duzenle_buton.clicked.connect(lambda: self.sifre_duzenle(sifre))
            
            # Paylaş butonu
            paylas_buton = QPushButton("🔗")
            paylas_buton.setFixedSize(35, 35)
            paylas_buton.setStyleSheet(buton_stili)
            paylas_buton.setToolTip("Şifreyi Paylaş")
            paylas_buton.setCursor(Qt.PointingHandCursor)
            paylas_buton.clicked.connect(lambda: self.sifre_paylas(sifre[0]))
            
            # Sil butonu
            sil_buton = QPushButton("🗑️")
            sil_buton.setFixedSize(35, 35)
            sil_buton.setStyleSheet(buton_stili)
            sil_buton.setToolTip("Şifreyi Sil")
            sil_buton.setCursor(Qt.PointingHandCursor)
            sil_buton.clicked.connect(lambda: self.sifre_sil(sifre[0]))
            
            buton_grubu.addWidget(goster_buton)
            buton_grubu.addWidget(kopyala_buton)
            buton_grubu.addWidget(duzenle_buton)
            buton_grubu.addWidget(paylas_buton)
            buton_grubu.addWidget(sil_buton)
            
            ust_kisim.addLayout(buton_grubu)
            kart_duzen.addLayout(ust_kisim)
            
            # Şifre alanını ekle
            kart_duzen.addWidget(sifre_alani)
            
            # Alt bilgiler
            if sifre[3]:  # Website
                website = QLabel(f"🌐 {sifre[3]}")
                website.setStyleSheet("font-size: 14px; padding: 2px;")
                kart_duzen.addWidget(website)
            
            if sifre[4]:  # Açıklama
                aciklama = QLabel(f"📝 {sifre[4]}")
                aciklama.setStyleSheet("font-size: 14px; padding: 2px;")
                kart_duzen.addWidget(aciklama)
            
            # Son güncelleme
            tarih = QLabel(f"🕒 Son güncelleme: {sifre[5]}")
            tarih.setStyleSheet("color: #7F8C8D; font-size: 12px; padding: 2px;")
            kart_duzen.addWidget(tarih)
            
            # Şifre güvenlik göstergesi
            guc, _ = self.ana_pencere.yonetici.sifre_gucunu_degerlendir(sifre[2])
            guc_container = QWidget()
            guc_duzen = QHBoxLayout()
            
            guc_bar = QProgressBar()
            guc_bar.setTextVisible(False)
            guc_bar.setFixedHeight(4)
            guc_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background-color: #333333;
                    border-radius: 2px;
                }
                QProgressBar::chunk {
                    border-radius: 2px;
                }
            """)
            
            # Güç seviyesine göre renk ve değer ayarla
            guc_deger = {
                "Zayıf": (33, "#E74C3C"),
                "Orta": (66, "#F1C40F"),
                "Güçlü": (100, "#27AE60")
            }.get(guc, (0, "#E74C3C"))
            
            guc_bar.setValue(guc_deger[0])
            guc_bar.setStyleSheet(guc_bar.styleSheet() + f"""
                QProgressBar::chunk {{
                    background-color: {guc_deger[1]};
                }}
            """)
            
            guc_label = QLabel(f"Güvenlik: {guc}")
            guc_label.setStyleSheet(f"""
                color: {guc_deger[1]};
                font-size: 12px;
                padding: 2px;
            """)
            
            guc_duzen.addWidget(guc_label)
            guc_duzen.addWidget(guc_bar)
            guc_container.setLayout(guc_duzen)
            kart_duzen.addWidget(guc_container)

            kart.setLayout(kart_duzen)
            self.kartlar_duzen.insertWidget(0, kart)  # En üste ekle
        
        # Boş alan ekle
        self.kartlar_duzen.addStretch()
    
    def sifre_goster_gizle(self, label, sifre, buton):
        if label.text() == "••••••••":
            label.setText(sifre)
            buton.setText("🔒")
        else:
            label.setText("••••••••")
            buton.setText("👁️")
    
    def sifre_kopyala(self, sifre):
        QApplication.clipboard().setText(sifre)
        QMessageBox.information(self, "Başarılı", "Şifre panoya kopyalandı!")
    
    def yeni_sifre_ekle(self):
        dialog = SifreEkleDuzenleDialog(self.ana_pencere)
        if dialog.exec_() == QDialog.Accepted:
            self.sifreleri_yukle()
    
    def sifre_duzenle(self, sifre_bilgisi):
        dialog = SifreEkleDuzenleDialog(self.ana_pencere, sifre_bilgisi)
        if dialog.exec_() == QDialog.Accepted:
            self.sifreleri_yukle()
    
    def sifre_paylas(self, sifre_id):
        # Paylaşım süresi için dialog
        sure_dialog = QDialog(self)
        sure_dialog.setWindowTitle("Şifre Paylaş")
        sure_dialog.setFixedWidth(400)
        
        duzen = QVBoxLayout()
        
        # Açıklama
        aciklama = QLabel("Şifre paylaşımı için süre seçin:")
        aciklama.setStyleSheet("""
            color: #00FF00;
            font-family: 'Consolas';
            font-size: 14px;
            padding: 10px;
        """)
        duzen.addWidget(aciklama)
        
        # Süre seçici
        sure_secici = QSpinBox()
        sure_secici.setRange(1, 60)
        sure_secici.setValue(10)
        sure_secici.setSuffix(" dakika")
        sure_secici.setStyleSheet("""
            QSpinBox {
                background-color: #1A1A1A;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px;
                font-family: 'Consolas';
                font-size: 14px;
            }
        """)
        duzen.addWidget(sure_secici)
        
        # Butonlar
        buton_duzen = QHBoxLayout()
        
        iptal_buton = QPushButton("İptal")
        onayla_buton = QPushButton("Paylaş")
        
        buton_stili = """
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 20px;
                font-family: 'Consolas';
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
        """
        iptal_buton.setStyleSheet(buton_stili)
        onayla_buton.setStyleSheet(buton_stili)
        
        iptal_buton.clicked.connect(sure_dialog.reject)
        onayla_buton.clicked.connect(sure_dialog.accept)
        
        buton_duzen.addWidget(iptal_buton)
        buton_duzen.addWidget(onayla_buton)
        duzen.addLayout(buton_duzen)
        
        sure_dialog.setLayout(duzen)
        sure_dialog.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
                border: 1px solid #00FF00;
            }
        """)
        
        if sure_dialog.exec_() == QDialog.Accepted:
            sure = sure_secici.value()
            paylasim_kodu, pin_kodu = self.ana_pencere.yonetici.sifre_paylas(sifre_id, sure)
            
            if paylasim_kodu and pin_kodu:
                # Paylaşım bilgileri için dialog
                bilgi_dialog = QDialog(self)
                bilgi_dialog.setWindowTitle("Paylaşım Bilgileri")
                bilgi_dialog.setFixedWidth(500)
                
                bilgi_duzen = QVBoxLayout()
                
                # Bilgiler
                bilgi_metni = f"""
                <p style='color: #00FF00;'>
                <b>Paylaşım Kodu:</b><br>
                {paylasim_kodu}<br><br>
                <b>PIN Kodu:</b><br>
                {pin_kodu}<br><br>
                <b>Geçerlilik Süresi:</b><br>
                {sure} dakika
                </p>
                """
                
                bilgi_label = QLabel(bilgi_metni)
                bilgi_label.setStyleSheet("""
                    QLabel {
                        background-color: #1A1A1A;
                        color: #00FF00;
                        font-family: 'Consolas';
                        font-size: 14px;
                        padding: 20px;
                        border: 1px solid #00FF00;
                        border-radius: 5px;
                    }
                """)
                bilgi_duzen.addWidget(bilgi_label)
                
                # Kopyala butonu
                kopyala_buton = QPushButton("Bilgileri Kopyala")
                kopyala_buton.setStyleSheet(buton_stili)
                kopyala_buton.clicked.connect(lambda: QApplication.clipboard().setText(
                    f"Paylaşım Kodu: {paylasim_kodu}\n"
                    f"PIN Kodu: {pin_kodu}\n"
                    f"Geçerlilik Süresi: {sure} dakika"
                ))
                bilgi_duzen.addWidget(kopyala_buton)
                
                # Kapat butonu
                kapat_buton = QPushButton("Kapat")
                kapat_buton.setStyleSheet(buton_stili)
                kapat_buton.clicked.connect(bilgi_dialog.close)
                bilgi_duzen.addWidget(kapat_buton)
                
                bilgi_dialog.setLayout(bilgi_duzen)
                bilgi_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #1A1A1A;
                        border: 1px solid #00FF00;
                    }
                """)
                
                bilgi_dialog.exec_()
            else:
                QMessageBox.warning(self, "Hata", "Paylaşım oluşturulamadı!")
    
    def sifre_sil(self, sifre_id):
        yanit = QMessageBox.question(
            self, "Şifre Sil",
            "Bu şifreyi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if yanit == QMessageBox.Yes:
            if self.ana_pencere.yonetici.sifre_sil(sifre_id):
                self.sifreleri_yukle()
            else:
                QMessageBox.warning(self, "Hata", "Şifre silinemedi!")
    
    def cikis_yap(self):
        self.ana_pencere.stacked_widget.setCurrentIndex(0)
        self.ana_pencere.yonetici.mevcut_kullanici = None

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.yonetici = SifreYoneticisi()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Lockly - Güvenli Şifre Yöneticisi')
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon('assets/lock_icon.png'))
        
        # Ana tema renklerini ayarla
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#000000"))          # Siyah arka plan
        palette.setColor(QPalette.WindowText, QColor("#00FF00"))      # Hacker yeşili
        palette.setColor(QPalette.Base, QColor("#1A1A1A"))           # Koyu gri
        palette.setColor(QPalette.AlternateBase, QColor("#333333"))   # Orta gri
        palette.setColor(QPalette.Text, QColor("#00FF00"))           # Hacker yeşili
        palette.setColor(QPalette.Button, QColor("#333333"))         # Koyu gri
        palette.setColor(QPalette.ButtonText, QColor("#00FF00"))     # Hacker yeşili
        self.setPalette(palette)
        
        # Global stil tanımlamaları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 8px 15px;
                border-radius: 4px;
                font-family: 'Consolas';
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #008800;
                color: #000000;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #00FF00;
                border-radius: 4px;
                background-color: #1A1A1A;
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #00FF00;
                background-color: #333333;
            }
            QLabel {
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 14px;
            }
            QTableWidget {
                background-color: #1A1A1A;
                color: #00FF00;
                border: 1px solid #00FF00;
                gridline-color: #333333;
                font-family: 'Consolas';
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #00FF00;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #00FF00;
                padding: 12px;
                border: 1px solid #00FF00;
                font-family: 'Consolas';
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #00FF00;
                color: #000000;
            }
            QMenu {
                background-color: #1A1A1A;
                color: #00FF00;
                border: 1px solid #00FF00;
                font-family: 'Consolas';
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #00FF00;
                color: #000000;
            }
            QMessageBox {
                background-color: #1A1A1A;
                color: #00FF00;
            }
            QMessageBox QLabel {
                color: #00FF00;
                font-family: 'Consolas';
            }
            QMessageBox QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #00FF00;
                min-width: 80px;
                font-family: 'Consolas';
            }
            QDialog {
                background-color: #1A1A1A;
            }
            QScrollBar:vertical {
                border: 1px solid #00FF00;
                background: #1A1A1A;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #00FF00;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QWidget {
                transition: all 0.3s ease;
            }
            @keyframes pulse {
                0% { background-color: #1A1A1A; }
                50% { background-color: #1F2F1F; }
                100% { background-color: #1A1A1A; }
            }
            .card-hover {
                animation: pulse 2s infinite;
            }
        """)
        
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

def main():
    app = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
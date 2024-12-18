import hashlib
import secrets
import string
import re
from datetime import datetime, timedelta
from veritabani import VeritabaniYoneticisi
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

class SifreYoneticisi:
    def __init__(self):
        self.vt = VeritabaniYoneticisi()
        self.vt.baglan()
        self.mevcut_kullanici = None
        self.maksimum_giris_denemesi = 3
        self.kilit_suresi_dakika = 30
        self.email_ayarlari = {
            'smtp_sunucu': 'smtp.gmail.com',
            'smtp_port': 587,
            'gonderen_email': 'mustafa44fbfb@gmail.com',
            'gonderen_sifre': 'mcwt szgs kefs jznq'  # Gmail uygulama şifresi
        }

    def sifre_gucunu_degerlendir(self, sifre: str) -> tuple:
        puan = 0
        geri_bildirim = []

        if len(sifre) >= 12:
            puan += 2
        elif len(sifre) >= 8:
            puan += 1
        else:
            geri_bildirim.append("Şifre en az 8 karakter olmalıdır.")

        if re.search(r"[A-Z]", sifre):
            puan += 1
        else:
            geri_bildirim.append("Büyük harf ekleyin.")

        if re.search(r"[a-z]", sifre):
            puan += 1
        else:
            geri_bildirim.append("Küçük harf ekleyin.")

        if re.search(r"\d", sifre):
            puan += 1
        else:
            geri_bildirim.append("Sayı ekleyin.")

        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", sifre):
            puan += 1
        else:
            geri_bildirim.append("Özel karakter ekleyin.")

        guc = "Zayıf"
        if puan >= 5:
            guc = "Güçlü"
        elif puan >= 3:
            guc = "Orta"

        return guc, geri_bildirim

    def guvenli_sifre_olustur(self, uzunluk=16, ozel_karakterler=True, sayilar=True) -> str:
        karakterler = string.ascii_letters
        if sayilar:
            karakterler += string.digits
        if ozel_karakterler:
            karakterler += "!@#$%^&*(),.?\":{}|<>"
        
        while True:
            sifre = ''.join(secrets.choice(karakterler) for _ in range(uzunluk))
            guc, _ = self.sifre_gucunu_degerlendir(sifre)
            if guc == "Güçlü":
                return sifre

    def kullanici_kayit(self, kullanici_adi: str, sifre: str, email: str) -> bool:
        """Yeni kullanıcı kaydı"""
        try:
            # Bağlantıyı kontrol et
            self.vt.baglanti_kontrol()
            
            # Transaction başlat
            self.vt.imlec.execute("BEGIN")
            
            # Kullanıcıyı kaydet
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            self.vt.imlec.execute("""
                INSERT INTO kullanicilar (kullanici_adi, sifre_hash, email)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (kullanici_adi, sifre_hash, email))
            
            # Transaction'ı tamamla
            self.vt.baglanti.commit()
            return True
            
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            self.vt.baglanti.rollback()
            return False

    def kullanici_giris(self, kullanici_adi: str, sifre: str) -> bool:
        try:
            print(f"Giriş denemesi - Kullanıcı: {kullanici_adi}")
            sonuc = self.vt.kullanici_dogrula(kullanici_adi, sifre)
            
            if sonuc:
                self.mevcut_kullanici = sonuc
                print(f"Giriş başarılı - Kullanıcı ID: {self.mevcut_kullanici}")
                return True
            
            print("Giriş başarısız - Kullanıcı doğrulanamadı")
            return False
            
        except Exception as e:
            print(f"Giriş hatası: {e}")
            return False

    def kullanici_cikis(self):
        self.mevcut_kullanici = None
        self.vt.baglanti.commit()  # Bekleyen işlemleri kaydet

    def sifre_paylas(self, sifre_id: int, gecerlilik_suresi: int = 10) -> tuple:
        try:
            self.vt.imlec.execute("""
                SELECT id FROM sifreler 
                WHERE id = %s AND kullanici_id = %s
            """, (sifre_id, self.mevcut_kullanici))
            
            if not self.vt.imlec.fetchone():
                return None, None

            paylasim_kodu = str(uuid.uuid4())
            pin_kodu = ''.join(secrets.choice(string.digits) for _ in range(6))
            son_kullanma = datetime.now() + timedelta(minutes=gecerlilik_suresi)

            self.vt.imlec.execute("""
                INSERT INTO paylasim_baglantilari 
                (sifre_id, paylasim_kodu, pin_kodu, son_kullanma_tarihi)
                VALUES (%s, %s, %s, %s)
            """, (sifre_id, paylasim_kodu, pin_kodu, son_kullanma))
            
            self.vt.baglanti.commit()
            return paylasim_kodu, pin_kodu
        except Exception as e:
            print(f"Paylaşım hatası: {e}")
            return None, None

    def paylasilan_sifreyi_al(self, paylasim_kodu: str, pin_kodu: str) -> str:
        try:
            self.vt.imlec.execute("""
                SELECT s.sifrelenmis_sifre, p.kullanildi, p.son_kullanma_tarihi
                FROM paylasim_baglantilari p
                JOIN sifreler s ON p.sifre_id = s.id
                WHERE p.paylasim_kodu = %s AND p.pin_kodu = %s
            """, (paylasim_kodu, pin_kodu))
            
            sonuc = self.vt.imlec.fetchone()
            if not sonuc:
                return None

            sifrelenmis_sifre, kullanildi, son_kullanma = sonuc

            if kullanildi or datetime.now() > son_kullanma:
                return None

            self.vt.imlec.execute("""
                UPDATE paylasim_baglantilari
                SET kullanildi = TRUE
                WHERE paylasim_kodu = %s
            """, (paylasim_kodu,))
            
            self.vt.baglanti.commit()
            return self.vt.sifre_coz(sifrelenmis_sifre)
        except Exception as e:
            print(f"Paylaşılan şifre alma hatası: {e}")
            return None

    def kapat(self):
        self.vt.kapat()

    def sifre_ekle(self, baslik: str, sifre: str, website: str = "", aciklama: str = "") -> bool:
        try:
            sifrelenmis_sifre = self.vt.sifre_sifrele(sifre)
            sorgu = """
            INSERT INTO sifreler (kullanici_id, baslik, sifrelenmis_sifre, website, aciklama)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.vt.imlec.execute(sorgu, (self.mevcut_kullanici, baslik, sifrelenmis_sifre, website, aciklama))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Şifre ekleme hatası: {e}")
            return False

    def sifreleri_getir(self):
        if not self.mevcut_kullanici:
            print("Aktif kullanıcı yok!")  # Debug için
            return []
        
        # Bağlantıyı kontrol et
        self.vt.baglanti_kontrol()
        
        try:
            return self.vt.sifreleri_getir(self.mevcut_kullanici)
        except Exception as e:
            print(f"Şifreleri getirme hatası: {e}")
            return []

    def sifre_guncelle(self, sifre_id: int, baslik: str, sifre: str, website: str, aciklama: str) -> bool:
        try:
            sifrelenmis_sifre = self.vt.sifre_sifrele(sifre)
            sorgu = """
            UPDATE sifreler
            SET baslik = %s, sifrelenmis_sifre = %s, website = %s, aciklama = %s,
                son_guncelleme_tarihi = CURRENT_TIMESTAMP
            WHERE id = %s AND kullanici_id = %s
            """
            self.vt.imlec.execute(sorgu, (baslik, sifrelenmis_sifre, website, aciklama, sifre_id, self.mevcut_kullanici))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Şifre güncelleme hatası: {e}")
            return False

    def sifre_sil(self, sifre_id: int) -> bool:
        try:
            print(f"Şifre silme isteği: ID={sifre_id}, Kullanıcı={self.mevcut_kullanici}")
            return self.vt.sifre_sil(sifre_id, self.mevcut_kullanici)
        except Exception as e:
            print(f"Şifre silme hatası: {e}")
            return False

    def kullanici_bul(self, kullanici_veya_email: str) -> int:
        """Kullanıcı adı veya email ile kullanıcıyı bul"""
        try:
            self.vt.imlec.execute("""
                SELECT id FROM kullanicilar 
                WHERE kullanici_adi = %s OR email = %s
            """, (kullanici_veya_email, kullanici_veya_email))
            
            sonuc = self.vt.imlec.fetchone()
            return sonuc[0] if sonuc else None
            
        except Exception as e:
            print(f"Kullanıcı arama hatası: {e}")
            return None

    def guvenlik_sorularini_getir(self, kullanici_id: int) -> list:
        """Kullanıcının güvenlik sorularını getir"""
        try:
            self.vt.imlec.execute("""
                SELECT soru_1, soru_2, soru_3, soru_4, soru_5, kritik_sorular
                FROM guvenlik_sorulari 
                WHERE kullanici_id = %s
            """, (kullanici_id,))
            
            sonuc = self.vt.imlec.fetchone()
            if not sonuc:
                return []
                
            sorular = list(sonuc[:5])  # İlk 5 eleman sorular
            kritik_sorular = sonuc[5]  # Son eleman kritik soru indeksleri
            
            # Kritik soruları işaretle
            for i in range(len(sorular)):
                if i + 1 in kritik_sorular:
                    sorular[i] = f"[KRİTİK] {sorular[i]}"
                    
            return sorular
            
        except Exception as e:
            print(f"Güvenlik soruları getirme hatası: {e}")
            return []

    def guvenlik_cevaplarini_kontrol_et(self, kullanici_id: int, cevaplar: list) -> bool:
        """Güvenlik sorularının cevaplarını kontrol et"""
        try:
            self.vt.imlec.execute("""
                SELECT cevap_1, cevap_2, cevap_3, cevap_4, cevap_5, kritik_sorular
                FROM guvenlik_sorulari 
                WHERE kullanici_id = %s
            """, (kullanici_id,))
            
            sonuc = self.vt.imlec.fetchone()
            if not sonuc:
                return False
                
            dogru_cevaplar = list(sonuc[:5])
            kritik_sorular = sonuc[5]
            
            # Kritik soruların doğruluğunu kontrol et
            kritik_dogru = 0
            for i in range(len(cevaplar)):
                if i + 1 in kritik_sorular and cevaplar[i].lower() == dogru_cevaplar[i].lower():
                    kritik_dogru += 1
            
            # En az 2 kritik soru doğru cevaplanmalı
            return kritik_dogru >= 2
            
        except Exception as e:
            print(f"Güvenlik cevapları kontrol hatası: {e}")
            return False

    def sifre_sifirla(self, kullanici_id: int, yeni_sifre: str) -> bool:
        """Kullanıcının şifresini sıfırla"""
        try:
            sifre_hash = hashlib.sha256(yeni_sifre.encode()).hexdigest()
            
            self.vt.imlec.execute("""
                UPDATE kullanicilar 
                SET sifre_hash = %s,
                    basarisiz_giris_sayisi = 0,
                    hesap_kilitli = FALSE,
                    kilit_bitis_tarihi = NULL
                WHERE id = %s
            """, (sifre_hash, kullanici_id))
            
            self.vt.baglanti.commit()
            return True
            
        except Exception as e:
            print(f"Şifre sıfırlama hatası: {e}")
            self.vt.baglanti.rollback()
            return False

    def sifirlama_kodu_gonder(self, email: str) -> tuple:
        """Kullanıcıya şifre sıfırlama kodu gönderir"""
        try:
            # Kullanıcıyı e-posta ile bul
            self.vt.imlec.execute("""
                SELECT id, kullanici_adi FROM kullanicilar 
                WHERE email = %s
            """, (email,))
            
            kullanici = self.vt.imlec.fetchone()
            if not kullanici:
                return False, "Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı."
            
            # Rastgele 6 haneli kod oluştur
            kod = ''.join(random.choices(string.digits, k=6))
            
            # Kodu veritabanına kaydet
            self.vt.imlec.execute("""
                UPDATE kullanicilar 
                SET sifirlama_kodu = %s,
                    sifirlama_kodu_son_kullanma = NOW() + INTERVAL '15 minutes'
                WHERE id = %s
            """, (kod, kullanici[0]))
            
            self.vt.baglanti.commit()
            
            # E-posta gönder
            mesaj = MIMEMultipart()
            mesaj['From'] = self.email_ayarlari['gonderen_email']
            mesaj['To'] = email
            mesaj['Subject'] = 'Lockly - Şifre Sıfırlama Kodu'
            
            body = f"""
            Merhaba {kullanici[1]},
            
            Şifre sıfırlama talebiniz için doğrulama kodunuz: {kod}
            
            Bu kod 15 dakika süreyle geçerlidir.
            
            Eğer bu talebi siz yapmadıysanız, lütfen bu e-postayı dikkate almayın.
            
            Saygılarımızla,
            Lockly Ekibi
            """
            
            mesaj.attach(MIMEText(body, 'plain'))
            
            # SMTP bağlantısı
            with smtplib.SMTP(self.email_ayarlari['smtp_sunucu'], 
                            self.email_ayarlari['smtp_port']) as server:
                server.starttls()
                server.login(self.email_ayarlari['gonderen_email'],
                           self.email_ayarlari['gonderen_sifre'])
                server.send_message(mesaj)
            
            return True, "Şifre sıfırlama kodu e-posta adresinize gönderildi."
            
        except Exception as e:
            print(f"E-posta gönderme hatası: {e}")
            return False, "E-posta gönderilirken bir hata oluştu."

    def sifirlama_kodunu_dogrula(self, email: str, kod: str) -> bool:
        """Şifre sıfırlama kodunu doğrular"""
        try:
            self.vt.imlec.execute("""
                SELECT id FROM kullanicilar 
                WHERE email = %s 
                AND sifirlama_kodu = %s
                AND sifirlama_kodu_son_kullanma > NOW()
            """, (email, kod))
            
            return bool(self.vt.imlec.fetchone())
            
        except Exception as e:
            print(f"Kod doğrulama hatası: {e}")
            return False

    def kullanici_eposta_getir(self, kullanici_adi):
        """Kullanıcı adına ait e-posta adresini getir"""
        return self.vt.kullanici_eposta_getir(kullanici_adi)
        
    def dogrulama_kodu_olustur(self, kullanici_adi):
        """Doğrulama kodu oluştur ve sakla"""
        return self.vt.dogrulama_kodu_olustur(kullanici_adi)
        
    def dogrulama_kodu_gonder(self, email, kod):
        """E-posta ile doğrulama kodunu gönder"""
        return self.vt.dogrulama_kodu_gonder(email, kod)

    def dogrulama_kodu_kontrol_et(self, kullanici_adi, kod):
        """Doğrulama kodunu kontrol et"""
        return self.vt.dogrulama_kodu_kontrol_et(kullanici_adi, kod)

    def kullanici_sifre_guncelle(self, kullanici_adi: str, yeni_sifre: str) -> bool:
        """Kullanıcının şifresini güncelle"""
        try:
            # Şifreyi hashle
            sifre_hash = hashlib.sha256(yeni_sifre.encode()).hexdigest()
            
            # Şifreyi güncelle
            self.vt.imlec.execute("""
                UPDATE kullanicilar 
                SET sifre_hash = %s,
                    basarisiz_giris_sayisi = 0,
                    hesap_kilitli = FALSE,
                    kilit_bitis_tarihi = NULL
                WHERE kullanici_adi = %s
                RETURNING id
            """, (sifre_hash, kullanici_adi))
            
            sonuc = self.vt.imlec.fetchone()
            if not sonuc:
                return False
            
            self.vt.baglanti.commit()
            return True
            
        except Exception as e:
            print(f"Şifre güncelleme hatası: {e}")
            self.vt.baglanti.rollback()
            return False
import hashlib
import secrets
import string
import re
from datetime import datetime, timedelta
from veritabani import VeritabaniYoneticisi
import uuid

class SifreYoneticisi:
    def __init__(self):
        self.vt = VeritabaniYoneticisi()
        self.vt.baglan()
        self.mevcut_kullanici = None
        self.maksimum_giris_denemesi = 3
        self.kilit_suresi_dakika = 30

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
        try:
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            sorgu = """
            INSERT INTO kullanicilar (kullanici_adi, sifre_hash, email)
            VALUES (%s, %s, %s)
            """
            self.vt.imlec.execute(sorgu, (kullanici_adi, sifre_hash, email))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            return False

    def kullanici_giris(self, kullanici_adi: str, sifre: str) -> bool:
        sonuc = self.vt.kullanici_dogrula(kullanici_adi, sifre)
        if sonuc:
            self.mevcut_kullanici = sonuc  # kullanıcı ID'si
            print(f"Giriş yapıldı. Kullanıcı ID: {self.mevcut_kullanici}")  # Debug için
            return True
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
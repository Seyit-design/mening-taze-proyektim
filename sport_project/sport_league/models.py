from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count, Q, Sum

class Fakultet(models.Model):
    ady = models.CharField(max_length=100, verbose_name="Fakultetiň ady")
    gysgaltma = models.CharField(max_length=10, verbose_name="Gysgaltma", blank=True)
    binasy = models.CharField(max_length=200, verbose_name="Fakultetiň binasy", blank=True)
    logo = models.ImageField(upload_to='fakultet_logo/', verbose_name="Logotipi", blank=True, null=True)
    gurulan_sene = models.DateField(verbose_name="Gurulan senesi", null=True, blank=True)
    
    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetler"
        ordering = ['ady']
    
    def __str__(self):
        return f"{self.ady} ({self.gysgaltma})" if self.gysgaltma else self.ady
    
    def yenis_sany(self):
        """Fakultetiň umumy ýeňiş sany"""
        return YarysGatnashyk.objects.filter(
            oyuncu__fakultet=self, 
            netije='yenis'
        ).count()
    
    def utuldy_sany(self):
        """Fakultetiň umumý ýeňliş sany"""
        return YarysGatnashyk.objects.filter(
            oyuncu__fakultet=self, 
            netije='utuldy'
        ).count()
    
    def aktiv_oyuncu_sany(self):
        """Fakultetiň aktiv oýunçylarynyň sany"""
        return self.oyuncu_set.filter(aktiv=True).count()
    
    def yarys_gatnashyk_sany(self):
        """Fakultetiň umumy gatnaşyk sany"""
        return YarysGatnashyk.objects.filter(oyuncu__fakultet=self).count()
    
    def utus_prosenti(self):
        """Ýeňiş prosenti"""
        umumy = self.yarys_gatnashyk_sany()
        if umumy == 0:
            return 0
        return round((self.yenis_sany() / umumy) * 100, 1)

class SportGornushi(models.Model):
    ady = models.CharField(max_length=100, verbose_name="Sport görnüşi")
    toparlygy = models.BooleanField(default=False, verbose_name="Toparlaýyn")
    dusundirish = models.TextField(blank=True, verbose_name="Düşündiriş")
    
    class Meta:
        verbose_name = "Sport görnüşi"
        verbose_name_plural = "Sport görnüşleri"
    
    def __str__(self):
        return self.ady

class Oyuncu(models.Model):
    # Şahsy maglumatlar
    ady = models.CharField(max_length=50, verbose_name="Ady")
    familiyasy = models.CharField(max_length=50, verbose_name="Familiýasy")
    surat = models.ImageField(upload_to='oyuncular/', verbose_name="Suraty", blank=True, null=True)
    doglan_sene = models.DateField(verbose_name="Doglan senesi", null=True, blank=True)
    
    # Okuw maglumatlary
    fakultet = models.ForeignKey(Fakultet, on_delete=models.CASCADE, verbose_name="Fakulteti")
    kurs = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)], verbose_name="Kursy")
    topar = models.CharField(max_length=20, verbose_name="Topary", help_text="Mysal: T-101, M-202")
    
    # Sport maglumatlary
    sport_gornushi = models.ManyToManyField(SportGornushi, through='OyuncuSport', verbose_name="Sport görnüşleri")
    esasgy_sport = models.ForeignKey(SportGornushi, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='esasgy_oyuncular', verbose_name="Esasy sport görnüşi")
    
    # Goşmaça maglumatlar
    telefon = models.CharField(max_length=20, verbose_name="Telefon belgisi", blank=True)
    email = models.EmailField(verbose_name="E-mail", blank=True)
    aktiv = models.BooleanField(default=True, verbose_name="Aktiw")
    gosulan_sene = models.DateTimeField(auto_now_add=True, verbose_name="Goşulan sene")
    
    class Meta:
        verbose_name = "Oýunçy"
        verbose_name_plural = "Oýunçylar"
        ordering = ['familiyasy', 'ady']
    
    def __str__(self):
        return f"{self.familiyasy} {self.ady}"
    
    @property
    def tamam_ady(self):
        return f"{self.familiyasy} {self.ady}"

class OyuncuSport(models.Model):
    oyuncu = models.ForeignKey(Oyuncu, on_delete=models.CASCADE, verbose_name="Oýunçy")
    sport_gornushi = models.ForeignKey(SportGornushi, on_delete=models.CASCADE, verbose_name="Sport görnüşi")
    tejribe_yyl = models.IntegerField(default=0, verbose_name="Tejribe ýyly")
    derejesi = models.CharField(max_length=50, blank=True, verbose_name="Derejesi (MS, CMS we ş.m.)")
    
    class Meta:
        verbose_name = "Oýunçynyň sporty"
        verbose_name_plural = "Oýunçylaryň sportlary"
        unique_together = ['oyuncu', 'sport_gornushi']
    
    def __str__(self):
        return f"{self.oyuncu} - {self.sport_gornushi}"

class Yarys(models.Model):
    STATUS_CHOICES = [
        ('planlanan', 'Meýilleşdirilen'),
        ('dowam_edyar', 'Dowam edýär'),
        ('tamamlanyldy', 'Tamamlanan'),
    ]
    
    ady = models.CharField(max_length=200, verbose_name="Ýaryşyň ady")
    sport_gornushi = models.ForeignKey(SportGornushi, on_delete=models.CASCADE, verbose_name="Sport görnüşi")
    baslanjak_sene = models.DateTimeField(verbose_name="Başlanjak senesi")
    gutaryan_sene = models.DateTimeField(verbose_name="Gutarjak senesi", null=True, blank=True)
    yer = models.CharField(max_length=200, verbose_name="Geçirilýän ýeri")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planlanan', verbose_name="Ýagdaýy")
    
    class Meta:
        verbose_name = "Ýaryş"
        verbose_name_plural = "Ýaryşlar"
        ordering = ['-baslanjak_sene']
    
    def __str__(self):
        return f"{self.ady} ({self.baslanjak_sene.strftime('%d.%m.%Y')})"

class YarysGatnashyk(models.Model):
    NETIJE_CHOICES = [
        ('yenis', 'Ýeňiş gazandy'),
        ('utuldy', 'Ýeňildi'),
        ('dowam', 'Dowam edýär'),
        ('gatnashmady', 'Gatnaşmady'),
    ]
    
    yarys = models.ForeignKey(Yarys, on_delete=models.CASCADE, verbose_name="Ýaryş")
    oyuncu = models.ForeignKey(Oyuncu, on_delete=models.CASCADE, verbose_name="Oýunçy")
    netije = models.CharField(max_length=20, choices=NETIJE_CHOICES, default='dowam', verbose_name="Netije")
    orun = models.IntegerField(null=True, blank=True, verbose_name="Tutan orny")
    bellik = models.TextField(blank=True, verbose_name="Bellik")
    gosulan_sene = models.DateTimeField(auto_now_add=True, verbose_name="Goşulan sene")
    
    class Meta:
        verbose_name = "Ýaryşa gatnaşyk"
        verbose_name_plural = "Ýaryşa gatnaşyklar"
        unique_together = ['yarys', 'oyuncu']
    
    def __str__(self):
        return f"{self.yarys} - {self.oyuncu}"
from django.db import models

class TutanakResimVeri(models.Model):
    ysk_no = models.CharField("ysk_no", null=False, blank=False, max_length=50, primary_key=True)

    def __str__(self):
        return self.ysk_no

    class Meta:
        verbose_name_plural="Tutanak Veri ve Resimleri"
        verbose_name="Tutanak Verisi ve Resimi"

class TutanakImage(models.Model):
    tutanak = models.TextField("tutanak", null=False, blank=False, unique=True)
    barcode = models.CharField("barcode", null=True, blank=True, max_length=50)
    tutanak_veri = models.ForeignKey(TutanakResimVeri, on_delete=models.CASCADE, null=True, blank=True)
    need_to_be_checked = models.BooleanField(default=False)

    def __str__(self):
        return "{}. Tutanak Resimi".format(str(self.pk))

    class Meta:
        verbose_name_plural="Tutanak Resimleri"
        verbose_name="Tutanak Resimi"

class Veri(models.Model):
    tutanak_veri = models.ForeignKey(TutanakResimVeri, on_delete=models.CASCADE, null=False, blank=False)
    rt_oy = models.IntegerField("rt_oy", null=False, blank=False)
    kk_oy = models.IntegerField("kk_oy", null=False, blank=False)
    toplam_oy = models.IntegerField("toplam_oy", null=False, blank=False)
    gecersiz_oy = models.IntegerField("gecersiz_oy", null=False, blank=False)
    sandik_no = models.CharField("sandik_no", null=False, blank=False, max_length=10)

    def equals(self, rhs):
        if self.tutanak_veri.ysk_no != rhs.tutanak_veri.ysk_no:
            return False
        if self.rt_oy != rhs.rt_oy:
            return False
        if self.kk_oy != rhs.kk_oy:
            return False
        if self.toplam_oy != rhs.toplam_oy:
            return False
        if self.gecersiz_oy != rhs.gecersiz_oy:
            return False
        if self.sandik_no != rhs.sandik_no:
            return False
        return True

    def __str__(self):
        return "{} nolu tutanak verisi".format(self.tutanak_veri.ysk_no)
    
    class Meta:
        verbose_name_plural="Tutanak Verileri"
        verbose_name="Tutanak Verisi"
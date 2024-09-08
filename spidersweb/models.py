from django.db import models

# Create your models here.

class WebsiteXPath(models.Model):
    city = models.CharField(max_length=255)
    state_id = models.CharField(max_length=10)
    website = models.URLField()
    municipality_main_tel_xpath = models.TextField(blank=True, null=True)
    building_department_main_email_xpath = models.TextField(blank=True, null=True)
    building_department_main_phone_xpath = models.TextField(blank=True, null=True)
    chief_building_official_name_xpath = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.website} - {self.city} - {self.state_id}"


class Record(models.Model):
    city = models.CharField(max_length=255)
    state_id = models.CharField(max_length=10)
    website = models.URLField()
    building_department_main_phone = models.CharField(max_length=20, blank=True, null=True)
    municipality_main_tel = models.CharField(max_length=20, blank=True, null=True)
    building_department_main_email = models.EmailField(blank=True, null=True)
    chief_building_official_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'records' 
        managed = False
        
    def __str__(self):
        return f"{self.city}, {self.state_id}"
from django.contrib.gis.db import models


class FaqGroup(models.Model):
    
    def __unicode__(self):
        return u"%s" % (self.faq_group_name)
    
    faq_group_name = models.CharField(max_length=50)

    
class Faq(models.Model):

    def __unicode__(self):
        return u"%s" % (self.id)

    IMPORTANCE_CHOICES = (
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        (6,'6'),
        (7,'7'),
        (8,'8'),
        (9,'9'),
        (10,'10')                      
    )
                                    
    question = models.TextField(max_length=200)
    answer = models.TextField(max_length=2000)
    importance = models.IntegerField(choices=IMPORTANCE_CHOICES)
    faq_group = models.ForeignKey(FaqGroup)    

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('core', '0007_accessrequest'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='accessrequest', name='council_status', field=models.CharField(choices=[('pending','Pending council review'),('approved','Council approved'),('rejected','Council rejected')], default='pending', max_length=12)),
        migrations.AddField(model_name='accessrequest', name='council_reviewed_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='accessrequest', name='council_reviewer', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='council_reviews', to=settings.AUTH_USER_MODEL)),
    ]

from django.db import migrations

LANGUAGES = [
    ('Bhojpuri Heritage Council', 'Bhojpuri', 'Preserving Bhojpuri folk stories, speech and oral traditions.'),
    ('Awadhi Language Collective', 'Awadhi', 'Supporting Awadhi storytellers, poetry and cultural heritage.'),
    ('Maithili Voice Community', 'Maithili', 'Community-led documentation of Maithili language and narratives.'),
    ('Bundeli Oral Heritage Group', 'Bundeli', 'Keeping Bundeli oral traditions and local voices alive.'),
    ('Hindi Speakers Forum', 'Hindi', 'A community space for Hindi speech contributions and responsible reuse.'),
]

def seed_communities(apps, schema_editor):
    Community = apps.get_model('core', 'Community')
    for name, language, description in LANGUAGES:
        Community.objects.get_or_create(language=language, defaults={'name':name, 'description':description})

class Migration(migrations.Migration):
    dependencies = [('core', '0004_community_communitymembership')]
    operations = [migrations.RunPython(seed_communities, migrations.RunPython.noop)]

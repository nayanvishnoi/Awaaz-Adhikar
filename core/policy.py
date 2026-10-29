from .models import CouncilPolicy

PURPOSE_FIELDS = {'research':'allow_research','education':'allow_education','ai':'allow_ai','commercial':'allow_commercial'}

def permission_allowed(recording, purpose):
    """Fail closed: both speaker and an explicit council policy must allow."""
    field = PURPOSE_FIELDS.get(purpose)
    if not field or recording.withdrawn or recording.deleted_at or not getattr(recording, field):
        return False
    return CouncilPolicy.objects.filter(language=recording.language, purpose=purpose, allowed=True).exists()


def researcher_permission_allowed(access_request):
    """A download needs all three live grants: category, council, named researcher."""
    return access_request.status == 'approved' and access_request.council_status == 'approved' and permission_allowed(
        access_request.recording, access_request.purpose
    )

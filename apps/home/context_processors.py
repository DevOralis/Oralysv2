def user_permissions(request):
    return {
        'user_permissions': request.session.get('user', {}).get('permissions', {}) if request.session.get('user') else {}
    }
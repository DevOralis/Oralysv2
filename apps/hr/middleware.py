"""Middleware to enforce HR URL access control.

Rules:
1. HR supervisor (session flag `hr_is_supervisor`) => full access to `/hr/*`.
2. HR employee non-supervisor (flag `is_hr_employee` true, `hr_is_supervisor` false)
   => all HR URLs **except** calendar (`/hr/leaves/calendar/`).
3. Other users => only URLs under `/hr/leaves/` are allowed (leave management & approval).
   Anything else redirects to the `unauthorized` page defined in `apps.home.views.unauthorized` (make sure this path exists) or returns 403.

IMPORTANT: add this middleware to `settings.py` after authentication middleware:
MIDDLEWARE += [
    'apps.hr.middleware.HRAccessMiddleware',
]
"""

import re
from typing import Optional
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


class HRAccessMiddleware(MiddlewareMixin):
    """Middleware that enforces role-based access to /hr URLs."""

    HR_LEAVE_PREFIX = re.compile(r"^/hr/leaves/?")


    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path
        if not path.startswith('/hr'):
            return None  # Not an HR URL – continue normally

        session_user: Optional[dict] = request.session.get('user') or {}
        is_hr_employee = session_user.get('is_hr_employee', False)
        hr_is_supervisor = session_user.get('hr_is_supervisor', False)
        is_supervisor = session_user.get('is_supervisor', False)

        # 1. HR supervisor -> always allowed
        if hr_is_supervisor:
            return None

        # 2. HR employee (non-supervisor)
        if is_hr_employee:
            # calendar restriction
            if path.startswith('/hr/leaves/calendar'):
                return self._unauthorized()
            return None  # allowed

        # 3. Non-HR user
        if self.HR_LEAVE_PREFIX.match(path):
            # Leave approval reserved for supervisors OR any HR employee
            if path.startswith('/hr/leaves/approval') and (not is_supervisor and not is_hr_employee):
                return self._unauthorized()
            # Block calendar for non-HR users
            if path.startswith('/hr/leaves/calendar'):
                return self._unauthorized()
            # Allow get endpoint for anyone who can access manager approval (bypass auth for API)
            if path.startswith('/hr/leaves/get/'):
                return None
            # Permit other leave management URLs (submit, list, etc.)
            return None
        
        # Allow manager decision endpoint for supervisors (outside of HR_LEAVE_PREFIX)
        if path.startswith('/hr/leave-request-manager-decision/') and is_supervisor:
            return None

        return self._unauthorized()

    @staticmethod
    def _unauthorized():
        # Try redirect to a unified unauthorized page if it exists, else 403
        try:
            return redirect(reverse('unauthorized'))
        except Exception:
            return HttpResponseForbidden("Accès non autorisé")

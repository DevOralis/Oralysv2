from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

class PaginationMixin:
    """
    Mixin pour ajouter la pagination à toutes les vues de liste
    """
    paginate_by = 20  # Nombre d'éléments par page par défaut
    
    def get_paginate_by(self, request):
        """Permet de personnaliser le nombre d'éléments par page via les paramètres GET"""
        return request.GET.get('per_page', self.paginate_by)
    
    def paginate_queryset(self, queryset, request):
        """Applique la pagination à un queryset"""
        paginate_by = self.get_paginate_by(request)
        
        # Convertir en entier et valider
        try:
            paginate_by = int(paginate_by)
            if paginate_by <= 0:
                paginate_by = self.paginate_by
        except (ValueError, TypeError):
            paginate_by = self.paginate_by
        
        # Limiter le nombre maximum d'éléments par page
        max_per_page = getattr(settings, 'MAX_PER_PAGE', 100)
        if paginate_by > max_per_page:
            paginate_by = max_per_page
        
        paginator = Paginator(queryset, paginate_by)
        page = request.GET.get('page')
        
        try:
            queryset_page = paginator.page(page)
        except PageNotAnInteger:
            # Si la page n'est pas un nombre, afficher la première page
            queryset_page = paginator.page(1)
        except EmptyPage:
            # Si la page est hors limites, afficher la dernière page
            queryset_page = paginator.page(paginator.num_pages)
        
        return queryset_page, paginator
    
    def get_pagination_context(self, queryset_page, paginator, request):
        """Génère le contexte de pagination pour les templates"""
        page_obj = queryset_page
        
        # Calculer les informations de pagination
        total_pages = paginator.num_pages
        current_page = page_obj.number
        
        # Déterminer la plage de pages à afficher
        delta = 2  # Nombre de pages à afficher de chaque côté de la page courante
        
        start_page = max(1, current_page - delta)
        end_page = min(total_pages, current_page + delta)
        
        # Ajouter la première et dernière page si elles ne sont pas dans la plage
        if start_page > 1:
            start_page = 1
        if end_page < total_pages:
            end_page = total_pages
        
        # Créer la liste des pages à afficher
        page_range = list(range(start_page, end_page + 1))
        
        # Ajouter des ellipses si nécessaire
        if start_page > 2:
            page_range.insert(0, '...')
        if end_page < total_pages - 1:
            page_range.append('...')
        
        # Informations sur la pagination
        pagination_info = {
            'page_obj': page_obj,
            'paginator': paginator,
            'page_range': page_range,
            'current_page': current_page,
            'total_pages': total_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
            'total_count': paginator.count,
            'per_page': paginator.per_page,
        }
        
        return pagination_info 
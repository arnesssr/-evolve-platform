"""Base repository class."""
from django.db import models
from django.core.paginator import Paginator


class BaseRepository:
    """Base repository with common data access patterns."""
    model = None
    
    def get_by_id(self, id):
        """Get a single object by ID."""
        try:
            return self.model.objects.get(pk=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self):
        """Get all objects."""
        return self.model.objects.all()
    
    def filter(self, **kwargs):
        """Filter objects by given criteria."""
        return self.model.objects.filter(**kwargs)
    
    def exclude(self, **kwargs):
        """Exclude objects by given criteria."""
        return self.model.objects.exclude(**kwargs)
    
    def create(self, **kwargs):
        """Create a new object."""
        return self.model.objects.create(**kwargs)
    
    def update(self, id, **kwargs):
        """Update an object."""
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        return obj
    
    def delete(self, id):
        """Delete an object."""
        obj = self.get_by_id(id)
        if obj:
            obj.delete()
            return True
        return False
    
    def exists(self, **kwargs):
        """Check if objects exist."""
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs):
        """Count objects."""
        return self.model.objects.filter(**kwargs).count()
    
    def paginate(self, queryset, page=1, per_page=20):
        """Paginate a queryset."""
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)
    
    def bulk_create(self, objects):
        """Bulk create objects."""
        return self.model.objects.bulk_create(objects)
    
    def bulk_update(self, objects, fields):
        """Bulk update objects."""
        return self.model.objects.bulk_update(objects, fields)

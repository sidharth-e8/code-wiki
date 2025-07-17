"""
Django project analyzer - extracts models, serializers, and views information
"""

import os
import sys
import inspect
import importlib
from typing import Dict, List, Any, Optional
from django.apps import apps
from django.db import models
from django.conf import settings


class DjangoAnalyzer:
    """Analyzes Django project structure and extracts documentation data"""
    
    def __init__(self, project_path: str, settings_module: str):
        self.project_path = project_path
        self.settings_module = settings_module
        self.models_data = {}
        self.serializers_data = {}
        self.views_data = {}
        
    def setup_django(self):
        """Setup Django environment for analysis"""
        if self.project_path not in sys.path:
            sys.path.insert(0, self.project_path)
            
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', self.settings_module)
        
        try:
            import django
            django.setup()
        except Exception as e:
            raise RuntimeError(f"Failed to setup Django: {e}")
    
    def analyze_models(self) -> Dict[str, Any]:
        """Extract information from Django models"""
        models_info = {}
        
        for app_config in apps.get_app_configs():
            app_models = {}
            
            for model in app_config.get_models():
                model_info = {
                    'name': model.__name__,
                    'app': app_config.name,
                    'table_name': model._meta.db_table,
                    'fields': {},
                    'relationships': {},
                    'methods': [],
                    'docstring': inspect.getdoc(model) or ""
                }
                
                # Analyze fields
                for field in model._meta.get_fields():
                    field_info = {
                        'type': field.__class__.__name__,
                        'null': getattr(field, 'null', False),
                        'blank': getattr(field, 'blank', False),
                        'unique': getattr(field, 'unique', False),
                        'help_text': getattr(field, 'help_text', ''),
                    }
                    
                    # Handle relationships
                    if hasattr(field, 'related_model') and field.related_model:
                        field_info['related_model'] = field.related_model.__name__
                        model_info['relationships'][field.name] = {
                            'type': field.__class__.__name__,
                            'related_model': field.related_model.__name__,
                            'related_app': field.related_model._meta.app_label
                        }
                    
                    model_info['fields'][field.name] = field_info
                
                # Get custom methods (excluding Django internals)
                for name, method in inspect.getmembers(model, predicate=inspect.ismethod):
                    if not name.startswith('_') and not hasattr(models.Model, name):
                        model_info['methods'].append({
                            'name': name,
                            'docstring': inspect.getdoc(method) or ""
                        })
                
                app_models[model.__name__] = model_info
            
            if app_models:
                models_info[app_config.name] = app_models
        
        self.models_data = models_info
        return models_info
    
    def analyze_serializers(self) -> Dict[str, Any]:
        """Extract information from DRF serializers"""
        serializers_info = {}
        
        for app_config in apps.get_app_configs():
            try:
                # Try to import serializers module
                serializers_module = importlib.import_module(f"{app_config.name}.serializers")
                app_serializers = {}
                
                for name, obj in inspect.getmembers(serializers_module):
                    if (inspect.isclass(obj) and 
                        hasattr(obj, '_meta') and 
                        hasattr(obj._meta, 'model')):
                        
                        serializer_info = {
                            'name': name,
                            'app': app_config.name,
                            'model': obj._meta.model.__name__ if obj._meta.model else None,
                            'fields': list(getattr(obj._meta, 'fields', [])),
                            'exclude': list(getattr(obj._meta, 'exclude', [])),
                            'read_only_fields': list(getattr(obj._meta, 'read_only_fields', [])),
                            'docstring': inspect.getdoc(obj) or ""
                        }
                        
                        app_serializers[name] = serializer_info
                
                if app_serializers:
                    serializers_info[app_config.name] = app_serializers
                    
            except ImportError:
                # No serializers module in this app
                continue
            except Exception as e:
                print(f"Warning: Could not analyze serializers in {app_config.name}: {e}")
        
        self.serializers_data = serializers_info
        return serializers_info
    
    def analyze_views(self) -> Dict[str, Any]:
        """Extract information from Django views"""
        views_info = {}
        
        for app_config in apps.get_app_configs():
            try:
                # Try to import views module
                views_module = importlib.import_module(f"{app_config.name}.views")
                app_views = {}
                
                for name, obj in inspect.getmembers(views_module):
                    if inspect.isclass(obj) and hasattr(obj, 'as_view'):
                        view_info = {
                            'name': name,
                            'app': app_config.name,
                            'type': 'class_based',
                            'base_classes': [cls.__name__ for cls in obj.__bases__],
                            'methods': [],
                            'docstring': inspect.getdoc(obj) or ""
                        }
                        
                        # Get HTTP methods
                        http_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
                        for method in http_methods:
                            if hasattr(obj, method):
                                method_obj = getattr(obj, method)
                                view_info['methods'].append({
                                    'name': method.upper(),
                                    'docstring': inspect.getdoc(method_obj) or ""
                                })
                        
                        app_views[name] = view_info
                    
                    elif inspect.isfunction(obj) and not name.startswith('_'):
                        view_info = {
                            'name': name,
                            'app': app_config.name,
                            'type': 'function_based',
                            'docstring': inspect.getdoc(obj) or ""
                        }
                        app_views[name] = view_info
                
                if app_views:
                    views_info[app_config.name] = app_views
                    
            except ImportError:
                # No views module in this app
                continue
            except Exception as e:
                print(f"Warning: Could not analyze views in {app_config.name}: {e}")
        
        self.views_data = views_info
        return views_info
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform complete project analysis"""
        self.setup_django()
        
        return {
            'models': self.analyze_models(),
            'serializers': self.analyze_serializers(),
            'views': self.analyze_views(),
            'project_info': {
                'path': self.project_path,
                'settings': self.settings_module,
                'apps': [app.name for app in apps.get_app_configs()]
            }
        }

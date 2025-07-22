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

    def __init__(self, project_path: str, settings_module: str, debug: bool = False):
        self.project_path = project_path
        self.settings_module = settings_module
        self.debug = debug
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
            app_serializers = {}

            if self.debug:
                print(f"DEBUG: Analyzing serializers in app: {app_config.name}")

            # Try different serializer module patterns
            serializer_modules = []

            # Pattern 1: app_name.serializers (single file)
            try:
                serializers_module = importlib.import_module(f"{app_config.name}.serializers")
                serializer_modules.append(serializers_module)
                if self.debug:
                    print(f"DEBUG: Found {app_config.name}.serializers module")
            except ImportError:
                pass

            # Pattern 2: app_name.serializer (single file, singular)
            try:
                serializer_module = importlib.import_module(f"{app_config.name}.serializer")
                serializer_modules.append(serializer_module)
                if self.debug:
                    print(f"DEBUG: Found {app_config.name}.serializer module")
            except ImportError:
                pass

            # Pattern 3: app_name.serializers.* (directory with multiple files)
            try:
                import pkgutil
                import os

                # Try to find serializers package
                try:
                    serializers_package = importlib.import_module(f"{app_config.name}.serializers")
                    if hasattr(serializers_package, '__path__'):
                        # It's a package, iterate through its modules
                        for importer, modname, ispkg in pkgutil.iter_modules(serializers_package.__path__):
                            if not ispkg:  # Only import modules, not sub-packages
                                try:
                                    submodule = importlib.import_module(f"{app_config.name}.serializers.{modname}")
                                    serializer_modules.append(submodule)
                                    if self.debug:
                                        print(f"DEBUG: Found {app_config.name}.serializers.{modname} module")
                                except ImportError as e:
                                    if self.debug:
                                        print(f"DEBUG: Could not import {app_config.name}.serializers.{modname}: {e}")
                except ImportError:
                    pass

                # Try to find serializer package (singular)
                try:
                    serializer_package = importlib.import_module(f"{app_config.name}.serializer")
                    if hasattr(serializer_package, '__path__'):
                        # It's a package, iterate through its modules
                        for importer, modname, ispkg in pkgutil.iter_modules(serializer_package.__path__):
                            if not ispkg:  # Only import modules, not sub-packages
                                try:
                                    submodule = importlib.import_module(f"{app_config.name}.serializer.{modname}")
                                    serializer_modules.append(submodule)
                                    if self.debug:
                                        print(f"DEBUG: Found {app_config.name}.serializer.{modname} module")
                                except ImportError as e:
                                    if self.debug:
                                        print(f"DEBUG: Could not import {app_config.name}.serializer.{modname}: {e}")
                except ImportError:
                    pass

            except Exception as e:
                if self.debug:
                    print(f"DEBUG: Error scanning for serializer packages in {app_config.name}: {e}")

            # If no serializer modules found, skip this app
            if not serializer_modules:
                if self.debug:
                    print(f"DEBUG: No serializer modules found in {app_config.name}")
                continue

            # Analyze all found serializer modules
            for serializers_module in serializer_modules:
                try:
                    for name, obj in inspect.getmembers(serializers_module):
                        # Check if it's a class and looks like a DRF serializer
                        if inspect.isclass(obj):
                            # Skip if the class is not defined in this module (imported from elsewhere)
                            if obj.__module__ != serializers_module.__name__:
                                if self.debug:
                                    print(f"DEBUG: Skipping {name} - imported from {obj.__module__}")
                                continue

                            # Skip DRF base classes that might be imported or referenced
                            if obj.__module__.startswith('rest_framework'):
                                if self.debug:
                                    print(f"DEBUG: Skipping DRF base class {name}")
                                continue

                            is_serializer = False

                            # Check if it inherits from DRF serializers (more comprehensive check)
                            for base in obj.__mro__:
                                base_name = base.__name__
                                base_module = getattr(base, '__module__', '')

                                # Check for DRF serializer base classes
                                if (base_name in ('Serializer', 'ModelSerializer', 'HyperlinkedModelSerializer',
                                                'ListSerializer', 'BaseSerializer') and
                                    ('rest_framework' in base_module or 'serializers' in base_module)):
                                    is_serializer = True
                                    if self.debug:
                                        print(f"DEBUG: Found serializer {name} inheriting from {base_name}")
                                    break

                                # Check for custom serializer base classes that might inherit from DRF
                                if 'Serializer' in base_name and base_module != 'builtins':
                                    # Check if this custom base class inherits from DRF serializers
                                    for grandbase in base.__mro__:
                                        if (grandbase.__name__ in ('Serializer', 'ModelSerializer', 'HyperlinkedModelSerializer') and
                                            'rest_framework' in getattr(grandbase, '__module__', '')):
                                            is_serializer = True
                                            if self.debug:
                                                print(f"DEBUG: Found serializer {name} inheriting from custom base {base_name}")
                                            break
                                    if is_serializer:
                                        break

                            # Also check for _meta attribute (ModelForm style)
                            if not is_serializer and hasattr(obj, '_meta') and hasattr(obj._meta, 'model'):
                                is_serializer = True
                                if self.debug:
                                    print(f"DEBUG: Found serializer {name} with _meta.model attribute")

                            if is_serializer:
                                # Get model name if it's a ModelSerializer
                                model_name = None
                                if hasattr(obj, 'Meta') and hasattr(obj.Meta, 'model'):
                                    model_name = obj.Meta.model.__name__
                                elif hasattr(obj, '_meta') and hasattr(obj._meta, 'model'):
                                    model_name = obj._meta.model.__name__

                                # Get fields
                                fields = []
                                exclude = []
                                read_only_fields = []

                                if hasattr(obj, 'Meta'):
                                    fields_attr = getattr(obj.Meta, 'fields', [])
                                    # Handle '__all__' case properly
                                    if fields_attr == '__all__':
                                        fields = ['__all__']
                                    else:
                                        fields = list(fields_attr) if fields_attr else []
                                    exclude = list(getattr(obj.Meta, 'exclude', []))
                                    read_only_fields = list(getattr(obj.Meta, 'read_only_fields', []))
                                elif hasattr(obj, '_meta'):
                                    fields_attr = getattr(obj._meta, 'fields', [])
                                    # Handle '__all__' case properly
                                    if fields_attr == '__all__':
                                        fields = ['__all__']
                                    else:
                                        fields = list(fields_attr) if fields_attr else []
                                    exclude = list(getattr(obj._meta, 'exclude', []))
                                    read_only_fields = list(getattr(obj._meta, 'read_only_fields', []))

                                # Generate meaningful description instead of using potentially generic docstring
                                description = self._generate_serializer_description(obj, name, model_name, fields, exclude, read_only_fields)

                                serializer_info = {
                                    'name': name,
                                    'app': app_config.name,
                                    'model': model_name,
                                    'fields': fields,
                                    'exclude': exclude,
                                    'read_only_fields': read_only_fields,
                                    'docstring': description,
                                    'module': serializers_module.__name__
                                }

                                # Avoid duplicates - use full qualified name as key if needed
                                serializer_key = f"{serializers_module.__name__.split('.')[-1]}.{name}" if len(serializer_modules) > 1 else name
                                if serializer_key not in app_serializers:
                                    app_serializers[serializer_key] = serializer_info
                                elif self.debug:
                                    print(f"DEBUG: Duplicate serializer {name} found, skipping")

                except Exception as e:
                    if self.debug:
                        print(f"DEBUG: Error analyzing module {serializers_module.__name__}: {e}")
                    continue

            # Store results for this app
            if app_serializers:
                serializers_info[app_config.name] = app_serializers
                if self.debug:
                    print(f"DEBUG: Found {len(app_serializers)} serializers in {app_config.name}: {list(app_serializers.keys())}")
            else:
                if self.debug:
                    print(f"DEBUG: No serializers found in {app_config.name}")

        total_serializers = sum(len(app_serializers) for app_serializers in serializers_info.values())
        if self.debug:
            print(f"DEBUG: Total serializers found: {total_serializers}")
            print(f"DEBUG: Serializers by app: {[(app, len(serializers)) for app, serializers in serializers_info.items()]}")

        self.serializers_data = serializers_info
        return serializers_info

    def _generate_serializer_description(self, serializer_class, name: str, model_name: str, fields: list, exclude: list, read_only_fields: list) -> str:
        """Generate a meaningful description for a serializer based on its purpose and configuration"""

        # First, check if the serializer has a custom docstring (not inherited from base classes)
        custom_docstring = None
        if hasattr(serializer_class, '__doc__') and serializer_class.__doc__:
            # Check if this docstring is different from base class docstrings
            base_docstrings = set()
            for base in serializer_class.__mro__[1:]:  # Skip the class itself
                if hasattr(base, '__doc__') and base.__doc__:
                    base_docstrings.add(base.__doc__.strip())

            current_docstring = serializer_class.__doc__.strip()
            if current_docstring and current_docstring not in base_docstrings:
                custom_docstring = current_docstring

        if custom_docstring:
            return custom_docstring

        # Generate description based on serializer characteristics
        description_parts = []

        # Determine serializer purpose based on name patterns
        name_lower = name.lower()
        if 'list' in name_lower:
            description_parts.append("Serializer for listing")
        elif 'detail' in name_lower or 'view' in name_lower:
            description_parts.append("Serializer for detailed view of")
        elif 'create' in name_lower:
            description_parts.append("Serializer for creating")
        elif 'update' in name_lower:
            description_parts.append("Serializer for updating")
        elif 'delete' in name_lower:
            description_parts.append("Serializer for deleting")
        else:
            description_parts.append("Serializer for")

        # Add model information
        if model_name:
            description_parts.append(f"{model_name} model data")
        else:
            # For non-model serializers, try to infer purpose from name
            base_name = name.replace('Serializer', '').replace('Serialiser', '')
            description_parts.append(f"{base_name} data")

        # Add field information
        field_info = []
        if fields:
            if fields == ['__all__']:
                field_info.append("all model fields")
            elif len(fields) <= 5:
                field_info.append(f"fields: {', '.join(fields)}")
            else:
                field_info.append(f"{len(fields)} fields including {', '.join(fields[:3])}")

        if exclude:
            field_info.append(f"excluding {', '.join(exclude)}")

        if read_only_fields:
            if len(read_only_fields) <= 3:
                field_info.append(f"read-only: {', '.join(read_only_fields)}")
            else:
                field_info.append(f"{len(read_only_fields)} read-only fields")

        description = " ".join(description_parts)

        if field_info:
            description += f". Includes {', '.join(field_info)}."
        else:
            description += "."

        return description
    
    def analyze_views(self) -> Dict[str, Any]:
        """Extract information from Django views"""
        views_info = {}

        for app_config in apps.get_app_configs():
            app_views = {}

            if self.debug:
                print(f"DEBUG: Analyzing views in app: {app_config.name}")

            # Try different view module patterns
            view_modules = []

            # Pattern 1: app_name.views (single file)
            try:
                views_module = importlib.import_module(f"{app_config.name}.views")
                view_modules.append(views_module)
                if self.debug:
                    print(f"DEBUG: Found {app_config.name}.views module")
            except ImportError:
                pass

            # Pattern 2: app_name.views.* (directory with multiple files)
            try:
                import pkgutil

                # Try to find views package
                try:
                    views_package = importlib.import_module(f"{app_config.name}.views")
                    if hasattr(views_package, '__path__'):
                        # It's a package, iterate through its modules
                        for importer, modname, ispkg in pkgutil.iter_modules(views_package.__path__):
                            if not ispkg:  # Only import modules, not sub-packages
                                try:
                                    submodule = importlib.import_module(f"{app_config.name}.views.{modname}")
                                    view_modules.append(submodule)
                                    if self.debug:
                                        print(f"DEBUG: Found {app_config.name}.views.{modname} module")
                                except ImportError as e:
                                    if self.debug:
                                        print(f"DEBUG: Could not import {app_config.name}.views.{modname}: {e}")
                except ImportError:
                    pass

            except Exception as e:
                if self.debug:
                    print(f"DEBUG: Error scanning for view packages in {app_config.name}: {e}")

            # If no view modules found, skip this app
            if not view_modules:
                if self.debug:
                    print(f"DEBUG: No view modules found in {app_config.name}")
                continue

            # Analyze all found view modules
            for views_module in view_modules:
                try:
                    for name, obj in inspect.getmembers(views_module):
                        # Skip if the class/function is not defined in this module (imported from elsewhere)
                        if hasattr(obj, '__module__') and obj.__module__ != views_module.__name__:
                            if self.debug:
                                print(f"DEBUG: Skipping {name} - imported from {obj.__module__}")
                            continue

                        if inspect.isclass(obj) and hasattr(obj, 'as_view'):
                            view_info = {
                                'name': name,
                                'app': app_config.name,
                                'type': 'class_based',
                                'base_classes': [cls.__name__ for cls in obj.__bases__],
                                'methods': [],
                                'docstring': inspect.getdoc(obj) or "",
                                'module': views_module.__name__
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

                            # Avoid duplicates - use full qualified name as key if needed
                            view_key = f"{views_module.__name__.split('.')[-1]}.{name}" if len(view_modules) > 1 else name
                            if view_key not in app_views:
                                app_views[view_key] = view_info
                                if self.debug:
                                    print(f"DEBUG: Found class-based view {name}")
                            elif self.debug:
                                print(f"DEBUG: Duplicate view {name} found, skipping")

                        elif inspect.isfunction(obj) and not name.startswith('_'):
                            # Additional check to see if it looks like a view function
                            sig = inspect.signature(obj)
                            params = list(sig.parameters.keys())

                            # Check if first parameter is 'request' (typical for Django views)
                            if params and params[0] == 'request':
                                view_info = {
                                    'name': name,
                                    'app': app_config.name,
                                    'type': 'function_based',
                                    'docstring': inspect.getdoc(obj) or "",
                                    'module': views_module.__name__
                                }

                                # Avoid duplicates
                                view_key = f"{views_module.__name__.split('.')[-1]}.{name}" if len(view_modules) > 1 else name
                                if view_key not in app_views:
                                    app_views[view_key] = view_info
                                    if self.debug:
                                        print(f"DEBUG: Found function-based view {name}")
                                elif self.debug:
                                    print(f"DEBUG: Duplicate view function {name} found, skipping")

                except Exception as e:
                    if self.debug:
                        print(f"DEBUG: Error analyzing module {views_module.__name__}: {e}")
                    continue

            # Store results for this app
            if app_views:
                views_info[app_config.name] = app_views
                if self.debug:
                    print(f"DEBUG: Found {len(app_views)} views in {app_config.name}: {list(app_views.keys())}")
            else:
                if self.debug:
                    print(f"DEBUG: No views found in {app_config.name}")

        total_views = sum(len(app_views) for app_views in views_info.values())
        if self.debug:
            print(f"DEBUG: Total views found: {total_views}")
            print(f"DEBUG: Views by app: {[(app, len(views)) for app, views in views_info.items()]}")

        self.views_data = views_info
        return views_info
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform complete project analysis"""
        self.setup_django()

        # Debug: Print all apps being analyzed
        all_apps = [app.name for app in apps.get_app_configs()]
        if self.debug:
            print(f"DEBUG: All Django apps found: {all_apps}")

        return {
            'models': self.analyze_models(),
            'serializers': self.analyze_serializers(),
            'views': self.analyze_views(),
            'project_info': {
                'path': self.project_path,
                'settings': self.settings_module,
                'apps': all_apps
            }
        }

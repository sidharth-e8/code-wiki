# Django AI Wiki - Models Documentation

## Overview

This document provides comprehensive documentation for the Django models in the AI Wiki project. The models are designed to support automatic generation of technical documentation from Django REST framework codebases.

## Core Models

### WikiPage

The `WikiPage` model represents individual documentation pages generated from the codebase analysis.

```python
class WikiPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100)
    tags = models.ManyToManyField('Tag', blank=True)
```

**Fields:**
- `title`: Human-readable page title
- `slug`: URL-friendly identifier
- `content`: Markdown content of the documentation
- `created_at`: Timestamp when page was first generated
- `updated_at`: Timestamp of last update
- `category`: Classification (e.g., "Models", "Views", "APIs")
- `tags`: Associated tags for categorization

### CodeElement

Represents individual code elements (classes, functions, methods) extracted from the codebase.

```python
class CodeElement(models.Model):
    name = models.CharField(max_length=200)
    element_type = models.CharField(max_length=50)
    file_path = models.CharField(max_length=500)
    line_number = models.IntegerField()
    docstring = models.TextField(blank=True)
    signature = models.TextField()
    wiki_page = models.ForeignKey(WikiPage, on_delete=models.CASCADE)
```

**Element Types:**
- `class`: Python classes
- `function`: Standalone functions
- `method`: Class methods
- `view`: Django views
- `serializer`: DRF serializers
- `model`: Django models

### Tag

Simple tagging system for organizing documentation.

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')
    description = models.TextField(blank=True)
```

### SearchIndex

Maintains search index for fast documentation lookup.

```python
class SearchIndex(models.Model):
    wiki_page = models.ForeignKey(WikiPage, on_delete=models.CASCADE)
    keywords = models.TextField()
    search_vector = SearchVectorField()
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
        ]
```

## Model Relationships

- `WikiPage` has many `CodeElement` instances (one-to-many)
- `WikiPage` has many `Tag` instances (many-to-many)
- `SearchIndex` has one `WikiPage` (one-to-one)

## Usage Examples

### Creating a Wiki Page

```python
from django_ai_wiki.models import WikiPage, Tag

# Create a new documentation page
page = WikiPage.objects.create(
    title="User Authentication API",
    slug="user-auth-api",
    content="# User Authentication\n\nThis API handles...",
    category="APIs"
)

# Add tags
auth_tag = Tag.objects.get_or_create(name="authentication")[0]
api_tag = Tag.objects.get_or_create(name="api")[0]
page.tags.add(auth_tag, api_tag)
```

### Querying Code Elements

```python
from django_ai_wiki.models import CodeElement

# Find all view classes
views = CodeElement.objects.filter(element_type='view')

# Find elements in a specific file
models_elements = CodeElement.objects.filter(
    file_path__contains='models.py'
)
```

## Database Migrations

The models use Django's migration system. Key migrations include:

1. **0001_initial**: Creates base models
2. **0002_add_search**: Adds full-text search capabilities
3. **0003_add_tags**: Implements tagging system

## Performance Considerations

- Search operations use PostgreSQL's full-text search
- Code element queries are optimized with database indexes
- Large codebases may require pagination for wiki pages

## Future Enhancements

- Version tracking for documentation changes
- Integration with Git for automatic updates
- Support for multiple programming languages
- Advanced search with filters and facets

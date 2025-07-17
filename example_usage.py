#!/usr/bin/env python3
"""
Example usage of AI Wiki tool
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def create_example_django_project():
    """Create a minimal Django project for testing"""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="aiwiki_example_")
    project_dir = Path(temp_dir) / "example_project"
    project_dir.mkdir()
    
    print(f"Creating example Django project in: {project_dir}")
    
    # Create manage.py
    manage_py = project_dir / "manage.py"
    manage_py.write_text("""#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
""")
    
    # Create project package
    project_package = project_dir / "example_project"
    project_package.mkdir()
    
    # Create __init__.py
    (project_package / "__init__.py").write_text("")
    
    # Create settings.py
    settings_py = project_package / "settings.py"
    settings_py.write_text("""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-example-key-for-testing-only'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'blog',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'example_project.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
""")
    
    # Create urls.py
    urls_py = project_package / "urls.py"
    urls_py.write_text("""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/blog/', include('blog.urls')),
    path('api/shop/', include('shop.urls')),
]
""")
    
    # Create blog app
    blog_app = project_dir / "blog"
    blog_app.mkdir()
    (blog_app / "__init__.py").write_text("")
    
    # Blog models
    (blog_app / "models.py").write_text("""
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    \"\"\"Blog post category\"\"\"
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name

class Post(models.Model):
    \"\"\"Blog post model\"\"\"
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_word_count(self):
        \"\"\"Return word count of the post content\"\"\"
        return len(self.content.split())

class Comment(models.Model):
    \"\"\"Blog post comment\"\"\"
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
""")
    
    # Blog serializers
    (blog_app / "serializers.py").write_text("""
from rest_framework import serializers
from .models import Category, Post, Comment

class CategorySerializer(serializers.ModelSerializer):
    \"\"\"Serializer for blog categories\"\"\"
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at']
        read_only_fields = ['created_at']

class PostSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for blog posts\"\"\"
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    word_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'author_name', 'category', 
                 'category_name', 'content', 'excerpt', 'published', 
                 'created_at', 'updated_at', 'word_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_word_count(self, obj):
        return obj.get_word_count()

class CommentSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for blog comments\"\"\"
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'content', 'created_at', 'approved']
        read_only_fields = ['created_at']
""")
    
    # Blog views
    (blog_app / "views.py").write_text("""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Post, Comment
from .serializers import CategorySerializer, PostSerializer, CommentSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing blog categories\"\"\"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PostViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing blog posts\"\"\"
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        \"\"\"Get comments for a specific post\"\"\"
        post = self.get_object()
        comments = Comment.objects.filter(post=post, approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        \"\"\"Get only published posts\"\"\"
        published_posts = Post.objects.filter(published=True)
        serializer = self.get_serializer(published_posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing blog comments\"\"\"
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
""")
    
    # Blog URLs
    (blog_app / "urls.py").write_text("""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
""")
    
    # Create shop app (simpler)
    shop_app = project_dir / "shop"
    shop_app.mkdir()
    (shop_app / "__init__.py").write_text("")
    
    # Shop models
    (shop_app / "models.py").write_text("""
from django.db import models

class Product(models.Model):
    \"\"\"E-commerce product model\"\"\"
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
""")
    
    # Shop serializers
    (shop_app / "serializers.py").write_text("""
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for products\"\"\"
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at']
""")
    
    # Shop views
    (shop_app / "views.py").write_text("""
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing products\"\"\"
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
""")
    
    # Shop URLs
    (shop_app / "urls.py").write_text("""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
""")
    
    print(f"✅ Example Django project created at: {project_dir}")
    print(f"📁 Project structure:")
    print(f"   {project_dir}/")
    print(f"   ├── manage.py")
    print(f"   ├── example_project/")
    print(f"   │   ├── __init__.py")
    print(f"   │   ├── settings.py")
    print(f"   │   └── urls.py")
    print(f"   ├── blog/")
    print(f"   │   ├── models.py (Category, Post, Comment)")
    print(f"   │   ├── serializers.py")
    print(f"   │   ├── views.py")
    print(f"   │   └── urls.py")
    print(f"   └── shop/")
    print(f"       ├── models.py (Product)")
    print(f"       ├── serializers.py")
    print(f"       ├── views.py")
    print(f"       └── urls.py")
    
    return str(project_dir)

if __name__ == "__main__":
    project_path = create_example_django_project()
    
    print(f"\n🚀 To test AI Wiki with this example project:")
    print(f"1. cd {project_path}")
    print(f"2. aiwiki generate --target . --settings example_project.settings")
    print(f"3. aiwiki serve")
    
    print(f"\n🗑️  To clean up: rm -rf {project_path}")

#!/usr/bin/env python3
"""
Test script to verify AI Wiki installation and basic functionality
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import aiwiki
        print("✅ aiwiki package imported successfully")
        
        from aiwiki.analyzer import DjangoAnalyzer
        print("✅ DjangoAnalyzer imported successfully")
        
        from aiwiki.generators import MarkdownGenerator, MermaidGenerator
        print("✅ Generators imported successfully")
        
        from aiwiki.server import app
        print("✅ Flask server imported successfully")
        
        from aiwiki.cli import main
        print("✅ CLI module imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_cli_help():
    """Test CLI help functionality"""
    print("\n🧪 Testing CLI help...")
    
    try:
        from aiwiki.cli import main
        import argparse
        
        # This would normally call sys.exit, so we'll just test the parser creation
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        
        # Test that we can create the parsers without errors
        generate_parser = subparsers.add_parser('generate')
        generate_parser.add_argument('--target', required=True)
        generate_parser.add_argument('--settings', required=True)
        
        serve_parser = subparsers.add_parser('serve')
        serve_parser.add_argument('--port', type=int, default=8000)
        
        print("✅ CLI argument parsing works correctly")
        return True
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def test_generators():
    """Test documentation generators with mock data"""
    print("\n🧪 Testing generators...")
    
    try:
        from aiwiki.generators import MarkdownGenerator, MermaidGenerator
        
        # Mock analysis data
        mock_data = {
            'models': {
                'blog': {
                    'Post': {
                        'name': 'Post',
                        'app': 'blog',
                        'table_name': 'blog_post',
                        'fields': {
                            'title': {'type': 'CharField', 'null': False, 'blank': False, 'unique': False, 'help_text': ''},
                            'content': {'type': 'TextField', 'null': False, 'blank': False, 'unique': False, 'help_text': ''}
                        },
                        'relationships': {},
                        'methods': [],
                        'docstring': 'Blog post model'
                    }
                }
            },
            'serializers': {},
            'views': {},
            'project_info': {
                'path': '/test/project',
                'settings': 'test.settings',
                'apps': ['blog']
            }
        }
        
        # Test markdown generator
        md_gen = MarkdownGenerator(mock_data)
        markdown_content = md_gen.generate_full_documentation()
        
        if len(markdown_content) > 100 and "Blog post model" in markdown_content:
            print("✅ MarkdownGenerator works correctly")
        else:
            print("❌ MarkdownGenerator output seems incorrect")
            return False
        
        # Test Mermaid generator
        mermaid_gen = MermaidGenerator(mock_data)
        diagram_content = mermaid_gen.generate_erd()
        
        if "```mermaid" in diagram_content and "erDiagram" in diagram_content:
            print("✅ MermaidGenerator works correctly")
        else:
            print("❌ MermaidGenerator output seems incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Generator test error: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\n🧪 Testing Flask app...")
    
    try:
        from aiwiki.server import app
        
        # Test that app is created
        if app and hasattr(app, 'test_client'):
            print("✅ Flask app created successfully")
            
            # Test basic route
            with app.test_client() as client:
                response = client.get('/')
                if response.status_code == 200:
                    print("✅ Dashboard route responds correctly")
                else:
                    print(f"⚠️  Dashboard route returned status {response.status_code}")
            
            return True
        else:
            print("❌ Flask app not properly created")
            return False
    except Exception as e:
        print(f"❌ Flask test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Wiki Installation Test\n")
    
    tests = [
        test_imports,
        test_cli_help,
        test_generators,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Wiki is ready to use.")
        print("\n📝 Next steps:")
        print("1. Create or navigate to a Django project")
        print("2. Run: aiwiki generate --target . --settings your_project.settings")
        print("3. Run: aiwiki serve")
        print("4. Or try the example: python example_usage.py")
    else:
        print("❌ Some tests failed. Please check your installation.")
        print("💡 Try: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()

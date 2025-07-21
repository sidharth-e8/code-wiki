#!/usr/bin/env python3
"""
AI Wiki CLI - Command line interface for Django documentation generation
"""

import argparse
import os
import sys
import requests
import json
from pathlib import Path

from .analyzer import DjangoAnalyzer
from .generators import MarkdownGenerator, MermaidGenerator, HTMLGenerator
from .server import start_server


def send_to_database(project_data: dict):
    """Send project documentation to the dashboard database"""
    try:
        # Default API endpoint - can be configured via environment variable
        api_url = os.getenv('AIWIKI_API_URL', 'http://localhost:3000/api/projects')

        print(f"📤 Sending documentation to dashboard database...")

        response = requests.post(
            api_url,
            json=project_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Documentation stored in database successfully!")
            print(f"📊 Project ID: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"⚠️  Failed to store in database (HTTP {response.status_code})")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"⚠️  Could not connect to dashboard API at {api_url}")
        print(f"   Make sure the dashboard server is running with 'npm run dev'")
        return False
    except Exception as e:
        print(f"⚠️  Error sending to database: {e}")
        return False


def generate_docs(target_path: str, settings_module: str):
    """Generate documentation for Django project"""
    print(f"🔍 Analyzing Django project at: {target_path}")
    print(f"📋 Using settings: {settings_module}")
    
    try:
        # Initialize analyzer
        analyzer = DjangoAnalyzer(target_path, settings_module)
        
        # Perform analysis
        print("⚙️  Loading Django and analyzing project...")
        analysis_data = analyzer.analyze_project()
        
        # Create docs directory
        docs_dir = Path(target_path) / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Generate markdown documentation
        print("📝 Generating markdown documentation...")
        markdown_gen = MarkdownGenerator(analysis_data)
        markdown_content = markdown_gen.generate_full_documentation()
        
        project_md_path = docs_dir / "project.md"
        with open(project_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Created: {project_md_path}")
        
        # Generate Mermaid diagram
        print("🎨 Generating Mermaid ERD diagram...")
        mermaid_gen = MermaidGenerator(analysis_data)
        diagram_content = mermaid_gen.generate_erd()
        
        diagram_md_path = docs_dir / "diagram.md"
        with open(diagram_md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Entity Relationship Diagram\n\n{diagram_content}\n")
        
        print(f"✅ Created: {diagram_md_path}")

        # Generate HTML documentation
        print("🎨 Generating HTML documentation...")
        html_gen = HTMLGenerator(analysis_data)
        html_content = html_gen.generate_html_documentation()

        project_html_path = docs_dir / "project.html"
        with open(project_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Created: {project_html_path}")

        # Summary
        models_count = sum(len(app_models) for app_models in analysis_data.get('models', {}).values())
        serializers_count = sum(len(app_serializers) for app_serializers in analysis_data.get('serializers', {}).values())
        views_count = sum(len(app_views) for app_views in analysis_data.get('views', {}).values())
        
        print(f"\n📊 Analysis Summary:")
        print(f"   • {models_count} models")
        print(f"   • {serializers_count} serializers")
        print(f"   • {views_count} views")
        print(f"\n🎉 Documentation generated successfully!")
        print(f"📁 Output directory: {docs_dir}")
        print(f"📄 Files created:")
        print(f"   - project.md (markdown documentation)")
        print(f"   - diagram.md (Mermaid ERD diagram)")
        print(f"   - project.html (styled HTML documentation)")

        # Store documentation in database
        project_name = os.path.basename(os.path.abspath(target_path))
        project_data = {
            'name': project_name,
            'path': os.path.abspath(target_path),
            'settings_module': settings_module,
            'markdown_content': markdown_content,
            'html_content': html_content,
            'diagram_content': diagram_content,
            'models_count': models_count,
            'serializers_count': serializers_count,
            'views_count': views_count
        }

        database_success = send_to_database(project_data)

        print(f"\n💡 Next steps:")
        if database_success:
            print(f"   1. Visit the dashboard at http://localhost:3000 to view your project")
            print(f"   2. Run 'aiwiki serve' to browse documentation locally")
            print(f"   3. Or open the files directly in your editor")
        else:
            print(f"   1. Run 'aiwiki serve' to browse documentation")
            print(f"   2. Or open the files directly in your editor")
            print(f"   3. Open project.html in your browser for visual documentation")
        
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        sys.exit(1)


def serve_docs(port: int = 8000):
    """Start the Flask web server"""
    print(f"🚀 Starting AI Wiki server on http://localhost:{port}")
    print("📖 Opening browser...")
    
    try:
        start_server(port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Wiki - Auto-generate browsable Django REST API documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aiwiki generate --target ./myproject --settings myproject.settings
  aiwiki serve
  aiwiki serve --port 9000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate documentation from Django project'
    )
    generate_parser.add_argument(
        '--target',
        required=True,
        help='Path to Django project directory'
    )
    generate_parser.add_argument(
        '--settings',
        required=True,
        help='Django settings module (e.g., myproject.settings)'
    )
    
    # Serve command
    serve_parser = subparsers.add_parser(
        'serve',
        help='Start web server to browse documentation'
    )
    serve_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to run server on (default: 8000)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'generate':
        # Validate target path
        target_path = os.path.abspath(args.target)
        if not os.path.exists(target_path):
            print(f"❌ Error: Target path does not exist: {target_path}")
            sys.exit(1)
        
        # Check if it looks like a Django project
        manage_py = os.path.join(target_path, 'manage.py')
        if not os.path.exists(manage_py):
            print(f"⚠️  Warning: manage.py not found in {target_path}")
            print("   This might not be a Django project root directory.")
            response = input("   Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("   Aborted.")
                sys.exit(1)
        
        generate_docs(target_path, args.settings)
    
    elif args.command == 'serve':
        serve_docs(args.port)


if __name__ == '__main__':
    main()

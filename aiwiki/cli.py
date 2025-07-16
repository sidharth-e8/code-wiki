#!/usr/bin/env python3
"""
Django AI Wiki CLI Tool

Command-line interface for the Django AI Wiki project.
"""

import argparse
import sys
import os
from .server import start_server

def serve_command(args):
    """Start the Flask dashboard server."""
    print("🚀 Starting AI Wiki Dashboard Server...")
    
    # Check if documentation files exist
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        print(f"⚠️  Warning: {docs_dir} directory not found. Creating sample documentation...")
        os.makedirs(docs_dir, exist_ok=True)
        
        # Create minimal sample files if they don't exist
        models_path = os.path.join(docs_dir, "models.md")
        if not os.path.exists(models_path):
            with open(models_path, 'w') as f:
                f.write("# Models Documentation\n\nNo models documentation generated yet. Run `aiwiki generate` to create documentation from your Django project.")
        
        diagram_path = os.path.join(docs_dir, "diagram.md")
        if not os.path.exists(diagram_path):
            with open(diagram_path, 'w') as f:
                f.write("# System Diagram\n\n```mermaid\ngraph LR\n    A[Django Project] --> B[AI Wiki]\n    B --> C[Documentation]\n```")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("   Chat functionality will not work without an OpenAI API key.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    # Start the server
    try:
        start_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Wiki Dashboard Server...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def generate_command(args):
    """Generate documentation from Django project (placeholder)."""
    print("📚 Documentation generation feature coming soon!")
    print("This will analyze your Django project and generate comprehensive documentation.")

def analyze_command(args):
    """Analyze Django project structure (placeholder)."""
    print("🔍 Code analysis feature coming soon!")
    print("This will analyze your Django project structure and dependencies.")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Django AI Wiki - Auto-generate browsable technical documentation",
        prog="aiwiki"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start the dashboard server')
    serve_parser.add_argument(
        '--host', 
        default='localhost', 
        help='Host to bind the server to (default: localhost)'
    )
    serve_parser.add_argument(
        '--port', 
        type=int, 
        default=8000, 
        help='Port to bind the server to (default: 8000)'
    )
    serve_parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Run server in debug mode'
    )
    serve_parser.set_defaults(func=serve_command)
    
    # Generate command (placeholder)
    generate_parser = subparsers.add_parser('generate', help='Generate documentation from Django project')
    generate_parser.add_argument(
        '--project-path', 
        default='.', 
        help='Path to Django project (default: current directory)'
    )
    generate_parser.set_defaults(func=generate_command)
    
    # Analyze command (placeholder)
    analyze_parser = subparsers.add_parser('analyze', help='Analyze Django project structure')
    analyze_parser.add_argument(
        '--project-path', 
        default='.', 
        help='Path to Django project (default: current directory)'
    )
    analyze_parser.set_defaults(func=analyze_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the command
    args.func(args)

if __name__ == '__main__':
    main()

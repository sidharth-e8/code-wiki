"""
Documentation generators for markdown, HTML, and Mermaid diagrams
"""

import os
from typing import Dict, Any
from datetime import datetime


class MarkdownGenerator:
    """Generates comprehensive markdown documentation from Django analysis data"""
    
    def __init__(self, analysis_data: Dict[str, Any]):
        self.data = analysis_data
    
    def generate_project_overview(self) -> str:
        """Generate project overview section"""
        project_info = self.data.get('project_info', {})
        apps = project_info.get('apps', [])
        
        overview = f"""# Django Project Documentation

## Project Overview

**Project Path:** `{project_info.get('path', 'N/A')}`  
**Settings Module:** `{project_info.get('settings', 'N/A')}`  
**Total Apps:** {len(apps)}

### Installed Apps
{chr(10).join(f"- {app}" for app in apps)}

---

"""
        return overview
    
    def generate_models_section(self) -> str:
        """Generate models documentation section"""
        models = self.data.get('models', {})
        if not models:
            return "## Models\n\nNo models found.\n\n---\n\n"
        
        section = "## Models\n\n"
        
        for app_name, app_models in models.items():
            section += f"### {app_name.title()} App Models\n\n"
            
            for model_name, model_info in app_models.items():
                section += f"#### {model_name}\n\n"
                
                if model_info.get('docstring'):
                    section += f"{model_info['docstring']}\n\n"
                
                section += f"**Table:** `{model_info.get('table_name', 'N/A')}`\n\n"
                
                # Fields
                fields = model_info.get('fields', {})
                if fields:
                    section += "**Fields:**\n\n"
                    section += "| Field | Type | Null | Blank | Unique | Help Text |\n"
                    section += "|-------|------|------|-------|--------|----------|\n"
                    
                    for field_name, field_info in fields.items():
                        null_str = "✓" if field_info.get('null') else "✗"
                        blank_str = "✓" if field_info.get('blank') else "✗"
                        unique_str = "✓" if field_info.get('unique') else "✗"
                        help_text = field_info.get('help_text', '').replace('|', '\\|')
                        
                        section += f"| {field_name} | {field_info.get('type', 'Unknown')} | {null_str} | {blank_str} | {unique_str} | {help_text} |\n"
                    
                    section += "\n"
                
                # Relationships
                relationships = model_info.get('relationships', {})
                if relationships:
                    section += "**Relationships:**\n\n"
                    for rel_name, rel_info in relationships.items():
                        section += f"- **{rel_name}**: {rel_info.get('type')} → `{rel_info.get('related_app')}.{rel_info.get('related_model')}`\n"
                    section += "\n"
                
                # Custom methods
                methods = model_info.get('methods', [])
                if methods:
                    section += "**Custom Methods:**\n\n"
                    for method in methods:
                        section += f"- **{method['name']}()**: {method.get('docstring', 'No description')}\n"
                    section += "\n"
                
                section += "---\n\n"
        
        return section
    
    def generate_serializers_section(self) -> str:
        """Generate serializers documentation section"""
        serializers = self.data.get('serializers', {})
        if not serializers:
            return "## Serializers\n\nNo serializers found.\n\n---\n\n"
        
        section = "## Serializers\n\n"
        
        for app_name, app_serializers in serializers.items():
            section += f"### {app_name.title()} App Serializers\n\n"
            
            for serializer_name, serializer_info in app_serializers.items():
                section += f"#### {serializer_name}\n\n"
                
                if serializer_info.get('docstring'):
                    section += f"{serializer_info['docstring']}\n\n"
                
                model = serializer_info.get('model')
                if model:
                    section += f"**Model:** `{model}`\n\n"
                
                fields = serializer_info.get('fields', [])
                if fields:
                    section += f"**Fields:** {', '.join(f'`{field}`' for field in fields)}\n\n"
                
                exclude = serializer_info.get('exclude', [])
                if exclude:
                    section += f"**Excluded Fields:** {', '.join(f'`{field}`' for field in exclude)}\n\n"
                
                read_only = serializer_info.get('read_only_fields', [])
                if read_only:
                    section += f"**Read-Only Fields:** {', '.join(f'`{field}`' for field in read_only)}\n\n"
                
                section += "---\n\n"
        
        return section
    
    def generate_views_section(self) -> str:
        """Generate views documentation section"""
        views = self.data.get('views', {})
        if not views:
            return "## Views\n\nNo views found.\n\n---\n\n"
        
        section = "## Views\n\n"
        
        for app_name, app_views in views.items():
            section += f"### {app_name.title()} App Views\n\n"
            
            for view_name, view_info in app_views.items():
                section += f"#### {view_name}\n\n"
                
                if view_info.get('docstring'):
                    section += f"{view_info['docstring']}\n\n"
                
                view_type = view_info.get('type', 'unknown')
                section += f"**Type:** {view_type.replace('_', ' ').title()}\n\n"
                
                if view_type == 'class_based':
                    base_classes = view_info.get('base_classes', [])
                    if base_classes:
                        section += f"**Base Classes:** {', '.join(f'`{cls}`' for cls in base_classes)}\n\n"
                    
                    methods = view_info.get('methods', [])
                    if methods:
                        section += "**HTTP Methods:**\n\n"
                        for method in methods:
                            method_doc = method.get('docstring', 'No description')
                            section += f"- **{method['name']}**: {method_doc}\n"
                        section += "\n"
                
                section += "---\n\n"
        
        return section
    
    def generate_full_documentation(self) -> str:
        """Generate complete markdown documentation"""
        doc = self.generate_project_overview()
        doc += self.generate_models_section()
        doc += self.generate_serializers_section()
        doc += self.generate_views_section()
        
        # Add generation timestamp
        doc += f"\n---\n\n*Documentation generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return doc


class MermaidGenerator:
    """Generates Mermaid ERD diagrams from Django models"""
    
    def __init__(self, analysis_data: Dict[str, Any]):
        self.data = analysis_data
    
    def generate_erd(self) -> str:
        """Generate Mermaid ERD diagram"""
        models = self.data.get('models', {})
        if not models:
            return "```mermaid\nerDiagram\n    NO_MODELS {\n        string message \"No models found\"\n    }\n```"
        
        diagram = "```mermaid\nerDiagram\n"
        
        # Generate entities
        for app_name, app_models in models.items():
            for model_name, model_info in app_models.items():
                diagram += f"    {model_name} {{\n"
                
                # Add fields
                fields = model_info.get('fields', {})
                for field_name, field_info in fields.items():
                    field_type = field_info.get('type', 'Unknown')
                    
                    # Convert Django field types to simpler types for diagram
                    type_mapping = {
                        'CharField': 'string',
                        'TextField': 'text',
                        'IntegerField': 'int',
                        'BigIntegerField': 'bigint',
                        'FloatField': 'float',
                        'DecimalField': 'decimal',
                        'BooleanField': 'boolean',
                        'DateField': 'date',
                        'DateTimeField': 'datetime',
                        'EmailField': 'email',
                        'URLField': 'url',
                        'UUIDField': 'uuid',
                        'ForeignKey': 'fk',
                        'OneToOneField': 'o2o',
                        'ManyToManyField': 'm2m'
                    }
                    
                    simple_type = type_mapping.get(field_type, field_type.lower())
                    
                    # Add constraints
                    constraints = []
                    if field_info.get('unique'):
                        constraints.append('UK')
                    if not field_info.get('null'):
                        constraints.append('NOT NULL')
                    
                    constraint_str = f" \"{' '.join(constraints)}\"" if constraints else ""
                    diagram += f"        {simple_type} {field_name}{constraint_str}\n"
                
                diagram += "    }\n"
        
        # Generate relationships
        for app_name, app_models in models.items():
            for model_name, model_info in app_models.items():
                relationships = model_info.get('relationships', {})
                for rel_name, rel_info in relationships.items():
                    rel_type = rel_info.get('type')
                    related_model = rel_info.get('related_model')
                    
                    if rel_type == 'ForeignKey':
                        diagram += f"    {model_name} ||--o{{ {related_model} : {rel_name}\n"
                    elif rel_type == 'OneToOneField':
                        diagram += f"    {model_name} ||--|| {related_model} : {rel_name}\n"
                    elif rel_type == 'ManyToManyField':
                        diagram += f"    {model_name} }}o--o{{ {related_model} : {rel_name}\n"
        
        diagram += "```"
        return diagram


class HTMLGenerator:
    """Generates comprehensive HTML documentation from Django analysis data"""

    def __init__(self, analysis_data: Dict[str, Any]):
        self.data = analysis_data

    def generate_html_documentation(self) -> str:
        """Generate complete HTML documentation with styling and images"""
        project_info = self.data.get('project_info', {})
        models = self.data.get('models', {})
        serializers = self.data.get('serializers', {})
        views = self.data.get('views', {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django Project Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            margin: 20px 0;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 15px;
            color: white;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #007bff;
        }}
        .section h2 {{
            color: #007bff;
            margin-top: 0;
            font-size: 2em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section h3 {{
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        .section h4 {{
            color: #6c757d;
            margin-top: 25px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #17a2b8;
        }}
        .info-card strong {{
            color: #17a2b8;
            display: block;
            margin-bottom: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background: #007bff;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            margin: 2px;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .apps-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .app-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }}
        .app-item:hover {{
            border-color: #007bff;
            transform: translateY(-2px);
        }}
        .relationships {{
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .relationship-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
            padding: 8px;
            background: white;
            border-radius: 6px;
        }}
        .methods {{
            background: #f0f8f0;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .method-item {{
            background: white;
            padding: 10px;
            margin: 8px 0;
            border-radius: 6px;
            border-left: 3px solid #28a745;
        }}
        .timestamp {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            color: #6c757d;
            font-style: italic;
        }}
        .icon {{
            font-size: 1.2em;
        }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
            color: #e83e8c;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Django Project Documentation</h1>
            <p>Comprehensive API Documentation with Visual Elements</p>
        </div>"""

        # Project Overview Section
        html += self._generate_project_overview_html(project_info)

        # Models Section
        html += self._generate_models_section_html(models)

        # Serializers Section
        html += self._generate_serializers_section_html(serializers)

        # Views Section
        html += self._generate_views_section_html(views)

        # Footer with timestamp
        html += f"""
        <div class="timestamp">
            📅 Documentation generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""

        return html

    def _generate_project_overview_html(self, project_info: Dict[str, Any]) -> str:
        """Generate HTML for project overview section"""
        apps = project_info.get('apps', [])

        html = f"""
        <div class="section">
            <h2><span class="icon">📋</span> Project Overview</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>📁 Project Path</strong>
                    <code>{project_info.get('path', 'N/A')}</code>
                </div>
                <div class="info-card">
                    <strong>⚙️ Settings Module</strong>
                    <code>{project_info.get('settings', 'N/A')}</code>
                </div>
                <div class="info-card">
                    <strong>📦 Total Apps</strong>
                    <span style="font-size: 1.5em; color: #007bff; font-weight: bold;">{len(apps)}</span>
                </div>
            </div>

            <h3>📱 Installed Applications</h3>
            <div class="apps-list">"""

        for app in apps:
            html += f"""
                <div class="app-item">
                    <strong>{app}</strong>
                </div>"""

        html += """
            </div>
        </div>"""

        return html

    def _generate_models_section_html(self, models: Dict[str, Any]) -> str:
        """Generate HTML for models section"""
        if not models:
            return """
        <div class="section">
            <h2><span class="icon">🗃️</span> Models</h2>
            <p style="text-align: center; color: #6c757d; font-style: italic;">No models found in this project.</p>
        </div>"""

        html = """
        <div class="section">
            <h2><span class="icon">🗃️</span> Models</h2>"""

        for app_name, app_models in models.items():
            html += f"""
            <h3>📦 {app_name.title()} App Models</h3>"""

            for model_name, model_info in app_models.items():
                html += f"""
                <h4>🏷️ {model_name}</h4>"""

                if model_info.get('docstring'):
                    html += f"""
                <p style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #007bff;">
                    <strong>Description:</strong> {model_info['docstring']}
                </p>"""

                html += f"""
                <div class="info-card" style="margin: 15px 0;">
                    <strong>🗂️ Database Table</strong>
                    <code>{model_info.get('table_name', 'N/A')}</code>
                </div>"""

                # Fields table
                fields = model_info.get('fields', {})
                if fields:
                    html += """
                <h5 style="color: #495057; margin-top: 20px;">📊 Fields</h5>
                <table>
                    <thead>
                        <tr>
                            <th>Field Name</th>
                            <th>Type</th>
                            <th>Constraints</th>
                            <th>Help Text</th>
                        </tr>
                    </thead>
                    <tbody>"""

                    for field_name, field_info in fields.items():
                        constraints = []
                        if not field_info.get('null'):
                            constraints.append('<span class="badge badge-danger">NOT NULL</span>')
                        if not field_info.get('blank'):
                            constraints.append('<span class="badge badge-warning">NOT BLANK</span>')
                        if field_info.get('unique'):
                            constraints.append('<span class="badge badge-info">UNIQUE</span>')

                        constraints_html = ' '.join(constraints) if constraints else '<span class="badge badge-success">None</span>'
                        help_text = field_info.get('help_text', '').replace('<', '&lt;').replace('>', '&gt;')

                        html += f"""
                        <tr>
                            <td><strong>{field_name}</strong></td>
                            <td><code>{field_info.get('type', 'Unknown')}</code></td>
                            <td>{constraints_html}</td>
                            <td>{help_text or '<em>No help text</em>'}</td>
                        </tr>"""

                    html += """
                    </tbody>
                </table>"""

                # Relationships
                relationships = model_info.get('relationships', {})
                if relationships:
                    html += """
                <h5 style="color: #495057; margin-top: 20px;">🔗 Relationships</h5>
                <div class="relationships">"""

                    for rel_name, rel_info in relationships.items():
                        rel_type = rel_info.get('type', 'Unknown')
                        related_model = rel_info.get('related_model', 'Unknown')
                        related_app = rel_info.get('related_app', 'Unknown')

                        icon = '🔗'
                        if rel_type == 'ForeignKey':
                            icon = '🔗'
                        elif rel_type == 'OneToOneField':
                            icon = '🔐'
                        elif rel_type == 'ManyToManyField':
                            icon = '🔀'

                        html += f"""
                    <div class="relationship-item">
                        <span style="font-size: 1.2em;">{icon}</span>
                        <strong>{rel_name}</strong>
                        <span class="badge badge-info">{rel_type}</span>
                        <span>→</span>
                        <code>{related_app}.{related_model}</code>
                    </div>"""

                    html += """
                </div>"""

                # Custom methods
                methods = model_info.get('methods', [])
                if methods:
                    html += """
                <h5 style="color: #495057; margin-top: 20px;">⚙️ Custom Methods</h5>
                <div class="methods">"""

                    for method in methods:
                        method_doc = method.get('docstring', 'No description available')
                        html += f"""
                    <div class="method-item">
                        <strong>🔧 {method['name']}()</strong>
                        <p style="margin: 5px 0 0 0; color: #6c757d;">{method_doc}</p>
                    </div>"""

                    html += """
                </div>"""

        html += """
        </div>"""

        return html

    def _generate_serializers_section_html(self, serializers: Dict[str, Any]) -> str:
        """Generate HTML for serializers section"""
        if not serializers:
            return """
        <div class="section">
            <h2><span class="icon">🔄</span> Serializers</h2>
            <p style="text-align: center; color: #6c757d; font-style: italic;">No serializers found in this project.</p>
        </div>"""

        html = """
        <div class="section">
            <h2><span class="icon">🔄</span> Serializers</h2>"""

        for app_name, app_serializers in serializers.items():
            html += f"""
            <h3>📦 {app_name.title()} App Serializers</h3>"""

            for serializer_name, serializer_info in app_serializers.items():
                html += f"""
                <h4>🔄 {serializer_name}</h4>"""

                if serializer_info.get('docstring'):
                    html += f"""
                <p style="background: #f0f8f0; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #28a745;">
                    <strong>Description:</strong> {serializer_info['docstring']}
                </p>"""

                model = serializer_info.get('model')
                if model:
                    html += f"""
                <div class="info-card" style="margin: 15px 0;">
                    <strong>🗃️ Related Model</strong>
                    <code>{model}</code>
                </div>"""

                # Fields information
                fields = serializer_info.get('fields', [])
                exclude = serializer_info.get('exclude', [])
                read_only = serializer_info.get('read_only_fields', [])

                if fields or exclude or read_only:
                    html += """
                <div class="info-grid">"""

                    if fields:
                        fields_html = ', '.join(f'<code>{field}</code>' for field in fields)
                        html += f"""
                    <div class="info-card">
                        <strong>📝 Included Fields</strong>
                        <div style="margin-top: 10px;">{fields_html}</div>
                    </div>"""

                    if exclude:
                        exclude_html = ', '.join(f'<code>{field}</code>' for field in exclude)
                        html += f"""
                    <div class="info-card">
                        <strong>🚫 Excluded Fields</strong>
                        <div style="margin-top: 10px;">{exclude_html}</div>
                    </div>"""

                    if read_only:
                        readonly_html = ', '.join(f'<code>{field}</code>' for field in read_only)
                        html += f"""
                    <div class="info-card">
                        <strong>🔒 Read-Only Fields</strong>
                        <div style="margin-top: 10px;">{readonly_html}</div>
                    </div>"""

                    html += """
                </div>"""

        html += """
        </div>"""

        return html

    def _generate_views_section_html(self, views: Dict[str, Any]) -> str:
        """Generate HTML for views section"""
        if not views:
            return """
        <div class="section">
            <h2><span class="icon">👁️</span> Views</h2>
            <p style="text-align: center; color: #6c757d; font-style: italic;">No views found in this project.</p>
        </div>"""

        html = """
        <div class="section">
            <h2><span class="icon">👁️</span> Views</h2>"""

        for app_name, app_views in views.items():
            html += f"""
            <h3>📦 {app_name.title()} App Views</h3>"""

            for view_name, view_info in app_views.items():
                html += f"""
                <h4>👁️ {view_name}</h4>"""

                if view_info.get('docstring'):
                    html += f"""
                <p style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
                    <strong>Description:</strong> {view_info['docstring']}
                </p>"""

                view_type = view_info.get('type', 'unknown')
                type_display = view_type.replace('_', ' ').title()

                html += f"""
                <div class="info-card" style="margin: 15px 0;">
                    <strong>🏷️ View Type</strong>
                    <span class="badge badge-info">{type_display}</span>
                </div>"""

                if view_type == 'class_based':
                    base_classes = view_info.get('base_classes', [])
                    if base_classes:
                        base_classes_html = ', '.join(f'<code>{cls}</code>' for cls in base_classes)
                        html += f"""
                <div class="info-card" style="margin: 15px 0;">
                    <strong>🏗️ Base Classes</strong>
                    <div style="margin-top: 10px;">{base_classes_html}</div>
                </div>"""

                    methods = view_info.get('methods', [])
                    if methods:
                        html += """
                <h5 style="color: #495057; margin-top: 20px;">🌐 HTTP Methods</h5>
                <div class="methods">"""

                        for method in methods:
                            method_doc = method.get('docstring', 'No description available')
                            html += f"""
                    <div class="method-item">
                        <strong>🌐 {method['name'].upper()}</strong>
                        <p style="margin: 5px 0 0 0; color: #6c757d;">{method_doc}</p>
                    </div>"""

                        html += """
                </div>"""

        html += """
        </div>"""

        return html

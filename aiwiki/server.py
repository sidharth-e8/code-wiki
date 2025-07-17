"""
Flask web server for AI Wiki documentation browser
"""

import os
import webbrowser
from pathlib import Path
from flask import Flask, render_template_string, send_file, request, jsonify
import markdown2
import requests


app = Flask(__name__)

# Global variables for docs content
docs_content = ""
diagram_content = ""
html_content = ""
docs_available = False


def load_docs():
    """Load documentation files if they exist"""
    global docs_content, diagram_content, html_content, docs_available

    docs_dir = Path.cwd() / "docs"
    project_md = docs_dir / "project.md"
    diagram_md = docs_dir / "diagram.md"
    project_html = docs_dir / "project.html"

    if project_md.exists() and diagram_md.exists():
        with open(project_md, 'r', encoding='utf-8') as f:
            docs_content = f.read()

        with open(diagram_md, 'r', encoding='utf-8') as f:
            diagram_content = f.read()

        # Load HTML content if available
        if project_html.exists():
            with open(project_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            print(f"📚 Loaded documentation from {docs_dir} (including HTML)")
        else:
            html_content = ""
            print(f"📚 Loaded documentation from {docs_dir} (HTML not available)")

        docs_available = True
    else:
        docs_available = False
        html_content = ""
        print(f"⚠️  No documentation found in {docs_dir}")
        print("   Run 'aiwiki generate' first to create documentation")


@app.route('/')
def dashboard():
    """Main dashboard route"""
    # Debug: Print content info
    print(f"DEBUG: docs_available = {docs_available}")
    print(f"DEBUG: docs_content length = {len(docs_content) if docs_content else 0}")
    print(f"DEBUG: diagram_content length = {len(diagram_content) if diagram_content else 0}")
    print(f"DEBUG: html_content length = {len(html_content) if html_content else 0}")

    return render_template_string(HTML_TEMPLATE,
                                docs_available=docs_available,
                                docs_content=docs_content,
                                diagram_content=diagram_content,
                                html_available=bool(html_content))


@app.route('/view/docs')
def view_docs():
    """View documentation in new tab"""
    if not docs_available:
        return "No documentation available", 404

    html = f"""<!DOCTYPE html>
<html><head><title>Django Documentation</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;line-height:1.6;}}
pre{{background:#f5f5f5;padding:15px;border-radius:5px;overflow-x:auto;}}</style>
</head><body><pre>{docs_content}</pre></body></html>"""
    return html

@app.route('/view/html')
def view_html():
    """View HTML documentation in new tab"""
    if not docs_available or not html_content:
        return "No HTML documentation available", 404

    return html_content

@app.route('/view/diagram')
def view_diagram():
    """View models as interactive table"""
    if not docs_available:
        return "No documentation available", 404

    # Parse the docs content to extract model information
    models_info = []
    lines = docs_content.split('\n')
    current_model = None

    for line in lines:
        if line.startswith('#### ') and not line.startswith('#### Serializer') and not line.startswith('#### View'):
            # This is a model name
            model_name = line.replace('#### ', '').strip()
            current_model = {'name': model_name, 'fields': [], 'relationships': []}
            models_info.append(current_model)
        elif current_model and '|' in line and 'Field' not in line and '---' not in line:
            # This is a field row in a table
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3:
                field_name = parts[0]
                field_type = parts[1]
                if 'ForeignKey' in field_type or 'OneToOne' in field_type or 'ManyToMany' in field_type:
                    current_model['relationships'].append({'name': field_name, 'type': field_type})
                else:
                    current_model['fields'].append({'name': field_name, 'type': field_type})

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html><head><title>Django Models Overview</title>
<style>
body{{font-family:Arial,sans-serif;margin:20px;}}
.search{{margin-bottom:20px;padding:10px;width:300px;font-size:16px;}}
.model{{margin-bottom:30px;border:1px solid #ddd;border-radius:8px;}}
.model-header{{background:#f0f8ff;padding:15px;font-weight:bold;font-size:18px;}}
.model-content{{padding:15px;}}
.fields{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:15px;}}
.field{{background:#f9f9f9;padding:8px;border-radius:4px;}}
.relationships{{background:#fff3cd;padding:10px;border-radius:4px;}}
.rel{{margin:5px 0;color:#856404;}}
</style>
<script>
function searchModels(){{
var input=document.getElementById('search');
var filter=input.value.toLowerCase();
var models=document.getElementsByClassName('model');
for(var i=0;i<models.length;i++){{
var name=models[i].getAttribute('data-name').toLowerCase();
models[i].style.display=name.includes(filter)?'':'none';
}}
}}
</script>
</head><body>
<h1>🎨 Django Models Overview</h1>
<input type="text" id="search" class="search" placeholder="Search models..." onkeyup="searchModels()">
<p><strong>Total Models:</strong> {len(models_info)}</p>
"""

    for model in models_info:
        html += f"""
<div class="model" data-name="{model['name']}">
<div class="model-header">{model['name']}</div>
<div class="model-content">
"""
        if model['fields']:
            html += '<div class="fields">'
            for field in model['fields']:
                html += f'<div class="field"><strong>{field["name"]}</strong><br>{field["type"]}</div>'
            html += '</div>'

        if model['relationships']:
            html += '<div class="relationships"><strong>🔗 Relationships:</strong><br>'
            for rel in model['relationships']:
                html += f'<div class="rel">• {rel["name"]} ({rel["type"]})</div>'
            html += '</div>'

        html += '</div></div>'

    html += '</body></html>'
    return html

@app.route('/download/<filename>')
def download_file(filename):
    """Download documentation files"""
    docs_dir = Path.cwd() / "docs"
    
    if filename == "project.md":
        file_path = docs_dir / "project.md"
    elif filename == "diagram.md":
        file_path = docs_dir / "diagram.md"
    elif filename == "project.html":
        file_path = docs_dir / "project.html"
    else:
        return "File not found", 404
    
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


@app.route('/debug')
def debug_info():
    """Debug route to check content loading"""
    return {
        'docs_available': docs_available,
        'docs_content_length': len(docs_content) if docs_content else 0,
        'diagram_content_length': len(diagram_content) if diagram_content else 0,
        'html_content_length': len(html_content) if html_content else 0,
        'html_available': bool(html_content),
        'docs_preview': docs_content[:200] + '...' if docs_content else 'No content',
        'diagram_preview': diagram_content[:200] + '...' if diagram_content else 'No content'
    }

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle chat questions (proxy to hosted API)"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not docs_available:
            return jsonify({'error': 'No documentation available. Please generate docs first.'}), 400
        
        # Combine docs and diagram content
        combined_docs = f"{docs_content}\n\n{diagram_content}"
        
        # Prepare request to hosted API
        api_payload = {
            'question': question,
            'docs': combined_docs
        }
        
        # API URL - Replace with your deployed Django AI Wiki API URL
        api_url = "http://localhost:3000/api/chat"

        # Optional: Add project API key if configured
        headers = {'Content-Type': 'application/json'}
        # Uncomment and set if you configured API_KEY in your deployed API:
        # headers['x-api-key'] = 'your-project-api-key'

        # Try to make request to hosted API, fall back to mock response
        try:
            response = requests.post(
                api_url,
                json=api_payload,
                timeout=30,  # Increased timeout for AI processing
                headers=headers
            )

            if response.status_code == 200:
                return jsonify(response.json())
            else:
                print(f"API request failed with status {response.status_code}, using mock response")
                raise requests.RequestException("API unavailable")

        except (requests.RequestException, requests.Timeout):
            # Fall back to mock response when API is unavailable
            mock_response = {
                'answer': f"**Mock Response** (API unavailable)\n\n"
                         f"Your question: '{question}'\n\n"
                         f"This is a demonstration response. In production, this would be processed by an AI model "
                         f"with access to your Django documentation ({len(combined_docs)} characters). "
                         f"To enable real AI responses, configure the hosted API endpoint in the server.py file."
            }
        
        return jsonify(mock_response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


def start_server(port=8000):
    """Start the Flask development server"""
    load_docs()
    
    # Open browser automatically
    webbrowser.open(f'http://localhost:{port}')
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port, debug=False)


# HTML Template with Tailwind CSS and Mermaid.js
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Wiki - Django Documentation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        .prose { max-width: none; }
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">🤖 AI Wiki</h1>
            <p class="text-gray-600">Auto-generated Django REST API Documentation</p>
            
            {% if docs_available %}
            <div class="mt-4 flex flex-wrap gap-3">
                {% if html_available %}
                <a href="/download/project.html"
                   class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors">
                    🎨 Download Visual Documentation
                </a>
                {% endif %}
                <a href="/download/project.md"
                   class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                    📄 Download Markdown Docs
                </a>
                <a href="/download/diagram.md"
                   class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors">
                    📊 Download Diagram
                </a>
            </div>
            {% endif %}
        </div>

        {% if not docs_available %}
        <!-- No docs warning -->
        <div class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-8 rounded">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm">
                        <strong>No documentation found!</strong> 
                        Run <code class="bg-yellow-200 px-1 rounded">aiwiki generate --target ./your-project --settings your.settings</code> 
                        to generate documentation first.
                    </p>
                </div>
            </div>
        </div>
        {% else %}
        
        <!-- Main content grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Documentation panel -->
            <div class="lg:col-span-2">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-2xl font-bold text-gray-800 mb-4">📚 Documentation</h2>
                    <div class="prose prose-sm max-w-none" id="docs-content">
                        <!-- Documentation will be rendered here -->
                    </div>
                </div>
                
                <!-- Diagram panel -->
                <div class="bg-white rounded-lg shadow-md p-6 mt-8">
                    <h2 class="text-2xl font-bold text-gray-800 mb-4">🎨 Entity Relationship Diagram</h2>
                    <div id="diagram-content" class="text-center">
                        <!-- Mermaid diagram will be rendered here -->
                    </div>
                </div>
            </div>
            
            <!-- Chat panel -->
            <div class="lg:col-span-1">
                <div class="bg-white rounded-lg shadow-md p-6 sticky top-8">
                    <h2 class="text-2xl font-bold text-gray-800 mb-4">💬 Ask AI</h2>
                    <p class="text-gray-600 text-sm mb-4">Ask questions about your Django project documentation.</p>
                    
                    <div class="chat-container bg-gray-50 rounded-lg p-4 mb-4" id="chat-messages">
                        <div class="text-gray-500 text-sm text-center">
                            Start a conversation by asking a question below!
                        </div>
                    </div>
                    
                    <div class="flex space-x-2">
                        <input type="text"
                               id="question-input"
                               placeholder="Ask about your Django project..."
                               class="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <button id="ask-button"
                                class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Toast container -->
    <div id="toast-container"></div>

    <script>
        // Initialize Mermaid
        mermaid.initialize({ startOnLoad: true, theme: 'default' });

        // Global variables
        var docsAvailable = {{ docs_available | tojson }};

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded, docs available:', docsAvailable);

            if (docsAvailable) {
                loadDocumentation();
                setupChat();

                // Add welcome message
                setTimeout(function() {
                    addMessage('ai', 'Hello! I am ready to answer questions about your Django project. Ask me anything!');
                }, 1000);
            }
        });

        function loadDocumentation() {
            // Load docs via AJAX to avoid template issues
            fetch('/debug')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    console.log('Loaded docs:', data.docs_content_length, 'chars');
                    console.log('HTML available:', data.html_available);

                    // Documentation display - prefer HTML if available
                    var docsDiv = document.getElementById('docs-content');
                    if (data.html_available) {
                        docsDiv.innerHTML = '<div class="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 text-purple-800 px-4 py-3 rounded cursor-pointer hover:from-purple-100 hover:to-blue-100 transition-all">' +
                            '<strong>🎨 Visual Documentation Available</strong><br>' +
                            'Enhanced HTML documentation with styling, icons, and better formatting (' + Math.round(data.html_content_length/1000) + 'KB).<br>' +
                            'Perfect for easy reading and understanding.<br><br>' +
                            '<strong>👆 Click to view visual documentation</strong></div>';
                        docsDiv.onclick = function() { window.open('/view/html', '_blank'); };
                    } else {
                        docsDiv.innerHTML = '<div class="whitespace-pre-wrap text-sm cursor-pointer hover:bg-gray-100 p-2 border rounded">' +
                            'Documentation loaded (' + data.docs_content_length + ' characters). ' +
                            'Content preview: ' + data.docs_preview + '<br><br><strong>👆 Click to view full documentation</strong></div>';
                        docsDiv.onclick = function() { window.open('/view/docs', '_blank'); };
                    }

                    // Interactive diagram display
                    var diagramDiv = document.getElementById('diagram-content');
                    diagramDiv.innerHTML = '<div class="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded cursor-pointer hover:bg-blue-100">' +
                        '<strong>📊 Interactive Models Overview</strong><br>' +
                        'Your project has ' + Math.round(data.diagram_content_length/1000) + 'KB of model relationships - too large for visual diagrams.<br>' +
                        'View as searchable, organized table instead.<br><br>' +
                        '<strong>👆 Click to view interactive models</strong></div>';
                    diagramDiv.onclick = function() { window.open('/view/diagram', '_blank'); };
                })
                .catch(function(error) {
                    console.error('Error loading docs:', error);
                    document.getElementById('docs-content').innerHTML = '<p class="text-red-500">Error loading documentation</p>';
                });
        }

        function setupChat() {
            // Setup event listeners
            var button = document.getElementById('ask-button');
            var input = document.getElementById('question-input');

            button.addEventListener('click', askQuestion);
            input.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    askQuestion();
                }
            });
        }

        function askQuestion() {
            var input = document.getElementById('question-input');
            var question = input.value.trim();

            if (!question) return;

            // Add user message to chat
            addMessage('user', question);
            input.value = '';

            // Show loading
            var button = document.getElementById('ask-button');
            button.disabled = true;
            button.textContent = 'Thinking...';

            // Send request to backend
            fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }
                return response.json();
            })
            .then(function(data) {
                if (data.error) {
                    addMessage('error', data.error);
                    showToast('Error: ' + data.error, 'error');
                } else {
                    addMessage('ai', data.answer);
                    showToast('Response received!', 'success');
                }
            })
            .catch(function(error) {
                console.error('Chat error:', error);
                addMessage('error', 'Failed to get response: ' + error.message);
                showToast('Network error occurred', 'error');
            })
            .finally(function() {
                button.disabled = false;
                button.textContent = 'Send';
            });
        }

        function addMessage(type, content) {
            const chatContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'mb-3 ' + (type === 'user' ? 'text-right' : 'text-left');

            let bgColor, textColor, icon;
            if (type === 'user') {
                bgColor = 'bg-blue-500';
                textColor = 'text-white';
                icon = '👤';
            } else if (type === 'ai') {
                bgColor = 'bg-gray-200';
                textColor = 'text-gray-800';
                icon = '🤖';
            } else {
                bgColor = 'bg-red-100';
                textColor = 'text-red-800';
                icon = '❌';
            }

            messageDiv.innerHTML =
                '<div class="inline-block ' + bgColor + ' ' + textColor + ' rounded-lg px-3 py-2 max-w-xs text-sm">' +
                    '<span class="text-xs">' + icon + '</span> ' + content +
                '</div>';

            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Clear initial message if this is the first real message
            const initialMsg = chatContainer.querySelector('.text-gray-500');
            if (initialMsg) {
                initialMsg.remove();
            }
        }

        function showToast(message, type) {
            type = type || 'info';
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');

            let bgColor;
            if (type === 'error') {
                bgColor = 'bg-red-500';
            } else if (type === 'success') {
                bgColor = 'bg-green-500';
            } else {
                bgColor = 'bg-blue-500';
            }

            toast.className = 'toast ' + bgColor + ' text-white px-4 py-2 rounded-lg shadow-lg';
            toast.textContent = message;

            container.appendChild(toast);

            setTimeout(function() {
                toast.remove();
            }, 3000);
        }


    </script>
</body>
</html>
"""

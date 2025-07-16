import os
import re
import webbrowser
from flask import Flask, render_template, request, jsonify, send_file, abort
import markdown2
import openai
from threading import Timer

app = Flask(__name__)

def get_docs_content():
    """Read and process documentation files."""
    models_content = ""
    diagram_code = ""

    # Get the current working directory (where the user runs the command)
    cwd = os.getcwd()

    # Read models.md
    models_path = os.path.join(cwd, "docs", "models.md")
    if os.path.exists(models_path):
        with open(models_path, 'r', encoding='utf-8') as f:
            models_content = f.read()

    # Read diagram.md and extract mermaid code
    diagram_path = os.path.join(cwd, "docs", "diagram.md")
    if os.path.exists(diagram_path):
        with open(diagram_path, 'r', encoding='utf-8') as f:
            diagram_content = f.read()
            # Extract mermaid code from markdown code blocks
            mermaid_pattern = r'```mermaid\n(.*?)\n```'
            match = re.search(mermaid_pattern, diagram_content, re.DOTALL)
            if match:
                diagram_code = match.group(1).strip()

    return models_content, diagram_code

@app.route('/')
def dashboard():
    """Main dashboard route."""
    models_content, diagram_code = get_docs_content()
    
    # Convert markdown to HTML
    models_html = markdown2.markdown(models_content, extras=['fenced-code-blocks', 'tables'])
    
    return render_template('index.html', 
                         models_html=models_html, 
                         diagram_code=diagram_code)

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle chat questions and return GPT response."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Check for OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenAI API key not found. Please set OPENAI_API_KEY environment variable.'}), 500
        
        # Set up OpenAI client
        openai.api_key = api_key
        
        # Get context from documentation
        models_content, diagram_code = get_docs_content()
        context = f"Documentation:\n{models_content}\n\nDiagram:\n{diagram_code}"
        
        # Create the prompt
        prompt = f"""You are an AI assistant helping with a Django project. Here's the project documentation:

{context}

User question: {question}

Please provide a helpful answer based on the documentation provided."""
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about Django projects based on provided documentation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        return jsonify({'answer': answer})
        
    except Exception as e:
        return jsonify({'error': f'Error processing question: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve documentation files as downloads."""
    allowed_files = ['models.md', 'diagram.md']

    if filename not in allowed_files:
        abort(404)

    # Get the current working directory (where the user runs the command)
    cwd = os.getcwd()
    file_path = os.path.join(cwd, "docs", filename)
    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True, download_name=filename)

def open_browser():
    """Open browser after a short delay."""
    webbrowser.open("http://localhost:8000")

def start_server(host='localhost', port=8000, debug=False):
    """Start the Flask server and open browser."""
    print(f"Starting AI Wiki dashboard server at http://{host}:{port}")
    
    # Open browser after a short delay
    if not debug:
        Timer(1.5, open_browser).start()
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_server(debug=True)

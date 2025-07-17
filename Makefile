.PHONY: install test example clean help

# Default target
help:
	@echo "🤖 AI Wiki - Django Documentation Generator"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and package"
	@echo "  make test      - Run installation tests"
	@echo "  make example   - Create and test with example Django project"
	@echo "  make clean     - Clean up temporary files"
	@echo "  make help      - Show this help message"

# Install dependencies and package
install:
	@echo "📦 Installing AI Wiki..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ Installation complete!"

# Run tests
test:
	@echo "🧪 Running installation tests..."
	python test_installation.py

# Create example project and test
example:
	@echo "🚀 Creating example Django project..."
	python example_usage.py
	@echo ""
	@echo "📝 Example project created! Follow the printed instructions to test AI Wiki."

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Development setup
dev: install test
	@echo "🎉 Development setup complete!"
	@echo "💡 Try: make example"

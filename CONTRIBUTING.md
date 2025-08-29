# Contributing to ModularAI Grocery Store System

Thank you for your interest in contributing to the ModularAI Grocery Store System! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd plutusai

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start services with Docker
cd infra
docker-compose up -d

# Initialize database
docker-compose exec grocery-api python -m core_services.database.init_db
```

## Project Structure

- **`core_services/`**: Infrastructure services (database, auth, RAG)
- **`domain_services/`**: Business logic and API endpoints
- **`webui/`**: Frontend applications (Streamlit demo, future Vue.js dashboard)
- **`infra/`**: Docker configurations and deployment files
- **`tests/`**: Unit and integration tests

## Development Guidelines

### Code Style
- Follow PEP8 for Python code
- Use type hints for all functions
- Write docstrings using Google style
- Format code with `black`
- Maximum line length: 88 characters

### Testing
- Write unit tests for all new features
- Tests should be in the `/tests` directory
- Use pytest for testing
- Aim for high test coverage

### Git Workflow
1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Update documentation if needed
6. Create a pull request

### Commit Messages
Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring

## API Development

### Adding New Endpoints
1. Create endpoint in appropriate API module (`domain_services/grocery/api/`)
2. Add corresponding database models if needed
3. Write unit tests
4. Update API documentation

### Database Changes
1. Modify models in `core_services/database/models.py`
2. Update initialization scripts if needed
3. Test with sample data

## Frontend Development

### Streamlit Demo
- Located in `webui/ds_workbench/`
- Use consistent styling and components
- Ensure API integration works properly

### Future Vue.js Dashboard
- Will be located in `webui/manager_dashboard/`
- Use Vue 3 + Tailwind CSS
- Follow modern frontend practices

## Docker and Deployment

### Building Images
```bash
# Build all services
docker-compose -f infra/docker-compose.yml build

# Build specific service
docker-compose -f infra/docker-compose.yml build grocery-api
```

### Environment Variables
- Use `.env.example` as template
- Never commit actual `.env` files
- Document new environment variables

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Update CHANGELOG.md if applicable
6. Request review from maintainers

## Issues and Bug Reports

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

## Questions and Support

- Check existing issues before creating new ones
- Use clear, descriptive titles
- Provide context and examples
- Be respectful and constructive

Thank you for contributing to ModularAI Grocery Store System!

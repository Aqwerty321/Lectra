# Contributing to LECTRA 🎓

We love your input! We want to make contributing to LECTRA as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Rust (latest stable)
- Ollama with llama3.1:latest
- FFmpeg

### Setup Steps

```powershell
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/LECTRA.git
cd LECTRA

# 2. Run setup script
.\setup-v2.ps1

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start development
.\launch.ps1
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use docstrings for functions and classes
- Format with `black`
- Lint with `flake8` or `ruff`

Example:
```python
def generate_quiz(
    slide_content: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> List[Dict[str, Any]]:
    """
    Generate multiple choice questions from slide content.
    
    Args:
        slide_content: Combined text from slides
        num_questions: Number of questions to generate
        difficulty: Question difficulty (easy/medium/hard)
        
    Returns:
        List of question dictionaries
    """
    pass
```

### JavaScript/Vue (Frontend)
- Use ESLint + Prettier
- Vue 3 Composition API with `<script setup>`
- Tailwind CSS for styling
- Max line length: 100 characters
- Use TypeScript types where beneficial

Example:
```vue
<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(false)
const data = ref([])

async function fetchData() {
  loading.value = true
  try {
    const response = await fetch('/api/data')
    data.value = await response.json()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
```

## Commit Message Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(quiz): add hint system to interactive study mode

fix(video): resolve sync issues with slide timings

docs(readme): update installation instructions

perf(api): optimize parallel LLM calls for 5x speedup
```

## Pull Request Process

1. **Create an Issue First**: For major changes, create an issue to discuss
2. **Branch Naming**: Use descriptive names
   - `feature/quiz-hints`
   - `fix/video-sync`
   - `docs/api-documentation`
3. **Keep PRs Focused**: One feature/fix per PR
4. **Update Documentation**: Include relevant doc updates
5. **Add Tests**: For bug fixes and new features
6. **Request Review**: Tag maintainers for review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All tests pass

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Testing

### Python Backend
```powershell
cd sidecar
pytest tests/ -v
```

### Vue Frontend
```powershell
cd ui
npm run test
npm run lint
```

### Integration Tests
```powershell
.\scripts\run-integration-tests.ps1
```

## Bug Reports

**Great Bug Reports** include:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening)

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 11]
 - Python Version: [e.g. 3.11.0]
 - Node Version: [e.g. 18.0.0]
 - Ollama Version: [e.g. 0.1.20]

**Additional context**
Any other context about the problem.
```

## Feature Requests

We love feature requests! Use this template:

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features.

**Additional context**
Mockups, diagrams, or examples.
```

## Project Structure

```
LECTRA/
├── sidecar/              # Python FastAPI backend
│   ├── app/
│   │   ├── api.py       # Main API routes
│   │   ├── config.py    # Configuration
│   │   └── services/    # Business logic
│   └── requirements.txt
├── ui/                   # Tauri + Vue frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── App.vue      # Main app
│   │   └── main.js
│   └── src-tauri/       # Rust Tauri app
└── scripts/             # Utility scripts
```

## Key Components to Know

### Backend (Python)
- `api.py`: FastAPI routes and endpoints
- `services/quiz_generator.py`: AI quiz generation
- `services/video_generator.py`: Video pipeline
- `services/slide_generator.py`: Slide content generation

### Frontend (Vue)
- `DocumentNotebook.vue`: Main document management
- `InteractiveStudyMode.vue`: Quiz and study interface
- `GenerateAudio.vue`: Audio generation UI

## Areas We Need Help With

- 🎨 UI/UX improvements
- 🧪 Test coverage
- 📚 Documentation
- 🌍 Internationalization (more languages)
- ♿ Accessibility features
- 🚀 Performance optimizations
- 🐛 Bug fixes

## Questions?

- Open an issue with the `question` label
- Join our discussions on GitHub
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Accepting constructive criticism gracefully
- Focusing on what is best for the community

Thank you for contributing to LECTRA! 🎓✨

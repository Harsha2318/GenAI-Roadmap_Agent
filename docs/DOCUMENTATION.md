# GENAI-ROADMAP-1 Documentation
Version 1.0.0

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Features In-Depth](#features-in-depth)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

## Introduction

GENAI-ROADMAP-1 is an AI-powered learning roadmap generator that creates personalized GenAI learning paths. It uses Google's Gemini Pro LLM to analyze user profiles and generate customized recommendations.

### Key Features Overview
- Resume Analysis
- Persona Classification
- Customized Roadmap Generation
- Multi-format Output Support
- Trace Logging System

## System Architecture

### High-Level Architecture
```
[User Interface] → [Flask Server] → [Roadmap Agent] → [Gemini API]
     ↑               ↑                    ↑              ↑
     └───────────────┴────────────────────┴──────────────┘
            Data Flow & State Management
```

### Technology Stack Details
1. **Frontend Layer**
   - HTML5/CSS3/JavaScript
   - Responsive design
   - File upload handling

2. **Application Layer**
   - Flask framework
   - Session management
   - Route handling

3. **Processing Layer**
   - Resume parser
   - Persona classifier
   - Roadmap generator

4. **AI Integration Layer**
   - Google Gemini Pro API
   - Prompt engineering
   - Response processing

## Core Components

### 1. UserUnderstanding Module
```python
class UserUnderstanding:
    """
    Processes user inputs and extracts structured information:
    - Technical skills
    - Experience level
    - Learning goals
    - Time availability
    """
```

### 2. PersonaClassifier Module
```python
class PersonaClassifier:
    """
    Classifies users into predefined personas:
    - College student
    - Working professional (tech/non-tech)
    - Career transitioner
    etc.
    """
```

### 3. RoadmapPlanner Module
```python
class RoadmapPlanner:
    """
    Generates personalized learning roadmaps using:
    - User profile
    - Classified persona
    - Learning preferences
    """
```

## Features In-Depth

### 1. Resume Processing
- Supported formats: PDF, DOCX, TXT
- Extraction capabilities:
  * Skills identification
  * Experience analysis
  * Education background
  * Project history

### 2. Persona Classification
- Classification criteria:
  * Technical background
  * Experience level
  * Current role
  * Career goals
- Machine learning approach
- Confidence scoring

### 3. Roadmap Generation
- Components:
  * Learning modules
  * Timeline estimation
  * Resource recommendations
  * Progress milestones
- Customization factors:
  * Weekly availability
  * Learning style
  * Prior knowledge

## API Reference

### Environment Variables
```env
GEMINI_API_KEY=your_api_key
FLASK_SECRET_KEY=your_secret_key
```

### API Endpoints
```
POST /api/analyze-resume
POST /api/classify-persona
POST /api/generate-roadmap
GET  /api/export-roadmap/{format}
```

## Usage Examples

### 1. Basic Usage
```python
from roadmap_agent import RoadmapGenerator

generator = RoadmapGenerator(api_key="your_key")
roadmap = generator.create_roadmap(
    resume_text="...",
    goals="...",
    weekly_hours=10
)
```

### 2. Advanced Configuration
```python
roadmap = generator.create_roadmap(
    resume_text="...",
    goals="...",
    weekly_hours=10,
    preferences={
        "learning_style": "project-based",
        "difficulty": "intermediate",
        "include_assessments": True
    }
)
```

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   ```
   Error: Failed to connect to Gemini API
   Solution: Check API key and internet connection
   ```

2. **File Processing Errors**
   ```
   Error: Unable to parse PDF
   Solution: Ensure PDF is not encrypted/password protected
   ```

3. **Roadmap Generation Failed**
   ```
   Error: Invalid user data format
   Solution: Verify input data structure matches expected schema
   ```

### Performance Optimization

1. **Response Time**
   - Cache frequent requests
   - Optimize prompt length
   - Use batch processing for multiple requests

2. **Memory Usage**
   - Clear temporary files
   - Implement pagination for large datasets
   - Use streaming responses for large outputs

## Best Practices

1. **Input Preparation**
   - Clean resume text
   - Structure goals clearly
   - Provide specific timeframes

2. **Configuration**
   - Use environment variables
   - Implement rate limiting
   - Set up logging

3. **Output Handling**
   - Validate generated roadmaps
   - Implement error recovery
   - Store results securely

---

## Updates and Maintenance

### Version History
- v1.0.0: Initial release
- v1.0.1: Bug fixes and performance improvements

### Contributing
See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

*Last updated: April 17, 2024*
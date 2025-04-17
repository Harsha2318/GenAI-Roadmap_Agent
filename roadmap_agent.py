
import os
import json
import re
import tempfile
import google.generativeai as genai
from typing import Dict, Any, Tuple, List

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

# Optional: PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ========== Gemini API Utility ========== #
class GeminiAPI:
    """
    Wrapper for Gemini API calls using google-generativeai library.
    Handles authentication, prompt sending, and error handling.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    def generate(self, prompt: str, temperature: float = 0.4, max_output_tokens: int = 2048) -> str:
        try:
            response = self.model.generate_content(prompt, generation_config={
                'temperature': temperature,
                'max_output_tokens': max_output_tokens
            })
            return response.text.strip()
        except Exception as e:
            print(f"[GeminiAPI] Error: {e}")
            return ""

# Utility to clean Gemini JSON output
def clean_json_output(output: str) -> str:
    """
    Remove triple backticks and language tags from LLM output to get valid JSON.
    """
    output = output.strip()
    # Remove triple backticks and optional language tag (e.g., ```json)
    if output.startswith('```'):
        output = re.sub(r'^```[a-zA-Z]*\n?', '', output)
        if output.endswith('```'):
            output = output[:-3]
    return output.strip()

# ========== User Understanding Module ========== #
class UserUnderstanding:
    """
    Extracts structured user data from resume, interview summary, and goals using Gemini API.
    """
    def __init__(self, gemini: GeminiAPI):
        self.gemini = gemini

    def extract_user_data(self, resume_text: str, interview_summary_text: str, goals_text: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert career coach and GenAI learning consultant. Given the following user inputs:

Resume:
{resume_text}

Interview Summary:
{interview_summary_text}

Personal Goals:
{goals_text}

Extract the following as a JSON object:
- domain: User's professional domain/field
- skills: {{ 'technical': [list with proficiency], 'soft': [list] }}
- goals: List of specific goals
- learning_preference: One of ['project-based', 'video-based', 'reading', 'mixed']
- weekly_availability_hours: Integer estimate

Output ONLY the JSON object. Do not include any explanation.
"""
        output = self.gemini.generate(prompt)
        try:
            output_clean = clean_json_output(output)
            user_data = json.loads(output_clean)
            return user_data
        except Exception as e:
            print(f"[UserUnderstanding] Failed to parse JSON: {e}\nRaw output: {output}")
            return {}

    def extract_user_data_trace(self, resume_text: str, interview_summary_text: str, goals_text: str):
        """
        Extracts user data with full trace: returns (parsed_user_data, prompt, raw_response)
        """
        prompt = f"""
You are an expert career coach and GenAI learning consultant. Given the following user inputs:

Resume:
{resume_text}

Interview Summary:
{interview_summary_text}

Personal Goals:
{goals_text}

Extract the following as a JSON object:
- domain: User's professional domain/field
- skills: {{ 'technical': [list with proficiency], 'soft': [list] }}
- goals: List of specific goals
- learning_preference: One of ['project-based', 'video-based', 'reading', 'mixed']
- weekly_availability_hours: Integer estimate

Output ONLY the JSON object. Do not include any explanation.
"""
        output = self.gemini.generate(prompt)
        try:
            output_clean = clean_json_output(output)
            user_data = json.loads(output_clean)
        except Exception as e:
            print(f"[UserUnderstanding] Failed to parse JSON: {e}\nRaw output: {output}")
            user_data = {}
        return user_data, prompt, output


# ========== Persona Classification Module ========== #
class PersonaClassifier:
    """
    Classifies user persona based on structured data using Gemini API.
    """
    def __init__(self, gemini: GeminiAPI):
        self.gemini = gemini
        self.categories = [
            'College student',
            'Working professional (tech)',
            'Working professional (non-tech)',
            'Marketing/Sales background',
            'Non-tech aiming to enter tech',
            'Senior professional (10+ years experience)'
        ]

    def classify_persona(self, user_data: Dict[str, Any]) -> Tuple[str, str]:
        prompt = f"""
Given the following user profile data (JSON):
{json.dumps(user_data, indent=2)}

Classify the user into ONE of these categories:
- {', '.join(self.categories)}

Respond as a JSON object:
{{
  "persona": <category>,
  "justification": <brief justification for your choice>
}}
"""
        output = self.gemini.generate(prompt)
        try:
            output_clean = clean_json_output(output)
            result = json.loads(output_clean)
            return result.get('persona', ''), result.get('justification', '')
        except Exception as e:
            print(f"[PersonaClassifier] Failed to parse JSON: {e}\nRaw output: {output}")
            return '', ''

    def classify_persona_trace(self, user_data: Dict[str, Any]):
        """
        Classifies persona and returns persona, justification, prompt, and raw response for traceability.
        """
        prompt = f"""
Given the following user profile data (JSON):
{json.dumps(user_data, indent=2)}

Classify the user into ONE of these categories:
- {', '.join(self.categories)}

Respond as a JSON object:
{{
  "persona": <category>,
  "justification": <brief justification for your choice>
}}
"""
        output = self.gemini.generate(prompt)
        try:
            output_clean = clean_json_output(output)
            result = json.loads(output_clean)
            persona = result.get('persona', '')
            justification = result.get('justification', '')
        except Exception as e:
            print(f"[PersonaClassifier] Failed to parse JSON: {e}\nRaw output: {output}")
            persona = ''
            justification = ''
        return persona, justification, prompt, output


# ========== Roadmap Planning Agent ========== #
class RoadmapPlanner:
    """
    Generates a personalized GenAI learning roadmap using multi-step reasoning via Gemini API.
    Implements Think -> Plan -> Rethink logic with justifications.
    """
    def __init__(self, gemini: GeminiAPI):
        self.gemini = gemini

    def plan_roadmap(self, user_data: Dict[str, Any], persona: str) -> Dict[str, Any]:
        # Step 1: Think - Identify topics
        think_prompt = f"""
You are an expert GenAI curriculum designer. Given the user's profile and persona below, identify the most relevant GenAI topics/use-cases for them. For each topic, include a brief justification of why it is relevant for this user.

User Profile:
{json.dumps(user_data, indent=2)}
Persona: {persona}

Respond as a JSON array of objects:
[
  {{"topic": <topic>, "justification": <why this topic is relevant>}}, ...
]
"""
        topics_output = self.gemini.generate(think_prompt)
        try:
            topics = json.loads(clean_json_output(topics_output))
        except Exception as e:
            print(f"[RoadmapPlanner][Think] Failed to parse topics JSON: {e}\nRaw output: {topics_output}")
            topics = []

        # Step 2: Plan - Duration and Structure
        plan_prompt = f"""
Given the user's profile and the following topics (with justifications):
{json.dumps(topics, indent=2)}

Propose a suitable roadmap duration (choose one: 21, 30, or 45 days) and structure the roadmap into levels (e.g., Foundations, Hands-on, Application). Assign topics to levels. Justify your choices based on the user's background, goals, and weekly availability.

Respond as a JSON object:
{{
  "duration_days": <21|30|45>,
  "levels": [
    {{"level": <int>, "title": <level title>, "topics": [<topic>, ...], "justification": <why this structure/leveling>}}, ...
  ],
  "structure_justification": <overall justification>
}}
"""
        structure_output = self.gemini.generate(plan_prompt)
        try:
            structure = json.loads(clean_json_output(structure_output))
        except Exception as e:
            print(f"[RoadmapPlanner][Plan] Failed to parse structure JSON: {e}\nRaw output: {structure_output}")
            structure = {}

        # Step 3: Plan - Activities and Time Allocation
        activities_prompt = f"""
Given the roadmap structure below, the user's learning preference, and their weekly availability, detail the specific learning activities for each topic. Estimate the hours required per activity so that the total fits within the duration and weekly hours. For each activity, provide a justification.

User Profile:
{json.dumps(user_data, indent=2)}
Persona: {persona}
Roadmap Structure:
{json.dumps(structure, indent=2)}

Respond as a JSON object in this format:
{{
  "levels": [
    {{
      "level": <int>,
      "title": <level title>,
      "estimated_hours": <int>,
      "topics": [
        {{
          "topic": <topic>,
          "activity": <activity description>,
          "estimated_hours": <int>,
          "justification": <why this activity/topic for this user>
        }}, ...
      ]
    }}, ...
  ],
  "total_estimated_hours": <int>
}}
"""
        activities_output = self.gemini.generate(activities_prompt)
        try:
            activities = json.loads(clean_json_output(activities_output))
        except Exception as e:
            print(f"[RoadmapPlanner][Activities] Failed to parse activities JSON: {e}\nRaw output: {activities_output}")
            activities = {}

        # Assemble final roadmap_data
        roadmap_data = {
            "user_profile_summary": {
                "persona": persona,
                "domain": user_data.get("domain", ""),
                "goals": user_data.get("goals", []),
                "weekly_availability_hours": user_data.get("weekly_availability_hours", 0)
            },
            "roadmap": {
                "title": f"Personalized GenAI Roadmap for {persona}",
                "duration_days": structure.get("duration_days", 30),
                "total_estimated_hours": activities.get("total_estimated_hours", 0),
                "levels": activities.get("levels", [])
            }
        }
        return roadmap_data

    def identify_topics(self, user_data: dict) -> list:
        """
        Identifies topics for the user. Returns parsed topics list.
        """
        prompt = f"""
You are an expert GenAI curriculum designer. Given the user's profile below, identify the most relevant GenAI topics/use-cases for them. For each topic, include a brief justification of why it is relevant for this user.

User Profile:
{json.dumps(user_data, indent=2)}

Respond as a JSON array of objects:
[
  {{"topic": <topic>, "justification": <why this topic is relevant>}}, ...
]
"""
        output = self.gemini.generate(prompt)
        try:
            topics = json.loads(clean_json_output(output))
        except Exception as e:
            print(f"[RoadmapPlanner][identify_topics] Failed to parse topics JSON: {e}\nRaw output: {output}")
            topics = []
        return topics

    def identify_topics_trace(self, user_data: dict):
        """
        Identifies topics with trace: returns (topics, prompt, raw_response)
        """
        prompt = f"""
You are an expert GenAI curriculum designer. Given the user's profile below, identify the most relevant GenAI topics/use-cases for them. For each topic, include a brief justification of why it is relevant for this user.

User Profile:
{json.dumps(user_data, indent=2)}

Respond as a JSON array of objects:
[
  {{"topic": <topic>, "justification": <why this topic is relevant>}}, ...
]
"""
        output = self.gemini.generate(prompt)
        try:
            topics = json.loads(clean_json_output(output))
        except Exception as e:
            print(f"[RoadmapPlanner][identify_topics_trace] Failed to parse topics JSON: {e}\nRaw output: {output}")
            topics = []
        return topics, prompt, output

    def plan_roadmap_trace(self, user_data: Dict[str, Any], persona: str, topics: list = None):
        """
        Like plan_roadmap, but returns roadmap_data, all prompts, all raw responses for traceability. Accepts topics optionally for parallel compatibility.
        """
        # Step 1: Think - Identify topics
        if topics is None:
            think_prompt = f"""
You are an expert GenAI curriculum designer. Given the user's profile and persona below, identify the most relevant GenAI topics/use-cases for them. For each topic, include a brief justification of why it is relevant for this user.

User Profile:
{json.dumps(user_data, indent=2)}
Persona: {persona}

Respond as a JSON array of objects:
[
  {{"topic": <topic>, "justification": <why this topic is relevant>}}, ...
]
"""
            topics_output = self.gemini.generate(think_prompt)
            try:
                topics = json.loads(clean_json_output(topics_output))
            except Exception as e:
                print(f"[RoadmapPlanner][Think] Failed to parse topics JSON: {e}\nRaw output: {topics_output}")
                topics = []
        else:
            # For trace, still need to provide a prompt and response for the trace
            think_prompt = f"""
You are an expert GenAI curriculum designer. Given the user's profile and persona below, identify the most relevant GenAI topics/use-cases for them. For each topic, include a brief justification of why it is relevant for this user.

User Profile:
{json.dumps(user_data, indent=2)}
Persona: {persona}

Respond as a JSON array of objects:
[
  {{"topic": <topic>, "justification": <why this topic is relevant>}}, ...
]
"""
            topics_output = json.dumps(topics, indent=2) if topics else "[]"

        # Step 2: Plan - Duration and Structure
        plan_prompt = f"""
Given the user's profile and the following topics (with justifications):
{json.dumps(topics, indent=2)}

Propose a suitable roadmap duration (choose one: 21, 30, or 45 days) and structure the roadmap into levels (e.g., Foundations, Hands-on, Application). Assign topics to levels. Justify your choices based on the user's background, goals, and weekly availability.

Respond as a JSON object:
{{
  "duration_days": <21|30|45>,
  "levels": [
    {{"level": <int>, "title": <level title>, "topics": [<topic>, ...], "justification": <why this structure/leveling>}}, ...
  ],
  "structure_justification": <overall justification>
}}
"""
        structure_output = self.gemini.generate(plan_prompt)
        try:
            structure = json.loads(clean_json_output(structure_output))
        except Exception as e:
            print(f"[RoadmapPlanner][Plan] Failed to parse structure JSON: {e}\nRaw output: {structure_output}")
            structure = {}

        # Step 3: Plan - Activities and Time Allocation
        activities_prompt = f"""
Given the roadmap structure below, the user's learning preference, and their weekly availability, detail the specific learning activities for each topic. Estimate the hours required per activity so that the total fits within the duration and weekly hours. For each activity, provide a justification.

User Profile:
{json.dumps(user_data, indent=2)}
Persona: {persona}
Roadmap Structure:
{json.dumps(structure, indent=2)}

Respond as a JSON object in this format:
{{
  "levels": [
    {{
      "level": <int>,
      "title": <level title>,
      "estimated_hours": <int>,
      "topics": [
        {{
          "topic": <topic>,
          "activity": <activity description>,
          "estimated_hours": <int>,
          "justification": <why this activity/topic for this user>
        }}, ...
      ]
    }}, ...
  ],
  "total_estimated_hours": <int>
}}
"""
        activities_output = self.gemini.generate(activities_prompt)
        try:
            activities = json.loads(clean_json_output(activities_output))
        except Exception as e:
            print(f"[RoadmapPlanner][Activities] Failed to parse activities JSON: {e}\nRaw output: {activities_output}")
            activities = {}

        # Assemble final roadmap_data
        roadmap_data = {
            "user_profile_summary": {
                "persona": persona,
                "domain": user_data.get("domain", ""),
                "goals": user_data.get("goals", []),
                "weekly_availability_hours": user_data.get("weekly_availability_hours", 0)
            },
            "roadmap": {
                "title": f"Personalized GenAI Roadmap for {persona}",
                "duration_days": structure.get("duration_days", 30),
                "total_estimated_hours": activities.get("total_estimated_hours", 0),
                "levels": activities.get("levels", [])
            }
        }
        plan_prompts = {
            'topics': think_prompt,
            'structure': plan_prompt,
            'activities': activities_prompt
        }
        plan_responses = {
            'topics': topics_output,
            'structure': structure_output,
            'activities': activities_output
        }
        return roadmap_data, plan_prompts, plan_responses


# ========== Output Formatting Module ========== #
class OutputFormatter:
    """
    Formats the roadmap data into a human-readable table. Optionally generates a PDF.
    """
    def __init__(self):
        pass

    def format_table(self, roadmap_data: Dict[str, Any]) -> str:
        roadmap = roadmap_data.get("roadmap", {})
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"{roadmap.get('title', 'GenAI Roadmap')}")
        lines.append(f"Duration: {roadmap.get('duration_days', 0)} days | Total Hours: {roadmap.get('total_estimated_hours', 0)}")
        lines.append(f"{'='*60}")
        for level in roadmap.get("levels", []):
            lines.append(f"\nLevel {level.get('level', '?')}: {level.get('title', '')} (Est. {level.get('estimated_hours', 0)} hrs)")
            lines.append(f"{'-'*60}")
            for topic in level.get("topics", []):
                lines.append(f"- Topic: {topic.get('topic', '')}")
                lines.append(f"  Activity: {topic.get('activity', '')}")
                lines.append(f"  Est. Hours: {topic.get('estimated_hours', 0)}")
                lines.append(f"  Justification: {topic.get('justification', '')}\n")
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)

    def generate_pdf(self, roadmap_data: Dict[str, Any], output_path: str = "roadmap.pdf") -> str:
        if not REPORTLAB_AVAILABLE:
            print("[OutputFormatter] reportlab not installed. Skipping PDF generation.")
            return ""
        from reportlab.lib.utils import simpleSplit
        roadmap = roadmap_data.get("roadmap", {})
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        margin = 40
        y = height - margin
        line_space = 18
        wrap_width = width - 2 * margin

        def draw_wrapped(text, x, y, font_name, font_size, max_width):
            c.setFont(font_name, font_size)
            lines = simpleSplit(str(text), font_name, font_size, max_width)
            for line in lines:
                c.drawString(x, y, line)
                y -= line_space
            return y

        # Title
        c.setFont("Helvetica-Bold", 16)
        y = draw_wrapped(roadmap.get('title', 'GenAI Roadmap'), margin, y, "Helvetica-Bold", 16, wrap_width)
        y -= 8
        # Duration/Hours
        c.setFont("Helvetica", 12)
        y = draw_wrapped(f"Duration: {roadmap.get('duration_days', 0)} days | Total Hours: {roadmap.get('total_estimated_hours', 0)}", margin, y, "Helvetica", 12, wrap_width)
        y -= 12

        for level in roadmap.get("levels", []):
            # Section header
            c.setFont("Helvetica-Bold", 13)
            y = draw_wrapped(f"Level {level.get('level', '?')}: {level.get('title', '')} (Est. {level.get('estimated_hours', 0)} hrs)", margin, y, "Helvetica-Bold", 13, wrap_width)
            y -= 4
            c.setFont("Helvetica", 11)
            for topic in level.get("topics", []):
                # Topic
                y = draw_wrapped(f"- Topic: {topic.get('topic', '')}", margin + 10, y, "Helvetica-Bold", 11, wrap_width - 10)
                # Activity
                y = draw_wrapped(f"Activity: {topic.get('activity', '')}", margin + 30, y, "Helvetica", 11, wrap_width - 30)
                # Hours
                y = draw_wrapped(f"Est. Hours: {topic.get('estimated_hours', 0)}", margin + 30, y, "Helvetica", 11, wrap_width - 30)
                # Justification
                y = draw_wrapped(f"Justification: {topic.get('justification', '')}", margin + 30, y, "Helvetica-Oblique", 11, wrap_width - 30)
                y -= 8
                if y < 80:
                    c.showPage()
                    y = height - margin
            y -= 8
        c.save()
        return output_path

# ========== Main Orchestrator ========== #
import concurrent.futures

class RoadmapAgent:
    """
    Orchestrates the sequential execution of all modules to generate a personalized roadmap.
    """
    def __init__(self, api_key: str):
        self.gemini = GeminiAPI(api_key)
        self.user_understanding = UserUnderstanding(self.gemini)
        self.persona_classifier = PersonaClassifier(self.gemini)
        self.roadmap_planner = RoadmapPlanner(self.gemini)
        self.output_formatter = OutputFormatter()

    def generate_roadmap(self, resume_text: str, interview_summary_text: str, goals_text: str, generate_pdf: bool = False):
        # Step 1: Understand
        user_data = self.user_understanding.extract_user_data(resume_text, interview_summary_text, goals_text)
        # Step 2: Persona
        persona, _ = self.persona_classifier.classify_persona(user_data)
        # Step 3: Plan
        roadmap_data = self.roadmap_planner.plan_roadmap(user_data, persona)
        roadmap_table = self.output_formatter.format_table(roadmap_data)
        pdf_path = None
        if generate_pdf and REPORTLAB_AVAILABLE:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                pdf_path = tmp.name
            self.output_formatter.generate_pdf(roadmap_data, output_path=pdf_path)
        return roadmap_data, roadmap_table, pdf_path

# ========== Example Usage ========== #
if __name__ == "__main__":
    # Replace with your Gemini API key or set via environment variable
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    agent = RoadmapAgent(GEMINI_API_KEY)

    # Example input texts
    resume_text = """
Experienced software engineer with 5 years in backend development. Skills: Python (Advanced), JavaScript (Intermediate), AWS (Basic), SQL (Advanced). Led teams, contributed to open source, and mentored juniors.
"""
    interview_summary_text = """
The candidate is highly motivated, prefers hands-on learning, and is interested in integrating GenAI into their workflow. Comfortable with Python and cloud platforms. Weekly learning availability: ~8 hours.
"""
    goals_text = """
1. Integrate GenAI into current development workflow
2. Build a GenAI-powered feature for a personal project
3. Understand LLM deployment strategies
"""

    # Generate roadmap (set generate_pdf=True to create PDF if reportlab is installed)
    roadmap_data, roadmap_table, pdf_path = agent.generate_roadmap(
        resume_text, interview_summary_text, goals_text, generate_pdf=False
    )

    print("\n===== Personalized GenAI Roadmap (JSON) =====\n")
    print(json.dumps(roadmap_data, indent=2))
    print("\n===== Roadmap Table =====\n")
    print(roadmap_table)
    if pdf_path:
        print(f"PDF generated at: {pdf_path}")

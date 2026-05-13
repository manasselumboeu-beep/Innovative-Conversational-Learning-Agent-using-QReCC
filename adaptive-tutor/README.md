# AdaptiveTutor: Conversational Learning System

AdaptiveTutor is a modern, pedagogically-intelligent AI assistant designed to adapt its teaching style in real-time based on student proficiency and confusion detection. It provides a high-fidelity chat experience optimized for deep learning and conceptual clarity.

## Key Features

### Pedagogical Intelligence
- **Skill-Based Prompting**: The core of how the tutor adapts its behavior without requiring a massive, static prompt for every turn. Instead of one long prompt, the system dynamically assembles a system prompt by layering several Markdown files (`SKILL.md`) based on the current context:
  - **Prompt Architecture**: Builds the final prompt in `modules/adaptive_teacher.py` using layers like `INDEX.md` (Global Principles) and **Style Skills** (Foundation/Standard/Expert).
  - **Efficiency & Consistency**: Only loads necessary skills to minimize latency while acting as "pedagogical guardrails" to ensure consistent, non-condescending language.
  - **Meta-Prompts**: Uses specialized prompts for background tasks like `question_classification` and `memory_extraction`.
- **Dynamic Style Adaptation**: Automatically switches between **Foundation**, **Standard**, and **Expert** explanation styles based on the student's estimated proficiency.
- **Confusion Detection**: Actively monitors student responses for signs of confusion and provides targeted clarification requests.
- **Session Memory**: Tracks known facts and learning progress across the entire conversation.

### Modern AI Interface
- **ChatGPT-Style Layout**: A clean, centered conversation view with professional avatars and smooth animations.
- **Pure White Theme**: A premium, focused design featuring an elevated "floating" prompt box and subtle off-white backgrounds.
- **Rich Text Support**: Full Markdown integration (bolding, lists, tables) and code syntax highlighting using `react-markdown` and `remark-gfm`.
- **Intelligent Prompt Box**: Auto-resizing textarea with intuitive action buttons and polished interactive feedback.

### Real-time Learning Insights
- **Insights Sidebar**: Dedicated panels for monitoring Teaching Style, Session Statistics (Turns, Proficiency), and a live-updated list of Known Facts.
- **Subtle Metadata**: Pedagogical tags (Style used, Question type, Confusion level) appear elegantly in message headers on hover.

## Tech Stack

- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) with `@tailwindcss/typography`
- **Icons**: [Lucide React](https://lucide.dev/)
- **Components**: [Radix UI](https://www.radix-ui.com/) (Tooltip, Popover, Dialog)
- **Content**: [React Markdown](https://github.com/remarkjs/react-markdown) & [Remark GFM](https://github.com/remarkjs/remark-gfm)
- **Language**: [TypeScript](https://www.typescriptlang.org/)

## Getting Started

Follow these steps to clone and run AdaptiveTutor on your local machine.

### 1. Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.10 or higher
- **Mistral API Key**: Required for the reasoning and teaching engine. Get one at [console.mistral.ai](https://console.mistral.ai/).

### 2. Clone the Repository
```bash
git clone <repository-url>
cd adaptive-tutor
```

### 3. Environment Setup
Create a `.env.local` file in the root directory and add your Mistral API key:
```bash
MISTRAL_API_KEY=your_api_key_here
```

### 4. Backend Setup (Python)
It is recommended to use a virtual environment:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Frontend Setup (Node.js)
```bash
npm install
```

### 6. Running the Project

#### Option A: One-click Start (Recommended)
Use the provided start script to launch both the Python API and the Next.js frontend simultaneously:
```bash
chmod +x start.sh  # Make it executable
./start.sh
```

#### Option B: Manual Start (Separate Terminals)
**Terminal 1: Backend**
```bash
source .venv/bin/activate
uvicorn api.server:app --reload --port 8001
```

**Terminal 2: Frontend**
```bash
npm run dev
```

### 7. Verify the Setup
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API Health**: [http://localhost:8001/api/health](http://localhost:8001/api/health)

## Project Structure

- `/src/app`: Main page logic and layout.
- `/src/components`: Reusable UI elements and pedagogical panels.
- `/src/hooks`: Custom hooks like `useSession` for state management.
- `/src/types`: TypeScript definitions for the learning system.
- `/src/components/ui`: Specialized, high-fidelity components like the `PromptBox`.

---

Developed as an intelligent bridge between AI capabilities and pedagogical excellence.

import api from './api'

export type LearningStyle = 'adaptive' | 'visual' | 'step_by_step' | 'conversational' | 'exam_focused'
export type Difficulty = 'beginner' | 'intermediate' | 'advanced'

export type Message = {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  learningStyle?: LearningStyle
  difficulty?: Difficulty
  provider?: string
}

export type Conversation = {
  id: string
  title: string
  learningStyle: LearningStyle
  difficulty: Difficulty
  messages: Message[]
  createdAt: number
}

// TODO: Replace this mock implementation with a real backend AI Chat / WebSocket endpoint.
// Currently, it integrates with the existing `/prompts/generate` backend API for prompt context
// and simulates a multi-turn dialogue tailored to the selected learning style and difficulty level.

const PROVIDERS = ['GPT-4o', 'Claude 3.5 Sonnet', 'Gemini 1.5 Pro', 'DeepSeek Coder']

export const sendChatMessage = async (
  conversation: Conversation,
  userMessageText: string,
  token?: string
): Promise<Message> => {
  const currentStyle = conversation.learningStyle
  const currentDiff = conversation.difficulty
  const textLower = userMessageText.toLowerCase()

  // Select a random AI Council provider for visual flavor
  const provider = PROVIDERS[Math.floor(Math.random() * PROVIDERS.length)]

  // Attempt to hit the backend prompts endpoint to get high-quality initial summaries if possible,
  // or fall back to our advanced contextual simulator.
  try {
    if (conversation.messages.length <= 2 && userMessageText.length > 5 && userMessageText.length < 100) {
      const response = await api.post<{
        optimized_prompt?: string
        consensus_reasoning?: string
      }>('/prompts/generate', {
        topic: userMessageText,
        learning_style: currentStyle,
        difficulty: currentDiff,
        bloom_level: 'understand',
        options: { skip_variants: true, skip_learning_path: true, timeout: 10 }
      }, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined
      })

      if (response.data.optimized_prompt) {
        return {
          id: 'msg_' + Math.random().toString(36).substr(2, 9),
          role: 'assistant',
          content: `### 🪐 AI Council Consensus Response (${provider})\n\n${response.data.consensus_reasoning || 'I have structured this learning content for you.'}\n\n${response.data.optimized_prompt}`,
          timestamp: Date.now(),
          learningStyle: currentStyle,
          difficulty: currentDiff,
          provider
        }
      }
    }
  } catch (error) {
    console.warn('Backend prompts API not used, falling back to simulated chat response:', error)
  }

  // Sleep to simulate network / generation latency
  await new Promise((resolve) => setTimeout(resolve, 1200))

  let content = ''

  // Contextual helper to match user topic
  let topicName = 'your topic'
  const topics = ['react', 'typescript', 'javascript', 'python', 'css', 'html', 'sql', 'git', 'api', 'database', 'docker', 'machine learning', 'rust']
  for (const t of topics) {
    if (textLower.includes(t)) {
      topicName = t.charAt(0).toUpperCase() + t.slice(1)
      break
    }
  }

  if (topicName === 'your topic' && userMessageText.length < 30) {
    topicName = userMessageText.trim()
  }

  // Tailor response based on the active learning style
  switch (currentStyle) {
    case 'visual':
      content = `### 🎨 Visual Layout & Analysis: **${topicName}**

Here is a visual map of the core concepts for \`${topicName}\` at **${currentDiff}** level:

\`\`\`
+-------------------------------------------------------------+
|                     VISUAL CONCEPT MAP                      |
+-------------------------------------------------------------+
|                                                             |
|   [Core Topic: ${topicName}]                                 |
|          │                                                  |
|          ├──► [Fundamentals] ──► (Syntax & Semantics)        |
|          │                                                  |
|          ├──► [Advanced Features] ──► (Optimization)        |
|          │                                                  |
|          └──► [Use Cases & Practical Applications]          |
|                                                             |
+-------------------------------------------------------------+
\`\`\`

#### Key Architecture Components:
| Component | Purpose | Complexity |
| :--- | :--- | :--- |
| **Foundation Layer** | Establishes the core rules and scope | Simple |
| **Execution Context** | Manages runtime allocations and scopes | Medium (${currentDiff}) |
| **Presentation Tier** | Handles structural layouts and outputs | Visual |

*Visual Tip: Think of this topic as a tree structure, where the roots represent the core configurations and the branches represent runtime functions.*

Would you like me to draw a more detailed schematic or render a code structure for a specific sub-concept?`
      break

    case 'step_by_step':
      content = `### 🪜 Step-by-Step Implementation Guide for **${topicName}**

Let's break down \`${topicName}\` (${currentDiff} difficulty) into a sequence of clear, manageable phases.

#### Step 1: Initial Workspace Setup
First, make sure your environment is configured. Create a file corresponding to your project setup:

\`\`\`javascript
// Step 1: Initialize the configuration block
const config = {
  name: "${topicName}",
  level: "${currentDiff}",
  strictMode: true,
  timestamp: Date.now()
};

console.log("Starting learning track for: " + config.name);
\`\`\`

#### Step 2: Implementation of the Main Handler
Next, write the core execution logic. Here is how we declare the main function block:

\`\`\`typescript
// Step 2: Declare the core handler module
interface Learnable {
  topic: string;
  difficulty: string;
  isReady: boolean;
}

export function executeLearningCycle(item: Learnable): string {
  if (!item.isReady) {
    return \`Preparing \${item.topic}...\\n\`;
  }
  
  // Custom logic based on difficulty level
  const multiplier = item.difficulty === 'advanced' ? 3 : 1.5;
  return \`Successfully executed \${item.topic} with challenge multiplier: \${multiplier}\`;
}

// Example usage:
const currentModule: Learnable = {
  topic: "${topicName}",
  difficulty: "${currentDiff}",
  isReady: true
};
console.log(executeLearningCycle(currentModule));
\`\`\`

#### Step 3: Execution and Verification
1. Run the script in your terminal: \`node workspace.js\`
2. Verify that the output shows the correct difficulty settings (**${currentDiff}**).
3. Validate that error paths handle uninitialized states.

Would you like to write the unit tests for Step 3, or should we refine Step 2 first?`
      break

    case 'conversational':
      content = `### 💬 Let's talk about **${topicName}**!

I'd love to help you wrap your head around this concept. Since we are focusing on a **${currentDiff}** difficulty level, let's start with a simple, everyday analogy.

> **The Analogy:** Think of \`${topicName}\` like a smart library. The library doesn't just store books (data); it helps you search for terms, compiles indexes, and gives you recommendations based on what you've read before. 

At a **${currentDiff}** level, here is the core thing you need to remember:
* We are focused on **efficiency** and **scalability**.
* It is not just about making it work, but making it clean and easy to maintain.
* We want to avoid common pitfalls like memory leaks or redundant computations.

For example, when starting out, people often make the mistake of overcomplicating the setup. Instead, you should keep your functions small and focused on one task.

How does that analogy sound to you? Does it match what you are working on, or should we apply this to a specific coding problem you're trying to solve? Let's discuss!`
      break

    case 'exam_focused':
      content = `### 📝 Exam & Interview Review: **${topicName}**

Welcome to your study guide. This review is tailored for **${currentDiff}**-level exams on \`${topicName}\`.

#### 🔍 Critical Topics to Memorize:
1. **Core Definition**: The fundamental design patterns governing \`${topicName}\`.
2. **Performance Boundaries**: How scale influences runtime operations (Big-O analysis).
3. **Common Trap Questions**: Watch out for implicit scope mutations and configuration overrides.

---

#### 🧠 Practice Quiz:
Try to answer this typical examination question:

**Question:** Which of the following best describes the main trade-off when optimizing \`${topicName}\` at a **${currentDiff}** tier?
* **A)** Increased readability at the cost of higher CPU cycles.
* **B)** Speed and latency benefits vs. memory storage allocation constraints.
* **C)** Easier deployment scripts but limited support for concurrent active users.
* **D)** Higher confidence scores but slower code hot-reloads.

*Tip: Think about resource management. (Reply with A, B, C, or D to see if you got it right!)*

#### 💡 Key Exam Formula:
> **Scale Rule:** $O(N \\log N)$ is typical for advanced lookups, whereas basic iterations run at $O(N)$ complexity.

Let me know your answer, or ask for the detailed explanation of the other options! Excellent prep starts here.`
      break

    case 'adaptive':
    default:
      content = `### 🪐 Adaptive Overview: **${topicName}**

You are currently exploring \`${topicName}\` set to **${currentDiff}** difficulty. I have adapted this module to start with a summary, followed by a deeper dive.

#### 📘 Brief Summary:
\`${topicName}\` is a core pillar in modern software design, responsible for organizing, optimizing, and processing inputs based on structured rules.

#### 💻 Technical Deep-Dive:
To implement this at a **${currentDiff}** tier, check out this reference structure:

\`\`\`json
{
  "module": "${topicName}",
  "difficulty": "${currentDiff}",
  "features": [
    "automatic-optimization",
    "consensus-scoring",
    "responsive-rendering"
  ],
  "isStable": true
}
\`\`\`

Here is a short code outline in Python demonstrating the concept:
\`\`\`python
# Adaptive template for ${topicName}
class LearningSession:
    def __init__(self, topic: str, difficulty: str):
        self.topic = topic
        self.difficulty = difficulty
        self.completed = False

    def get_challenge_score(self) -> float:
        # Scale score based on difficulty
        levels = {"beginner": 1.0, "intermediate": 2.5, "advanced": 5.0}
        return levels.get(self.difficulty.lower(), 1.5)

# Initialize session
session = LearningSession(topic="${topicName}", difficulty="${currentDiff}")
print(f"Session: {session.topic} (Challenge Score: {session.get_challenge_score()})")
\`\`\`

Tell me what aspect of this topic you'd like to adjust. We can dial up the complexity, or zoom in on the source syntax!`
      break
  }

  return {
    id: 'msg_' + Math.random().toString(36).substr(2, 9),
    role: 'assistant',
    content,
    timestamp: Date.now(),
    learningStyle: currentStyle,
    difficulty: currentDiff,
    provider
  }
}

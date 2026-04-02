# 🧠 Brainny

A multi-layer memory engine for AI conversations that remembers context, learns from interactions, and retrieves relevant information intelligently.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/yourusername/brainnny)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Overview

**Brainny** is an intelligent memory system designed to enhance AI chat experiences by storing and retrieving conversational context across multiple cognitive layers. Unlike traditional chatbots that forget past conversations, Brainny maintains persistent memory that evolves with each interaction.

### Key Features

- **🧩 Multi-Layer Memory Architecture**: Inspired by human cognitive memory systems
  - **Working Memory**: Recent conversation context (in-memory cache)
  - **Episodic Memory**: Past conversation sessions with semantic search
  - **Semantic Memory**: Extracted knowledge, preferences, and facts about users
  - **Conversation Logs**: Complete message history with timestamps

- **🔍 Intelligent Context Retrieval**: Combines importance scoring, recency weighting, and semantic similarity to surface the most relevant memories

- **👤 User Authentication**: Secure authentication via Clerk with multi-user support

- **💾 Scalable Storage**: Powered by Snowflake for enterprise-grade data warehousing with vector search capabilities

- **🎨 Modern UI**: Beautiful, responsive Next.js interface with real-time memory visualization

## 🏗️ Architecture

### Technology Stack

#### Frontend (`/client`)
- **Framework**: Next.js 16 with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Authentication**: Clerk
- **UI Components**: Radix UI primitives with shadcn/ui patterns
- **Icons**: Phosphor Icons

#### Backend (`/server`)
- **Framework**: FastAPI (Python)
- **Database**: Snowflake with Cortex AI
- **Vector Search**: Snowflake Cortex embeddings (768 dimensions)
- **Deployment**: AWS Lambda-ready with Mangum adapter
- **Dependencies**: See `requirements.txt`

### Memory Layers Explained

```
┌─────────────────────────────────────────────────┐
│  LAYER 1: Working Memory (In-Memory Cache)     │
│  • Last 5-10 messages                           │
│  • Instant access, no DB queries                │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  LAYER 2: Episodic Memory (Snowflake)          │
│  • Conversation summaries with embeddings       │
│  • Importance scoring & recency weighting       │
│  • Semantic similarity search                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  LAYER 3: Semantic Memory (Snowflake)          │
│  • Extracted preferences, facts, topics         │
│  • Skills, goals, and user patterns             │
│  • Confidence-scored knowledge                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  LAYER 4: Conversation Logs (Snowflake)        │
│  • Complete message history                     │
│  • Timestamped interactions                     │
│  • Session-based organization                   │
└─────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+ and npm/bun
- **Python** 3.11+
- **Snowflake Account** (with Cortex AI enabled)
- **Clerk Account** (for authentication)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/brainnny.git
   cd brainnny
   ```

2. **Setup Backend**
   ```bash
   cd server
   
   # Create virtual environment
   python -m venv lenv
   source lenv/bin/activate  # On Windows: lenv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your Snowflake credentials
   
   # Run migrations
   # Execute SQL files in migrations/ folder in Snowflake
   ```

3. **Setup Frontend**
   ```bash
   cd ../client
   
   # Install dependencies
   npm install  # or: bun install
   
   # Configure environment
   cp .env.example .env.local
   # Edit .env.local with your Clerk keys and API URL
   ```

4. **Run the Application**

   **Terminal 1 - Backend:**
   ```bash
   cd server
   uvicorn app.main:app --reload --port 8000
   ```

   **Terminal 2 - Frontend:**
   ```bash
   cd client
   npm run dev  # or: bun dev
   ```

5. **Access the App**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Configuration

#### Backend Environment Variables (`server/.env`)
```env
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=your-warehouse
SNOWFLAKE_DATABASE=SECOND_BRAIN_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

#### Frontend Environment Variables (`client/.env.local`)
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📖 API Documentation

### Core Endpoints

#### Store Message
```http
POST /conversation
Content-Type: application/json

{
  "user_id": "user_123",
  "session_id": "session_456",
  "message": "Hello, I love JavaScript!",
  "role": "user"
}
```

#### Retrieve Context
```http
POST /retrieve-context
Content-Type: application/json

{
  "user_id": "user_123",
  "query": "What programming languages do I like?",
  "session_id": "session_456",
  "max_episodes": 10,
  "max_semantic": 5,
  "include_recent": 5
}
```

#### Create User Profile
```http
POST /user/{user_id}
```

Full API documentation available at: http://localhost:8000/docs

## 🎯 Use Cases

- **Personal AI Assistant**: Remembers your preferences, past conversations, and context
- **Customer Support**: Maintains conversation history and user preferences
- **Educational Tutoring**: Tracks learning progress and adapts to student needs
- **Mental Health Support**: Maintains therapeutic context across sessions
- **Project Management**: Remembers project details and team interactions

## 🗺️ Roadmap

### Current Version (v2.0.0)
✅ Multi-layer memory architecture  
✅ Clerk authentication  
✅ Snowflake integration with vector search  
✅ Session management  
✅ Real-time memory visualization  

### Planned Features
- [ ] **Memory Export**: Download your conversation history
- [ ] **Advanced Filters**: Filter memories by date, topic, or importance
- [ ] **Multi-modal Memory**: Support for images and files
- [ ] **Memory Summarization**: AI-powered memory consolidation
- [ ] **Collaborative Memory**: Shared team memory spaces
- [ ] **Analytics Dashboard**: Insights into conversation patterns
- [ ] **LLM Integration**: Direct integration with OpenAI, Anthropic, Google
- [ ] **Memory Pruning**: Automatic cleanup of low-value memories
- [ ] **Graph-based Memory**: Knowledge graph for relationship mapping
- [ ] **Mobile App**: iOS and Android clients

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by cognitive science research on human memory systems
- Built with modern web technologies and AI-powered embeddings
- Special thanks to the Snowflake Cortex AI team for vector search capabilities

## 📞 Contact

For questions, suggestions, or collaboration:
- **Issues**: [GitHub Issues](https://github.com/yourusername/brainnny/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/brainnny/discussions)

---

## 📋 Changelog

### [2.0.0] - Current Version

#### 🎉 Major Features
- **Multi-Layer Memory Architecture**: Complete redesign from page-node to cognitive memory layers
  - Working Memory (in-memory cache)
  - Episodic Memory (conversation sessions with embeddings)
  - Semantic Memory (extracted user knowledge)
  - Conversation Logs (complete message history)
  
- **Intelligent Context Retrieval**: Advanced scoring algorithm combining:
  - Semantic similarity (via Snowflake Cortex embeddings)
  - Importance weighting
  - Recency decay
  - Contextual relevance

- **User Authentication**: Clerk integration for secure multi-user support

- **Modern Frontend**: Complete Next.js 16 interface with:
  - Real-time memory panel visualization
  - Session management UI
  - Auto-retrieval toggle
  - Responsive design with Tailwind CSS 4

#### 🏗️ Architecture
- **Backend**: FastAPI with Snowflake integration
- **Database**: Snowflake with Cortex AI for vector search (768-dimensional embeddings)
- **Deployment Ready**: AWS Lambda support via Mangum adapter
- **API Design**: RESTful endpoints with Pydantic validation

#### 📦 Dependencies
- React 19 & Next.js 16
- FastAPI 0.135+
- Snowflake Connector Python 4.3+
- Clerk authentication
- Radix UI & shadcn/ui components

#### 🗄️ Database Schema
- `users` - User profiles and preferences
- `episodes` - Episodic memory with vector embeddings
- `semantic_memory` - Extracted knowledge entries
- `conversation_logs` - Complete message history

#### 🔧 Services
- `llm_service.py` - LLM integration layer
- `memory_service.py` - Memory storage and management
- `retrieval_service.py` - Context retrieval with scoring
- `prompt_service.py` - Prompt engineering utilities

#### 🛣️ Routers
- `/user` - User profile management
- `/conversation` - Message storage
- `/context` - Context retrieval
- `/health` - Health checks

### [1.0.0] - Initial Version (Deprecated)
- Basic page-node architecture
- Simple conversation storage
- No vector search
- No authentication

---

**Built with ❤️ for better AI conversations**
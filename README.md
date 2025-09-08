# Brand Intelligence Platform

Eine Enterprise-Level Plattform, die Social Media, News und Review-Daten in Echtzeit analysiert, um Marken vor Reputationskrisen zu schützen und Marktchancen zu identifizieren.

###  **Phase 3 Complete - Advanced ML Integration**

- **Backend API**: FastAPI with SQLite database + 9 ML endpoints
- **Frontend Dashboard**: Next.js React app running on port 3000
- **Database**: SQLite with sample brands and mentions data
- **ML Pipeline**: BERT sentiment analysis + crisis detection operational
- **Real-time Processing**: Async ML analysis with batch processing
-  **API Endpoints**: 13 total endpoints including 9 ML-specific endpoints
- **BERT Integration**: nlptown/bert-base-multilingual-uncased-sentiment (669MB model)
- **Crisis Detection**: Multi-level threat assessment with keyword matching

### 🎯 **Quick Start - Full ML Pipeline Ready!**

```bash
# Backend with ML (Terminal 1)
cd backend
pip install fastapi uvicorn sqlalchemy aiosqlite transformers torch
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# ML Demo (Terminal 3)
python simple_ml_demo.py

# Access Points:
# 🌐 Dashboard: http://localhost:3000
# 📡 API Docs: http://localhost:8000/docs
# 🤖 ML Endpoints: http://localhost:8000/ml/status
# 💾 Sample Data: http://localhost:8000/api/demo/sample-data
# 🧪 ML Demo: http://localhost:8000/ml/test/demo
```

## 📁 Project Structure (Current Implementation)

```
brand-intelligence-platform/
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py              # odule initialization
│   │   ├── main.py                  # FastAPI app with CORS & ML routes
│   │   ├── core/                    # Core Configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Settings with SQLite support
│   │   │   ├── database.py          # SQLAlchemy async engine
│   │   │   └── init_db.py           # Database initialization
│   │   ├── api/                     # API Router Modules
│   │   │   ├── __init__.py
│   │   │   ├── analytics.py         # Analytics endpoints
│   │   │   ├── brands.py            # Brand management API
│   │   │   ├── mentions.py          # Mention data API
│   │   │   ├── demo.py              # Demo data endpoints
│   │   │   └── ml.py                # 🤖 ML Pipeline API (9 endpoints)
│   │   ├── services/                # Business Logic Services
│   │   │   ├── __init__.py
│   │   │   ├── ml_service.py        # 🧠 Core ML Service orchestrator
│   │   │   ├── data_ingestion.py    # Data collection services
│   │   │   └── notification.py     # Alert and notification system
│   │   ├── ml/                      # 🤖 Machine Learning Components
│   │   │   ├── __init__.py
│   │   │   ├── sentiment/           # Sentiment Analysis Models
│   │   │   │   ├── analyzer.py      # Keyword-based sentiment analyzer
│   │   │   │   ├── bert_analyzer.py # BERT transformer model
│   │   │   │   └── crisis_detector.py # Crisis detection algorithm
│   │   │   ├── preprocessing/       # Text Processing Pipeline
│   │   │   │   └── text_cleaner.py  # Text preprocessing utilities
│   │   │   └── models/              # ML Model Storage
│   │   │       └── (BERT models cached here)
│   │   ├── models/                  # Database Models
│   │   │   ├── __init__.py
│   │   │   ├── brand.py             # Brand model (SQLite compatible)
│   │   │   ├── mention.py           # Mention model with sentiment
│   │   │   └── user.py              # User management model
│   │   └── schemas/                 # Pydantic Data Schemas
│   │       ├── __init__.py
│   │       ├── brand.py             # Brand API schemas
│   │       └── mention.py           # Mention API schemas
│   │       └── mention.py           # Mention model with sentiment
│   ├── brand_intelligence.db        # SQLite database file
│   ├── test_ml_complete.py          # 🧪 ML pipeline comprehensive test
│   ├── test_ml_service.py           # 🔬 ML service unit tests
│   └── .env                         # Environment configuration
│
├── simple_ml_demo.py                # 🚀 Quick ML demo script
├── demo_ml_api.py                   # 📡 Complete API demonstration
├── ML_IMPLEMENTATION_SUMMARY.md     # 📖 Detailed ML implementation docs
│
├── frontend/                        # Next.js React Frontend
│   ├── app/                         # App Router structure
│   │   ├── layout.tsx               # Root layout with fonts
│   │   └── page.tsx                 # Dashboard main page
│   ├── src/
│   │   ├── app.tsx                  # Dashboard component
│   │   ├── components/              # UI Components
│   │   │   └── layout/
│   │   │       └── DashboardLayout.tsx
│   │   ├── services/                # API Services
│   │   │   └── api.ts
│   │   └── globals.css              # TailwindCSS styles
│   ├── package.json                 # Dependencies
│   └── tsconfig.json                # TypeScript config
│
├── scripts/                         # 🔧 Development Scripts
│   └── dev.bat                      # Windows development commands
├── infrastructure/                  # 🔧 Docker & DevOps (ready for scaling)
│   └── docker/
│       ├── docker-compose.yml
│       └── docker-compose.dev.yml
├── Makefile                         # 🔧 Development commands
└── README.md                        # 📖 This file
```

### **API Endpoints** 🔌

```bash
# Core API Endpoints
GET /                           # API status and version
GET /health                     # Health check
GET /api/brands                 # List all brands
GET /api/mentions               # Recent mentions (limit 10)
GET /api/demo/sample-data       # Complete demo dataset

# 🤖 ML Pipeline Endpoints (9 total)
GET  /ml/status                 # ML service status and health
POST /ml/analyze/sentiment      # Single text sentiment analysis
POST /ml/analyze/crisis         # Crisis detection for mentions
POST /ml/analyze/brand-health   # Comprehensive brand health analysis
POST /ml/analyze/batch          # Batch analysis of multiple mentions
GET  /ml/analyze/realtime/{brand} # Real-time streaming analysis
POST /ml/process/mention        # Process new mention through ML pipeline
GET  /ml/test/demo              # Demo ML analysis with sample data
POST /ml/extract/features       # Extract text features and keywords
```

### **Database Schema** 💾

```sql
-- SQLite Tables (Auto-created)
brands (
    id VARCHAR PRIMARY KEY,           -- UUID as string
    name VARCHAR NOT NULL,            -- Brand name
    industry VARCHAR,                 -- Industry sector
    website VARCHAR,                  -- Website URL
    is_active BOOLEAN DEFAULT TRUE,   -- Active status
    created_at DATETIME,              -- Timestamp
    updated_at DATETIME               -- Last update
)

mentions (
    id VARCHAR PRIMARY KEY,           -- UUID as string
    brand_id VARCHAR,                 -- Foreign key to brands
    content VARCHAR,                  -- Mention text
    platform VARCHAR,                 -- Social platform
    sentiment_score FLOAT,            -- 0.0 to 1.0 sentiment
    sentiment_label VARCHAR,          -- positive/negative/neutral
    crisis_probability FLOAT,         -- Crisis risk score
    published_at DATETIME,            -- Original publish time
    likes_count INTEGER,              -- Engagement metrics
    shares_count INTEGER,
    comments_count INTEGER,
    created_at DATETIME               -- Record creation
)
```

## 🛠️ **Technology Stack (Currently Implemented)**

### **Backend Stack** 🔧

- **FastAPI**: High-performance async Python API framework with 13 endpoints
- **SQLAlchemy**: Async ORM with SQLite support
- **Pydantic**: Data validation and settings management
- **SQLite**: Lightweight database (easily upgradeable to PostgreSQL)
- **AsyncIO**: Asynchronous request handling and ML processing
- **CORS**: Cross-origin resource sharing for frontend

### **🤖 ML Stack** 🧠

- **Transformers**: Hugging Face transformers library for BERT models
- **PyTorch**: Deep learning framework for BERT inference
- **BERT Model**: nlptown/bert-base-multilingual-uncased-sentiment (669MB)
- **Crisis Detection**: Custom keyword-based algorithm with threshold scoring
- **Text Processing**: Advanced feature extraction and preprocessing
- **Async ML**: Concurrent sentiment analysis and crisis detection

### **Frontend Stack** 🎨

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript development
- **TailwindCSS**: Utility-first CSS framework
- **React Hooks**: State management with useState/useEffect
- **Responsive Design**: Mobile-first interface

## 🗺️ **Development Roadmap**

### **✅ Phase 1: Foundation (COMPLETED)**

```bash
✅ Docker development environment setup
✅ SQLite database with sample data
✅ FastAPI backend with async endpoints
✅ Next.js dashboard with real-time data
✅ Basic sentiment analysis display
✅ Working API-Frontend communication
```

### **✅ Phase 2: ML Pipeline (COMPLETED)**

```bash
✅ Advanced NLP preprocessing pipeline
✅ BERT-based sentiment analysis model (nlptown/bert-base-multilingual-uncased-sentiment)
✅ Crisis detection algorithm with multi-level classification
✅ Real-time ML data processing with async operations
✅ ML service orchestration with error handling
✅ Comprehensive testing framework
```

### **✅ Phase 3: Real-time ML Integration (COMPLETED)**

```bash
✅ 9 ML API endpoints operational
✅ Sentiment analysis (keyword + BERT hybrid)
✅ Crisis detection with threat level assessment
✅ Brand health scoring algorithm
✅ Batch processing for multiple mentions
✅ Real-time streaming analysis capability
✅ Feature extraction and text analysis
✅ Production-ready ML pipeline with fallbacks
✅ Interactive API documentation
```

### **🔄 Phase 4: Frontend ML Integration (IN PROGRESS)**

```bash
🔄 Dashboard integration with ML endpoints
🔄 Real-time sentiment visualization
🔄 Crisis alert system with notifications
🔄 Brand health metrics dashboard
🔄 Live sentiment trend charts
🔄 Crisis detection monitoring interface
```

### **📋 Phase 5: Production Enhancement (PLANNED)**

```bash
📋 PostgreSQL migration for production
📋 Real social media data ingestion
📋 Advanced ML model training pipeline
📋 Performance optimization and caching
📋 User authentication & authorization
📋 Multi-brand comparison analytics
```

### **🚀 Phase 6: Scale & Deploy (FUTURE)**

```bash
🚀 Kubernetes deployment manifests
🚀 CI/CD pipeline with GitHub Actions
🚀 Monitoring with Prometheus/Grafana
🚀 ML model versioning with MLflow
🚀 Security hardening & HTTPS
🚀 Cloud deployment (AWS/GCP)
```

### **Current Data Pipeline Flow**

```
Text Input → ML Service → Analysis → Results → API Response → Dashboard
     ↓           ↓          ↓         ↓          ↓          ↓
 "I love this!" → MLService → BERT+Keywords → positive(0.8) → JSON → React UI
 "URGENT Issue" → MLService → Crisis Detect → major(0.7) → Alert → Dashboard
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

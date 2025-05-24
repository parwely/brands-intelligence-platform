# Brand Intelligence Platform
## "Real-time Brand Monitoring mit AI-powered Crisis Detection"

Eine Enterprise-Level Plattform, die Social Media, News und Review-Daten in Echtzeit analysiert, um Marken vor Reputationskrisen zu schützen und Marktchancen zu identifizieren.

## 🚀 Current Status: **FUNCTIONAL MVP** ✅

### ✅ **Phase 1 Complete - Working Foundation** 
- ✅ **Backend API**: FastAPI with SQLite database running on port 8000
- ✅ **Frontend Dashboard**: Next.js React app running on port 3000
- ✅ **Database**: SQLite with sample brands and mentions data
- ✅ **API Endpoints**: `/api/brands`, `/api/mentions`, `/api/demo/sample-data`, `/health`
- ✅ **Live Dashboard**: Real-time data display with sentiment analysis
- ✅ **CORS Setup**: Frontend-backend communication working

### 🎯 **Quick Start - It's Running!**
```bash
# Backend (Terminal 1)
cd backend
pip install fastapi uvicorn sqlalchemy aiosqlite
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2) 
cd frontend
npm install
npm run dev

# Access Points:
# 🌐 Dashboard: http://localhost:3000
# 📡 API Docs: http://localhost:8000/docs
# 💾 Sample Data: http://localhost:8000/api/demo/sample-data
```

## 📁 Project Structure (Current Implementation)

```
brand-intelligence-platform/
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py              # odule initialization
│   │   ├── main.py                  # FastAPI app with CORS & routes
│   │   ├── core/                    # Core Configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Settings with SQLite support
│   │   │   ├── database.py          # SQLAlchemy async engine
│   │   │   └── init_db.py           # Database initialization
│   │   └── models/                  # Database Models
│   │       ├── __init__.py
│   │       ├── brand.py             # Brand model (SQLite compatible)
│   │       └── mention.py           # Mention model with sentiment
│   ├── brand_intelligence.db        # SQLite database file
│   └── .env                         # Environment configuration
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

## 🎯 **Live Features Currently Working**

### **Dashboard Features** 📊
- **Brand Monitoring**: 3 sample brands (TechCorp, GreenEnergy, HealthPlus)
- **Metrics Cards**: Total mentions, average sentiment, crisis alerts, engagement
- **Recent Mentions**: Real-time mention feed with sentiment scoring
- **Brand Selector**: Switch between monitored brands
- **Responsive Design**: Mobile-friendly TailwindCSS interface

### **API Endpoints** 🔌
```bash
GET /                           # API status and version
GET /health                     # Health check
GET /api/brands                 # List all brands
GET /api/mentions               # Recent mentions (limit 10)
GET /api/demo/sample-data       # Complete demo dataset
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
- **FastAPI**: High-performance async Python API framework
- **SQLAlchemy**: Async ORM with SQLite support
- **Pydantic**: Data validation and settings management
- **SQLite**: Lightweight database (easily upgradeable to PostgreSQL)
- **AsyncIO**: Asynchronous request handling
- **CORS**: Cross-origin resource sharing for frontend

### **Frontend Stack** 🎨
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript development
- **TailwindCSS**: Utility-first CSS framework
- **React Hooks**: State management with useState/useEffect
- **Responsive Design**: Mobile-first interface

### **Development Tools** 🔨
- **uvicorn**: ASGI server for FastAPI
- **npm/Node.js**: Frontend package management
- **VS Code**: Recommended IDE
- **Git**: Version control

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

### **🔄 Phase 2: ML Pipeline (IN PROGRESS)**
```bash
🔄 Advanced NLP preprocessing pipeline
🔄 BERT-based sentiment analysis model
🔄 Crisis detection algorithm
🔄 Real-time data processing
🔄 ML model training infrastructure
🔄 Redis caching implementation
```

### **📋 Phase 3: Enhanced Features (PLANNED)**
```bash
📋 PostgreSQL migration for production
📋 Real social media data ingestion
📋 Advanced visualization charts
📋 Alert system with notifications
📋 User authentication & authorization
📋 Multi-brand comparison tools
```

### **🚀 Phase 4: Production Ready (FUTURE)**
```bash
🚀 Kubernetes deployment manifests
🚀 CI/CD pipeline with GitHub Actions
🚀 Monitoring with Prometheus/Grafana
🚀 Performance optimization
🚀 Security hardening & HTTPS
🚀 Cloud deployment (AWS/GCP)
```

## 🧠 **ML Pipeline Architecture (Planned)**

### **Data Pipeline Flow**
```
Data Sources → Ingestion → Processing → ML Analysis → Storage → API → Dashboard
     ↓             ↓          ↓           ↓          ↓      ↓       ↓
Twitter API → Kafka → Preprocessing → BERT Model → SQLite → FastAPI → React
News APIs   → Queues → NLP Pipeline → Crisis AI  → Cache  → REST   → Charts
Reddit API  → Stream → Clean Data   → Sentiment  → Redis  → WebSocket → Alerts
```

### **ML Components (Development Priority)**
1. **🔄 Sentiment Analyzer** (In Progress)
   - BERT-based transformer model
   - Multi-language support
   - Confidence scoring
   - Real-time inference

2. **📋 Crisis Detection** (Planned)
   - Anomaly detection algorithms
   - Trend analysis
   - Alert threshold configuration
   - Severity classification

3. **🚀 Data Ingestion** (Future)
   - Twitter API integration
   - News API collectors
   - Reddit sentiment tracking
   - Real-time streaming

## 🎯 **Next Development Steps**

### **Immediate (Next 1-2 weeks)**
1. **Implement Redis caching** for better performance
2. **Add real sentiment ML model** instead of static scores
3. **Create brand management UI** (add/edit/delete brands)
4. **Add time-based filtering** for mentions

### **Short-term (Next month)**
1. **PostgreSQL migration** for better scalability
2. **Real Twitter API integration** for live data
3. **Advanced charts** with Chart.js/D3.js
4. **User authentication** system

### **Medium-term (Next quarter)**
1. **ML model training pipeline** with MLflow
2. **Crisis detection algorithms**
3. **Real-time notifications** system
4. **Competitive analysis** features

## 🔧 **Quick Development Commands**

```bash
# Start development environment
make backend-dev    # Start backend only
make frontend-dev   # Start frontend only

# Database operations
python -c "from app.core.init_db import init_database; import asyncio; asyncio.run(init_database())"

# View logs and debug
tail -f backend/logs/app.log
curl http://localhost:8000/api/demo/sample-data | jq

# Run tests (when implemented)
pytest backend/tests/
npm test --prefix frontend
```

## 🎉 **Success Metrics**

- ✅ **Backend API**: Responding on http://localhost:8000
- ✅ **Frontend Dashboard**: Loading on http://localhost:3000  
- ✅ **Database**: 3 brands, 9 mentions loaded successfully
- ✅ **API Communication**: CORS working, data flowing
- ✅ **UI Components**: Responsive dashboard with metrics
- ✅ **Development Ready**: Easy to extend and modify

## 📞 **Getting Help**

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Sample Data**: http://localhost:8000/api/demo/sample-data
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:3000
  
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI, React, and SQLAlchemy
- Uses TailwindCSS for styling
- Inspired by enterprise brand monitoring solutions

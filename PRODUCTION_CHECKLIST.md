# 🚀 PRODUCTION DEPLOYMENT CHECKLIST

## Pre-Deployment Security

### 1. Environment Variables
- [ ] Change `SECRET_KEY` to a strong random value
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Move all secrets to environment variables
- [ ] Create `.env` file (never commit to git)
- [ ] Use different secrets for dev/staging/production

### 2. CORS Configuration
- [ ] Update `backend/app/main.py` CORS settings
- [ ] Replace `allow_origins=["*"]` with specific domains
  ```python
  allow_origins=[
      "https://yourdomain.com",
      "https://www.yourdomain.com"
  ]
  ```

### 3. Database Security
- [ ] Use MongoDB Atlas or managed database
- [ ] Enable authentication on MongoDB
- [ ] Use connection string with credentials
- [ ] Enable SSL/TLS for database connections
- [ ] Set up database backups
- [ ] Configure replica sets for high availability

### 4. API Security
- [ ] Add rate limiting (use `slowapi`)
- [ ] Implement request validation
- [ ] Add input sanitization
- [ ] Enable HTTPS only
- [ ] Set secure cookie flags
- [ ] Add CSRF protection
- [ ] Implement API key rotation

### 5. Authentication
- [ ] Increase password minimum length to 8+
- [ ] Add password complexity requirements
- [ ] Implement account lockout after failed attempts
- [ ] Add email verification
- [ ] Implement password reset flow
- [ ] Add 2FA (optional but recommended)
- [ ] Set shorter JWT expiration (e.g., 1 hour)
- [ ] Implement refresh tokens

## Infrastructure Setup

### 1. Backend Deployment

#### Option A: Docker
```bash
# Build image
docker build -t triage-x-backend ./backend

# Run container
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=$SECRET_KEY \
  -e MONGO_URL=$MONGO_URL \
  --name triage-backend \
  triage-x-backend
```

#### Option B: Systemd Service (Linux)
```bash
# Create service file: /etc/systemd/system/triage-backend.service
[Unit]
Description=Triage-X Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/triage-x/backend
Environment="PATH=/opt/triage-x/backend/.venv/bin"
ExecStart=/opt/triage-x/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Option C: Cloud Platforms
- **AWS**: Elastic Beanstalk, ECS, or Lambda
- **Google Cloud**: App Engine or Cloud Run
- **Azure**: App Service
- **Heroku**: Simple deployment with Procfile

### 2. Frontend Deployment

#### Build Production Bundle
```bash
cd frontend
npm run build
```

#### Option A: Static Hosting
- **Netlify**: Connect GitHub repo, auto-deploy
- **Vercel**: Similar to Netlify
- **AWS S3 + CloudFront**: Static hosting with CDN
- **GitHub Pages**: Free for public repos

#### Option B: Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /var/www/triage-x/frontend/build;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Database Setup

#### MongoDB Atlas (Recommended)
1. Create account at mongodb.com/cloud/atlas
2. Create cluster
3. Whitelist IP addresses
4. Create database user
5. Get connection string
6. Update `MONGO_URL` environment variable

#### Self-Hosted MongoDB
```bash
# Install MongoDB
# Enable authentication
mongosh
> use admin
> db.createUser({
    user: "triageAdmin",
    pwd: "strongPassword",
    roles: ["readWrite", "dbAdmin"]
  })

# Update connection string
MONGO_URL=mongodb://triageAdmin:strongPassword@localhost:27017/triage_system
```

## Monitoring & Logging

### 1. Application Monitoring
- [ ] Set up APM (Application Performance Monitoring)
  - Datadog
  - New Relic
  - AWS CloudWatch
- [ ] Monitor API response times
- [ ] Track error rates
- [ ] Set up alerts for critical issues

### 2. Error Tracking
- [ ] Integrate Sentry or similar
  ```python
  import sentry_sdk
  sentry_sdk.init(dsn="your-dsn")
  ```
- [ ] Configure error notifications
- [ ] Set up error grouping

### 3. Logging
- [ ] Configure structured logging
- [ ] Set up log aggregation (ELK, Splunk, CloudWatch)
- [ ] Implement log rotation
- [ ] Set appropriate log levels
- [ ] Remove sensitive data from logs

### 4. Health Checks
- [ ] Implement comprehensive health check endpoint
- [ ] Monitor database connectivity
- [ ] Check ML model availability
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)

## Performance Optimization

### 1. Backend
- [ ] Enable Gzip compression
- [ ] Implement caching (Redis)
- [ ] Use connection pooling for database
- [ ] Optimize database queries
- [ ] Add database indexes
- [ ] Use async operations where possible

### 2. Frontend
- [ ] Enable code splitting
- [ ] Lazy load components
- [ ] Optimize images
- [ ] Use CDN for static assets
- [ ] Enable browser caching
- [ ] Minify CSS/JS

### 3. Database
- [ ] Create indexes on frequently queried fields
  ```javascript
  db.cases.createIndex({ timestamp: -1 })
  db.cases.createIndex({ severity: 1 })
  db.cases.createIndex({ ambulance_number: 1, timestamp: -1 })
  ```
- [ ] Implement data archiving for old cases
- [ ] Set up database monitoring

## Backup & Recovery

### 1. Database Backups
- [ ] Set up automated daily backups
- [ ] Test backup restoration
- [ ] Store backups in different location
- [ ] Implement point-in-time recovery

### 2. Application Backups
- [ ] Version control (Git)
- [ ] Tag releases
- [ ] Document deployment process
- [ ] Keep rollback plan ready

## Testing

### 1. Pre-Deployment Tests
- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Perform load testing
- [ ] Security scanning
- [ ] Penetration testing

### 2. Staging Environment
- [ ] Deploy to staging first
- [ ] Test all features
- [ ] Verify integrations
- [ ] Check performance
- [ ] Review logs

## Documentation

- [ ] Update API documentation
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document environment variables
- [ ] Create user guides
- [ ] Document backup/recovery procedures

## Compliance & Legal

- [ ] Review data privacy requirements (GDPR, HIPAA)
- [ ] Implement data encryption at rest
- [ ] Implement data encryption in transit
- [ ] Add privacy policy
- [ ] Add terms of service
- [ ] Implement audit logging
- [ ] Set up data retention policies

## Post-Deployment

### 1. Immediate Actions
- [ ] Verify all services are running
- [ ] Check health endpoints
- [ ] Monitor error rates
- [ ] Review logs for issues
- [ ] Test critical user flows

### 2. Ongoing Maintenance
- [ ] Set up automated dependency updates
- [ ] Schedule regular security audits
- [ ] Monitor performance metrics
- [ ] Review and optimize costs
- [ ] Keep documentation updated

## Quick Deployment Commands

### Docker Compose (Recommended for Quick Deploy)
```bash
# Production docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - MONGO_URL=${MONGO_URL}
      - ENVIRONMENT=production
    restart: always
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes (For Scale)
```bash
# Create namespace
kubectl create namespace triage-x

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Expose services
kubectl apply -f k8s/ingress.yaml
```

## Emergency Procedures

### Rollback
```bash
# Docker
docker-compose down
docker-compose -f docker-compose.backup.yml up -d

# Git
git revert HEAD
git push origin main
```

### Database Recovery
```bash
# Restore from backup
mongorestore --uri="mongodb://..." --archive=backup.archive
```

## Support Contacts

- [ ] Set up on-call rotation
- [ ] Document escalation procedures
- [ ] Create incident response plan
- [ ] Set up status page

---

**Remember**: Never deploy to production on Friday! 😄

**Last Updated**: 2026-04-11

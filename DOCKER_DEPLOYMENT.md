# Docker Deployment Guide

## Quick Start

### Development Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### Production Deployment
```bash
# Build and run with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile production up --build -d
```

## Environment Setup

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```bash
OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-4
MAX_TOKENS=1000
TEMPERATURE=0.1
RISK_THRESHOLD_HIGH=75
RISK_THRESHOLD_MEDIUM=40
APPROVED_DOMAINS=internal-ai.local,ai.company.com
```

## Access the Application

- **Development**: http://localhost:8501
- **Production with Nginx**: http://localhost

## Docker Commands

### Build only
```bash
docker build -t ai-sentinel .
```

### Run standalone container
```bash
docker run -p 8501:8501 --env-file .env ai-sentinel
```

### View logs
```bash
docker-compose logs -f ai-sentinel
```

### Stop the application
```bash
docker-compose down
```

### Clean up (remove containers, images, volumes)
```bash
docker-compose down -v --rmi all
```

## Production Considerations

### SSL/TLS Setup
1. Place SSL certificates in `./ssl/` directory:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key

2. Uncomment HTTPS configuration in `nginx.conf`

### Resource Limits
Production configuration includes:
- CPU limit: 2 cores
- Memory limit: 2GB
- Automatic restart policy

### Monitoring
- Health checks enabled on port 8501
- Nginx health check on `/health` endpoint
- Application logs available via `docker-compose logs`

## Optional Services

### Redis for Session Management
```bash
docker-compose --profile redis up -d
```

### Scaling
```bash
# Scale to multiple instances
docker-compose up --scale ai-sentinel=3 -d
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8501 and 80/443 are available
2. **Environment variables**: Verify `.env` file is properly configured
3. **Permission issues**: Check Docker permissions and volume mounts

### Debug Mode
```bash
# Run with debug logging
docker-compose run --rm ai-sentinel streamlit run app.py --logger.level=debug
```

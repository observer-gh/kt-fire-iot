# Fire IoT Dashboard

Next.js + Tailwind dashboard for the Fire IoT MSA platform.

## Features

- **Custom Theme**: Safety-orange accent colors with status indicators
- **Dark/Light Mode**: Automatic theme switching
- **Responsive Design**: Mobile-first approach
- **Containerized**: Docker support for consistent deployment
- **Real-time Connection**: Connects to DataLake service

## Quick Start

### With Docker Compose (Recommended)
```bash
# Start all services including dashboard
docker-compose up -d

# Start just dashboard and dependencies
docker-compose up -d datalake dashboard
```

### Local Development
```bash
# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8084" > .env.local

# Start development server
npm run dev
```

### Docker Deployment
```bash
# Build the image
docker build -t fire-iot-dashboard .

# Run the container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://datalake:8080 fire-iot-dashboard
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8084)

## Theme

Custom Tailwind theme with:
- Safety-orange primary color
- Status colors (ok, warn, emergency, info)
- Dark/light mode support
- Predefined component classes (card, btn, badge)

## Project Structure

```
dashboard/
├── src/
│   └── app/
│       ├── globals.css    # Custom theme
│       ├── layout.tsx     # Root layout
│       ├── page.tsx       # Main dashboard
│       └── api.ts         # DataLake API client
├── Dockerfile            # Container configuration
├── next.config.ts        # Next.js config
└── package.json
```

## Connection Status

The dashboard displays real-time connection status to DataLake:
- **Connected**: Green badge with health data
- **Error**: Red badge with error details
- **Loading**: Gray badge while connecting

## Access Points

- **Dashboard**: http://localhost:3000
- **DataLake API**: http://localhost:8084
- **API Documentation**: http://localhost:8084/docs

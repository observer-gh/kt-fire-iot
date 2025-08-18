# Fire IoT Dashboard

Next.js + Tailwind dashboard for the Fire IoT MSA platform.

## Features

- **Custom Theme**: Safety-orange accent colors with status indicators
- **Dark/Light Mode**: Automatic theme switching
- **Responsive Design**: Mobile-first approach
- **Containerized**: Docker support for consistent deployment

## Quick Start

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
# Create .env.local
NEXT_PUBLIC_API_URL=http://localhost:8080
```

3. Start development server:
```bash
npm run dev
```

### Docker Deployment

1. Build the image:
```bash
docker build -t fire-iot-dashboard .
```

2. Run the container:
```bash
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8080 fire-iot-dashboard
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8080)

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
│       └── page.tsx       # Main dashboard
├── Dockerfile            # Container configuration
├── next.config.ts        # Next.js config
└── package.json
```

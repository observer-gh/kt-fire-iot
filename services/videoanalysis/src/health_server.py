import threading
import time
from datetime import datetime
from flask import Flask, jsonify
from loguru import logger
from .config import Config
from .event_publisher import EventPublisher


class HealthServer:
    """Health check server for videoanalysis service"""

    def __init__(self, frame_processor=None, ws_client=None):
        self.app = Flask(__name__)
        self.frame_processor = frame_processor
        self.ws_client = ws_client
        self.event_publisher = EventPublisher()
        self.start_time = datetime.utcnow()
        self.server_thread = None
        self.running = False

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register Flask routes"""

        @self.app.route('/healthz', methods=['GET'])
        def health_check():
            """Basic health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'videoanalysis',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
            })

        @self.app.route('/healthz/detailed', methods=['GET'])
        def detailed_health_check():
            """Detailed health check with all service components"""
            health_status = {
                'status': 'healthy',
                'service': 'videoanalysis',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'environment': Config.ENVIRONMENT,
                'components': {}
            }

            # Event Publisher Health
            health_status['components']['event_publisher'] = {
                'status': 'healthy' if self.event_publisher.is_available() else 'unhealthy',
                'type': 'kafka' if Config.ENVIRONMENT == 'local' else 'eventhub',
                'available': self.event_publisher.is_available()
            }

            # WebSocket Client Health
            if self.ws_client:
                health_status['components']['websocket'] = {
                    'status': 'healthy' if self.ws_client.is_connected() else 'disconnected',
                    'connected': self.ws_client.is_connected(),
                    'url': Config.WEBSOCKET_URL
                }
            else:
                health_status['components']['websocket'] = {
                    'status': 'not_initialized',
                    'connected': False
                }

            # Frame Processor Health
            if self.frame_processor:
                stats = self.frame_processor.get_frame_stats()
                health_status['components']['frame_processor'] = {
                    'status': 'healthy',
                    'total_frames_processed': stats.get('total_frames_processed', 0),
                    'last_frame_time': stats.get('last_frame_time', None),
                    'azure_vision_available': self.frame_processor.azure_vision_client is not None
                }
            else:
                health_status['components']['frame_processor'] = {
                    'status': 'not_initialized'
                }

            # Azure Vision Health
            health_status['components']['azure_vision'] = {
                'status': 'available' if Config.AZURE_VISION_ENDPOINT and Config.AZURE_VISION_KEY else 'not_configured',
                'endpoint_configured': bool(Config.AZURE_VISION_ENDPOINT),
                'key_configured': bool(Config.AZURE_VISION_KEY)
            }

            # Overall status
            all_healthy = all(
                comp.get('status') in ['healthy', 'available', 'disconnected']
                for comp in health_status['components'].values()
            )
            health_status['status'] = 'healthy' if all_healthy else 'degraded'

            return jsonify(health_status)

        @self.app.route('/healthz/ready', methods=['GET'])
        def readiness_check():
            """Readiness check - service is ready to receive traffic"""
            # Service is ready if it can start (basic dependencies met)
            ready = (
                self.event_publisher.is_available() and
                Config.AZURE_VISION_ENDPOINT is not None and
                Config.AZURE_VISION_KEY is not None
            )

            return jsonify({
                'ready': ready,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200 if ready else 503

        @self.app.route('/healthz/live', methods=['GET'])
        def liveness_check():
            """Liveness check - service is alive and running"""
            return jsonify({
                'alive': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

    def start(self):
        """Start the health server in a separate thread"""
        if self.running:
            return

        self.running = True
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()
        logger.info(f"Health server started on port {Config.HEALTH_PORT}")

    def _run_server(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host='0.0.0.0',
                port=Config.HEALTH_PORT,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Health server error: {e}")

    def stop(self):
        """Stop the health server"""
        self.running = False
        logger.info("Health server stopped")

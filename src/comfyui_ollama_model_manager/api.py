"""ComfyUI API routes for Ollama model management."""

from typing import Any, Dict

from .async_utils import run_async
from .log_config import get_logger
from .ollama_client import fetch_models_from_ollama

log = get_logger()


def setup_api_routes():
    """
    Register custom API routes with ComfyUI's server.
    This is called when the extension loads.
    """
    try:
        # Import ComfyUI's server - this will only work when running in ComfyUI
        import server
        from aiohttp import web
        
        routes = server.PromptServer.instance.routes
        
        @routes.get("/ollama/models")
        async def fetch_models_api(request):
            """
            API endpoint to fetch models from Ollama without CORS issues.
            
            Query params:
                endpoint: Ollama server URL (default: http://localhost:11434)
            
            Returns:
                JSON response with models list or error
            """
            try:
                endpoint = request.rel_url.query.get("endpoint", "http://localhost:11434")
                log.info(f"🌐 API request to fetch models from {endpoint}")
                
                # Fetch models using our async client
                models = await fetch_models_from_ollama(endpoint)
                
                return web.json_response({
                    "success": True,
                    "models": models,
                    "count": len(models),
                    "endpoint": endpoint
                })
                
            except Exception as e:
                log.error(f"❌ API error fetching models: {e}")
                return web.json_response({
                    "success": False,
                    "error": str(e)
                }, status=500)
        
        log.info("✅ Registered Ollama API route: GET /ollama/models")
        
    except ImportError:
        # Not running in ComfyUI context (e.g., during testing)
        log.debug("ComfyUI server not available, skipping API routes registration")

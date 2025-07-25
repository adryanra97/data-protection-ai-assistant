"""
Data Protection AI Assistant - Main Application Entry Point

This module serves as the main entry point for the Data Protection AI Assistant,
providing options to run the API server, Gradio UI, or both.

Author: Adryan R A
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings
from src.utils.logging_config import setup_logging


def run_api():
    """Run the FastAPI server."""
    try:
        import uvicorn
        from src.api.main import app
        
        logger.info("Starting Data Protection AI Assistant API...")
        
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)


def run_ui():
    """Run the Gradio web interface."""
    try:
        from src.ui.gradio_app import launch_interface
        
        logger.info("Starting Data Protection AI Assistant Web Interface...")
        
        launch_interface(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=settings.DEBUG
        )
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start web interface: {e}")
        sys.exit(1)


async def run_both():
    """Run both API and UI servers concurrently."""
    import multiprocessing
    
    logger.info("Starting both API server and Web Interface...")
    
    # Start API server in a separate process
    api_process = multiprocessing.Process(target=run_api)
    api_process.start()
    
    # Wait a moment for API to start
    await asyncio.sleep(3)
    
    try:
        # Start UI (this will block)
        run_ui()
    finally:
        # Cleanup API process
        if api_process.is_alive():
            api_process.terminate()
            api_process.join()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Data Protection AI Assistant - Legal Question Answering System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --api          # Run only the API server
  python main.py --ui           # Run only the web interface  
  python main.py --both         # Run both API and UI
  python main.py --api --debug  # Run API with debug mode
        """
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run the FastAPI server"
    )
    
    parser.add_argument(
        "--ui",
        action="store_true", 
        help="Run the Gradio web interface"
    )
    
    parser.add_argument(
        "--both",
        action="store_true",
        help="Run both API server and web interface"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (default: logs to console only)"
    )
    
    args = parser.parse_args()
    
    # Set debug mode if specified
    if args.debug:
        import os
        os.environ["DEBUG"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Setup logging
    setup_logging(args.log_file)
    global logger
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Data Protection AI Assistant")
    logger.info("Author: Adryan R A")
    logger.info("Version: 1.0.0")
    logger.info("=" * 60)
    
    # Check if no arguments provided
    if not (args.api or args.ui or args.both):
        logger.info("No mode specified. Running both API and UI by default.")
        args.both = True
    
    try:
        if args.both:
            asyncio.run(run_both())
        elif args.api:
            run_api()
        elif args.ui:
            run_ui()
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

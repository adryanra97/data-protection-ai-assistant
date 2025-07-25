"""
Legacy Files Notice

These files are the original implementation of the Data Protection AI Assistant.
They have been moved here to maintain backward compatibility while the new 
structured implementation is in the src/ directory.

Author: Adryan R A

Files moved:
- config.py -> src/core/config.py (enhanced)
- search_engine.py -> src/services/search_engine.py (enhanced)
- ingest.py -> src/services/ingestion.py (enhanced)
- tools.py -> src/agents/tools.py (enhanced)
- qa_engine.py -> src/agents/qa_engine.py (enhanced)
- utils.py -> src/utils/document_processor.py (enhanced)
- ui.py -> src/ui/gradio_app.py (enhanced)

The new implementation provides:
- Better error handling and logging
- Professional code documentation
- Type hints and validation
- Comprehensive testing
- Modular architecture
- Configuration management
- Health monitoring
- API documentation

To use the new implementation, run:
python main.py --both

To use the legacy implementation (not recommended):
python legacy/main_legacy.py
"""

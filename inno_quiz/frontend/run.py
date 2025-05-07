import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Set PYTHONPATH to include the project root
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + os.pathsep + str(project_root)

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Point to the app/main.py file
    app_path = os.path.join(project_root, "frontend", "app", "main.py")
    
    # Run Streamlit CLI with our app
    sys.argv = ["streamlit", "run", app_path, "--server.port=8501", "--server.address=0.0.0.0"]
    stcli.main() 
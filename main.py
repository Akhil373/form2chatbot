import subprocess
import sys

subprocess.run([sys.executable, "extractor_tui.py"])
subprocess.run([sys.executable, "chat_tui.py"])
subprocess.run([sys.executable, "form_agent.py"])

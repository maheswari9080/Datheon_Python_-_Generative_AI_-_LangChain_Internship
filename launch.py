"""
AI Research Workbench - Master Application Launcher CLI
Provides unified process orchestration for launching individual tasks or running the entire suite.
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

TASKS = {
    1: {
        "name": "Task 1: Structured Extractor",
        "dir": ROOT_DIR / "task1-structured-extractor",
        "command": [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        "url": "http://localhost:8501",
        "type": "streamlit"
    },
    2: {
        "name": "Task 2: RAG Document Research",
        "dir": ROOT_DIR / "task2-rag-research",
        "command": [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8502"],
        "url": "http://localhost:8502",
        "type": "streamlit"
    },
    3: {
        "name": "Task 3: Autonomous Research Agent",
        "dir": ROOT_DIR / "task3-research-agent",
        "command": [sys.executable, "main.py"],
        "url": "Console CLI Application",
        "type": "cli"
    },
    4: {
        "name": "Task 4: Conversation Studio",
        "dir": ROOT_DIR / "task4-conversation-studio",
        "command": [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8504"],
        "url": "http://localhost:8504",
        "type": "streamlit"
    }
}


def print_banner():
    banner = """
======================================================================
  AI RESEARCH WORKBENCH - CENTRAL LAUNCHER & ORCHESTRATOR
  Unified Management for Intelligent Systems Suite (Tasks 1 - 4)
======================================================================
    """
    print(banner)


def run_task(task_id: int):
    config = TASKS.get(task_id)
    if not config:
        print(f"Error: Invalid task ID {task_id}. Supported tasks: 1, 2, 3, 4.")
        return

    print(f"\n[Launching {config['name']}]...")
    print(f"Directory: {config['dir']}")
    print(f"Access URL: {config['url']}")
    print(f"Command:   {' '.join(config['command'])}\n")
    
    try:
        subprocess.run(config["command"], cwd=str(config["dir"]), check=True)
    except KeyboardInterrupt:
        print(f"\n[{config['name']} stopped by user].")
    except Exception as e:
        print(f"Process terminated with error: {e}")


def run_tests():
    print("\n[Executing Full Pytest Verification Suite across all 4 tasks]...\n")
    test_dirs = [
        "task1-structured-extractor/tests/",
        "task2-rag-research/tests/",
        "task3-research-agent/tests/",
        "task4-conversation-studio/tests/"
    ]
    cmd = [sys.executable, "-m", "pytest"] + test_dirs + ["-v"]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    sys.exit(res.returncode)


def run_all():
    print("\n[Launching all web applications simultaneously]...")
    processes = []
    
    # Launch tasks 1, 2, and 4
    for tid in (1, 2, 4):
        cfg = TASKS[tid]
        print(f"[*] Starting {cfg['name']} -> {cfg['url']}")
        p = subprocess.Popen(cfg["command"], cwd=str(cfg["dir"]))
        processes.append((cfg["name"], p))
        time.sleep(1.5)

    print("\n[All web services initiated successfully!]")
    print("Task 1 Extractor:           http://localhost:8501")
    print("Task 2 Document RAG:        http://localhost:8502")
    print("Task 4 Conversation Studio: http://localhost:8504")
    print("\nPress Ctrl+C to terminate all services...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all services...")
        for name, p in processes:
            p.terminate()
        print("All processes cleanly terminated.")


def main():
    parser = argparse.ArgumentParser(description="AI Research Workbench Launcher")
    parser.add_argument("--task", type=int, choices=[1, 2, 3, 4], help="Run specific task application")
    parser.add_argument("--all", action="store_true", help="Launch all web applications simultaneously")
    parser.add_argument("--test", action="store_true", help="Run full automated verification test suite")

    args = parser.parse_args()
    print_banner()

    if args.test:
        run_tests()
    elif args.all:
        run_all()
    elif args.task:
        run_task(args.task)
    else:
        print("Select an option to launch:")
        print("  1) Task 1: Structured Extractor (Streamlit port 8501)")
        print("  2) Task 2: RAG Document Research (Streamlit port 8502)")
        print("  3) Task 3: Autonomous Research Agent (Console CLI)")
        print("  4) Task 4: Conversation Studio (Streamlit port 8504)")
        print("  5) Run All Web Applications (Ports 8501, 8502, 8504)")
        print("  6) Run Full Automated Test Suite (39 Pytest tests)")
        print("  0) Exit\n")
        try:
            choice = input("Enter choice [1-6]: ").strip()
            if choice == "1":
                run_task(1)
            elif choice == "2":
                run_task(2)
            elif choice == "3":
                run_task(3)
            elif choice == "4":
                run_task(4)
            elif choice == "5":
                run_all()
            elif choice == "6":
                run_tests()
            else:
                print("Exiting.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script to create the project structure for PartSelect Chat Agent
Run this from your instalily directory
"""

import os
import json

def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        "backend",
        "backend/agents", 
        "backend/data",
        "backend/models",
        "backend/utils",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/styles",
        "frontend/public"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
        
        # Create __init__.py files for Python packages
        if directory.startswith("backend") and directory != "backend":
            init_file = os.path.join(directory, "__init__.py")
            open(init_file, 'a').close()
            print(f"Created: {init_file}")

def main():
    """Main setup function"""
    print("Setting up PartSelect Chat Agent project structure...")
    
    # Create directories
    create_directory_structure()
    
    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Copy the provided code files to their respective locations")
    print("2. Install backend dependencies: pip install -r requirements.txt")
    print("3. Navigate to frontend/ and run: npm install")
    print("4. Start the backend: cd backend && uvicorn main:app --reload")
    print("5. Start the frontend: cd frontend && npm start")
    print("\nMake sure your .env file has OPENAI_API_KEY and/or DEEPSEEK_API_KEY set!")

if __name__ == "__main__":
    main()
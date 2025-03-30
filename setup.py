import os


def create_directory_structure():
    """Create the necessary directory structure for the application."""
    directories = ["templates", "static/css", "static/js"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


if __name__ == "__main__":
    create_directory_structure()
    print("Directory structure created successfully!")

from app import create_app
import os, sys

app = create_app()
if __name__ == '__main__':
    app.run()
from app import create_app
import webview

app = create_app()
if __name__ == '__main__':
    window = webview.create_window("RentalManager", app)
    webview.start()
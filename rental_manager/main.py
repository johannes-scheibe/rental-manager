from website import create_app
from website.database import db_service

app = create_app()

if __name__ == '__main__':
    app.config["CLIENT_AGREEMENTS"] = "C:/Users/Johannes/Desktop/VSProjekte/RentalManager/website/static/agreements/"
    app.run(debug=True)
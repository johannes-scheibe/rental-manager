from RentalManager.website import create_app
from RentalManager.website.database import db_service
import os

app = create_app()
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website/static/agreements/")
app.config["CLIENT_AGREEMENTS"] = path

if __name__ == '__main__':    
    app.run(host= "0.0.0.0", debug=True)
    #app.run(debug=True)

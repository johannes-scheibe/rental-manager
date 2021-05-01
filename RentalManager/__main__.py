from rental_manager.website import create_app
from rental_manager.website.database import db_service
import os
app = create_app()

if __name__ == '__main__':
    path = os.path.join(os.path.abspath("rental_manager"), "website/static/agreements/")
    app.config["CLIENT_AGREEMENTS"] = path
    #app.run(host= "0.0.0.0", port=80, debug=True)
    app.run(debug=True)

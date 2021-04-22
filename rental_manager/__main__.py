from rental_manager.website import create_app
from rental_manager.website.database import db_service
import os
app = create_app()

if __name__ == '__main__':
    app.config["CLIENT_AGREEMENTS"] = os.path.join(os.path.abspath("website"), "/static/agreements/")
    app.run(debug=True)
    
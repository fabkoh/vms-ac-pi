import src.app as app

flaskApp = app.create_app()

if __name__ == "__main__":
    flaskApp.run(host="0.0.0.0", port=5000)

from quart_project import app_factory
import uvicorn

# Creates the Quart application (must be outside __main__ so uvicorn can use reload)
app = app_factory.create_app()

# when running python app.py can optionally specify host / port to run the webserver on a specific ip:port
if __name__ == "__main__":   
    # creates your Quart app and runs it with ASGI uvicorn
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, reload=True, timeout_graceful_shutdown=3)
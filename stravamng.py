###
### python standard library imports
###

# we're going to get our configuration from a file, here's a configuration helper library
import configparser
import http.server
import webbrowser

###
### python downloaded library imports
###

# Strava REST API wrapper
from stravalib.client import Client as StravaClient

###
### the app
###

class AuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Authorized")
        self.get_code()

    def get_code(self):
        self.server.code = [ x[5:]for x in self.path.split("?")[-1].split('&')  if x.startswith('code=') ][0]
        
# Only run this if we call this script directly
if __name__ == "__main__":

    # Let's load the config from a file
    cfg = configparser.ConfigParser(default_section="Application")
    cfg.read("stravamng.cfg")

    # Load credentials
    token = cfg.get("UserAcct", "Token")

    # get a strava client
    client = StravaClient()
    
    # if we haven't authorized yet, let's do it:
    if not token:
        # get token from strava
        client_id = cfg.get("StravaClient", "ClientId")
        client_secret = cfg.get("StravaClient", "ClientSecret")
        port = int(cfg.get("Application", "Port"))
        
        # setup webserver for authentication redirect
        httpd = http.server.HTTPServer(('127.0.0.1', port), AuthHandler)

        # The url to authorize from
        authorize_url = client.authorization_url(client_id=client_id, redirect_uri='http://localhost:{port}/authorized'.format(port=port), scope='view_private,write')
        # Open the url in your browser
        webbrowser.open(authorize_url, new=0, autoraise=True)

        # wait until you click the authorize link in the browser
        httpd.handle_request()
        code = httpd.code

        # Get the token
        token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)

        # Now store that access token in the config
        cfg.set("UserAcct", "Token", token)
        with open("stravamng.cfg", "w") as cfg_file:
            cfg.write(cfg_file)

    client.access_token = token

    # do stuff
    athlete = client.get_athlete()
    print("For {id}, I now have an access token {token}".format(id=athlete.id, token=token))


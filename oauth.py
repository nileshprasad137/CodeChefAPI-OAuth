from flask import Flask, abort, request
from uuid import uuid4
import requests
import requests.auth
import urllib
import config

app = Flask(__name__)

CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
REDIRECT_URI = config.REDIRECT_URI

@app.route('/')
def homepage():
	text = '<a href="%s">Authenticate with chef</a>'
	return text % make_authorization_url()

def make_authorization_url():
	# Generate a random string for the state parameter
	# Save it for use later to prevent xsrf attacks
	from uuid import uuid4
	state = str(uuid4())
	save_created_state(state)
	params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  }
	import urllib
	url = "https://api.codechef.com/oauth/authorize?" + urllib.parse.urlencode(params)
	return url

# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(state):
	pass
def is_valid_state(state):
	return True

@app.route('/chef_callback')
def chef_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    access_token = get_token(code)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
    return "Access Token :: %s" % access_token


def get_token(code):
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "client_id": CLIENT_ID,
                 "client_secret": CLIENT_SECRET,  
                 "redirect_uri": REDIRECT_URI}
    # headers = base_headers()
    response = requests.post("https://api.codechef.com/oauth/token",                             
                             data=post_data)    
    token_json = response.json()  

    return token_json["result"]["data"]["access_token"]


if __name__ == '__main__':
	app.run(debug=True, port=65010)
import base64,hashlib,os

def generateRandom(length):
	random_bytes = os.urandom(length)
	return base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode('utf-8')

def calculateChallenge(codeVerifier):
	hash_object = hashlib.sha256(codeVerifier.encode('utf-8'))
	codeChallenge = base64.urlsafe_b64encode(hash_object.digest()).rstrip(b'=').decode('utf-8')
	return codeChallenge

def getNSOLogin():
	temp = generateRandom(32)
	params = {
        'state': generateRandom(36),
        'redirect_uri': 'npf71b963c1b7b6d119://auth',
		'client_id' : '71b963c1b7b6d119',
        'scope': 'openid+user+user.birthday+user.mii+user.screenName',
        'response_type': 'session_token_code',
        'session_token_code_challenge': calculateChallenge(temp),
        'session_token_code_challenge_method': 'S256',
        'theme': 'login_form'
	}
	query_string = ""
	for key,value in params.items():
		query_string += f'{key}={value}&'
	return 'https://accounts.nintendo.com/connect/1.0.0/authorize?' + query_string, temp

if __name__ == "__main__":
	loginURL = getNSOLogin()
	print(loginURL)

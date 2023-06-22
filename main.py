import gen_url
import requests,re,json,time,uuid

def get_session_token():
	login_url,session_token_code_verifier = gen_url.getNSOLogin()
	print(login_url)
	session_url = input(">")
	session_token_code = re.search("de=(.*)&", session_url).group(1)
	url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
	headers = {
		"Host" : "accounts.nintendo.com",
		"Content-Type" : "application/json",
		"Accept" : "application/json"
	}
	body = {
		"session_token_code" : session_token_code,
		"session_token_code_verifier" : session_token_code_verifier,
		"client_id" : "71b963c1b7b6d119"
	}
	response = requests.post(url, headers=headers, json=body)
	return json.loads(response.text)["session_token"]

def get_access_token(session_token):
	url = "https://accounts.nintendo.com/connect/1.0.0/api/token"
	headers = {
		"Host" : "accounts.nintendo.com",
		"Content-Type" : "application/json",
		"Accept" : "application/json"
	}
	body = {
		"session_token": session_token,
		"client_id": "71b963c1b7b6d119",
		"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token"
	}
	response = requests.post(url, headers=headers, json=body)
	return json.loads(response.text)["access_token"], json.loads(response.text)["id_token"]

def get_f(access_token):
	url = "https://api.imink.app/f"
	body = {
		"token": access_token,
		"hash_method": 1
	}
	response = requests.post(url, json=body)
	return {
		"f" : json.loads(response.text)["f"],
		"timestmp" :  json.loads(response.text)["timestamp"],
		"requestId" : json.loads(response.text)["request_id"]
	}

def get_me(access_token):
	url = "https://api.accounts.nintendo.com/2.0.0/users/me"
	headers = {
		"Host" : "api.accounts.nintendo.com",
		"Authorization" : f"Bearer {access_token}",
		"Content-Type" : "application/json"
	}
	response = requests.get(url, headers=headers)
	user_info = json.loads(response.text)
	return user_info["language"],user_info["country"],user_info["birthday"]

def get_login(user_info,access_token,id_token):
	f_param = get_f(access_token)
	url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"
	user_lang, user_country, user_birthday = user_info
	body = {
		"parameter" : {
			"f" : f_param["f"],
			"language" : user_lang,
			"naBirthday" : user_birthday,
			"naCountry" : user_country,
			"naIdToken" : id_token,
			"timestamp" : f_param["timestmp"],
			"requestId" : f_param["requestId"]
			}
	}
	headers = {
		"X-ProductVersion" : "2.5.2",
		"Content-Type" : "application/json; charset=utf-8",
		"Host" : "api-lp1.znc.srv.nintendo.net",
		"X-Platform" : "iOS",
		"Accept-Encoding": "gzip",
		"Connection": "Keep-Alive",
		"User-Agent": "Coral/2.5.2 (com.nintendo.znca; iOS 16.5)"
	}
	response = requests.post(url, headers=headers, json=body)
	return response.text

if __name__ == "__main__":
	access_token, id_token = get_access_token(get_session_token())
	user_lang, user_country, user_birthday = get_me(access_token)
	print("----------------------------")
	# print(f"f : {f}")
	# print(f"language : {user_lang}")
	# print(f"naBirthday : {user_birthday}")
	# print(f"naCountry : {user_country}")
	# print(f"naIdToken : {id_token}")
	# print("----------------------------")
	print(get_login(get_me(access_token),access_token,id_token))
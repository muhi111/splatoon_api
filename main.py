import gen_url
import requests,re,json,time,sys

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

def get_f(id_token,hash_method):
	url = "https://api.imink.app/f"
	body = {
		"token": id_token,
		"hash_method": hash_method
	}
	response = requests.post(url, json=body)
	if response.status_code // 100 != 2:
		print("error occur in generating f")
		print("check \"https://status.imink.app/\"")
		sys.exit()
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

def get_login(access_token,id_token):
	f_param = get_f(id_token,1)
	url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"
	user_lang, user_country, user_birthday = get_me(access_token)
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
		"X-ProductVersion" : X_ProductVersion,
		"Host" : "api-lp1.znc.srv.nintendo.net",
		"X-Platform" : "iOS"
	}
	response = requests.post(url, headers=headers, json=body)
	return json.loads(response.text)["result"]["webApiServerCredential"]["accessToken"]

def get_gtoken(access_token):
	f_param = get_f(access_token,2)
	url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"
	body = {
		"parameter" : {
			"f" : f_param["f"],
			"timestamp" : f_param["timestmp"],
			"requestId" : f_param["requestId"],
			"registrationToken" : access_token,
			"id" :  4834290508791808
			}
	}
	headers = {
		"X-Platform" : "iOS",
		"X-ProductVersion" : X_ProductVersion,
		"Authorization" : f"Bearer {access_token}"
	}
	response = requests.post(url, headers=headers, json=body)
	return json.loads(response.text)["result"]["accessToken"]

def get_bulllet_token(gtoken):
	url = "https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens"
	headers = {
		"X-Web-View-Ver" : X_Web_View_Ver
	}
	cookies = {
		"_gtoken": gtoken,
	}
	response = requests.post(url, headers=headers, cookies=cookies)
	return json.loads(response.text)["bulletToken"]

def api_test(gtokne,bullet_token):
	url = "https://api.lp1.av5ja.srv.nintendo.net/api/graphql"
	body = {
		"variables": {},
		"extensions": {
			"persistedQuery": {
				"version": 1,
				"sha256Hash": "0d90c7576f1916469b2ae69f64292c02"
			}
		}
	}
	headers = {
		"Authorization" : f"Bearer {bullet_token}",
		"X-Web-View-Ver" : X_Web_View_Ver

	}
	cookies = {
		"_gtoken": gtokne,
	}
	response = requests.post(url, headers=headers, cookies=cookies, json=body)
	return json.loads(response.text)


if __name__ == "__main__":
	X_Web_View_Ver = "4.0.0-d5178440"
	X_ProductVersion = "2.5.2"
	access_token,id_token = get_access_token(get_session_token())
	print("----------------------------")
	gtoken = get_gtoken(get_login(access_token,id_token))
	bullet_token = get_bulllet_token(gtoken)
	print(api_test(gtoken,bullet_token))
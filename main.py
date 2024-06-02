import cache_token, gen_token
import requests, json, time, sys, json

X_Web_View_Ver = "6.0.0-2ba8cb04"
X_ProductVersion = "2.10.0"

def api_test(gtokne,bullet_token):
	url = "https://api.lp1.av5ja.srv.nintendo.net/api/graphql"
	body = {
		"variables": {
			"naCountry": "JP"
		},
		"extensions": {
			"persistedQuery": {
				"version": 1,
				# 直近50戦の情報を取得
				"sha256Hash": "58bf17200ca97b55d37165d44902067b617d635e9c8e08e6721b97e9421a8b67"
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
	return response.status_code, response.text

def print_info(response):
	summary = response["data"]["latestBattleHistories"]["summary"]
	killAverage = round(summary["killAverage"], 2)
	deathAverage = round(summary["deathAverage"], 2)
	assistAverage = round(summary["assistAverage"], 2)
	print("----------------------------")
	print(f"battle summary:")
	print(f"{summary["win"]}勝{summary["lose"]}敗")
	print(f"{summary["perUnitTimeMinute"]}分あたり {killAverage}キル {deathAverage}デス {assistAverage}アシスト")
	history = response["data"]["latestBattleHistories"]["historyGroups"]["nodes"][0]["historyDetails"]["nodes"]
	for i in range(len(history)):
		print("----------------------------")
		print(f"mode: {history[i]["vsMode"]["mode"]}")
		print(f"rule: {history[i]["vsRule"]["name"]}")
		print(f"stage: {history[i]["vsStage"]["name"]}")
		print(f"weapon: {history[i]["player"]["weapon"]["name"]}")
		print(f"result: {history[i]["judgement"]}")
		if history[i]["myTeam"]["result"] is None:
			print(f"paint: NULL")
		elif history[i]["myTeam"]["result"]["score"] is None:
			print(f"paintPoint: {history[i]["myTeam"]["result"]["paintPoint"]}")
		else:
			print(f"score: {history[i]["myTeam"]["result"]["score"]}")
		print(f"knockout: {history[i]["knockout"]}")

if __name__ == "__main__":
	data = cache_token.load_data()
	if (data is not None) and (time.time() - data["timestamp"].timestamp() < 21600):
		status_code, response = api_test(data["gtoken"], data["bullet_token"])
		if (status_code == 200):
			print_info(json.loads(response))
			sys.exit()
	access_token,id_token = gen_token.get_access_token(gen_token.get_session_token())
	print("----------------------------")
	gtoken = gen_token.get_gtoken(gen_token.get_login(access_token,id_token))
	bullet_token = gen_token.get_bulllet_token(gtoken)
	status_code, response = api_test(gtoken,bullet_token)
	if (status_code != 200):
		print("API Error")
		sys.exit()
	print_info(json.loads(response))
	cache_token.cache_data(gtoken, bullet_token)
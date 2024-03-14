import pathlib
import json
import requests
import globals
import time
import aiohttp
import asyncio
import sys
import os.path
import pathlib
import vdf

class MainLogic():  
        
    session = requests.Session()

    def __init__(self, PRIVATE_KEY = None) -> None:        
        self.KEY = globals.MAIN_KEY if PRIVATE_KEY == None else PRIVATE_KEY
                
        self.info_file = pathlib.Path('info.json')
        self.file_info = self.fetch_file_info()
    
    def find_users(self):
        users_path = pathlib.Path('C:\Program Files (x86)\Steam\config\loginusers.vdf')
        if users_path.exists():
            file = vdf.load(users_path.open())
            return file['users']
            
    
    def write_info_file(self):
        if not self.info_file.exists():
            with self.info_file.open('w', encoding='utf-8') as f:
                json.dump(asyncio.run(self.get_user_games(self.get_app_list())), f, ensure_ascii=False, indent=4)
    
    def fetch_file_app_info(self, index):
        app = self.file_info['games'][index]
        return [app['name'], format(app['value'], ".02f")]
        
    def fetch_file_info(self):
        with self.info_file.open('r', encoding='utf-8') as f:
            try:
                info = json.load(f)
                return info
            except:
                return None
    
    
    def fetch_file_app_list(self):
        app_info_list = []
        for app in self.file_info['games']:
            app_info_list.append([app['name'], format(app['value'], ".02f")])
            
        return app_info_list
        
    
    def get_app_list(self) -> dict:
        apps = requests.request("GET", f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={self.KEY}&steamid={globals.current_user}&include_free_games=false&include_appinfo=true").json()['response']
        return apps
          
    async def get_user_games(self, raw_games : dict) -> dict:
        async with aiohttp.ClientSession() as session:
            purge_entries = []
            for game in raw_games['games']:
                game['price'] = await self.get_game_price(game['appid'], session)
                if game['price'] == 'no':
                    purge_entries.append(game)
                    print(f'Deleting : {game["name"]} - Price InValid')
                    continue
                
                game['value'] = self.calculate_steam_value(game['playtime_forever'], game['price']['data']['price_overview']['initial'])


                self._purge_raw_user_game(game)
        
        raw_games['games'] = [x for x in raw_games['games'] if x not in purge_entries]
                
        return raw_games

    def calculate_steam_value(session, playtime : str, price : str):
        converted_price = float(format(price / 100, '.02f'))
        converted_playtime = playtime / 60
        
        return converted_playtime / converted_price        
                 
    def _purge_raw_user_game(self, game : dict):
        try:
            del game['playtime_windows_forever']
            del game['playtime_mac_forever']
            del game['playtime_linux_forever']
            del game['rtime_last_played']
            del game['playtime_disconnected']
        except:
            pass
    
    async def get_game_price(self, app_id : int, session : aiohttp.ClientSession) -> str:
        try:
            async with session.get(url=f"https://store.steampowered.com/api/appdetails/?appids={app_id}&cc=US&filters=price_overview") as response:
                game_price = await response.json()
                game_price = game_price[str(app_id)]
                print(f'Success! current app is {game_price.keys()}')
                return game_price if game_price['data'] != [] else 'no'
        except Exception as e:
            print(e)
            print('Failure!')
            return 'no'
import pandas as pd
import re

# TODO: learn more about user behavior's address distance
# TODO: learn about distances between shops in a mall

class WIFIInfo:
    def __init__(self, tp):
        self.name = tp[0]
        self.strength = tp[1]
        self.connected = tp[2] == 'true'
    def __str__(self):
        return  ('-' if self.connected else 'x') + ' ' + self.name + ' with ' + self.strength

class WIFIInfos:
    def __init__(self, raw_wifi_infos):
        wifi_info_matches = re.findall(r'(b_\d+)\|(\-\d+)\|(false|true)', raw_wifi_infos)
        self.wifi_infos = list(map(WIFIInfo, wifi_info_matches))
        self.wifi_infos.sort(key = lambda info: info.strength)
    def __str__(self):
        return '\n   '.join(map(str, self.wifi_infos))
    def connected_name(self):
        '''connected wifi SSID or None'''
        for wifi in self.wifi_infos:
            if wifi.connected: 
                return f'{wifi.name} with {wifi.strength}'
        return None

class UserBehavior:
    def __init__(self, index, row):
        self.index = index
        self.id = row[0]
        self.shop_id = row[1]
        self.time_stamp = row[2]
        self.longitude = row[3]
        self.latitude = row[4]
        self.wifi_infos = WIFIInfos(row[5])
    def __str__(self):
        result = f'#{self.index}, id = {self.id}, shop = {self.shop_id}, time = {self.time_stamp}, address = {self.latitude}N, {self.longitude}E\n'
        if hasattr(self, 'shop'):
            result += f'   {str(self.shop)}\n'
        result += f'   {self.wifi_infos}'
        return result

    def set_shop(self, shop):
        self.shop = shop
        self.latitude_offset = self.latitude - self.shop.latitude
        self.longitude_offset = self.longitude - self.shop.longitude
        shop.latitude_offsets.append(self.latitude_offset)
        shop.longitude_offsets.append(self.longitude_offset)

class UserBehaviors:
    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        self.users = [UserBehavior(index, row) for index, row in self.df.iterrows()]
        self.users.sort(key = lambda user: int(user.id[2:]))
        for index, user in enumerate(self.users):
            user.index = index
    def __iter__(self):
        return self.users.__iter__()

class ShopInfo:
    def __init__(self, index, row):
        self.id = row[0]
        self.mall = row[4]
        self.cat = row[1]
        self.longitude = row[2]
        self.latitude = row[3]
        self.longitude_offsets = []
        self.latitude_offsets = []
    def __str__(self):
        return f'id = {self.id}, mall = {self.mall}, cat = {self.cat}, address = {self.latitude}N, {self.longitude}E'

class ShopInfos:
    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        self.shops = [ShopInfo(index, row) for index, row in self.df.iterrows()]
        self.shops.sort(key = lambda shop: shop.mall)
    def __iter__(self):
        return self.shops.__iter__()

def link_shop_to_user(users, shops):
    for user in users:
        for shop in shops:
            if user.shop_id == shop.id:
                user.set_shop(shop)
                break

users = UserBehaviors('data/train_user_1k.csv')
shops = ShopInfos('data/train_shop.csv')
link_shop_to_user(users, shops)

# for user in users: print(user)
# for shop in shops: print(shop)

for user in users:
    print(f'#{user.index}', end = '')
    print(f', connected to wifi: {user.wifi_infos.connected_name()}', end = '')
    print(f', addr offset (x100000): {(int((user.longitude_offset) * 100000), int((user.latitude_offset) * 100000))}')

for shop in shops:
    if shop.latitude_offsets:
        print(f'#{shop.id}, offsets: {list(map(lambda offset: (int(offset[0] * 100000), int(offset[1] * 100000)), zip(shop.latitude_offsets, shop.longitude_offsets)))}')
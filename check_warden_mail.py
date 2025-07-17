#!/usr/bin/env python3
"""
ウォーデンメイルの素材確認
"""

import requests

patch_version = "15.13.1"

def check_warden_mail():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== ウォーデンメイル素材確認 ===')
    
    # ウォーデンメイル (3082)
    if '3082' in data['data']:
        item = data['data']['3082']
        price = item['gold']['total']
        print(f'\n🛡️ ウォーデンメイル (3082): {price}G')
        print(f'  英語名: {item["name"]}')
        
        if 'from' in item:
            print(f'  素材ID: {item["from"]}')
            for material_id in item['from']:
                if material_id in data['data']:
                    material = data['data'][material_id]
                    material_price = material['gold']['total']
                    print(f'    - {material["name"]} (ID: {material_id}, {material_price}G)')
        else:
            print('  素材: なし（基本アイテム）')

if __name__ == "__main__":
    check_warden_mail()
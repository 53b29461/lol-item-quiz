#!/usr/bin/env python3
"""
ハートスチールとライライクリスタルセプターの素材確認
"""

import requests

patch_version = "15.13.1"

def check_materials():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== ハートスチールとライライクリスタルセプターの素材確認 ===')
    
    # ハートスチール (3084)
    heartsteel = data['data']['3084']
    print(f'\n🔥 ハートスチール (3084):')
    print(f'  アイテム名: {heartsteel["name"]}')
    if 'from' in heartsteel:
        print(f'  素材ID: {heartsteel["from"]}')
        for material_id in heartsteel['from']:
            if material_id in data['data']:
                material = data['data'][material_id]
                print(f'    - {material["name"]} (ID: {material_id}, {material["gold"]["total"]}G)')
    
    # ライライクリスタルセプター (3116)  
    rylai = data['data']['3116']
    print(f'\n❄️ ライライクリスタルセプター (3116):')
    print(f'  アイテム名: {rylai["name"]}')
    if 'from' in rylai:
        print(f'  素材ID: {rylai["from"]}')
        for material_id in rylai['from']:
            if material_id in data['data']:
                material = data['data'][material_id]
                print(f'    - {material["name"]} (ID: {material_id}, {material["gold"]["total"]}G)')
    
    # 日本語名マッピング
    japanese_names = {
        '1011': 'ジャイアントベルト',
        '3801': 'クリスタラインブレーサー', 
        '1026': 'ブラスティングワンド',
        '1052': 'アンプリファイングトーム'
    }
    
    print(f'\n📝 追加するノードとエッジ:')
    
    print(f'\n🔥 ハートスチール用:')
    if 'from' in heartsteel:
        for material_id in heartsteel['from']:
            if material_id in japanese_names:
                jp_name = japanese_names[material_id]
                if material_id == '1011':
                    print(f'  - {jp_name} → ハートスチール (既存接続)')
                else:
                    print(f'  - {jp_name} → ハートスチール (新規接続)')
    
    print(f'\n❄️ ライライクリスタルセプター用:')
    if 'from' in rylai:
        for material_id in rylai['from']:
            if material_id in japanese_names:
                jp_name = japanese_names[material_id]
                if material_id == '1011':
                    print(f'  - {jp_name} → ライライクリスタルセプター (既存接続)')
                else:
                    print(f'  - {jp_name} → ライライクリスタルセプター (新規接続)')

if __name__ == "__main__":
    check_materials()
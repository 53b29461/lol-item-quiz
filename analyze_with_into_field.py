#!/usr/bin/env python3
"""
intoフィールドを使った正確な関係性ベース分類
"""

import requests

patch_version = "15.13.1"

def analyze_with_into():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()
    
    print('=== intoフィールドを使った関係性分析 ===\n')
    
    # 現在のグラフに含まれるアイテムIDリスト
    graph_items = {
        '1011': 'Giant\'s Belt',
        '1028': 'Ruby Crystal', 
        '3083': 'Warmog\'s Armor',
        '3143': 'Randuin\'s Omen',
        '3116': 'Rylai\'s Crystal Scepter',
        '3084': 'Heartsteel',
        '3067': 'Kindlegem',
        '3066': 'Winged Moonplate',
        '3044': 'Phage',
        '3801': 'Crystalline Bracer',
        '3082': 'Warden\'s Mail',
        '1026': 'Blasting Wand',
        '1052': 'Amplifying Tome',
        '2022': 'Glowing Mote',
        '1006': 'Rejuvenation Bead',
        '1036': 'Long Sword',
        '1029': 'Cloth Armor'
    }
    
    # 各アイテムを分類
    basic_items = []      # 素材アイテム（子がいない）
    intermediate_items = [] # 中間アイテム（親も子もいる）
    legendary_items = []   # レジェンダリー（親がいない）
    
    for item_id, name in graph_items.items():
        if item_id in data['data']:
            item = data['data'][item_id]
            has_from = 'from' in item
            has_into = 'into' in item
            price = item['gold']['total']
            
            # デバッグ出力
            print(f'{name} (ID: {item_id}):')
            print(f'  価格: {price}G')
            print(f'  from（子）: {"あり" if has_from else "なし"}')
            print(f'  into（親）: {"あり" if has_into else "なし"}')
            
            if not has_from and has_into:
                # 子がいない、親がいる = 素材アイテム
                basic_items.append((item_id, name, price))
                print(f'  → 素材アイテム')
            elif has_from and has_into:
                # 親も子もいる = 中間アイテム
                intermediate_items.append((item_id, name, price))
                print(f'  → 中間アイテム')
            elif has_from and not has_into:
                # 子がいる、親がいない = レジェンダリー
                legendary_items.append((item_id, name, price))
                print(f'  → レジェンダリーアイテム')
            else:
                # どちらもない（理論上は存在しないはず）
                print(f'  → ⚠️ 特殊なアイテム')
            print()
    
    print('\n📊 関係性ベース分類結果:')
    
    print(f'\n🟢 素材アイテム（子がいない）: {len(basic_items)}個')
    for item_id, name, price in sorted(basic_items, key=lambda x: x[2]):
        print(f'  {name} (ID: {item_id}, {price}G)')
    
    print(f'\n🔵 中間アイテム（親も子もいる）: {len(intermediate_items)}個')
    for item_id, name, price in sorted(intermediate_items, key=lambda x: x[2]):
        print(f'  {name} (ID: {item_id}, {price}G)')
    
    print(f'\n🟡 レジェンダリーアイテム（親がいない）: {len(legendary_items)}個')
    for item_id, name, price in sorted(legendary_items, key=lambda x: x[2]):
        print(f'  {name} (ID: {item_id}, {price}G)')

if __name__ == "__main__":
    analyze_with_into()
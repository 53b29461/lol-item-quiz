#!/usr/bin/env python3
"""
全アイテムの価格ベースvs関係性ベース分類の完全比較
"""

import requests

patch_version = "15.13.1"

def analyze_all_items():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()
    
    print('=== 全アイテム分類比較分析 ===\n')
    
    # intoマップの構築（どのアイテムの素材になるか）
    into_map = {}
    for item_id, item in data['data'].items():
        if 'from' in item:
            for material_id in item['from']:
                if material_id not in into_map:
                    into_map[material_id] = []
                into_map[material_id].append(item_id)
    
    mismatches = []
    total_items = 0
    
    # サモナーズリフトで使用可能で、消耗品でないアイテムのみ
    for item_id, item in data['data'].items():
        # スキップ条件
        if not item['gold']['purchasable']:
            continue
        if 'requiredChampion' in item:
            continue
        if 'requiredAlly' in item:
            continue
        if 'consumed' in item['tags'] or 'Consumable' in item['tags']:
            continue
        if 'Boots' in item['tags']:
            continue
        if 'Trinket' in item['tags']:
            continue
        if 'Jungle' in item['tags'] or 'Lane' in item['tags']:
            continue
        if item['name'].startswith('Enchantment:'):
            continue
        
        total_items += 1
        
        price = item['gold']['total']
        name = item['name']
        
        # 価格ベース分類
        if price <= 799:
            price_category = '素材'
        elif price <= 1600:
            price_category = '中間'
        else:
            price_category = 'レジェンダリー'
        
        # 関係性ベース分類
        has_from = 'from' in item
        has_into = item_id in into_map
        
        if not has_from and has_into:
            relation_category = '素材'
        elif has_from and has_into:
            relation_category = '中間'
        elif has_from and not has_into:
            relation_category = 'レジェンダリー'
        else:
            relation_category = '特殊（素材も親もない）'
        
        if price_category != relation_category:
            mismatches.append({
                'id': item_id,
                'name': name,
                'price': price,
                'price_cat': price_category,
                'rel_cat': relation_category,
                'has_from': has_from,
                'has_into': has_into
            })
    
    # 結果表示
    print(f'総アイテム数: {total_items}')
    print(f'不一致アイテム数: {len(mismatches)} ({len(mismatches)/total_items*100:.1f}%)\n')
    
    # カテゴリ別の不一致を集計
    mismatch_types = {}
    for m in mismatches:
        key = f"{m['price_cat']} → {m['rel_cat']}"
        if key not in mismatch_types:
            mismatch_types[key] = []
        mismatch_types[key].append(m)
    
    print('📊 不一致パターン別集計:')
    for pattern, items in sorted(mismatch_types.items()):
        print(f'\n【{pattern}】 ({len(items)}件)')
        for item in sorted(items, key=lambda x: x['price'])[:10]:  # 最初の10件のみ表示
            print(f"  {item['name']} (ID: {item['id']}, {item['price']}G)")
        if len(items) > 10:
            print(f"  ... 他 {len(items) - 10} 件")
    
    # 特に問題のあるケース
    print('\n⚠️ 特に注目すべき不一致:')
    
    # 価格が高いのに素材扱い
    expensive_basics = [m for m in mismatches if m['rel_cat'] == '素材' and m['price'] > 800]
    if expensive_basics:
        print('\n1. 高価格なのに素材アイテム（子がいない）:')
        for item in sorted(expensive_basics, key=lambda x: -x['price'])[:5]:
            print(f"  {item['name']}: {item['price']}G")
    
    # 価格が安いのにレジェンダリー扱い
    cheap_legendaries = [m for m in mismatches if m['rel_cat'] == 'レジェンダリー' and m['price'] < 1601]
    if cheap_legendaries:
        print('\n2. 低価格なのにレジェンダリー（親がいない）:')
        for item in sorted(cheap_legendaries, key=lambda x: x['price'])[:5]:
            print(f"  {item['name']}: {item['price']}G")

if __name__ == "__main__":
    analyze_all_items()
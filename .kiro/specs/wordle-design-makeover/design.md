# Design Document

## Overview

このデザイン文書では、既存のFlaskアプリケーションをWordleスタイルのモダンなデザインに変更するための詳細な設計を説明します。Wordleの特徴的なデザイン要素を取り入れながら、既存の機能を損なうことなく、ユーザーエクスペリエンスを大幅に向上させることを目指します。

## Architecture

### Design System Architecture

```
Design System
├── Color Palette
│   ├── Primary Colors (Wordle-inspired)
│   ├── Semantic Colors (success, warning, error)
│   └── Neutral Colors (backgrounds, text)
├── Typography
│   ├── Font Family (system fonts)
│   ├── Font Sizes (responsive scale)
│   └── Font Weights
├── Components
│   ├── Tiles/Cards
│   ├── Buttons
│   ├── Navigation
│   └── Forms
└── Layout System
    ├── Grid System
    ├── Spacing Scale
    └── Breakpoints
```

### File Structure Changes

```
static/
├── styles/
│   ├── main.css (新しいメインスタイル)
│   ├── components.css (コンポーネント用)
│   ├── animations.css (アニメーション)
│   └── responsive.css (レスポンシブ)
└── js/
    └── animations.js (インタラクション用)
```

## Components and Interfaces

### 1. Color Palette

**Primary Colors (Wordle-inspired)**
- `--color-correct`: #6aaa64 (緑 - 正解)
- `--color-present`: #c9b458 (黄 - 部分正解)
- `--color-absent`: #787c7e (グレー - 不正解)
- `--color-empty`: #ffffff (白 - 未回答)

**Background Colors**
- `--bg-primary`: #ffffff (メイン背景)
- `--bg-secondary`: #f6f7f8 (セカンダリ背景)
- `--bg-tile`: #ffffff (タイル背景)

**Text Colors**
- `--text-primary`: #1a1a1b (メインテキスト)
- `--text-secondary`: #787c7e (セカンダリテキスト)
- `--text-on-color`: #ffffff (カラー背景上のテキスト)

**Border Colors**
- `--border-default`: #d3d6da (デフォルトボーダー)
- `--border-focus`: #878a8c (フォーカス時)

### 2. Typography System

**Font Stack**
```css
font-family: 'Helvetica Neue', Arial, sans-serif;
```

**Font Sizes (responsive)**
- `--font-size-xs`: clamp(0.75rem, 2vw, 0.875rem)
- `--font-size-sm`: clamp(0.875rem, 2.5vw, 1rem)
- `--font-size-base`: clamp(1rem, 3vw, 1.125rem)
- `--font-size-lg`: clamp(1.125rem, 3.5vw, 1.25rem)
- `--font-size-xl`: clamp(1.25rem, 4vw, 1.5rem)
- `--font-size-2xl`: clamp(1.5rem, 5vw, 2rem)

**Font Weights**
- `--font-weight-normal`: 400
- `--font-weight-medium`: 500
- `--font-weight-bold`: 700

### 3. Component Designs

#### Tile Component
```css
.tile {
  width: 62px;
  height: 62px;
  border: 2px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  background-color: var(--bg-tile);
  transition: all 0.2s ease-in-out;
}

.tile:hover {
  border-color: var(--border-focus);
  transform: scale(1.05);
}

.tile.correct {
  background-color: var(--color-correct);
  border-color: var(--color-correct);
  color: var(--text-on-color);
}

.tile.present {
  background-color: var(--color-present);
  border-color: var(--color-present);
  color: var(--text-on-color);
}

.tile.absent {
  background-color: var(--color-absent);
  border-color: var(--color-absent);
  color: var(--text-on-color);
}
```

#### Button Component
```css
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: var(--color-correct);
  color: var(--text-on-color);
}

.btn-primary:hover {
  background-color: #5a9a54;
  transform: translateY(-1px);
}
```

#### Card Component
```css
.card {
  background-color: var(--bg-tile);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

### 4. Layout System

#### Grid System
```css
.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.grid {
  display: grid;
  gap: 5px;
  justify-content: center;
}

.quiz-grid {
  grid-template-columns: 1fr;
  gap: 8px;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}
```

#### Spacing Scale
- `--space-xs`: 4px
- `--space-sm`: 8px
- `--space-md`: 16px
- `--space-lg`: 24px
- `--space-xl`: 32px
- `--space-2xl`: 48px

## Data Models

### CSS Custom Properties Structure
```css
:root {
  /* Colors */
  --color-correct: #6aaa64;
  --color-present: #c9b458;
  --color-absent: #787c7e;
  --color-empty: #ffffff;
  
  /* Backgrounds */
  --bg-primary: #ffffff;
  --bg-secondary: #f6f7f8;
  --bg-tile: #ffffff;
  
  /* Text */
  --text-primary: #1a1a1b;
  --text-secondary: #787c7e;
  --text-on-color: #ffffff;
  
  /* Borders */
  --border-default: #d3d6da;
  --border-focus: #878a8c;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  
  /* Typography */
  --font-size-xs: clamp(0.75rem, 2vw, 0.875rem);
  --font-size-sm: clamp(0.875rem, 2.5vw, 1rem);
  --font-size-base: clamp(1rem, 3vw, 1.125rem);
  --font-size-lg: clamp(1.125rem, 3.5vw, 1.25rem);
  --font-size-xl: clamp(1.25rem, 4vw, 1.5rem);
  --font-size-2xl: clamp(1.5rem, 5vw, 2rem);
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
}
```

## Error Handling

### Design Consistency
- すべてのエラー状態で一貫したカラーパレットを使用
- エラーメッセージは `--color-absent` を使用
- 成功メッセージは `--color-correct` を使用
- 警告メッセージは `--color-present` を使用

### Fallback Strategies
- CSS Custom Propertiesがサポートされていない場合のfallback値を提供
- 古いブラウザ向けのベーシックなスタイリング
- プログレッシブエンハンスメントアプローチ

## Testing Strategy

### Visual Regression Testing
1. **スクリーンショット比較**
   - 各ページの変更前後の比較
   - 異なるブラウザでの表示確認
   - モバイル・デスクトップでの表示確認

2. **レスポンシブテスト**
   - 320px（モバイル）から1920px（デスクトップ）まで
   - 主要なブレークポイントでの確認
   - タッチデバイスでの操作性確認

3. **アクセシビリティテスト**
   - カラーコントラスト比の確認（WCAG AA準拠）
   - キーボードナビゲーションの確認
   - スクリーンリーダーでの読み上げ確認

### Performance Testing
1. **CSS最適化**
   - 未使用CSSの削除
   - CSSファイルサイズの最適化
   - Critical CSSの特定

2. **アニメーション性能**
   - 60fps維持の確認
   - GPU加速の活用
   - アニメーション中のメモリ使用量確認

### Browser Compatibility
- **モダンブラウザ**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **CSS Grid/Flexbox**: 完全サポート
- **CSS Custom Properties**: 完全サポート
- **CSS Animations**: 完全サポート

### Implementation Phases

#### Phase 1: Core Styling
- CSS Custom Propertiesの設定
- 基本的なタイポグラフィとカラーパレットの適用
- レイアウトシステムの実装

#### Phase 2: Component Implementation
- タイル/カードコンポーネントの実装
- ボタンコンポーネントの実装
- フォームコンポーネントの実装

#### Phase 3: Interactive Elements
- ホバー効果とアニメーションの追加
- トランジション効果の実装
- マイクロインタラクションの追加

#### Phase 4: Responsive Design
- モバイル最適化
- タブレット対応
- デスクトップ向け調整

#### Phase 5: Polish & Optimization
- パフォーマンス最適化
- アクセシビリティ改善
- ブラウザ互換性確認
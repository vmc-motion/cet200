[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# cet200

VMT-CET200: A fictional 20-ton-class hydraulic excavator model for
the [AGX Dynamics](https://www.algoryx.se/agx-dynamics) physics engine.  
VMT-CET200: 物理エンジンAGX Dynamicsに対応した架空20tクラス油圧ショベルモデル。

<img src="docs/cet200_excavation.gif" width="720">

## リポジトリ構造

```shell
cet200
|-cet200_agxpy_standalone  # AGX Pythonサンプルプログラム
|-cet200_description       # URDFモデル
|-agx_file                 # AGXファイル
|-openplx                  # (WIP)OpenPLXファイル
|-spaceclaim_momentum      # SpaceClaim+Algoryx Momentumファイル
|-generic_models           # 汎用モデルファイル(glb、step)
|-tools                    # モデル変換などのツール 
|-docs                     # スペックシートなどのドキュメント
```

## ダウンロード

リポジトリには複数の3Dモデルが含まれている。
フルクローンまたは必要なモデルのみをチェックアウトして使う。

- フルクローン: `git clone <REPO>`
- [部分チェックアウト](docs/git_sparse_checkout.md)

## cet200_agxpy_standalone

### 動作確認環境

- Windows 11
    - Python 3.9.9
    - AGX-2.40.1.5
- Ubuntu 22.04(ROS2 Humble)
    - Python 3.10.12
    - AGX-2.41.1.0

### Pythonコマンドでサンプルプログラムを実行する

```shell
# Windows例
# AGXの環境変数が設定されたプロンプトを実行

# インストール
git clone <REPO>
cd cet200

# 【推奨】仮想環境の作成と有効化
python -m venv .venv
.venv\Scrpits\activate

# cet200_agxpy_standalone pythonパッケージのeditableインストール
cd cet200_agxpy_standalone
python -m pip install -r requirements.txt
python -m pip show cet200_agxpy_standalone

# プログラムの実行
cd src/cet200_agxpy_standalone/apps
python cet200_on_terrain.py
```

### ros2 runコマンドでサンプルプログラムを実行する(Ubuntuのみ)

```shell
# AGXの環境変数が設定されたシェル
# インストール
mkdir -p ~/ros_ws/src
cd ~/ros_ws/src 
git clone <REPO>

# 依存パッケージのインストール
cd ~/ros_ws
rosdep install --from-paths src --ignore-src -r -y

# ビルドとインストール
colcon build　--symlink-install
source ~/ros2_ws/install/setup.bash
# インストール確認
ros2 pkg executables cet200_agxpy_standalone

# プログラムの実行
ros2 run cet200_agxpy_standalone cet200_on_terrain
```

### 操作方法

```shell
# ゲームパッド（XInput方式に対応)
LB、RB: 前進
LT、RT: 後退
左スティック左右: 旋回
左スティック上下: アーム上げ下げ
右スティック左右: バケット掘削、ダンプ
右スティック上下: ブーム上げ下げ

# キーボード
カーソルキー: 走行
a、s: 旋回
m、,: ブーム上げ下げ
z、x: アーム上げ下げ
j、k: バケット掘削、ダンプ
```

## cet200_description

URDFモデル。

### RVizによる可視化

cet200_agxpy_standaloneを参考にcolcon build後に次のコマンドを実行する。

```shell
ros2 launch cet200_description display.launch.py 
```

## その他

- [3Dモデル変換パイプライン](docs/3d_modeling_pipeline.md)

## お問い合わせ/Contact

support@vmc-motion.com

## License

Copyright 2026 VMC Motion Technologies Co., Ltd.  
Licensed under the Apache-2.0 license.
See [LICENSE](LICENSE) and [Notice](NOTICE).

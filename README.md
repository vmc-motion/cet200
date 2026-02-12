[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# cet200

VMT-CET200 : **C**onstruction **E**xcavator, **T**racked  
A fictional 20-ton-class hydraulic excavator model for the [AGX Dynamics](https://www.algoryx.se/agx-dynamics) physics engine.  
物理エンジンAGX Dynamicsに対応した架空20tクラス油圧ショベルモデル。

Xacro／URDFファイル、STEP形式のCADファイル、GLB(glTF)形式の3Dモデルファイルを含んでおり、AGX Dynamics以外の用途にも使用できます。

<img src="docs/cet200_excavation.gif" width="720">

## Repository structure

```shell
cet200
|-cet200_agxpy_standalone  # AGX Pythonサンプルプログラム
|-cet200_description       # URDFモデル
|-agx_file                 # AGXファイル
|-openplx                  # (WIP)OpenPLXファイル
|-spaceclaim_momentum      # SpaceClaim + Algoryx Momentumファイル
|-exchange_formats         # 汎用モデルファイル(glb、step)
|-tools                    # モデル変換などのツール
|-docs                     # スペックシートなどのドキュメント
```

## Requirements

### [cet200_agxpy_standalone](#cet200_agxpy_standalone) 要件

- OS: Windows、Ubuntu
- AGX Dynamics >= 2.40.1.5
    - License modules: Core、Tracks、Terrain、Granular
    - 参考: [VMT Developer Portal(外部サイト)](https://developer.vmc-motion.com)
    - [お問合せ・トライアルライセンスの申し込み(外部サイト)](https://www.vmc-motion.com/%E3%81%8A%E5%95%8F%E3%81%84%E5%90%88%E3%82%8F%E3%81%9B/)
- Python: AGX Dynamicsが対応しているPythonバージョン
- オプション: XInput方式のゲームパッド

### [cet200_description](#cet200_description) 要件

- OS: Ubuntu (Windowsは未確認)
- ROS2

### spaceclaim_momentum 要件

- OS: Windows (Ubuntu非対応)
- Ansys SpaceClaim >= 2024 R2
- Algoryx Momentum >= 2.8.1

## Tested environments

- Windows 11、Python 3.9.9、AGX-2.40.1.5
- Ubuntu 22.04、ROS2 Humble、Python 3.10.12、AGX-2.41.1.0

## Download

リポジトリには複数の3Dモデルが含まれている。
フルクローンまたは必要なモデルのみをチェックアウトして使う。

- フルクローン: `git clone <REPO>`
- [部分チェックアウト](docs/git_sparse_checkout.md)

## cet200_agxpy_standalone

AGX DynamicsのPython APIを使用した、Python単体実行用のサンプルプログラムパッケージ。

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

### ros2 runコマンドでサンプルプログラムを実行する

```shell
# AGXの環境変数が設定されたシェルで実行する

# インストール
mkdir -p ~/ros_ws/src
cd ~/ros_ws/src
git clone <REPO>

# 依存パッケージのインストール
cd ~/ros_ws
rosdep install --from-paths src --ignore-src -r -y

# ビルドとインストール
colcon build --symlink-install
source ~/ros2_ws/install/setup.bash
# インストール確認
ros2 pkg executables cet200_agxpy_standalone

# プログラムの実行
ros2 run cet200_agxpy_standalone cet200_on_terrain
```

### 操作方法

```shell
# ゲームパッド（XInput方式)
前進: LB、RB
後退: LT、RT 
旋回: 左スティック左右
アーム上げ下げ: 左スティック上下 
バケット掘削、ダンプ: 右スティック左右 
ブーム上げ下げ: 右スティック上下: 

# キーボード
走行: カーソルキー 
旋回: a、s 
アーム上げ下げ: z、x 
ブーム上げ下げ: m、, 
バケット掘削、ダンプ: j、k 
```

## cet200_description

Xacro/URDFモデル。

### RVizによる可視化

cet200_agxpy_standaloneを参考にcolcon build後に次のコマンドを実行する。

```shell
ros2 launch cet200_description display.launch.py
```

## その他

- [プログラムが参照するモデルファイル](docs/program_dependent_model_files.md)
- [3Dモデル変換パイプライン](docs/3d_modeling_pipeline.md)

## Contact

support@vmc-motion.com

## License

Copyright 2026 VMC Motion Technologies Co., Ltd.  
Licensed under the Apache-2.0 license.
See [LICENSE](LICENSE) and [Notice](NOTICE).


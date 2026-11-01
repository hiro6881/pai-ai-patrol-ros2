# AI-prioritized patrol using ROS 2 and Gazebo

Physical AI 応用編1 最終課題：**AIによる巡回優先順位判断を利用した自律移動ロボット**

ROS 2 Humble / Gazebo Classic / TurtleBot3 Burger を使用して、点検地点の緊急度と出発地点からの直線距離を入力とする k-NN の優先スコア推定を実施し、推定スコアの高い順にロボットを巡回させます。

## 必要な環境

- ROS 2 Humble (`rclpy`, `geometry_msgs`, `nav_msgs`)
- Gazebo Classic と ROS 2 連携パッケージ
- TurtleBot3 Burger (`turtlebot3_gazebo`, `turtlebot3_teleop` など)
- Python 3

講座で使用した Docker イメージ: `airobotbook/ros2-desktop-ai-robot-book-humble:latest`。コンテナやディスプレイ構成により追加の環境変数設定が必要です。

## ファイル

- `auto_drive.py` : `/odom` を参照し、`/cmd_vel` に速度指令を送るウェイポイント制御
- `ai_patrol.py` : 実験1（A:2、B:5、C:3）に基づくk-NN優先順位推定と走行
- `ai_patrol_case2.py` : 実験2（A:5、B:2、C:3）に基づくk-NN優先順位推定と走行
- `knn_audit.py` : k-NN計算の検算用補助コード（配置した場合）

## 実行方法

別ターミナルで Gazebo の TurtleBot3 Burger を起動します。

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

その後、別ターミナルで以下を実行します。

```bash
source /opt/ros/humble/setup.bash
cd ~/pai_final
python3 ai_patrol.py
# 実験2は次を実行
python3 ai_patrol_case2.py
```

**実験1と実験2は同時に実行しないでください。** 走行停止後に `Ctrl+C` で終了してから次の実験を実行します。GUIのモデル描画には、環境に応じて `GAZEBO_MODEL_PATH` やソフトウェアレンダリングの設定が必要です。

## AI部分の仕組み

入力特徴量は緊急度 `u` と出発地点からの距離 `d`。5段階×6段階の組み合わせから、設計した数式に基づく合成サンプル30件を作成します。入力に近い5件を特徴量空間で探索し、距離の逆数に基づく加重平均で優先スコアを推定します。

この学習データは実際の設備点検で収集したデータではなく、評価用の人工的なサンプルです。k-NNはニューラルネットワークのように反復的な重み学習を行わない事例ベースの推論方式です。AIが決定するのは**巡回優先順位**であり、移動そのものはROS 2の位置フィードバック制御です。障害物回避・巡回距離の全体最適化・実データでの精度評価は未実施です。

## 実験結果（走行ログ）

| | 実験1 | 実験2 |
|---|---|---|
| 緊急度 A/B/C | 2/5/3 | 5/2/3 |
| 推定順位 | B→C→A | A→C→B |
| 推定スコア | B=8.29, C=4.48, A=2.48 | A=9.31, C=4.48, B=1.47 |
| 結果 | `TASK COMPLETED` | `TASK COMPLETED` |

上記は実際に得た実行ログに基づきます。到達判定は `/odom` に基づくプログラム内の判定であり、真値との誤差検証は実施していません。

## 公開に関する注意

このリポジトリには自作コードのみを追加し、講義の非公開資料・配布スライド・講義動画、個人情報、認証情報などは含めないでください。TurtleBot3等の依存パッケージそのものをコピーする必要はありません。

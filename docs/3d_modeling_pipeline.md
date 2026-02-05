# 3Dモデル変換パイプライン(Windows)

1. 起点はCADソフトSpaceClaimのscdocファイル: `spaceclaim_momentum/cet200.scdoc`
1. SpaceClaimからエクスポート

   ```
   cet200.scdoc
   |-> agx_file/cet200.agx
   |-> exchange_formats/cet200.step, cet200.glb
   |-> exchange_formats/parts/各パーツのglb
   ```

1. URDF用のCollda(dae)ファイルの生成
   - tools/run_blender_convert_glb_to_dae.batでglbファイルからdaeファイルをcet200_description/meshesに生成する [^1]

[^1]: SpaceClaimが出力するglbファイルは黒線が入ってしまうので、Blenderを使いglbを再変換して、daeファイルに出力している。Blender4.2を使用。

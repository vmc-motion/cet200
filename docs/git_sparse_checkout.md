# 部分チェックアウト

## コマンドテンプレート

```shell
git clone --filter=blob:none --sparse <REPO>
cd cet200
git sparse-checkout set <DIR1> [<DIR2>..] 
```

## CADファイル以外をチェックアウト

```shell
git clone --filter=blob:none --sparse <REPO>
cd cet200
git sparse-checkout set agx_file cet200_agxpy_standalone cet200_description docs openplx
```

## AGX関係のみチェックアウト

```shell
git clone --filter=blob:none --sparse <REPO>
cd cet200
git sparse-checkout set agx_file cet200_agxpy_standalone docs openplx
```

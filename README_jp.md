# ComfyUI-PromptList
ComfyUI-PromptListは、[ComfyUI](https://github.com/comfyanonymous/ComfyUI)用のyamlに記録したプロンプトを出力するシンプルなプロンプト管理ノードです。

## 機能

- prompts.yamlからプロンプトを読み込み、ポジティブプロンプトとネガティブプロンプトをそれぞれString形式で出力します。
- 新しいプロンプトをyamlへ書き込む
- yamlに登録されているプロンプトの修正

## インストール
[ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)をインストールしている場合
1. メインメニューのManager -> Install via Git URLの順にクリックする
2. ウインドウ上部に出てくるテキストボックスにURLを貼り付けてOKを押す  
   https://github.com/NakamuraShippo/ComfyUI-NS-PromptList
3. インストールが完了したら、ComfyUIを再起動

[ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)をインストールしていない場合
1. ComfyUIのカスタムノードディレクトリに移動します。（通常は ComfyUI/custom_nodes/）
2. このリポジトリをクローンします。  
`git clone https://github.com/NakamuraShippo/ComfyUI-NS-PromptList`
3. ComfyUIを再起動します。
4. ComfyUI\venv\ScriptsでShift+右クリック→ターミナルで開く -> activateと入力
~~~
pip install pyyaml watchdog filelock
~~~

## 使用方法
ノードの場所
Add Node -> NS -> NS Prompt List

ノードのウィジェット
- select_yaml : ComfyUI-Create\custom_nodes\ComfyUI-NS-PromptList\yaml にあるyamlのリスト、選んだyamlをロードします
- select : select_yamlで選択したyaml内のtitleキーの一覧を選択すると、titleと文字列を読み込みます
- title and text area : ロードされたtitleと文字列情報の内容です

プロンプトの登録方法
1. titleに識別用の見出しを入力します
2. テキストエリアに任意の文字列を入力します
3. 生成するとyamlへ書き込まれます

プロンプトの編集方法
1. titleに編集したいプロンプトの名前を入力
2. テキストエリアに任意の文字列を入力
3. 生成
4. 指定したyaml内に同じtitle名があれば、文字列を上書きします

誤って編集した場合
CTRL + Z でredoすると文字列が復元されるので、再度生成して上書きしてください

## アップデート履歴
2025/05/31 2.0.0 根本的に作り直しました。ComfyUI上で完結するようにしました。
2024/09/06 1.2.0 ノード入力欄をmultilineに修正。編集用スプレッドシートを公開。  
2024/08/24 1.0.0 とりあえず動いてるので公開

## ライセンス
このプロジェクトは MIT ライセンスに基づいてリリースされています。詳細については、[LICENSE.txt](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/License.txt)ファイルを参照してください。
元の著作権表示と免責事項を含める限りは、このソフトウェアを個人的および商業的な目的で自由に使用、変更、配布できます。

## その他
バグレポートや機能リクエストは、連絡が取れる手段であれば何でも構いません。
プルリクエストも歓迎します。

## 連絡先
[NakamuraShippo](https://lit.link/admin/creator)

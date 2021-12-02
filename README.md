# フォームへのreCAPTCHA実装

- index.html - 表画面の実装サンプル
- exec_recaptcha.php - reCAPTCHA実行プログラム

## 事前準備
Googleの[reCAPTCHAコンソール](https://www.google.com/recaptcha/admin)にアクセスし、サイトキーとシークレットキーを取得する。

## ステップ1
1. exec_recaptcha.phpを開き、シークレットキー(`$secret_key`)とフォーム送信プログラムのURL(`$mailsender_url`)を設定する。
2. exec_recaptcha.phpをサーバーの任意の場所にアップロードする。`$mailsender_url`と同じディレクトリがおすすめ。

```php
/**
 * SETTINGS
 * @var $secret_key RECAPTCHAのシークレットキーを指定
 * @var $mailsender_url メール送信プログラムファイル(例:mail.php)のURLを指定
 * 　　　　　　　　　　　(相対パス不可) mail.phpやformmail.cgiなど
 */

$secret_key = 'YOUR_SECRET_KEY';
$mailsender_url = "./mail.php";
```

### ステップ２
1. フォームのHTMLファイルに以下のコードを追加する。
2. サイトキーと設定する。form要素のIDも必要に応じて変更する。

```html
<!-- recaptcha本体読み込み　※クエリパラメータのrenderにサイトキーを指定 -->
<script src="https://www.google.com/recaptcha/api.js?render=YOUR_SITE_KEY"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {

    //サイトキーを設定
    var siteKey = 'YOUR_SITE_KEY';
    //フォーム要素を取得
    var formElem = document.querySelector('form');

    /* tokenを取得してformを送信 */
    function executeRecaptcha(event) {
      event.preventDefault();
      grecaptcha.ready(function () {
        grecaptcha.execute(siteKey).then(function (token) {
          var inputTokenElem = document.createElement('input');
          inputTokenElem.type = 'hidden';
          inputTokenElem.name = 'g-recaptcha-response';
          inputTokenElem.value = token;
          formElem.appendChild(inputTokenElem);
          formElem.removeEventListener('submit', executeRecaptcha);
          formElem.submit();
        });
      });
    }
    formElem.addEventListener('submit', executeRecaptcha);
  });
</script>
```

### ステップ３
フォーム要素のaction属性を、exec_recaptcha.phpへのパスに変更する。
```html
<form method="post" action="pathTo/exec_recaptcha.php">
```

### 備考
ページのHTML上にform要素が複数あると、JavaScriptがform要素をうまく取得できないことがあります。
その場合は以下の２か所にに書かれたscriptタグ内の`document.querySelector`メソッドの引数を変更してください。
- ステップ2で設定した`siteKey`の下
- exec_recaptch.phpの一番下の方にあるscriptタグ内（下記参照）

```html
<!-- exec_recaptcha.php　の一番下の方　-->
<script>
  document.addEventListener('DOMContentLoaded', function() {
    var formElem = document.querySelector('form'); //←　ここを変更
    if (!formElem) return;
    formElem.setAttribute('action', '<?php echo $mailsender_url ?>');
  });
</script>
```

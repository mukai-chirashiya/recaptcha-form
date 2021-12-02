<?php

/**
 * SETTINGS
 * @var $secret_key RECAPTCHAのシークレットキーを指定
 * @var $mailsender_url メール送信プログラムファイル(例:mail.php)のURLを指定(相対パス不可) mail.phpやformmail.cgiなど
 */

$secret_key = 'YOUR_SECRET_KEY';
$mailsender_url = 'https://www.exmaple.com/mail.php';


/**********/
#ini_set('display_errors', "On");
//API Request URL
$url = 'https://www.google.com/recaptcha/api/siteverify';
//パラメータを指定
$data = array(
  'secret' => $secret_key,
  'response' =>  $_POST['g-recaptcha-response']
);
$context = array(
  'http' => array(
    'method'  => 'POST',
    'header'  => implode("\r\n", array('Content-Type: application/x-www-form-urlencoded',)),
    'content' => http_build_query($data)
  ),
  'ssl' => array(
    'verify_peer'      => false,
    'verify_peer_name' => false
  )
);

//上記パラメータを指定して file_get_contents でレスポンスを取得
$api_response = file_get_contents($url, false, stream_context_create($context));
$result = json_decode($api_response);

//スコアを評価
// var_dump($result);
// die();
if (!$result->success || $result->score < 0.5) {
  header('Location: ' . $_SERVER['HTTP_REFERER']);
  exit('Error');
}

//フォームプログラムを実行
unset($_POST['g-recaptcha-response']);
unset($_POST['action']);

$context = array(
  'http' => array(
    'method'  => 'POST',
    'header'  => implode("\r\n", array('Content-Type: application/x-www-form-urlencoded',)),
    'content' => http_build_query($_POST)
  ),
  'ssl' => array(
    'verify_peer'      => false,
    'verify_peer_name' => false
  )
);

$html = file_get_contents($mailsender_url, false, stream_context_create($context));
echo ($html);

?>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    var formElem = document.querySelector('form');
    if (!formElem) return;
    formElem.setAttribute('action', '<?php echo $mailsender_url ?>');
  });
</script>
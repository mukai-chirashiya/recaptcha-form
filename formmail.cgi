#!/usr/bin/perl --

#use strict;
use lib qw(./lib);
use Jcode;
use CGI;
#use Encode;

use Unicode::Japanese;
#http://tech.ymirlink.co.jp/　より

#設定ファイルの読込
require 'config.pl';

#文字コードを指定してください。
#（それにともない本CGIの保存文字コードも同じにしてください）
my $moji_code = "UTF-8";		#SHIFT-JIS or UTF-8 ....


my $form = new CGI;
my @names = $form->param; 

my (@indispen,@to_mail,$from_mail, @message, $thanks);

#my ($subject, $subject_ad, $body, $body_ad);
my @errs;

#reCAPTCHA用に追記
if(!$form->param("g-recaptcha-response")){
  exit(1);
}
if($form->param("_indispen")){
	@indispen = split(/,/, $form->param("_indispen"));
}

if($form->param("_entry")){

	foreach(@names){

		my $name = $_;
		my @values = $form->param($name);

		if($name eq "_emailset"){
			$from_mail = _Check_from_mail(@values);

		}elsif($name ne "_indispen" and $name ne "_entry" and $name ne "g-recaptcha-response"){ #reCAPTCHA用に追記
			my $values = join(", ",@values);
			$values =~ s/NNN/\n/g;

			$body_ad .= "<< $name >>\n" . $values . "\n\n";
			$mail_body .= "<< $name >>\n" . $values . "\n\n";
		}
	}

	$mail_body .= $mail_footer;

	if($to_name){
		$to_mail = "$to_name <$to_mail>";
	}

	if($to_mail){
		_Send_mail($from_mail, $to_mail, $subject_ad, $body_ad);		#管理者へ
	}

	if($send_ok){
		_Send_mail($to_mail, $from_mail, $subject, $mail_body);		#入力者へ
	}

	print "Location:$html_thanks\n\n";

}else{

	push(@message, "<form method=\"POST\" action=\"formmail.cgi\">\n");
	push(@message, "<p class=\"mess_txt\">ご記入頂きました事項にお間違えがないかご確認頂けましたら<br>【送信】ボタンを１回押してください。</p>\n"); 

	push(@message, "<table id=\"formmail\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" class=\"mess_table\">\n");
	$body .= "<input type=\"hidden\" name=\"_entry\" value=\"2\">\n";

	my %err_name;
	foreach(@names){
	
		my $name = $_;
		my @values = $form->param($name);

		if($name eq "_indispen"){			#入力必須項目
			#push(@indispen,@values);		##reCAPTCHA用：コメントアウトする

		}elsif($name eq "_emailset"){		#送信元メールアドレス（入力者入力）
			$from_mail = _Check_from_mail(@values);

		}elsif($name ne "_tomail" 
			and $name ne "_subject_ad" 
			and $name ne "_subject" 
			and $name ne "_body" 
			and $name ne "_message"){			#その他の変数

			my $values;
			foreach(@values){
				my $value = $_;
				foreach(@indispen){
					if($err_name{$_}){ next; }

					if($name eq $_ and $value eq ''){
						my $err = "<p class=\"error_txt\">$nameが入力されていません。</p>";
						push(@errs, $err);
						$err_name{$_} = 1;
					}else{
						my $radio = $form->param($_);
						if(!$radio){
							my $err = "<p class=\"error_txt\">$_が入力されていません。</p>";
							push(@errs, $err);
							$err_name{$_} = 1;
						}
					}
				}
				
			}

			my $values = join(", ",@values);
			$values =~ s/\r\n/<br>/g;

			push(@message, "<tr><th>$name</th><td>$values</td></tr>\n");

		}


		foreach (@values){
			$_ =~ s/\r\n/NNN/g;
			$body .= "<input type=\"hidden\" name=\"$name\" value=\"$_\">\n";
		}
	}

	
	$body .= "</form>";



	push(@message, "</table>");
	push(@message, "<div class=\"mess_button\"><input type=\"button\" value=\"戻る\" onclick=\"javascript:history.back()\"><button type=\"submit\" style=\"background:none;width:257px;height:44px;border:none;\"><img src=\"/img/inner/sou.gif\" alt=\"\" width=\"253\" height=\"39\" /></button></div>\n");

	push(@message, $body);

	if(@errs){ 
		push(@errs, "<div class=\"mess_button\"><input type=\"button\" value=\"戻る\" onclick=\"javascript:history.back()\"></div>");

		_Message(@errs);
	}

	_Message(@message);

}

sub _Message{

	print "Content-Type: text/html; charset=".$moji_code."\n\n";

	my @messages = @_;
	my @lines;
	open(FILE, "< $html_message") or print "「$html_message」ファイルがありません。設定ファイルを確認してください。";
		@lines = <FILE>;
	close(FILE);

	my $message = join("",@messages);
	foreach (@lines){
		$_ =~ s/<!--.*MESSAGE.*-->/$message/g;
		print $_;
	}
	exit;
}

	
sub _Check_from_mail{
	my @mail,@errs;
	foreach(@_){						#_emailset指定name属性　取出し
		my @values = $form->param($_);
		push (@mail,@values );
	}
		

	my $checkmail;
	for(my $i=0; $i<@mail; $i++){

		if(@mail == 1){
			if($mail[0] !~ /^[a-zA-Z0-9-_\.]+\@[a-zA-Z0-9-_\.]+$/){
				my $err = "<p class=\"error_mail\">メールアドレスの記述が間違っているようです。もう一度ご確認下さい。</p>";
				push(@errs, $err);

				return;
			}
			return $mail[0];

		}elsif(!$i){
			$checkmail = $mail[$i];

		}else{
			if($mail[$i] ne $checkmail or $checkmail !~ /^[a-zA-Z0-9-_\.]+\@[a-zA-Z0-9-_\.]+$/){
				my $err = "<p class=\"error_mail\">メールアドレスの記述が間違っているようです。もう一度ご確認下さい。</p>";
				push(@errs, $err);

				return;
			}
		}
	}
	return $checkmail;

}
	
sub _Send_mail {

	my ($fromaddress, $toaddress, $subject, $body) = @_;

	$fromaddress =~ s/\n//g; $fromaddress =~ s/\r//g;
	$toaddress =~ s/\n//g; $toaddress =~ s/\r//g;
	$toname =~ s/\n//g; $toname =~ s/\r//g;
	$subject =~ s/\n//g; $subject =~ s/\r//g;


#	$subject = 	encode("cp932", decode("utf-8", $subject));
#	$body = encode("cp932", decode("utf-8", $body));
	if($moji_code eq "UTF-8"){
		$subject = Unicode::Japanese->new($subject)->sjis;
		$body = Unicode::Japanese->new($body)->sjis;
		$toaddress = Unicode::Japanese->new($toaddress)->sjis;
	}

	open(SENDMAIL, "|/usr/sbin/sendmail -t");
		my $str = Jcode->new("From: $fromaddress\n")->mime_encode;
		$str .= Jcode->new("To: $toaddress\n")->mime_encode;
		$str .= Jcode->new("Subject: $subject\n")->mime_encode;
		$str .=  "MIME-Version: 1.0\n";
		$str .=  "Content-Type: text/plain;charset=\"ISO-2022-JP\"\n";

		print SENDMAIL $str;
		print SENDMAIL Jcode->new("$body")->jis;

	close(SENDMAIL);

}


__END__


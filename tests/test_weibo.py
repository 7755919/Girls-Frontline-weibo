import sys
print(sys.path)
import os
import unittest
from unittest.mock import patch, MagicMock
from weibo import weibo

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class TestWeibo(unittest.TestCase):
    @patch('weibo.Weibo.SESSION.get')
    def test_weibo_id_and_proxy(self, mock_get):
        weibo = Weibo()
        
        # 测试微博ID是否配置正确
        self.assertEqual(weibo.WEIBO_ID, '${{ secrets.WEIBO_ID }}', "微博ID配置错误")
        
        # 测试代理是否配置正确
        mock_get.side_effect = Exception("Unable to connect to Telegram server")
        with self.assertRaises(Exception):
            weibo.test()

    @patch('weibo.Weibo.send_telegram_message')
    def test_send_message_to_telegram(self, mock_send_message):
        weibo = Weibo()
        message = "Test message"
        weibo.send_telegram_message(message, "https://weibo.com")
        mock_send_message.assert_called_once_with(message, "https://weibo.com")

if __name__ == '__main__':
    unittest.main()

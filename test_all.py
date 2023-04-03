# -*- coding: utf-8 -*-
import unittest

from tests.mock_commands.parse import TestParseCommands
# from dbs.bots import bots

if __name__ == '__main__':

    # 创建测试套件
    suite = unittest.TestSuite()
    # 添加所有测试用例到测试套件
    # 数据库的测试用例，不需要每次都跑
    # suite.addTest(unittest.makeSuite(TestDBBots))
    # suite.addTest(unittest.makeSuite(TestDBSKs))
    # suite.addTest(unittest.makeSuite(TestDBChats))
    suite.addTest(unittest.makeSuite(TestParseCommands))
    # suite.addTest(unittest.makeSuite(TestAppChat))
    # 创建测试运行器并运行测试套件
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

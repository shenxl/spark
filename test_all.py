# -*- coding: utf-8 -*-
import unittest

from tests.mock_commands.parse import TestParseCommands

if __name__ == '__main__':

    # 创建测试套件
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParseCommands))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

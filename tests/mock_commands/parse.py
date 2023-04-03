import unittest

from commands.parse import parse_command, CommandType


class TestParseCommands(unittest.TestCase):

    def test_parse_command_help(self):
        result = parse_command("@user %help%")
        self.assertEqual(result, (CommandType.HELP, None))
    
    # @不在指令的最前端的情况
    def test_parse_command_help_at(self):
        result = parse_command(" %help% @沈霄雷 ") 
        self.assertEqual(result, (CommandType.HELP, None))

    def test_parse_command_init(self):
        result = parse_command("@user %init%" )
        self.assertEqual(result, (CommandType.INIT, None))
    
    def test_parse_command_init_unknow(self):
        result = parse_command("@user %init% unknow" )
        self.assertEqual(result, (CommandType.UNKNOWN, None))
    
    # 指令中包括多种空格的情况
    def test_parse_command_init_at_space(self):
        result = parse_command("@user  %init % ")
        self.assertEqual(result, (CommandType.INIT, None))
    
    def test_parse_command_init_with_space_unknown(self):
        result = parse_command("@user %init%  sdsaa")
        self.assertEqual(result, (CommandType.UNKNOWN, None))

    def test_parse_command_arts(self):
        result = parse_command("@user %arts%")
        self.assertEqual(result, (CommandType.ARTS, None))

    def test_parse_command_arts_set(self):
        result = parse_command("@user %arts set xxx%")
        self.assertEqual(result, (CommandType.ARTS_SET, "xxx"))

    def test_parse_command_files(self):
        result = parse_command("@user %files%")
        self.assertEqual(result, (CommandType.FILES, None))

    def test_parse_command_files_ask(self):
        result = parse_command("@user %files ask xxx%")
        self.assertEqual(result, (CommandType.FILES_ASK, "xxx"))

    def test_parse_command_status(self):
        result = parse_command("@user %status%")
        self.assertEqual(result, (CommandType.STATUS, None))
    
    def test_parse_command_sk_set(self):
        result = parse_command("@user %sk set abc%")
        self.assertEqual(result, (CommandType.SK_SET, "abc"))
        
    def test_parse_command_online_search(self):
        result = parse_command("@user %online search%")
        self.assertEqual(result, (CommandType.ONLINE_SEARCH, None))

    def test_parse_command_online_url(self):
        result = parse_command("@user %online url%")
        self.assertEqual(result, (CommandType.ONLINE_URL, None))
                
    def test_parse_command_message(self):
        result = parse_command("@user hello")
        self.assertEqual(result, (CommandType.MSG, "hello"))

    # @不是在第一处的情况
    def test_parse_command_message_at(self):
        result = parse_command("123456@沈霄雷 7890")
        self.assertEqual(result, (CommandType.MSG, "1234567890"))

    def test_parse_command_unknown_command(self):
        result = parse_command("@user %invalid%")
        self.assertEqual(result, (CommandType.UNKNOWN, None))

if __name__ == '__main__':
    unittest.main()

from .parse import CommandType,parse_command

class CommandExecutor:
    def __init__(self):
        # CommandType 是一个枚举类，表示命令的类型，并且 `NullCommandStrategy` 是该命令类型的默认策略
        self.strategies = {command_type: NullCommandStrategy() for command_type in CommandType}
        self.instruction_desc = {command_type: '' for command_type in CommandType}
        self.instruction_example = {command_type: '' for command_type in CommandType}

    def add_strategy(self, command_type, command_strategy):
        self.strategies[command_type] = command_strategy

    def set_instruction_desc(self, command_type, desc):
        self.instruction_desc[command_type] = desc

    def set_instruction_example(self, command_type, example):
        self.instruction_example[command_type] = example

    def execute_command(self, robot, command_type, command_arg=None):
        return self.strategies[command_type].execute(robot, command_arg)

    def execute(self, robot, input_str, **kwargs):
        command_type, command_arg = parse_command(input_str)
        return self.execute_command(robot, command_type, command_arg, **kwargs)

class CommandStrategy:
    def execute(self, robot, command_arg):
        raise NotImplementedError

class NullCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        return None

# 帮助指令
class HelpCommandStrategy(CommandStrategy):
    def __init__(self, executor):
        self.executor = executor

    def execute(self, robot, command_arg):
        if command_arg:
            # 显示指定指令的描述信息
            command_type = CommandType[command_arg.upper()]
            return self.executor.instruction_desc[command_type]
        else:
            # 显示所有指令的描述信息
            desc_list = [f"- <font color='#FF0000'>**{command_type.name.lower()}**</font> 指令 - {self.executor.instruction_desc[command_type]}"
                        for command_type in CommandType if self.executor.instruction_desc[command_type]]
            title = "📖<font color='#1E90FF'>帮助</font>"
            info = "\n".join(desc_list)
            
            message = {
                "msgtype": "markdown",
                "content": f"#### {title}  \n\n {info}"
            }
            return (message , None)

class UnknownCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        message = {
            "msgtype": "markdown",
            "content":"无法识别的指令"
        }
        return (message , None)



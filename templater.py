import re


class Template(object):
    __variable_condition_symbols = r"{:?[^?}]*\:}"
    __if_condition_pattern = r"{\?[^?}]*\?}"

    __structure_patterns_list = {'var': __variable_condition_symbols, 'if': __if_condition_pattern}

    def __init__(self, fragment: str):
        self.fragment = fragment

    def render(self, **kwargs):
        temp_string = self.fragment
        for key, pattern in self.__structure_patterns_list.items():
            temp_var = re.findall(pattern, temp_string)
            if temp_var:
                if key == 'var':
                    for i in temp_var:
                        temp_string = temp_string.replace(i, self._variable_render(kwargs, i))
                elif key == "if":
                    for i in temp_var:
                        temp_string = temp_string.replace(i, self._condition_render(kwargs, i))
        return temp_string

    @staticmethod
    def _variable_render(kwargs, variable: str):
        for key, value in kwargs.items():
            if key in variable:
                return str(value)
        return ""

    @staticmethod
    def _condition_render(kwargs, conditions: str):
        var_pattern = r"{\?(?P<condition>[^?}]*)\?}"
        temp_conditions = re.match(var_pattern, conditions).group("condition")
        conditions_list = temp_conditions.split(',')
        for condition in conditions_list:
            temp_condition = condition.split('->')
            for key, value in kwargs.items():
                if temp_condition[0].find(key) != -1:
                    temp_condition[0] = temp_condition[0].replace(key, f"'{value}'" if str(value).isdigit() is False else str(value))
            if 'else' in temp_condition[0]:
                return temp_condition[1]
            if eval(temp_condition[0]) is True:
                return temp_condition[1]
        return ""

# example:

# variable replacement statement

# text = 'Hello {: name :}!'
# test = Template(text)
# print(test.render(name = "Mike"))

# output : "Hello Mike!"
# ---------------------------------

# if statement

# text = 'Your result: {?count==5->{:name:},count<5->less than five,else->more than five?}!'
# test = Template(text)
# print(test.render(count = 5, name = 'Mike'))

# output : "Your result: more than five!"

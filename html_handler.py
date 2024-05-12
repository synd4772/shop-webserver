import re


class HTMLHandler(object):
    @staticmethod
    def import_code(file):
        default_html_code = ""
        with open(file=file, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                default_html_code += str(line.strip())
        return default_html_code

    @staticmethod
    def export_into_file(file, HTML_code):
        with open(file, "w", encoding="utf-8") as spf:
            spf.write(HTML_code)

    @staticmethod
    def html_code_into_list(html_code):
        temp_list = list()
        temp_string = ''
        element_in_loop = False
        for symbol in html_code:
            if symbol == "<" and not element_in_loop:
                if temp_string != "":
                    temp_list.append(temp_string)
                    temp_string = ""
                element_in_loop = True
                temp_string += symbol
            elif symbol == ">":
                element_in_loop = False
                temp_string += symbol
                temp_list.append(temp_string)
                temp_string = ""
            elif element_in_loop:
                temp_string += symbol

            elif not element_in_loop:
                temp_string += symbol
        return temp_list

    @staticmethod
    def html_list_into_string(html_list):
        return "".join(html_list)


class HTMLElementsHandler(HTMLHandler):
    def __init__(self, html_file=None, code=None):
        if code is None:
            self.html_code = self.import_code(html_file)
        else:
            self.html_code = code

    def get_html_code(self):
        return self.html_code

    def set_html_code(self, new_code):
        self.html_code = new_code

    def get_element(self, element):
        start_default_pattern = fr"<{element}[^>]*>"
        end_default_pattern = fr"</{element}[^>]*>"
        html_list = self.html_code_into_list(self.html_code)
        start_element = None
        x = False
        y = []
        for index, element in enumerate(html_list):
            if re.match(start_default_pattern, element) and x is False:
                x = True
                start_element = index
            elif x is True and re.match(start_default_pattern, element):
                y.append(element)
            elif len(y) and re.match(end_default_pattern, element):
                y.pop()
            elif x is True and re.match(end_default_pattern, element):
                return start_element, index

    def get_element_by_id(self, element_id):
        start_default_pattern = fr"<(?P<name>.+) id=\"{element_id}\"[^>]*>"
        temp_pattern = ''
        end_default_pattern = ''
        html_list = self.html_code_into_list(self.html_code)
        start_element = list()
        element_in_loop_found = False
        temp_list = []
        for index, element in enumerate(html_list):
            x_match = re.match(start_default_pattern, element)
            if re.match(start_default_pattern, element):
                tag_name = x_match.group('name')
                temp_pattern = fr"<{tag_name}[^>]*>"
                start_element = index
                end_default_pattern = fr"</{tag_name[0]}[^>]*>"
                element_in_loop_found = True
            elif element_in_loop_found is True and re.match(temp_pattern, element):
                temp_list.append(element)
            elif len(temp_list) and re.match(end_default_pattern, element):
                temp_list.pop()
            elif element_in_loop_found is True and re.match(end_default_pattern, element):
                return start_element, index
        return None

    def get_text_element_by_id(self, element_id):
        start, end = self.get_element_by_id(element_id)
        return self.html_code_into_list(self.get_html_code())[start + 1]

    def change_text_element_by_id(self, text, element_id):
        start, end = self.get_element_by_id(element_id)
        html_list = self.html_code_into_list(self.get_html_code())
        html_list[start + 1] = text
        self.html_code = self.html_list_into_string(html_list)

    def push_into_element(self, code_fragment, element="body", element_id=None):
        html_list = self.html_code_into_list(self.html_code)

        if element_id is not None:
            start_element, end_element = self.get_element_by_id(element_id)
        else:
            start_element, end_element = self.get_element(element)

        html_list.insert(start_element + 1, code_fragment)
        self.set_html_code(self.html_list_into_string(html_list))

    def delete_element(self, element_id, element=None):
        html_list = self.html_code_into_list(self.html_code)
        if element is None:
            start_tag_index, end_tag_index = self.get_element_by_id(element_id)
            x = end_tag_index - start_tag_index
            for i in range(x):
                html_list.pop(start_tag_index)
            self.set_html_code(self.html_list_into_string(html_list))


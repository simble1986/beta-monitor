#!/usr/bin/env python
# encoding: utf-8

import time


class HtmlBase(object):
    colors = {
        'danger': "#f0506e",
        'light_danger': "#fef4f6",
        'success': "#32d296",
        'light_success': "#edfbf6",
        'warning': "#faa05a",
        'light_warning': "#fff6ee",
        'primary': "#1e87f0",
        'light_primary': "#d8eafc",
        'dark': "#222",
        'mute': "#f8f8f8",
        'light': "#fff",
        'default': "#fff"
    }

    def __init__(self):
        super(HtmlBase, self).__init__()
        self.title = ""
        self.html = ""

    @property
    def base_start(self):
        html = '<html><head><meta charset="UTF-8"></head>'
        html += '<body style="margin: 0">'
        html += '<div style="width: 75%; text-align: center; margin-left:auto; margin-right:auto; padding-left: 40px; padding-right: 40px">'
        html += '<div style="box-shadow: 0 5px 15px rgba(0,0,0,.08);">'
        return html

    @property
    def base_end(self):
        html = "</div></div></body></html>"
        return html

    @property
    def header(self):
        title = self.title
        this_time = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        html = '<div id="header" style="background: #1e87f0; text-align: center; padding-top: 3px; padding-bottom: 3px;">'
        html += '<h2 style="color: #fff; margin-bottom: 0">%s</h2>' %title
        html += '<p style="color: rgba(255,255,255,.5); margin-top: 0">%s</p>' % this_time
        html += '</div>'
        return html

    @property
    def body(self):
        html = '<div id="body" style="padding: 20 40">'
        html += self.section1
        html += self.section2
        html += "</div>"
        return html

    @property
    def footer(self):
        html = '<div id="footer" style="text-align: center; padding: 20 40;"></div>'
        return html

    @property
    def section1(self):
        html = ""
        return html

    @property
    def section2(self):
        html = ""
        return html

    def gen(self):
        self.html = self.base_start + self.header + self.body + self.footer + self.base_end
        return self.html


class HtmlReport(HtmlBase):

    def __init__(self, title):
        super(HtmlReport, self).__init__()
        self.title = title
        self.basic_info = [
            {"title": "当前状态", "value": "Online", "color": 'success', "bg_color": "default"},
            {"title": "在线时长", "value": "2天3小时5分40秒", "color": 'dark', "bg_color": "default"},
            {"title": "License状态", "value": "剩余30天", "color": 'warning', "bg_color": "default"},
            {"title": "Coredumps", "value": "0", "color": 'success', "bg_color": "default"},
            {"title": "启动文件", "value": "SG6000-M-2-5.5R6.bin", "color": 'dark', "bg_color": "default"}
        ]
        self.tables = [
            {"title": "应用Top 10",
             "total": 10,
             "thead": ["名称", "流量", "并发连接"],
             "flex": [1, 1, 1],
             "value": [["HTTP", "114.05M", "18265"],
                       ["SMTP", "97.2M", "627"],
                       ["FTP", "35M", "236"],
                       ["SSH", "21M", "101"],
                       ["DNS", "562K", "21"]
                       ]
             },
            {"title": "用户Top 10",
             "total": 10,
             "thead": ["名称", "流量", "并发连接"],
             "flex": [1, 1, 1],
             "value": [["192.168.0.1", "234.05M", "9265"],
                       ["192.168.11.2", "197.2M", "1627"],
                       ["10.180.13.4", "55M", "636"],
                       ["10.160.12.12", "11M", "91"],
                       ["10.160.36.251", "5.3M", "37"]
                       ]
             },
            {"title": "威胁Top 10",
             "total": 10,
             "thead": ["名称", "流量", "并发连接"],
             "flex": [1, 1, 1],
             "value": [["192.168.0.1", "234.05M", "9265"],
                       ["192.168.11.2", "197.2M", "1627"],
                       ["10.180.13.4", "55M", "636"],
                       ["10.160.12.12", "11M", "91"],
                       ["10.160.36.251", "5.3M", "37"]
                       ]
             },
        ]

    def set_title(self, title="Beta Monitor Daily Report - Test Device"):
        self.title = title

    @property
    def section1(self):
        # 第一部分为基本信息，信息每行3个
        # 基本信息
        # --------------------------------------------------------------------------
        #  当前状态： Online        在线时长： 2天3小时5分40秒   License状态： 剩余30天
        #  Coredumps： 0           启动文件： SG6000-M-2-5.5R6.bin

        # 第一部分开始
        html = '<div style="text-align: left;">' \
               '<h3 style="margin-bottom: 5px">基本信息</h3>' \
               '<hr style="border-top: 1px solid #e5e5e5; width: 100%;">' \
               '<div style="padding-left: 10px; padding-right: 10px; display: flex; flex-direction: column;">'
        # 将数组每3个分割为一个小数组
        tmp_list = [self.basic_info[i:i+3] for i in range(0, len(self.basic_info), 3)]
        for i in tmp_list:
            # 行开始
            html += '<div style="flex: 1;">' \
                    '<div style="padding-top: 20px; height: 20px; display:flex; flex-direction:row;">'
            for j in i:
                # 逐个元素
                html += '<div style="flex: 1">%s: <span style="color: %s">%s</span></div>' % (j["title"],
                                                                                              self.colors[j["color"]],
                                                                                              j["value"])
            # 如果该行元素不足三个，补足
            for k in range(3-len(i)):
                html += '<div style="flex: 1">&nbsp;</div>'
            # 行结尾，闭合div
            html += "</div></div>"
        # 第一部分结束，闭合div
        html += "</div></div>"
        return html

    @property
    def section2(self):
        html = ""
        # Section 2的头部
        html += '<div style="text-align: left;">' \
                '<h3 style="margin-bottom: 5px">统计信息</h3>' \
                '<hr style="border-top: 1px solid #e5e5e5; width: 100%;">'
        tmp_table = [self.tables[i:i + 2] for i in range(0, len(self.tables), 2)]
        for i in tmp_table:
            # 一行
            html += '<div style="display: flex; flex-direction: row; padding-top: 10px; padding-bottom: 10px;">'
            for j in i:
                # block开始
                html += '<div style="flex: 1">'
                html += '<div style="width: 96%; margin-left: auto; margin-right: auto;box-shadow: 0 5px 5px rgba(0,0,0,.08)">'
                # 标题拦
                html += '<div style="background: #1e87f0; text-align: center; color: #fff; padding-top: 3px; padding-bottom: 3px;">'
                html += '<h4 style="margin-top: 3px; margin-bottom: 3px;">%s</h4></div>' %j["title"]
                # 表框体开始
                html += '<div style="width: 92%; margin-left: auto; margin-right: auto; display:flex; flex-direction: column; padding-bottom: 10px; padding-top: 10px;">'
                # 表头开始
                html += '<div style="flex: 1; display: flex; flex-direction: row; border-bottom: 1px solid #e5e5e5;">'
                for th in range(len(j["thead"])):
                    if th == 0:
                        html += '<div style="flex: %s; text-align: left; padding: 0 5;">%s</div>' %(
                            j["flex"][th], j["thead"][th])
                    else:
                        html += '<div style="flex: %s; text-align: right; padding: 0 5;">%s</div>' % (
                            j["flex"][th], j["thead"][th])
                # 表头结束
                html += '</div>\n'
                # 表体开始
                for item in j["value"]:
                    # 行开始
                    html += '<div style="flex: 1; display: flex; flex-direction: row">'
                    for v in range(len(item)):
                        if v == 0:
                            # 第一个元素靠左对齐，打印右边框
                            html += '<div style="flex: %s; text-align: left; padding: 0 5; border-right: 1px solid #e5e5e5;">%s</div>' % (
                                j["flex"][v], item[v])
                        elif v+1 == len(item):
                            # 最后一个元素不打印右边框
                            html += '<div style="flex: %s; text-align: right; padding: 0 5;">%s</div>' %(j["flex"][v], item[v])
                        else:
                            # 其他元素靠右对齐，打印右边框
                            html += '<div style="flex: %s; text-align: right; padding: 0 5; border-right: 1px solid #e5e5e5;">%s</div>' % (
                                j["flex"][v], item[v])
                    # 行结束
                    html += '</div>\n'

                # 元素不足时，处理为空行
                # for k in range(j["total"] - len(j["value"])):
                #     # 行开始
                #     html += '<div style="flex: 1; display: flex; flex-direction: row">'
                #     for f in range(len(j["flex"])):
                #         if f == 0:
                #             # 第一个元素靠左对齐，打印右边框
                #             html += '<div style="flex: %s; text-align: left; padding: 0 5; border-right: 1px solid #e5e5e5;">&nbsp;</div>' % (
                #                 j["flex"][f])
                #         elif f+1 == len(j["flex"]):
                #             # 最后一个元素不打印右边框
                #             html += '<div style="flex: %s; text-align: right; padding: 0 5;">&nbsp;</div>' %(j["flex"][f])
                #         else:
                #             # 其他元素靠右对齐，打印右边框
                #             html += '<div style="flex: %s; text-align: right; padding: 0 5; border-right: 1px solid #e5e5e5;">&nbsp;</div>' % (
                #                 j["flex"][f])
                #     # 行结束
                #     html += '</div>'
                # 表体结束
                html += "</div>"
                # 表框体结束
                html += "</div>"
                # Block结束
                html += "</div>"
            # 如果该行元素不足2个，补足
            for k in range(2 - len(i)):
                html += '<div style="flex: 1">&nbsp;</div>'
            # 行结束
            html += "</div>"
        # section2 结束
        html += "</div>"
        return html


    @property
    def line1(self):
        html = '<div style="display: flex; flex-direction: row; padding-top: 10px; padding-bottom: 10px;">'
        # 第一行被分割为两个block
        # Block1
        html += '<div style="flex: 1">'
        if self.app_top_10:
            html += self.app_top_10
        else:
            html += "&nbsp;"
        html += "</div>"
        # Block2
        html += '<div style="flex: 1">'
        if self.user_top_10:
            html += self.user_top_10
        else:
            html += "&nbsp;"
        html += '</div>'
        return html

    @property
    def line2(self):
        html = '<div style="display: flex; flex-direction: row; padding-top: 10px; padding-bottom: 10px;">'
        # 第二行被分割为两个block
        # Block1
        html += '<div style="flex: 1">'
        if self.threat_top_10:
            html += self.threat_top_10
        else:
            html += "&nbsp;"
        html += "</div>"
        # Block2
        html += '<div style="flex: 1">'
        if self.xxx_top_10:
            html += self.xxx_top_10
        else:
            html += "&nbsp;"
        html += '</div>'
        return html

    @property
    def app_top_10(self):
        html = ""
        return html

    @property
    def user_top_10(self):
        html = ""
        return html

    @property
    def threat_top_10(self):
        html = ""
        return html

    @property
    def xxx_top_10(self):
        html = ""
        return html


if __name__ == '__main__':
    daily_report = HtmlReport("Test Daily Report - Demo")
    print daily_report.gen()
import scrapy
import re

class IonicSpider(scrapy.Spider):
    name = "ionic_spider"
    start_urls = ['https://www.tutorialspoint.com/ionic/index.htm']
    page_pattern_count = 0
    with open('input_format.txt') as f:
        page_patterns = [words.strip().split() for words in f]

    def parse(self, response):
        div_selector = '/html/body/div[4]/div[1]/div/div[2]/div[1]/div'
        content = response.xpath(div_selector)
        num_h1 = num_h2 = num_para = num_ul = num_pre = num_img = 1
        header_name = ""

        while(True):
            n = IonicSpider.page_patterns[IonicSpider.page_pattern_count]
            IonicSpider.page_pattern_count += 1
            if n[0] == 'h1':
                header_name = ""
                heading_selector = div_selector + '/h1[' + str(num_h1) + ']/text()'
                num_h1 += 1
                header_name = content.xpath(heading_selector).extract_first()
            elif n[0] == 'h2':
                header_name = ""
                heading_selector = div_selector + '/h2[' + str(num_h2) + ']/text()'
                num_h2 += 1
                header_name = content.xpath(heading_selector).extract_first()
            elif n[0] == 'p' and n[1] == '0':
                num_para += int(n[2])
                continue
            elif n[0] == 'p':
                para_content = ""
                for i in range(int(n[1])):
                    para_selector = div_selector + '/p[' + str(num_para) + ']'
                    num_para += 1
                    para_content += re.sub('<[^>]*>', '', content.xpath(para_selector).extract_first()) + " "
                    para_content = re.sub('\u2212', '-', para_content)
                yield {
                    header_name: para_content,
                }
            elif n[0] == 'ul':
                ul_selector = div_selector + '/ul[' + str(num_ul) + ']'
                num_ul += 1
                num_li=1
                list_contents = []
                for i in range(int(n[1])):
                    ul_para_selector = ul_selector + '/li[' + str(num_li) + ']/p'
                    num_li += 1
                    list_content = re.sub('<[^>]*>', '', content.xpath(ul_para_selector).extract_first())
                    list_content = re.sub('\u2212', '-', list_content)
                    list_contents.append(list_content)
                yield {
                    header_name: list_contents,
                }
            elif n[0] == 's':
                length = len(n)
                mini_para_content = ""
                steps = []
                dic = {}
                for i in range(1,length):
                    if n[i] == 'p':
                        para_selector = div_selector + '/p[' + str(num_para) + ']'
                        num_para += 1
                        mini_para_content += re.sub('<[^>]*>', '', content.xpath(para_selector).extract_first())
                    elif n[i] == 'pre':
                        pre_selector = div_selector + '/pre[' + str(num_pre) + ']'
                        num_pre += 1
                        pre_content = re.sub('<[^>]*>', '', content.xpath(pre_selector).extract_first())
                        pre_content = re.sub('\r\n', '', pre_content)
                        pre_content = re.sub('&gt;', '>', pre_content)
                        pre_content = re.sub('&lt;', '<', pre_content)
                        dic["para"] = mini_para_content
                        mini_para_content = ""
                        dic["command"] = pre_content
                        steps.append(dic)
                        dic = {}
                    elif n[i] == 'img':
                        img_selector = div_selector + '/img[' + str(num_img) + ']/@src'
                        num_img += 1
                        img_content = 'https://www.tutorialspoint.com' + content.xpath(img_selector).extract_first()
                        dic["para"] = mini_para_content
                        mini_para_content = ""
                        dic["image"] = img_content
                        steps.append(dic)
                        dic = {}
                yield {
                    header_name : steps
                }
            elif n[0] == 'e':
                break

        next_page_selector = div_selector + '/div[3]/a/@href'
        next_page = response.xpath(next_page_selector).extract_first()
        if next_page != '/ionic/ionic_js_action_sheet.htm':
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )
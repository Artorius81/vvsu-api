import re
from datetime import datetime

from lxml import etree


# TIME_TABLE
def parse_time(td):
    start, end = td.text.strip().split('-')
    time = {
        'start': start,
        'end': end
    }
    return time


def parse_title_vebinar(td):
    vebinar_url = None
    a = td.xpath('./a')
    span = td.xpath('./span')
    if a:
        title = a[0].text.strip()
    else:
        title = td.text.strip()
    if span:
        if 'вебинар' not in span[0].text.strip():
            raise Exception('какой-то странный спан')
        span_a = span[0].xpath('./a')[0]
        vebinar_url = span_a.get('href')
    return title, vebinar_url


def parse_teacher(td):
    teacher_elements = td.xpath('./a/text()')
    teacher_vacancy = td.text.strip()
    if teacher_elements:
        teacher = teacher_elements[0].strip()
    elif teacher_vacancy:
        teacher = teacher_vacancy
    else:
        teacher = None
    return teacher


def parse_label(td):
    label = {
        'title': td.text.strip(),
        # 'class': 'label-blue'
    }
    return label


def parse_room(td):
    room = td.text.strip()
    return room


def parse_lesson(tds):
    data = {}

    time = parse_time(tds[0])
    data.update({'time': time})

    title, vebinar = parse_title_vebinar(tds[1])
    if vebinar:
        _chunk = {
            'title': title,
            'vebinar': vebinar
        }
    else:
        _chunk = {'title': title}
    data.update(_chunk)

    teacher = parse_teacher(tds[2])
    data.update({'teacher': teacher})

    label = parse_label(tds[3])
    data.update({'label': label})

    room = parse_room(tds[4])
    data.update({'room': room})
    return data


def get_time_table(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    plan_details = tree.xpath('//div[@id="cabinetMain"]//table')
    data = []
    for table in plan_details:
        for tr in table.xpath('.//tr'):
            tds = tr.xpath('.//td')
            if len(tds) == 1:
                date = tds[0].xpath('.//b/text()')[0].split()[-1]
                data.append(
                    {
                        'date': date,
                        'lessons': []
                    })
            elif len(tds) == 5:
                lesson = parse_lesson(tds)
                data[-1]['lessons'].append(lesson)
            else:
                raise Exception(f'Неожиданное значение len(tds): {len(tds)}')
    return data


# RESULTS
def parse_semester_part(control_td, score_td, teacher_td):
    control_type = control_td.xpath('./text/text()')[0].strip()
    score, max_score = score_td.text.strip().split(' из ')
    score = int(score)
    max_score = int(max_score)
    teacher = teacher_td.xpath('./text/text()')[0].strip()
    part = {
        'controlType': control_type,
        'score': score,
        'max_score': max_score,
    }
    if teacher:
        part.update({'teacher': teacher})
    return part


def parse_semester_results(div):
    data = []
    for tr in div.xpath('./div/table/tr')[:-1]:
        tds = tr.xpath('./td')
        if len(tds) == 5:
            title = tds[0].text.strip()
            part = parse_semester_part(tds[1], tds[2], tds[3])
            *_mark_string, _mark = tds[4].text.strip().split()
            mark_string = ' '.join(_mark_string)
            mark = int(_mark.replace('(', '').replace(')', ''))
            data.append({
                'title': title,
                'parts': [part],
                'mark': mark,
                'markString': mark_string
            })
        else:
            part = parse_semester_part(tds[0], tds[1], tds[2])
            data[-1]['parts'].append(part)
    return data


def get_results(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    plan_details = tree.xpath('//div[@id="PlanDetails"]/div/div/div')[1:]
    _results = {}
    for semester_num, semester_div in enumerate(plan_details, 1):
        semester_results = parse_semester_results(semester_div)
        _results[semester_num] = semester_results
    return _results


# CURRICULUM
def get_curriculum(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    semester_div_ids = tree.xpath("//*[@id='PlanDetails']//div[contains(@id, 'tabs-')]/@id")
    #print(semester_div_ids)
    semester_wise_data = {}

    for div_id in semester_div_ids:
        rows = tree.xpath(f"//div[@id='{div_id}']//tr") #/div/table/tbody/tr[1]
        data = []

        for row in rows[1:]:
            discipline = row.xpath("td[1]//text()")
            #print(discipline)
            department = row.xpath("td[2]//text()")
            #print(department)
            teacher_elements = row.xpath("(td[3]//a[1]/text() | td[3]//text()[1]) | (td[3]//a[1] | td[3])")
            #print(teacher_elements)
            attestation = row.xpath("td[contains(@class, 'text-center')]/text()")
            #print(attestation)

            if discipline:
                disciplines = ' '.join(discipline).strip()
            else:
                disciplines = None

            if department:
                department_text = department[0].strip()
                if department_text:
                    departments = department_text
                else:
                    departments = None
            else:
                departments = None

            if teacher_elements:
                teacher_text = ' '.join([elem.strip() for elem in teacher_elements if isinstance(elem, str)]).strip()
                if teacher_text:
                    teacher_match = re.search(r'\w+\s[А-ЯЁ]\.[А-ЯЁ]\.', teacher_text)
                    if teacher_match:
                        teachers = teacher_match.group()
                    else:
                        teachers = None
                else:
                    teachers = None
            else:
                teachers = None

            if attestation:
                filtered_attestation = [a for a in attestation if a in ["Э", "З", "КР", "Р", "ЗП", "УП", "ПП", "НИП", "КЭ", "ЗНР", "ЗВР", "НИР", "ДЗ"]]
                if filtered_attestation:
                    attestations = filtered_attestation[0]
                else:
                    attestations = None
            else:
                attestations = None

            # Check if all values are None and skip the entry if true
            if all(val is None for val in [teachers, disciplines, attestations]):
                continue

            entry = {
                "teacher": teachers,
                "discipline": disciplines,
                "department": departments,
                "attestation": attestations
            }
            data.append(entry)

        semester_number = div_id.split('-')[-1]
        semester_wise_data[semester_number] = data

    return semester_wise_data


# MY_GROUP
def get_group(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    cards = tree.xpath("//*[@id='PlanDetails']//div[contains(@class, 'card')]")
    extracted_data = []

    for card in cards:
        photo_element = card.xpath(".//img[contains(@class, 'card-img-top')]/@src")
        photo = photo_element[0] if photo_element else None

        if not photo:  # Skip the entry if photo is null
            continue

        fullname_element = card.xpath(".//h6/text()")
        fullname = fullname_element[0].strip() if fullname_element else None

        email_element = card.xpath(".//a/text()")
        email = email_element[0].strip() if email_element else None

        card_data = {
            "photo": photo,
            "fullname": fullname,
            "email": email
        }

        extracted_data.append(card_data)

    return extracted_data


# MAIN
def get_main(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    fio = tree.xpath("/html/body/div[3]/div/div[1]/div/div[1]/div/div/div[1]/div/h1/text()")
    email = tree.xpath("/html/body/div[3]/div/div[1]/div/div[1]/div/div/div[2]/div[1]/div[2]/a/text()")
    group = tree.xpath("/html/body/div[3]/div/div[1]/div/div[1]/div/div/div[3]/div[1]/div[2]/text()")
    portfolio_link = tree.xpath('//*[@id="cnt"]/div/ul/li[10]/a/@href')

    if portfolio_link:
        portfolio_url = "https:" + portfolio_link[0]
    else:
        portfolio_url = None

    additional_info_parts = tree.xpath(
        "/html/body/div[3]/div/div[1]/div/div[1]/div/div/div[3]/div[3]/div[2]/span//text()")
    additional_info_cleaned = [text.strip() for text in additional_info_parts if
                               text.strip()]

    additional_info_field1 = additional_info_cleaned[0] if len(additional_info_cleaned) > 0 else None
    additional_info_field2 = additional_info_cleaned[1] if len(additional_info_cleaned) > 1 else None
    additional_info_field3 = additional_info_cleaned[2] if len(additional_info_cleaned) > 2 else None

    style_element = tree.xpath("/html/body/div[3]/div/div[1]/div/div[2]/div/div/@style")
    url_match = re.search(r'url\((.*?)\)', style_element[0].strip()) if style_element else None
    url = url_match.group(1) if url_match else None

    data = {
        "fullname": fio[0].strip() if fio else None,
        "email": email[0].strip() if email else None,
        "group": group[0].strip() if group else None,
        "specialty": additional_info_field1,
        "institute": additional_info_field2,
        "department": additional_info_field3,
        "photo": url,
        "portfolioURL": portfolio_url
    }

    return data


# PAYMENTS
def get_grants(html):
    tree = etree.fromstring(html, etree.HTMLParser())

    data = {}

    tab_names_xpath = "//*[@id='tabs']/div/ul/li/a/b/text()"

    excluded_headers = ["Период", "Сумма, руб", "Начисления"]

    tab_names = tree.xpath(tab_names_xpath)

    last_name = tab_names[-1]

    tab_content_xpath = f"//*[@id='tabs-{last_name}']//text()"

    content_elements = tree.xpath(tab_content_xpath)
    cleaned_content = [item.strip() for item in content_elements if
                       item.strip() and item.strip() not in excluded_headers]

    tab_data = []

    for i in range(0, len(cleaned_content), 3):
        tab_entry = {
            "type": cleaned_content[i] if i < len(cleaned_content) else "",
            "period": cleaned_content[i + 1] if i + 1 < len(cleaned_content) else "",
            "sum": cleaned_content[i + 2] if i + 2 < len(cleaned_content) else ""
        }
        tab_data.append(tab_entry)

    data = tab_data

    return data


def get_payment(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    field_names = [
        "plan_code",
        "duration",
        "status",
        "total_cost",
        "monthly_payment",
        "total_paid",
        "remaining_cost",
        "cost_to_end"
    ]

    primary_xpath = "//*[@id='PlanDetails']/div/div/div/div"
    num_divs = len(tree.xpath(primary_xpath))

    extracted_data = []

    if num_divs > 0:
        for i in range(1, num_divs + 1, 2):
            if (i + 1) <= num_divs:
                xpath_odd = f"//*[@id='PlanDetails']/div/div/div/div[{i}]//p/text()"
                xpath_even = f"//*[@id='PlanDetails']/div/div/div/div[{i + 1}]//p/text()"

                p_tag_odd = tree.xpath(xpath_odd)
                p_tag_even = tree.xpath(xpath_even)

                concatenated_tag = ''
                if p_tag_odd:
                    concatenated_tag += p_tag_odd[0].strip()
                if p_tag_even:
                    concatenated_tag += ' ' + p_tag_even[0].strip()
                if concatenated_tag:
                    extracted_data.append(concatenated_tag)
    else:
        alternate_xpath = "//*[@id='PlanDetails']/div/p/strong"
        strong_tags = tree.xpath(alternate_xpath)

        for tag in strong_tags:
            cleaned_tag = tag.text.strip() if tag.text else None
            if cleaned_tag:
                extracted_data.append(cleaned_tag)

    data = {field_names[index]: value for index, value in enumerate(extracted_data) if index < len(field_names)}

    return data


def get_dormitory(html):
    tree = etree.fromstring(html, etree.HTMLParser())

    tab_names_xpath = "//*[@id='tabs']/div/ul/li/a/b/text()"

    excluded_headers = ["Период", "Сумма, руб", "Платеж"]

    tab_names = tree.xpath(tab_names_xpath)

    if not tab_names:
        alternative_tab_name_xpath = "//*[@id='cabinetMain']/p/strong/text()"
        alternative_tab_name = tree.xpath(alternative_tab_name_xpath)[0].strip()
        tab_data = [{"type": alternative_tab_name}]
    else:
        last_name = tab_names[-1]

        tab_content_xpath = f"//*[@id='tabs-{last_name}']//text()"

        content_elements = tree.xpath(tab_content_xpath)
        cleaned_content = [item.strip() for item in content_elements if
                           item.strip() and item.strip() not in excluded_headers]

        tab_data = []

        for i in range(1, len(cleaned_content), 3):
            tab_entry = {
                "type": cleaned_content[i] if i < len(
                    cleaned_content) else "Данные по оплате за общежитие отсутствуют",
                "period": cleaned_content[i + 1] if i + 1 < len(cleaned_content) else "",
                "sum": cleaned_content[i + 2] if i + 2 < len(cleaned_content) else ""
            }
            tab_data.append(tab_entry)

    data = tab_data

    return data


def get_internet_pay(html):
    tree = etree.fromstring(html, etree.HTMLParser())

    tab_names_xpath = "//*[@id='tabs']/div/ul/li/a/b/text()"

    excluded_headers = ["Период", "Сумма, руб", "Платеж"]

    tab_names = tree.xpath(tab_names_xpath)

    if not tab_names:
        alternative_tab_name_xpath = "//*[@id='cabinetMain']/p/strong/text()"
        alternative_tab_name = tree.xpath(alternative_tab_name_xpath)[0].strip()
        tab_data = [{"type": alternative_tab_name}]
    else:
        last_name = tab_names[-1]

        tab_content_xpath = f"//*[@id='tabs-{last_name}']//text()"

        content_elements = tree.xpath(tab_content_xpath)
        cleaned_content = [item.strip() for item in content_elements if
                           item.strip() and item.strip() not in excluded_headers]

        tab_data = []

        for i in range(1, len(cleaned_content), 3):
            tab_entry = {
                "type": cleaned_content[i] if i < len(
                    cleaned_content) else "Данные по оплате за интернет отсутствуют",
                "period": cleaned_content[i + 1] if i + 1 < len(cleaned_content) else "",
                "sum": cleaned_content[i + 2] if i + 2 < len(cleaned_content) else ""
            }
            tab_data.append(tab_entry)

    data = tab_data

    return data


def get_traffic(html):
    tree = etree.fromstring(html, etree.HTMLParser())

    month_dict = {
        "янв": "01",
        "фев": "02",
        "мар": "03",
        "апр": "04",
        "май": "05",
        "июн": "06",
        "июл": "07",
        "авг": "08",
        "сен": "09",
        "окт": "10",
        "ноя": "11",
        "дек": "12"
    }

    def transform_date(input_date, condition):
        current_year = datetime.now().year
        month_num = month_dict.get(input_date)
        if month_num is None:
            return "Неверный месяц"
        if condition:
            formatted_date = f"{month_num}-{current_year}"
        else:
            # formatted_date = f"{month_num}-{current_year - 1}" ваще не помню че это потом разобраться
            formatted_date = f"{month_num}-{current_year}"
        return formatted_date

    tab_names_xpath = "//*[@id='tabs']/div/ul/li/a/b/text()"

    excluded_headers = ["Дата", "Трафик, Mb"]

    tab_names = tree.xpath(tab_names_xpath)

    if not tab_names:
        alternative_tab_name_xpath = "//*[@id='cabinetMain']/p/strong/text()"
        alternative_tab_name = tree.xpath(alternative_tab_name_xpath)[0].strip()
        tab_data = [{"period": alternative_tab_name}]
    else:
        last_name = tab_names[-1]
        last_name_transformed = transform_date(last_name, False)

        tab_content_xpath = f"//*[@id='tabs-{last_name_transformed}']//text()"

        content_elements = tree.xpath(tab_content_xpath)
        cleaned_content = [item.strip() for item in content_elements if
                           item.strip() and item.strip() not in excluded_headers]

        tab_data = []

        for i in range(0, len(cleaned_content), 2):
            tab_entry = {
                "period": cleaned_content[i] if i < len(cleaned_content) else "Данные по интернет-трафику отсутствуют",
                "traffic": cleaned_content[i + 1] if i + 1 < len(cleaned_content) else ""
            }
            tab_data.append(tab_entry)

    data = tab_data

    if not data:
        last_name = tab_names[-1]
        last_name_transformed = transform_date(last_name, True)

        tab_content_xpath = f"//*[@id='tabs-{last_name_transformed}']//text()"

        content_elements = tree.xpath(tab_content_xpath)
        cleaned_content = [item.strip() for item in content_elements if
                           item.strip() and item.strip() not in excluded_headers]

        tab_data = []

        for i in range(0, len(cleaned_content), 2):
            tab_entry = {
                "period": cleaned_content[i] if i < len(cleaned_content) else "Данные по интернет-трафику отсутствуют",
                "traffic": cleaned_content[i + 1] if i + 1 < len(cleaned_content) else ""
            }
            tab_data.append(tab_entry)

    return data


# MY_TASKS
def get_forms(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    table_xpath = '//*[@id="cabinetMain"]/div/table/tbody'
    rows = tree.xpath(table_xpath + '/tr')
    data = []
    for row in rows:
        cells = row.xpath('./td')
        discipline = cells[0].xpath('.//text()')[0].strip() if len(cells) > 0 else None
        session_type = cells[1].xpath('.//text()')[0].strip() if len(cells) > 1 else None
        teacher = cells[2].xpath('.//text()')[0].strip() if len(cells) > 2 else None
        anketa_link = cells[3].xpath('.//a/@href')
        anketa = 'https://cabinet.vvsu.ru' + anketa_link[0].strip() if anketa_link else None
        data.append({
            'discipline': discipline,
            'type': session_type,
            'teacher': teacher,
            'form_link': anketa
        })
    return data


def get_projects(html):
    tree = etree.fromstring(html, etree.HTMLParser())
    rows_alt = tree.xpath('//*[@id="cabinetMain"]/h4')
    data = []
    if rows_alt:
        xpath_alt = '//*[@id="cabinetMain"]/div[3]/div/div/table//tr'
        rows = tree.xpath(xpath_alt)
        if rows:
            for row in rows[1:]:
                cells = row.xpath('./td')
                project_name = cells[0].xpath('.//a/text()')[0].strip() if len(cells) > 0 and cells[0].xpath(
                    './/a/text()') else "Проекты по выбору отсутствуют"
                project_link = 'https://cabinet.vvsu.ru' + cells[0].xpath('.//a/@href')[0].strip() if len(cells) > 0 and \
                                                                                                      cells[0].xpath(
                                                                                                          './/a/@href') else None
                project_type = cells[1].xpath('.//text()')[0].strip() if len(cells) > 1 and cells[1].xpath(
                    './/text()') else None
                project_leader = cells[2].xpath('.//text()')[0].strip() if len(cells) > 2 and cells[2].xpath(
                    './/text()') else None
                project_action = cells[3].xpath('.//text()')[0].strip() if len(cells) > 3 and cells[3].xpath(
                    './/text()') else None

                data.append({
                    'prj_name': project_name,
                    'prj_link': project_link,
                    'prj_type': project_type,
                    'prj_leader': project_leader,
                    'prj_time': project_action
                })
        else:
            no_prj = tree.xpath('//*[@id="cabinetMain"]/div[2]/div/p/strong/text()')[0].strip()
            data.append({
                'prj_name': no_prj
            })
    elif not rows_alt:
        xpath = '//*[@id="cabinetMain"]/div[2]/div/div/table//tr'
        rows = tree.xpath(xpath)
        if rows:
            for row in rows[1:]:
                cells = row.xpath('./td')
                project_name = cells[0].xpath('.//a/text()')[0].strip() if len(cells) > 0 and cells[0].xpath(
                    './/a/text()') else None
                project_link = 'https://cabinet.vvsu.ru' + cells[0].xpath('.//a/@href')[0].strip() if len(cells) > 0 and \
                                                                                                      cells[0].xpath(
                                                                                                          './/a/@href') else None
                project_type = cells[1].xpath('.//text()')[0].strip() if len(cells) > 1 and cells[1].xpath(
                    './/text()') else None
                project_leader = cells[2].xpath('.//text()')[0].strip() if len(cells) > 2 and cells[2].xpath(
                    './/text()') else None
                project_action = cells[3].xpath('.//text()')[0].strip() if len(cells) > 3 and cells[3].xpath(
                    './/text()') else None

                data.append({
                    'prj_name': project_name,
                    'prj_link': project_link,
                    'prj_type': project_type,
                    'prj_leader': project_leader,
                    'prj_time': project_action
                })
        else:
            no_prj = tree.xpath('//*[@id="cabinetMain"]/div[2]/div/p/strong/text()')[0].strip()
            data.append({
                'prj_name': no_prj
            })
    return data

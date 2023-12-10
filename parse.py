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
    teacher = td.xpath('./a/text()')[0].strip()
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

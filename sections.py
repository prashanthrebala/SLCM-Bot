from bs4 import BeautifulSoup as bs
import time
import re
import string_utils
from pprint import pprint
from string_utils import subject_title

days = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday',
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

roman = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII'}


def bunks_to_seventy_five(a, b):
    a, b = int(a), int(b)
    ans = 0
    while a * 100.0 / (b + ans) >= 75:
        ans += 1
    ans = max(0, ans - 1)
    if ans == 1:
        return "1 class"
    return str(ans) + " classes"


def v(string):
    f = float(string)
    return str(int(f)) if f == int(f) else str(f)


def perform_action(user, command):
    command = str(command)
    print command.isdigit()
    if command in tabs:
        return tabs[command](user)
    elif command.isdigit():
        try:
            # return user.temporary_utils[user.current_tab][int(command)]
            print "in perform action"
            return tabs[user.current_tab](user, command)
        except Exception as err:
            print err, "in perform action"
            pass
    print "not command and not digit"
    return "Please enter a valid command"


""" PAGE NAVIGATION """


def go_to_academics(driver):
    if str(driver.current_url) != "http://slcm.manipal.edu/Academics.aspx":
        driver.get("http://slcm.manipal.edu/Academics.aspx")
        time.sleep(1)
    return


def go_to_grade_sheets(driver):
    if str(driver.current_url) != "http://slcm.manipal.edu/GradeSheet.aspx":
        driver.get("http://slcm.manipal.edu/GradeSheet.aspx")
        time.sleep(1)
    return


def timetable(driver):
    print "here"
    go_to_timetable(driver)
    tt = bs(driver.page_source, "html.parser").find_all('table')[6]
    day_classes = tt.find_all("div", class_="fc-content-col")
    ans = ""
    for i in range(len(day_classes)):
        ans += "**" + days[i] + "**:\n"
        for period in day_classes[i].find_all("div", class_="fc-content"):
            ans += period.span.string + " -- " \
                  + subject_title(period.find_all("div", class_="fc-title")[0].string.split(", Section")[0]) + "\n"
    ans += "\n"
    # print ans
    return str(ans), "timetable"


def go_to_basic_details(driver):
    driver.get("http://slcm.manipal.edu/Academics.aspx")
    time.sleep(1)
    soup = bs(driver.page_source, "html.parser")
    table_contents = soup.find_all("ul")[8].find_all("label")
    basic_details = {}
    previous_key = None
    for element in table_contents:
        if element.string is None:
            basic_details[previous_key] = element.span.string
        else:
            previous_key = element.string
    return basic_details


""" ATTENDANCE """


def attendance(user, command=None):
    user.current_tab = "attendance"
    if "attendance" not in user.temporary_utils:
        go_to_academics(user.driver)
        get_attendance(user)
    if command is None:
        return user.temporary_utils["attendance"]["menu"]
    else:
        print "here in attendance"
        return user.temporary_utils["attendance"][int(command)]


def get_attendance(user):
    page_source = bs(user.driver.page_source, "html.parser")
    table = page_source.find_all('tbody')[1]
    attendance_map = {}
    command = ""
    index = 1
    all = ""
    for subject in table.find_all('tr'):
        cells = subject.find_all('td')
        sub = subject_title(cells[2].string)
        ans = ""
        ans += "*" + sub + "*\n"
        ans += "Attended: " + cells[5].string + "\n"
        ans += "Bunked: " + cells[6].string + "\n"
        ans += "Percentage: " + cells[7].string + "\n"
        ans += "You can bunk " + bunks_to_seventy_five(cells[5].string, cells[4].string) + \
               " while maintaining 75%" + "\n\n"
        if sub[-3:] != "Lab":
            all += ans
        attendance_map[index] = ans
        command += "/" + str(index) + " " + sub + "\n"
        index += 1
    command += "/" + str(index) + " " + "All subjects" + "\n"
    attendance_map[index] = all
    attendance_map["menu"] = command
    user.temporary_utils["attendance"] = attendance_map
    return user


""" GRADESHEETS """


def gradesheet(user, command=None):
    user.current_tab = "gradesheet"
    go_to_grade_sheets(user.driver)
    if "gradesheet" in user.temporary_utils:
        if command is None:
            return user.temporary_utils["gradesheet"]["menu"]
        elif int(command) in user.temporary_utils["gradesheet"]:
            return user.temporary_utils["gradesheet"][int(command)]
    else:
        user.temporary_utils["gradesheet"] = {}
    if command is not None:
        total_sems = change_grade_sheet_semester(user, command)
        if int(command) > total_sems:
            return "Please enter a valid command"
    else:
        total_sems = change_grade_sheet_semester(user, 0)
    soup = bs(user.driver.page_source, "html.parser")
    table = soup.find("tbody")
    subjects = table.find_all("tr")[1:]
    gpa = soup.find("span", {"id": "ContentPlaceHolder1_lblGPA"}).string
    cgpa = soup.find("span", {"id": "ContentPlaceHolder1_lblCGPA"}).string
    ans = ""
    ans += "CGPA: *" + str(cgpa) + "*\n"
    ans += "GPA: *" + str(gpa) + "*\n"
    for sub in subjects:
        x = sub.find_all("td")[2:4]
        name, grade = x[0].span.string, x[1].span.string
        ans += subject_title(str(name)) + ": *" + str(grade) + "*\n"

    if "menu" not in user.temporary_utils["gradesheet"]:
        menu = ""
        for n in range(1, total_sems + 1):
            menu += "/" + str(n) + " Semester " + roman[n] + "\n"
        user.temporary_utils["gradesheet"]["menu"] = menu

    current_sem = total_sems
    if command is not None:
        current_sem = int(command)
    ans = "Semester " + str(roman[current_sem]) + "\n" + ans
    user.temporary_utils["gradesheet"][current_sem] = ans
    if command is None:
        ans += ":::" + user.temporary_utils["gradesheet"]["menu"]
    print "went all the way lol"
    return ans


def change_grade_sheet_semester(user, value):
    drop_down = user.driver.find_element_by_xpath("//select[@id='ContentPlaceHolder1_ddlSemester']")
    list_elements = 0
    options = drop_down.find_elements_by_tag_name("option")
    for option in options:
        if option.get_attribute('value') not in "IVIII":
            continue
        list_elements += 1
    for option in options:
        if value != 0 and option.get_attribute('value') == roman[int(value)]:
            option.click()
            time.sleep(1)
            break
    return list_elements


""" MARKS """


def marks(user, command=None):
    user.current_tab = "marks"
    if "marks" not in user.temporary_utils:
        go_to_academics(user.driver)
        scrape_marks(user)
    if command is None:
        return user.temporary_utils["marks"]["menu"]
    else:
        return user.temporary_utils["marks"][int(command)]


def scrape_marks(user):
    marks_map = {}
    soup = bs(user.driver.page_source, "html.parser")
    divs = soup.find("div", {"class": "panel-group internalMarks"}).find_all("div", {"class": "panel panel-default"})
    menu = ""
    sessional1 = ""
    sessional2 = ""
    sessional1_score = 0
    sessional1_total = 0
    sessional2_score = 0
    sessional2_total = 0
    index = 1
    for subject in divs:
        subject_name = subject_title(string_utils.extract_subject_name(subject.h4.text))
        if " Lab" == subject_name[-4:]:
            continue
        s1 = 0.0
        s2 = 0.0
        am = 0.0
        tl = 0.0
        ans = "*" + subject_name + "*\n"
        tables = subject.find_all("tbody")
        for table in tables:
            rows = table.find_all("tr")
            if str(rows[0].th.string) == "Internal":
                for row in rows[1:-1]:
                    cols = row.find_all("td")
                    if "Sessional 1" in str(cols[0].string):
                        ans += "Sessional 1: *" + v(cols[2].string) + "/" + v(cols[1].string) + "*\n"
                        s1 += float(cols[2].string)
                        sessional1_score += float(cols[2].string)
                        sessional1_total += float(cols[1].string)
                        sessional1 += subject_name + ": *" + v(cols[2].string) + "/" + v(cols[1].string) + "*\n"
                        tl += float(cols[1].string)
                    elif "Sessional 2" in str(cols[0].string):
                        ans += "Sessional 2: *" + v(cols[2].string) + "/" + v(cols[1].string) + "*\n"
                        s2 += float(cols[2].string)
                        sessional2_score += float(cols[2].string)
                        sessional2_total += float(cols[1].string)
                        sessional2 += subject_name + ": *" + v(cols[2].string) + "/" + v(cols[1].string) + "*\n"
                        tl += float(cols[1].string)
            elif str(rows[0].th.string) == "Assignment":
                for row in rows[1:-1]:
                    cols = row.find_all("td")
                    ans += str(cols[0].string) + ": *" + v(cols[2].string) + "/" + v(cols[1].string) + "*\n"
                    am += float(cols[2].string)
                    tl += float(cols[1].string)
        if s1 + s2 + am > 0:
            ans += "Total: *" + v(s1 + s2 + am) + "/" + v(tl) + "*\n"
        marks_map[index] = ans
        menu += "/" + str(index) + " " + subject_name + "\n"
        index += 1
    if sessional1_total != 0:
        marks_map[index] = sessional1
        menu += "/" + str(index) + " Sessional 1\n"
        index += 1
    if sessional2_total != 0:
        marks_map[index] = sessional2
        menu += "/" + str(index) + " Sessional 2\n"
        index += 1
    marks_map["menu"] = menu
    user.temporary_utils["marks"] = marks_map


def logout(user):
    # user.current_tab = "logout"
    # user.temporary_utils["logout"]["menu"] = "Are you sure you want to log out?\n/1 Yes\n/2 No\n"
    # user.end_session()
    print "lol it does nothing yet"


def go_to_course_details(driver):
    driver.get("http://slcm.manipal.edu/Academics.aspx")
    time.sleep(1)
    driver.execute_script("document.querySelectorAll(\"[href='#2']\")[0].click()")
    time.sleep(1)


def go_to_timetable(driver):
    driver.get("http://slcm.manipal.edu/StudentTimeTable.aspx")
    time.sleep(1)


def semester_details(driver, n, current_tab):
    if current_tab != "course_details":
        go_to_course_details(driver)
    drop_down = driver.find_element_by_xpath("//select[@id='ContentPlaceHolder1_ddlSemesterCourseDetails']")
    options = drop_down.find_elements_by_tag_name("option")
    for o in options:
        if o.get_attribute('value') == roman[n]:
            o.click()
            break
    driver.find_element_by_xpath("//a[@id='ContentPlaceHolder1_LinkButton1']").click()
    time.sleep(1)
    soup = bs(driver.page_source, "html.parser")
    ret = []
    table = soup.find_all('table')[0]
    should_print = False
    for tag in table.tbody.find_all('td'):
        if should_print:
            ret.append(subject_title(tag.string))
            should_print = False
        if len(subject_code.findall(str(tag))) > 0:
            should_print = True
    return ret


def get_timetable(driver):
    soup = bs(driver.page_source, "html.parser")
    days_tt = soup.find_all("div", class_="fc-content-col")
    for i in range(len(days_tt)):
        print days[i] + ": "
        for period in days_tt[i].find_all("div", class_="fc-content"):
            print "\t" + period.span.string + "  -->  " \
                + subject_title(period.find_all("div", class_="fc-title")[0].string.split(", Section")[0])


def get_grade_details(driver, n):
    # go_to_grade_sheet(driver)
    drop_down = driver.find_element_by_xpath("//select[@id='ContentPlaceHolder1_ddlSemester']")
    for o in drop_down.find_elements_by_tag_name("option"):
        if o.get_attribute('value') == roman[n]:
            o.click()
            time.sleep(0.5)
            break
    soup = bs(driver.page_source, "html.parser")
    table = soup.find("tbody")
    subjects = table.find_all("tr")[1:]
    values = []
    for sub in subjects:
        x = sub.find_all("td")[2:4]
        name, grade = x[0].span.string, x[1].span.string
        values.append((name, grade))

    for x, y in values:
        print subject_title(x) + ":", y


tabs = {

        'attendance': attendance,
        'marks': marks,
        # 'timetable': timetable,
        # 'logout': logout
        'gradesheet': gradesheet

    }

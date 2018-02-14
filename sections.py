from bs4 import BeautifulSoup as bs
import time
import re
import string_utils
from pprint import pprint

subject_code = re.compile('[A-Z]{3} [0-9]{4}')

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


def go_to_academics(user):
    if str(user.driver.current_url) != "http://slcm.manipal.edu/Academics.aspx":
        user.driver.get("http://slcm.manipal.edu/Academics.aspx")
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
                  + string_utils.pascal_case(period.find_all("div", class_="fc-title")[0].string.split(", Section")[0]) + "\n"
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
        go_to_academics(user)
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
        sub = string_utils.pascal_case(cells[2].string)
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
        ans += string_utils.pascal_case(str(name)) + ": *" + str(grade) + "*\n"

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


def logout(user):
    # user.current_tab = "logout"
    # user.temporary_utils["logout"]["menu"] = "Are you sure you want to log out?\n/1 Yes\n/2 No\n"
    # user.end_session()
    print "lol it does nothing yet"


def marks(user):
    user.current_tab = "marks"
    go_to_academics(driver)


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
            ret.append(string_utils.pascal_case(tag.string))
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
                + string_utils.pascal_case(period.find_all("div", class_="fc-title")[0].string.split(", Section")[0])


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
        print string_utils.pascal_case(x) + ":", y


tabs = {

        'attendance': attendance,
        # 'marks': marks
        # 'timetable': timetable,
        # 'logout': logout
        'gradesheet': gradesheet

    }

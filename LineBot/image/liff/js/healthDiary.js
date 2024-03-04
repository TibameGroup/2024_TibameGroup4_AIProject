let weekList = [];

function getDateValue(userId) {
  let dateInput = document.getElementById("dateInput");
  let selectedDate = dateInput.value; // 2024-02-07
  date = new Date(selectedDate);
  datetime(date);
  dayofweek(date);
  fetchData(selectedDate, userId);
}

function ShowTime() {
  let Today = new Date();
  datetime(Today);
  dayofweek(Today);
}

async function fetchData(date, userId) {
  try {
    const dataToSend = {
      time: date,
      userId: userId,
    };
    const response = await fetch("/diary/healthDiary?userId=" + userId, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(dataToSend),
    });
    const html = await response.text();

    document.getElementById("content").innerHTML = html;
  } catch (error) {
    console.error("Error sending or fetching data:", error);
  }
}

function datetime(date) {
  let month = date.getMonth() + 1;
  let day = date.getDate();
  let year = date.getFullYear();
  let week = "";
  const days = [
    "星期日",
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
  ];
  week = days[date.getDay()];
  mondayDate = getMonday(date);
  document.getElementById("showtime").innerHTML =
    month + " 月 " + day + " 日 " + " " + week;
}

function changeWeekList(year, month, mondayDate) {
  let MonthLastDay = new Date(year, month, 0).getDate();
  for (let i = 0; i < 7; i++) {
    monthStr = month < 10 ? "0" + month : month.toString();
    mondayDateStr = mondayDate < 10 ? "0" + mondayDate : mondayDate.toString();
    weekList[i] = year + "-" + monthStr + "-" + mondayDateStr;
    mondayDate++;
    if (mondayDate > MonthLastDay) {
      mondayDate = 1;
      month++;
      if (month > 12) {
        month = 1;
        year++;
      }
    }
  }
  console.log(weekList);
}

function getMonday(date) {
  let day = date.getDate();
  let month = date.getMonth() + 1;
  let dayOfWeek = date.getDay();
  let year = date.getFullYear();
  dayOfWeek = dayOfWeek === 0 ? 6 : --dayOfWeek;
  let mondayDate = day - dayOfWeek;
  if (mondayDate <= 0) {
    let prevMonthLastDay = new Date(year, month - 1, 0).getDate();
    mondayDate = prevMonthLastDay + mondayDate;
    month--;
    if (month == 0) {
      year--;
      month = 12;
    }
  }
  console.log(year, month, mondayDate);
  changeWeekList(year, month, mondayDate);
  return mondayDate;
}

function dayofweek(date) {
  let week = "";
  const days = [".sun", ".mon", ".tue", ".wed", ".thu", ".fri", ".sat"];
  days.forEach((day) => {
    let activeLink = document.querySelector(day);
    activeLink.style.backgroundColor = "";
    activeLink.style.color = "";
  });
  week = days[date.getDay()];
  let activeLink = document.querySelector(week);
  activeLink.style.backgroundColor = "blue";
  activeLink.style.color = "white";
  activeLink.style.borderRadius = "50%";
}

function changeDay(index, userId) {
  let selectedDate = weekList[index]; // 2024-02-07
  date = new Date(selectedDate);
  datetime(date);
  dayofweek(date);
  fetchData(selectedDate, userId);
}

// let userinfo = document.getElementById("goHome");
// userinfo.addEventListener("click", function () {
//   window.location.href = "/diary/";
// });

function homeBtn(userId) {
  window.location.href = "/diary/?liff.state=/diary?userId=" + userId;
}

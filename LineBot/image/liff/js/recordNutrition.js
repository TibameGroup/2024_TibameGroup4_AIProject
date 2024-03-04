function ShowTime() {
  let Today = new Date();
  let month = Today.getMonth() + 1;
  let day = Today.getDate();
  let dayOfWeek = "";
  const days = [
    "星期日",
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
  ];
  dayOfWeek = days[Today.getDay()];
  document.getElementById("showtime").innerHTML =
    month + " 月 " + day + " 日 " + " " + dayOfWeek;
}


// let healthDiaryBtn = document.getElementById("healthDiaryBtn");

// healthDiaryBtn.addEventListener("click", function () {
//   window.location.href = `/diary/healthDiary?userId={{userId}}`;
// });

function healthDiary(userId) {
  console.log(userId);
  window.location.href = "/diary/healthDiary?userId=" + userId;
}

function changeUserInfo(userId) {
  window.location.href = "/diary/userinfo?userId=" + userId;
}

function toggleUserInfo() {
  const userInfoContainer = document.querySelector('.user-info');
  const userinfoButton = document.getElementById('userinfo');
  const bottomRightImg = document.querySelector('.bottom-right-img');

  if (userInfoContainer.style.display === 'none' || userInfoContainer.style.display === '') {
    userInfoContainer.style.display = 'flex';
    userinfoButton.style.display = 'inline-block';
    bottomRightImg.style.display = 'none'; 
  } else {
    userInfoContainer.style.display = 'none';
    userinfoButton.style.display = 'none';
    bottomRightImg.style.display = 'block'; 
  }
}




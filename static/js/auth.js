function initAuth() {
  //綁定登入及註冊事件監聽
  let auth_btn = document.querySelector("#auth_btn");
  let switchBtn = document.querySelector(".switchBtn");
  let modal_title = document.querySelector("#modal_title");
  let name_input = document.querySelector("#name_input");
  let email = document.querySelector("#email_input");
  let password = document.querySelector("#password_input");
  let modal_submit = document.querySelector(".modal_submit");
  let closeBtn = document.querySelector("#close_modal");
  let show_error_msg = document.querySelector("#show_error_message");
  closeBtn.addEventListener("click", () => {
    document.querySelector(".modal").style.display = "none";
  });
  auth_btn.addEventListener("click", () => {
    if (auth_btn.textContent == "登入/註冊") {
      document.querySelector(".modal").style.display = "block";
    }
  });
  switchBtn.addEventListener("click", () => {
    if (modal_title.textContent == "註冊會員帳號") {
      modal_title.textContent = "登入會員帳號";
      name_input.style.display = "none";
      modal_submit.textContent = "登入帳戶";
      switchBtn.textContent = "還沒有帳戶？點此註冊";
    } else {
      modal_title.textContent = "註冊會員帳號";
      modal_submit.textContent = "註冊新帳號";
      name_input.style.display = "block";
      switchBtn.textContent = "已經有帳戶了？點此登入";
      show_error_msg.textContent = "";
      email.value = "";
      password.value = "";
    }
  });

  // user 註冊帳號 ＆ 登入會員

  modal_submit.addEventListener("click", () => {
    let user_name = name_input.value;
    let user_email = email.value;
    let user_password = password.value;

    //註冊時給後端的request body
    let signupData = {
      name: user_name,
      email: user_email,
      password: user_password,
    };

    //登入時給後端的request body
    let signinData = {
      email: user_email,
      password: user_password,
    };

    //因為註冊和登入按鈕是同一個，所以先判斷在什麼頁面
    if (modal_title.textContent == "註冊會員帳號") {
      fetch("/api/user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(signupData),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.ok) {
            show_error_msg.textContent = "註冊成功請登入";
            setTimeout(() => {
              switchBtn.click(); //跳轉到登入視窗
              show_error_msg.textContent = "";
            }, 1000);

            //清空註冊欄位的資料
            name_input.value = "";
            email.value = "";
            password.value = "";
          } else {
            show_error_msg.textContent = data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    } else {
      //登入會員帳號的頁面
      fetch("/api/user/auth", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(signinData),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.token) {
            localStorage.setItem("token", data.token);
            show_error_msg.textContent = "登入成功";
            //清空欄位的資料
            name_input.value = "";
            email.value = "";
            password.value = "";
            setTimeout(() => {
              closeBtn.click();
              location.reload();
            }, 2000);
          } else {
            show_error_msg.textContent = data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  });
}

//檢查登入狀態
async function checkLoginStatus() {
  //去local storage拿token
  let token = localStorage.getItem("token");
  console.log(token);

  //如果沒有token就return
  if (!token) {
    return;
  }
  //有token
  try {
    let response = await fetch("/api/user/auth", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });
    let result = await response.json();
    console.log(result);

    if (result.data) {
      let authBtn = document.querySelector("#auth_btn");
      authBtn.textContent = "登出系統";
      //點擊登出系統
      authBtn.onclick = (e) => {
        e.stopPropagation();
        localStorage.removeItem("token");
        location.reload(); //重新整理頁面
      };
    }
  } catch (error) {
    console.error("error:", error);
  }
}

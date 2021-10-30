var login = document.getElementsByName("login-value")[0].value;
var copyLogin = document.getElementsByName("copy-login")[0];
var password = document.getElementsByName("pw-value")[0].value;
var pwField = document.getElementById("pw-field");
var pwLength = password.length;
var toggleBtn = document.getElementsByName("toggle")[0];
var copyPw = document.getElementsByName("copy-pw")[0];
var loginCopied = document.getElementById("login-copied");
var pwCopied = document.getElementById("pw-copied");


function pwVisibility() {
    pwField.textContent = pwField.className == "hide" ? '*'.repeat(pwLength) : password;
}

function toggleVisibility() {
    pwField.className = pwField.className == "hide" ? "show" : "hide";
    if (toggleBtn.classList.contains("hide-btn")) {
        toggleBtn.classList.remove("hide-btn");
        toggleBtn.classList.add("show-btn");
    }
    else if (toggleBtn.classList.contains("show-btn")) {
        toggleBtn.classList.remove("show-btn");
        toggleBtn.classList.add("hide-btn");
    }
    pwVisibility();
}

copyLogin.addEventListener("click", () => {
    navigator.clipboard.writeText(login);
    loginCopied.textContent = "Copied!";
    loginCopied.classList.add("copied");
    setTimeout(() => {
        loginCopied.textContent = "";
        loginCopied.classList.remove("copied");
    }, 3000);
});

pwVisibility();

toggleBtn.addEventListener("click", toggleVisibility);

copyPw.addEventListener("click", () => {
    navigator.clipboard.writeText(password);
    pwCopied.textContent = "Copied!";
    pwCopied.classList.add("copied");
    setTimeout(() => {
        pwCopied.textContent = "";
        pwCopied.classList.remove("copied");
    }, 3000);
});
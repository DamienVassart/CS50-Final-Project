var password = document.getElementsByName("password")[0];
var toggleBtn = document.getElementsByName("toggle")[0];
var genBtn = document.getElementById("generate");
var strength = document.getElementById("strength");

function pwVisibility(type) {
    switch (type) {
        case "password":
            password.setAttribute("type", "text");
            break;
        case "text":
            password.setAttribute("type", "password");
            break;
    }
}

function toggleVisibility(e) {
    e.preventDefault();

    if (toggleBtn.classList.contains("hide-btn")) {
        toggleBtn.classList.remove("hide-btn");
        toggleBtn.classList.add("show-btn");
    }
    else if (toggleBtn.classList.contains("show-btn")) {
        toggleBtn.classList.remove("show-btn");
        toggleBtn.classList.add("hide-btn");
    }

    pwVisibility(password.getAttribute("type"));
}

function pwdSettings() {
    var length = +document.getElementsByName("pw-length")[0].value;
    var useDigits = +document.getElementsByName("use-digits")[0].value !== 0;
    var useLower = +document.getElementsByName("use-lower")[0].value !== 0;
    var useUpper = +document.getElementsByName("use-upper")[0].value !== 0;
    var useSymbols = +document.getElementsByName("use-symbols")[0].value !== 0;

    var regex, range;
    var sum = [useDigits ? 1 : 0, useLower ? 2 : 0, useUpper ? 4 : 0, useSymbols ? 8 : 0].reduce((acc, curr) => acc + curr, 0);
    switch (sum) {
        case 1:
            regex = /[0-9]/;
            break;
        case 2:
            regex = /[a-z]/;
            break;
        case 3:
            regex = /[a-z0-9]/;
            break;
        case 4:
            regex = /[A-Z]/;
            break;
        case 5:
            regex = /[A-Z0-9]/;
            break;
        case 6:
            regex = /[A-Za-z]/;
            break;
        case 7:
            regex = /[A-Za-z0-9]/;
            break;
        case 8:
            regex = /\W|_/;
            break;
        case 9:
            regex = /\W|_|\d/;
            break;
        case 10:
            regex = /\W|_|[a-z]/;
            break;
        case 11:
            regex = /\W|_|[a-z0-9]/
            break;
        case 12:
            regex = /\W|_|[A-Z]/;
            break;
        case 13:
            regex = /\W|_|[A-Z0-9]/;
            range = 69;
            break;
        case 14:
            regex = /\W|_|[A-Za-z]/;
            break;
        case 15:
            regex = /./;
            break;
        }

        return [length, regex];
    }

function randomNumber() {
    let n = Math.trunc(Math.random() * 100) + 32;
    return n > 126 ? n - 5 : n;
}

function pwdGen() {
    var s = '';
    var pwLength = pwdSettings()[0];
    var regex = pwdSettings()[1];

    while (s.length < pwLength) {
        let c = String.fromCharCode(randomNumber());
        if (regex.test(c) && s.indexOf(c) === -1) s += c;
    }
    return s;
}

function computeStrength(s) {
    var hasDigits = (/[0-9]/g).test(s) ? 10 : 0;
    var hasLower = (/[a-z]/g).test(s) ? 26 : 0;
    var hasUpper = (/[A-Z]/g).test(s) ? 26 : 0;
    var hasSymbols = (/[A-Za-z0-9]/g).test(s) ? 33 : 0;

    var alphabetLength = hasDigits + hasLower + hasUpper + hasSymbols;

    var entropy = s.length * (Math.log(alphabetLength) / Math.log(2));

    return s.length > 0 ? Math.round(entropy) : 0;
}

function pwdStrength(password) {
    var entropy = computeStrength(password);
    if (password.length == 0) {
        strength.textContent = "--";
        strength.style.color= "grey";
    }
    else if (entropy < 50) {
        strength.textContent = "Weak";
        strength.style.color = "darkred";
    }
    else if (entropy > 50 && entropy < 100) {
        strength.textContent = "Average";
        strength.style.color = "orange";
    }
    else {
        strength.textContent = "Good";
        strength.style.color = "darkgreen";
    }
}

toggleBtn.addEventListener("click", toggleVisibility)

genBtn.addEventListener("click", () => {
        password.value = pwdGen();
        pwdStrength(password.value);
    });

window.addEventListener("load", () => pwdStrength(password.value));

password.addEventListener("input", () => pwdStrength(password.value));
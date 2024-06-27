// ---------- SignIn Btn ---------- //
const signInContainer = document.getElementById("signin-container");
const signInBtn = document.getElementById("signin-btn");
const signInSuccess = document.getElementById("signin-success");
const signInError = document.getElementById("signin-error");

signInBtn.addEventListener("click", () => {
    if (signInSuccess.style.display == "block") {
        location.reload();
        return;
    }
    const email = document.getElementById("signin-email").value.trim();
    const password = document.getElementById("signin-password").value.trim();

    if (email === "" || password === "") {
        signInError.textContent = "";
        signInError.textContent = "請填寫完整的信箱和密碼";
        signInContainer.style.height = "310px";
        signInError.style.display = "block";
    } else {
        fetch("/api/user/auth", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email,
                password,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.token) {
                    const token = data.token;
                    localStorage.setItem("authToken", token);

                    signInError.style.display = "none";
                    signInContainer.style.height = "310px";
                    signInSuccess.style.display = "block";

                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                }
                if (data.error) {
                    signInError.textContent = "";
                    signInError.textContent = "信箱或密碼錯誤";
                    signInContainer.style.height = "310px";
                    signInError.style.display = "block";
                }
            })
            .catch((error) => console.error("Error: ", error));
    }
});

// ---------- SignUp Btn ---------- //
const signUpContainer = document.getElementById("signup-container");
const signUpBtn = document.getElementById("signup-btn");
const signUpSuccess = document.getElementById("signup-success");
const signUpError = document.getElementById("signup-error");

signUpBtn.addEventListener("click", () => {
    if (signUpSuccess.style.display == "block") {
        signUpContainer.style.display = "none";
        signUpSuccess.style.display = "none";
        signUpError.style.display = "none";
        signUpContainer.style.height = "335px";
        clearSignUpInputs();
        signInContainer.style.display = "block";
    }

    const name = document.getElementById("signup-name").value;
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value.trim();

    if (name === "" || email === "" || password === "") {
        signUpError.textContent = "";
        signUpError.textContent = "請填寫完整的姓名、信箱和密碼";
        signUpContainer.style.height = "370px";
        signUpError.style.display = "block";
    } else {
        fetch("/api/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                email,
                password,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.ok) {
                    signUpError.style.display = "none";
                    signUpContainer.style.height = "370px";
                    signUpSuccess.style.display = "block";

                    setTimeout(() => {
                        signUpContainer.style.display = "none";
                        signInContainer.style.display = "block";
                    }, 2000);
                }
                if (data.error) {
                    signUpError.textContent = "";
                    signUpError.textContent = "此信箱已被註冊";
                    signUpContainer.style.height = "370px";
                    signUpError.style.display = "block";
                }
            })
            .catch((error) => console.error("Error: ", error));
    }
});

// ------- Switch between SignIn & SignUp dialog ------- //
const clickToSignUp = document.getElementById("click-to-signup");
const clickToSignIn = document.getElementById("click-to-signin");

const clearSignInInputs = () => {
    const signInInputs = signInContainer.querySelectorAll("input");
    signInInputs.forEach((input) => {
        input.value = "";
    });
};

const clearSignUpInputs = () => {
    const signUpInputs = signUpContainer.querySelectorAll("input");
    signUpInputs.forEach((input) => {
        input.value = "";
    });
};

clickToSignUp.addEventListener("click", () => {
    if (signInSuccess.style.display == "block") {
        location.reload();
        return;
    }
    signInContainer.style.display = "none";
    signInError.style.display = "none";
    signInContainer.style.height = "275px";
    clearSignInInputs();
    signUpContainer.style.display = "block";
});

clickToSignIn.addEventListener("click", () => {
    signUpContainer.style.display = "none";
    signUpSuccess.style.display = "none";
    signUpError.style.display = "none";
    signUpContainer.style.height = "335px";
    clearSignUpInputs();
    signInContainer.style.display = "block";
});

// ---------- Close Btn ---------- //
const popupBackground = document.getElementById("popup-background");
const closeBtns = document.querySelectorAll(".popup-close");

closeBtns.forEach((closeBtn) => {
    closeBtn.addEventListener("click", () => {
        if (signInSuccess.style.display == "block") {
            location.reload();
            return;
        }

        popupBackground.style.visibility = "hidden";
        popupBackground.style.opacity = 0;

        signInContainer.style.display = "none";
        signInContainer.style.height = "275px";
        signInError.style.display = "none";
        clearSignInInputs();

        signUpContainer.style.display = "none";
        signUpContainer.style.height = "335px";
        signUpSuccess.style.display = "none";
        signUpError.style.display = "none";
        clearSignUpInputs();
    });
});

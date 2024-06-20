const menuItems = document.getElementById("menu-items");
let menuTitle = "";
let idName = "";
const createMenuItem = (menuTitle, idName) => {
    if (menuItems.children.length > 1) {
        menuItems.removeChild(menuItems.lastElementChild);
    }
    const menuItem = document.createElement("li");
    menuItem.id = idName;
    menuItem.textContent = menuTitle;
    return menuItem;
};

const token = localStorage.getItem("authToken");
if (!token) {
    menuTitle = "登入/註冊";
    idName = "signin-signup";
    menuItems.appendChild(createMenuItem(menuTitle, idName));

    const signInSignUp = document.getElementById("signin-signup");
    signInSignUp.addEventListener("click", () => {
        const popupBackground = document.getElementById("popup-background");
        popupBackground.style.visibility = "visible";
        popupBackground.style.opacity = 1;

        const signInContainer = document.getElementById("signin-container");
        if (signInContainer.style.display === "none") {
            signInContainer.style.display = "block";
        }
    });
} else {
    fetch("/api/user/auth", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.data) {
                menuTitle = "登出系統";
                idName = "signout";
                menuItems.appendChild(createMenuItem(menuTitle, idName));

                const signout = document.getElementById("signout");
                signout.addEventListener("click", () => {
                    const tokenKey = "authToken";
                    const token = localStorage.getItem(tokenKey);
                    if (!token) {
                        location.reload();
                    } else {
                        localStorage.removeItem(tokenKey);
                        location.reload();
                    }
                });
            } else {
                menuTitle = "登入/註冊";
                idName = "signin-signup";
                menuItems.appendChild(createMenuItem(menuTitle, idName));

                const signInSignUp = document.getElementById("signin-signup");
                signInSignUp.addEventListener("click", () => {
                    const popupBackground =
                        document.getElementById("popup-background");
                    popupBackground.style.visibility = "visible";
                    popupBackground.style.opacity = 1;

                    const signInContainer =
                        document.getElementById("signin-container");
                    if (signInContainer.style.display === "none") {
                        signInContainer.style.display = "block";
                    }
                });
            }
        })
        .catch((error) => console.error("Error: ", error));
}

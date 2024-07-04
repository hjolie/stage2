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

const messageContainer = document.getElementById("message-container");
const renderOrderNumber = (orderNumber) => {
    const number = document.createElement("p");
    number.id = "order-number";
    number.textContent = orderNumber;
    return number;
};

const getOrderNumberFromUrl = () => {
    const queryString = window.location.search.substring(1);
    const queryStrSplit = queryString.split("=");
    const orderNumber = queryStrSplit[queryStrSplit.length - 1];
    return orderNumber;
};

const token = localStorage.getItem("authToken");
if (!token) {
    window.location.href = "/";
} else {
    fetch("/api/user/auth", {
        method: "GET",
        headers: {
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
                        window.location.href = "/";
                    } else {
                        localStorage.removeItem(tokenKey);
                        window.location.href = "/";
                    }
                });

                const orderNumber = getOrderNumberFromUrl();
                messageContainer.appendChild(renderOrderNumber(orderNumber));
            } else {
                window.location.href = "/";
            }
        })
        .catch((error) => console.error("Error: ", error));
}

const cartBtn = document.getElementById("cart-btn");
cartBtn.addEventListener("click", () => {
    const token = localStorage.getItem("authToken");
    if (!token) {
        const signInSignUp = document.getElementById("signin-signup");
        if (!signInSignUp) {
            location.reload();
        } else {
            signInSignUp.click();
        }
    } else {
        window.location.href = "/booking";
    }
});

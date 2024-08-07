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

let id;
let image;
let name1;
let date;
let time;
let price;
let address;

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
                const name = data.data.name;
                const email = data.data.email;
                renderGreeting(name);
                renderUserInfo(name, email);

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
            } else {
                window.location.href = "/";
            }
        })
        .catch((error) => console.error("Error: ", error));

    fetch("/api/booking", {
        method: "GET",
        headers: {
            Authorization: "Bearer " + token,
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.data === null) {
                const footer = document.querySelector("footer");
                footer.style.height = "72vh";
                footer.style.alignItems = "flex-start";
                footer.style.paddingTop = "40px";

                const noBookingContainer = document.getElementById(
                    "no-booking-container"
                );
                noBookingContainer.style.display = "block";
            } else {
                image = data.data.attraction.image;
                name1 = data.data.attraction.name;
                date = data.data.date;
                time = data.data.time;
                price = data.data.price;
                address = data.data.attraction.address;
                id = data.data.attraction.id;

                renderAttractionInfo(image, name1, date, time, price, address);
                renderTotalPrice(price);

                const hasBookingContainer = document.getElementById(
                    "has-booking-container"
                );
                hasBookingContainer.style.display = "block";

                handleDeleteBtn();
            }
        })
        .catch((error) => console.error("Error: ", error));
}

const renderGreeting = (name) => {
    const greetingContainer = document.getElementById("greeting-container");
    greetingContainer.textContent = `您好，${name}，待預訂的行程如下：`;
};

const renderAttractionInfo = (image, name, date, time, price, address) => {
    const imageContainer = document.getElementById("image-container");
    imageContainer.style.backgroundImage = `url(${image})`;

    const titleContainer = document.getElementById("title-container");
    titleContainer.textContent = `台北一日遊：${name}`;

    const dateContainer = document.getElementById("date-container");
    const bookedDate = document.createElement("p");
    bookedDate.textContent = date;
    dateContainer.appendChild(bookedDate);

    const timeContainer = document.getElementById("time-container");
    const bookedTime = document.createElement("p");
    if (time === "morning") {
        bookedTime.textContent = "早上 9 點到下午 4 點";
    }
    if (time === "afternoon") {
        bookedTime.textContent = "下午 2 點到晚上 9 點";
    }
    timeContainer.appendChild(bookedTime);

    const priceContainer = document.getElementById("price-container");
    const bookingPrice = document.createElement("p");
    bookingPrice.textContent = `新台幣 ${price} 元`;
    priceContainer.appendChild(bookingPrice);

    const addressContainer = document.getElementById("address-container");
    const spotAddress = document.createElement("p");
    spotAddress.textContent = address;
    addressContainer.appendChild(spotAddress);
};

const renderUserInfo = (name, email) => {
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    nameInput.value = name;
    emailInput.value = email;
};

const renderTotalPrice = (price) => {
    const totalPrice = document.getElementById("total-price");
    totalPrice.textContent = `總價：新台幣 ${price} 元`;
};

const handleSubmitBtn = (
    prime,
    id,
    image,
    name,
    date,
    time,
    price,
    address
) => {
    const token = localStorage.getItem("authToken");
    if (!token) {
        window.location.href = "/";
    } else {
        const contactName = document.getElementById("name").value;
        const contactEmail = document.getElementById("email").value;
        const contactCell = document.getElementById("cell").value;

        const requestBody = {
            prime: prime,
            order: {
                price: price,
                trip: {
                    attraction: {
                        id: id,
                        name: name,
                        address: address,
                        image: image,
                    },
                    date: date,
                    time: time,
                },
                contact: {
                    name: contactName,
                    email: contactEmail,
                    phone: contactCell,
                },
            },
        };

        fetch("/api/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token,
            },
            body: JSON.stringify(requestBody),
        })
            .then((response) => response.json())
            .then((data) => {
                const orderNumber = data.data.number;
                const status = data.data.payment.status;
                if (status === 0) {
                    window.location.href = `/thankyou?number=${orderNumber}`;
                } else {
                    alert(`付款失敗，訂單編號：${orderNumber}`);
                }
            })
            .catch((error) => console.error("Error: ", error));
    }
};

const handleDeleteBtn = () => {
    const deleteBtn = document.getElementById("delete-btn");
    deleteBtn.addEventListener("click", () => {
        const token = localStorage.getItem("authToken");
        if (!token) {
            window.location.href = "/";
        } else {
            fetch("/api/booking", {
                method: "DELETE",
                headers: {
                    Authorization: "Bearer " + token,
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.ok) {
                        location.reload();
                    }
                })
                .catch((error) => console.error("Error: ", error));
        }
    });
};

const cartBtn = document.getElementById("cart-btn");
cartBtn.addEventListener("click", () => {
    location.reload();
});

// Image Slider
const imageSliderContainer = document.getElementById("image-slider-container");
const imageContainer = document.createElement("div");
imageContainer.className = "image-container";

const createImage = (image) => {
    imageContainer.style.backgroundImage = "none";
    imageContainer.style.backgroundImage = `url(${image})`;
    return imageContainer;
};

const createImageDots = (length) => {
    const dotsContainer = document.createElement("div");
    dotsContainer.id = "dots-container";
    for (let i = 0; i < length; i++) {
        const dot = document.createElement("p");
        dot.className = "dot";
        dotsContainer.appendChild(dot);
    }
    return dotsContainer;
};

const renderImages = (data) => {
    const images = data.data.images;
    const firstImage = images[0];
    const imagesLength = images.length;

    imageSliderContainer.appendChild(createImage(firstImage));
    imageSliderContainer.appendChild(createImageDots(imagesLength));
};

const switchImages = (data) => {
    const images = data.data.images;
    const imagesLength = images.length;

    const arrowLeft = document.getElementById("arrow-left");
    const arrowRight = document.getElementById("arrow-right");
    const dots = document.querySelectorAll(".dot");

    let index = 0;
    dots[index].classList.add("dot-current");

    arrowRight.addEventListener("click", () => {
        dots[index].classList.remove("dot-current");
        index++;
        if (index == imagesLength) {
            index = 0;
        }

        const nextImage = images[index];
        imageSliderContainer.appendChild(createImage(nextImage));
        dots[index].classList.add("dot-current");
    });

    arrowLeft.addEventListener("click", () => {
        dots[index].classList.remove("dot-current");
        index--;
        if (index < 0) {
            index = imagesLength - 1;
        }

        const prevImage = images[index];
        imageSliderContainer.appendChild(createImage(prevImage));
        dots[index].classList.add("dot-current");
    });
};

// Spot Title & Info
const titleDateContainer = document.getElementById("title-date-container");

const createTitleInfo = (name, category, mrt) => {
    const titleContainer = document.createElement("div");
    titleContainer.id = "title-container";

    const spotName = document.createElement("p");
    spotName.id = "spot-name";
    spotName.textContent = name;

    const spotInfo = document.createElement("p");
    spotInfo.id = "spot-info";
    if (mrt === null) {
        spotInfo.textContent = category;
    } else {
        spotInfo.textContent = `${category} at ${mrt}`;
    }

    titleContainer.appendChild(spotName);
    titleContainer.appendChild(spotInfo);

    return titleContainer;
};

const renderTitleInfo = (data) => {
    const name = data.data.name;
    const category = data.data.category;
    const mrt = data.data.mrt;

    const titleDiv = titleDateContainer.appendChild(
        createTitleInfo(name, category, mrt)
    );
    titleDateContainer.insertBefore(titleDiv, titleDateContainer.firstChild);
};

// Display fee based on the time selected
const selectTime = () => {
    const feeContainer = document.getElementById("fee-container");
    const timeOptions = document.querySelectorAll("input[name='time']");
    const fee = document.createElement("p");

    fee.id = "fee";
    fee.textContent = " 新台幣 2000 元";
    feeContainer.appendChild(fee);

    timeOptions.forEach((option) => {
        const selectedTime = option.value;
        option.addEventListener("change", () => {
            fee.textContent = "";
            if (selectedTime === "first-half-day") {
                fee.textContent = " 新台幣 2000 元";
            } else if (selectedTime === "second-half-day") {
                fee.textContent = " 新台幣 2500 元";
            }
            feeContainer.appendChild(fee);
        });
    });
};

// Spot Details
const detailsContainer = document.getElementById("details-container");

const createDetails = (description, address, transport) => {
    const descriptionContainer = document.createElement("div");
    descriptionContainer.id = "description-container";
    const addressContainer = document.createElement("div");
    addressContainer.id = "address-container";
    const transportContainer = document.createElement("div");
    transportContainer.id = "transport-container";

    const spotDescription = document.createElement("p");
    spotDescription.textContent = description;
    const spotAddressTitle = document.createElement("p");
    spotAddressTitle.textContent = "景點地址：";
    const spotAddress = document.createElement("p");
    spotAddress.textContent = address;
    const spotTransportTitle = document.createElement("p");
    spotTransportTitle.textContent = "交通方式：";
    const spotTransport = document.createElement("p");
    spotTransport.textContent = transport;

    descriptionContainer.appendChild(spotDescription);
    addressContainer.appendChild(spotAddressTitle);
    addressContainer.appendChild(spotAddress);
    transportContainer.appendChild(spotTransportTitle);
    transportContainer.appendChild(spotTransport);

    return [descriptionContainer, addressContainer, transportContainer];
};

const renderDetails = (data) => {
    const description = data.data.description;
    const address = data.data.address;
    const transport = data.data.transport;

    const elements = createDetails(description, address, transport);
    elements.forEach((element) => {
        detailsContainer.appendChild(element);
    });
};

// Fetch Attraction API
const fetchDataById = (id) => {
    return fetch(`/api/attraction/${id}`).then((response) => {
        if (!response.ok) {
            if (response.status === 400) {
                window.location.href = "/";
            } else {
                throw new Error(`HTTP Error Status: ${response.status}`);
            }
        }
        return response.json();
    });
};

const getIdFromUrl = () => {
    const path = window.location.pathname; // "/attraction/1"
    const pathSplit = path.split("/"); // ["", "attraction", "1"]
    const idString = pathSplit[pathSplit.length - 1]; // last one which is "1"
    const idInt = parseInt(idString, 10); // Convert "1" to 1
    return idInt;
};

const id = getIdFromUrl();
if (id) {
    fetchDataById(id)
        .then((data) => {
            if (data) {
                renderImages(data);
                switchImages(data);
                renderTitleInfo(data);
                selectTime();
                renderDetails(data);
            } else {
                console.error("Unexpected response structure: ", data);
            }
        })
        .catch((error) =>
            console.error("Error Loading Selected Attraction: ", error)
        );
} else {
    window.location.href = "/";
}

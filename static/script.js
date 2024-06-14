function createSpotItems(id, imageUrl, name, mrt, category) {
    const link = document.createElement("a");
    const linkUrl = `/attraction/${id}`;
    link.setAttribute("href", linkUrl);
    link.setAttribute("target", "_blank");

    const spotItem = document.createElement("div");
    spotItem.className = "spot-item";

    const spotImage = document.createElement("div");
    spotImage.className = "spot-image";
    spotImage.style.backgroundImage = `url(${imageUrl})`;

    const spotName = document.createElement("p");
    spotName.className = "spot-name";
    spotName.textContent = name;

    const spotDetails = document.createElement("div");
    spotDetails.className = "spot-details";

    const spotMrt = document.createElement("p");
    spotMrt.textContent = mrt;

    const spotCategory = document.createElement("p");
    spotCategory.textContent = category;

    spotDetails.appendChild(spotMrt);
    spotDetails.appendChild(spotCategory);

    spotItem.appendChild(spotImage);
    spotItem.appendChild(spotName);
    spotItem.appendChild(spotDetails);

    link.appendChild(spotItem);

    return link;
}

function createMrtList(mrt) {
    const mrtItem = document.createElement("button");
    mrtItem.textContent = mrt;
    return mrtItem;
}

document.addEventListener("DOMContentLoaded", () => {
    const spotContainerByPage = document.getElementById(
        "spot-container-by-page"
    );
    const spotContainerByKeyword = document.getElementById(
        "spot-container-by-keyword"
    );
    const searchBox = document.getElementById("search-box");
    const searchBtn = document.getElementById("search-btn");
    const loadMore = document.getElementById("load-more");
    const mrtListContainer = document.getElementById("mrt-list-container");

    let nextPage = 0;
    let keyword = "";
    let isLoading = true;
    let loadedPages = new Set();

    const fetchDataByPage = (page) => {
        return fetch(`/api/attractions?page=${page}`).then((response) =>
            response.json()
        );
    };

    const fetchDataByKeyword = (page, keyword) => {
        return fetch(`/api/attractions?page=${page}&keyword=${keyword}`).then(
            (response) => response.json()
        );
    };

    const fetchMrtList = () => {
        return fetch("/api/mrts").then((response) => response.json());
    };

    const renderDataByPage = (data) => {
        for (let i = 0; i < data.data.length; i++) {
            const spotId = data.data[i].id;
            const firstImage = data.data[i].images[0];
            const spotName = data.data[i].name;
            const spotMrt = data.data[i].mrt;
            const spotCategory = data.data[i].category;

            spotContainerByPage.appendChild(
                createSpotItems(
                    spotId,
                    firstImage,
                    spotName,
                    spotMrt,
                    spotCategory
                )
            );
        }
    };

    const renderDataByKeyword = (data) => {
        for (let i = 0; i < data.data.length; i++) {
            const spotId = data.data[i].id;
            const firstImage = data.data[i].images[0];
            const spotName = data.data[i].name;
            const spotMrt = data.data[i].mrt;
            const spotCategory = data.data[i].category;

            spotContainerByKeyword.appendChild(
                createSpotItems(
                    spotId,
                    firstImage,
                    spotName,
                    spotMrt,
                    spotCategory
                )
            );
        }
    };

    const renderMrtList = (data) => {
        for (let i = 0; i < data.data.length; i++) {
            const mrt = data.data[i];
            mrtListContainer.appendChild(createMrtList(mrt));
        }
    };

    const loadNextPage = () => {
        if (nextPage === null || isLoading || loadedPages.has(nextPage)) return;

        isLoading = true;

        if (keyword) {
            fetchDataByKeyword(nextPage, keyword)
                .then((data) => {
                    loadedPages.add(nextPage);
                    nextPage = data.nextPage;
                    renderDataByKeyword(data);
                    isLoading = false;
                })
                .catch((error) => {
                    console.error("Error Loading Search Data:", error);
                    isLoading = false;
                });
        } else {
            fetchDataByPage(nextPage)
                .then((data) => {
                    loadedPages.add(nextPage);
                    nextPage = data.nextPage;
                    renderDataByPage(data);
                    isLoading = false;
                })
                .catch((error) => {
                    console.error("Error Loading Data:", error);
                    isLoading = false;
                });
        }
    };

    fetchMrtList()
        .then((data) => {
            renderMrtList(data);

            const mrtStations = mrtListContainer.querySelectorAll("button");

            mrtStations.forEach((station) => {
                station.addEventListener("click", searchByMrt);
            });
        })
        .catch((error) => {
            console.error("Error Loading Mrt List:", error);
        });

    // Load the initial 12 items
    fetchDataByPage(nextPage)
        .then((data) => {
            loadedPages.add(nextPage);
            nextPage = data.nextPage;
            renderDataByPage(data);
            spotContainerByPage.style.display = "grid";
            isLoading = false;
        })
        .catch((error) => {
            console.error("Error Loading Initial Data:", error);
            isLoading = false;
        });

    const observer = new IntersectionObserver((elements) => {
        if (elements[0].isIntersecting) {
            loadNextPage();
        }
    });

    observer.observe(loadMore);

    // -------------- KEYWORD SEARCH -------------- //
    searchBtn.addEventListener("click", () => {
        keyword = searchBox.value;

        if (keyword) {
            isLoading = true;
            nextPage = 0;
            loadedPages.clear();

            fetchDataByKeyword(nextPage, keyword)
                .then((data) => {
                    loadedPages.add(nextPage);
                    nextPage = data.nextPage;
                    spotContainerByKeyword.innerHTML = "";
                    renderDataByKeyword(data);
                    spotContainerByPage.style.display = "none";
                    spotContainerByKeyword.style.display = "grid";
                    isLoading = false;
                })
                .catch((error) => {
                    console.error("Error Loading Search Data:", error);
                    isLoading = false;
                });
        } else {
            return;
        }
    });

    // -------------- MRT SEARCH -------------- //
    function searchByMrt(event) {
        isLoading = true;
        searchBox.value = event.target.innerText;
        keyword = searchBox.value;
        nextPage = 0;
        loadedPages.clear();

        fetchDataByKeyword(nextPage, keyword)
            .then((data) => {
                loadedPages.add(nextPage);
                nextPage = data.nextPage;
                spotContainerByKeyword.innerHTML = "";
                renderDataByKeyword(data);
                spotContainerByPage.style.display = "none";
                spotContainerByKeyword.style.display = "grid";
                isLoading = false;
            })
            .catch((error) => {
                console.error("Error Loading Search Data:", error);
                isLoading = false;
            });
    }

    // -------------- MRT SCROLL -------------- //
    const arrowLeft = document.getElementById("arrow-left");
    const arrowRight = document.getElementById("arrow-right");

    arrowLeft.addEventListener("click", () => {
        mrtListContainer.scrollBy({
            left: -250,
            behavior: "smooth",
        });
    });

    arrowRight.addEventListener("click", () => {
        mrtListContainer.scrollBy({
            left: 250,
            behavior: "smooth",
        });
    });
});

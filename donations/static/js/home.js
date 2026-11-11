const searchInput = document.getElementById("foodSearch");
    const filterButtons = document.querySelectorAll(".filter-btn");
    const foodItems = document.querySelectorAll(".food-item");
    const noResults = document.getElementById("noSearchResults");

    let activeFilter = "all";

    function getFoodCategory(name) {
        const food = name.toLowerCase();

        const riceMeals = [
            "rice", "biryani", "pulao", "khichdi", "thali",
            "paratha", "roti", "chapati", "dal", "curry",
            "dosa", "idli", "poha", "upma", "meal"
        ];

        const vegetables = [
            "vegetable", "vegetables", "potato", "tomato",
            "onion", "carrot", "spinach", "cabbage",
            "cauliflower", "broccoli", "beans", "peas"
        ];

        const fruits = [
            "fruit", "fruits", "apple", "banana", "mango",
            "orange", "grapes", "papaya", "watermelon",
            "pineapple", "guava"
        ];

        if (riceMeals.some(word => food.includes(word))) {
            return "rice";
        }

        if (vegetables.some(word => food.includes(word))) {
            return "vegetables";
        }

        if (fruits.some(word => food.includes(word))) {
            return "fruits";
        }

        return "other";
    }


    foodItems.forEach(item => {
        item.dataset.category = getFoodCategory(item.dataset.name);
    });

    function filterFood() {
        const searchText = searchInput.value.toLowerCase().trim();
        let visibleCount = 0;

        foodItems.forEach(item => {
            const name = item.dataset.name || "";
            const location = item.dataset.location || "";

            const matchesSearch =
                name.includes(searchText) ||
                location.includes(searchText);

            const matchesCategory =
                activeFilter === "all" ||
                item.dataset.category === activeFilter;

            const visible = matchesSearch && matchesCategory;

            item.style.display = visible ? "" : "none";

            if (visible) visibleCount++;
        });

        noResults.style.display =
            visibleCount === 0 && foodItems.length > 0
                ? "block"
                : "none";
    }

    searchInput.addEventListener("input", filterFood);

    filterButtons.forEach(button => {
        button.addEventListener("click", () => {
            filterButtons.forEach(btn =>
                btn.classList.remove("active")
            );

            button.classList.add("active");
            activeFilter = button.dataset.filter;

            filterFood();
        });
    });

$(document).ready(function () {
    $('#filterButton').on('click', function (event) {
        update_items(event);
    });
    $('#limitDropdown').on('change', function (event) {
        update_items(event)
    });
    $('#sortDropdown').on('change', function (event) {
        update_items(event);
    });
    $('#searchQuery').keydown(function (event) {
        if (event.key === "Enter") {
            update_items(event);
            event.preventDefault();
        }
    });
    $('#clearFilterButton').on('click', function (event) {
        update_items(event);
    });

    var lastScrollTop = 0;

    $(window).scroll(function () {
        var currentScroll = $(this).scrollTop();

        if (currentScroll > lastScrollTop) {
            $('.navbar').addClass('nav-hidden');
        } else {
            $('.navbar').removeClass('nav-hidden');
        }
        lastScrollTop = currentScroll;
    });
});

function update_items(event) {
    let elementId = event.target.id;

    let price_min = $('#priceMin').val();
    let price_max = $('#priceMax').val();
    let c = $('#category');
    let category = $('option:selected', c).attr('category_id');
    let avg_product_rating_min = $('#avgProductRatingMin').val();
    let avg_seller_rating_min = $('#avgSellerRatingMin').val();

    let searchQuery = '';
    if (elementId === 'searchQuery') {
        searchQuery = $('#searchQuery').val();
    }

    let filter_dict = {
        'price_min': price_min,
        'price_max': price_max,
        'category': category,
        'avg_product_rating_min': avg_product_rating_min,
        'avg_seller_rating_min': avg_seller_rating_min,
        'search_query': searchQuery,
    };

    let per_page = $('#limitDropdown').val();
    let sort_by = $('#sortDropdown').val();

    let queryParams = $.param(filter_dict);
    let url = '/?sort_by=' + encodeURIComponent(sort_by) + '&' + queryParams + '&per_page=' + per_page + '&elementId=' + elementId;
    window.location.href = url;
}
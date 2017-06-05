$(function() {
    $('#search').keyup(function() {
        $.ajax({
            type: "POST",
            url: "/chat/search/",
            data: {
                'category': $('#search-toggle').text(),
                'message' : $('#search').val(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });

    });

});

function searchSuccess(data, textStatus, jqXHR)
{
    $('#search-results').html(data);
}
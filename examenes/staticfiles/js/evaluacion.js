$(document).ready(function()
    {
        // alert("Welcome to JQuery")
        $('#valor').text($('#rango').val())
        $('#rango').click(()=> $('#valor').text($('#rango').val()));
        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
          })

          $('.my-rating').click(()=>console.log($('.my-rating').starRating('getRating')));
          $('.my-rating').click(()=>$('#rating').val(($('.my-rating').starRating('getRating'))));
    }
)

$(".my-rating").starRating({
    initialRating:parseFloat($('#rating').val()),
    strokeColor: 'lightgray',
    activeColor: '#FFE000',
    hoverColor: '#FFE000',
    ratedColor: '#FFE000',
    strokeWidth: 10,
    starSize: 28,
    starShape: 'rounded',
    useGradient: false
  });

